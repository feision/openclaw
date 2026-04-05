#!/usr/bin/env python3
"""
灵活部署 - 推送指定文件/目录到 GitHub

用法:
  # 直接模式：推送到指定分支（可创建 PR）
  python3 github_deploy.py --repo feision/repo --branch main --path file1.md --path dir1/

  # F方案（feature 模式）：先推送到开发分支，再 PR 到主分支
  python3 github_deploy.py --repo feision/repo --dev-branch openclaw --path file1.md --path dir1/ --mode feature

示例:
  # 推送多个文件到 main（直接）
  python3 deploy/github_deploy.py \
    --repo feision/openclaw \
    --branch main \
    --path SOUL.md --path USER.md

  # F方案：推送到 openclaw 子分支，再 PR 合并到 main
  python3 deploy/github_deploy.py \
    --repo feision/openclaw \
    --dev-branch openclaw \
    --base-branch main \
    --mode feature \
    --path SOUL.md --path USER.md --path MEMORY.md \
    --commit-msg "Update configs"

  # 强制推送开发分支（谨慎）
  python3 deploy/github_deploy.py \
    --repo feision/openclaw \
    --dev-branch feature/new-ui \
    --mode feature \
    --path ui/ \
    --force
"""

import os
import sys
import json
import argparse
import tempfile
import shutil
from pathlib import Path

def run_cmd(cmd, capture=True):
    """执行 shell 命令"""
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        if capture:
            print(f"   错误: {result.stderr}")
        sys.exit(1)
    return result.stdout if capture else None

def check_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ 请先设置 GITHUB_TOKEN 环境变量")
        print("   export GITHUB_TOKEN='ghp_...'")
        sys.exit(1)
    return token

def github_request(url, token, method='GET', data=None):
    """GitHub API 请求"""
    import urllib.request
    headers = {'Authorization': f'token {token}'}
    if data:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        response = urllib.request.urlopen(req, timeout=15)
        return json.load(response)
    except urllib.error.HTTPError as e:
        error = e.read().decode() if hasattr(e, 'read') and e.read() else str(e)
        print(f"❌ GitHub API 错误: {e.code} - {error}")
        sys.exit(1)

def ensure_repo(token, repo, description="Deployed via OpenClaw"):
    """确保仓库存在"""
    try:
        github_request(f'https://api.github.com/repos/{repo}', token)
        print(f"✅ 仓库已存在: {repo}")
        return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"🔄 创建仓库: {repo}")
            name = repo.split('/')[-1]
            data = {'name': name, 'description': description, 'private': False, 'auto_init': False}
            result = github_request('https://api.github.com/user/repos', token, method='POST', data=data)
            print(f"✅ 仓库创建成功: {result['html_url']}")
            return True
        else:
            raise

def ensure_branch(token, repo, branch, from_branch=None):
    """确保分支存在，如不存在则从 from_branch 创建"""
    try:
        github_request(f'https://api.github.com/repos/{repo}/branches/{branch}', token)
        print(f"✅ 分支已存在: {branch}")
        return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            if from_branch:
                print(f"🔄 创建分支: {branch} (基于 {from_branch})")
                # 获取 from_branch 的最新 commit SHA
                branch_info = github_request(f'https://api.github.com/repos/{repo}/branches/{from_branch}', token)
                sha = branch_info['commit']['sha']
                # 创建新分支引用
                data = {'ref': f'refs/heads/{branch}', 'sha': sha}
                github_request(f'https://api.github.com/repos/{repo}/git/refs', token, method='POST', data=data)
                print(f"✅ 分支创建成功: {branch}")
                return True
            else:
                # 无法创建空分支，需要先有提交
                print(f"⚠️  分支 {branch} 不存在且未指定来源，将被推送时自动创建")
                return True
        else:
            raise

def setup_git_repo(target_paths, branch, commit_msg):
    """在临时目录创建 Git 仓库，包含指定路径的文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 临时工作区: {tmpdir}")
        tmpdir = Path(tmpdir)

        # 复制指定路径到临时目录
        for path_str in target_paths:
            src = Path(path_str).expanduser().resolve()
            if not src.exists():
                print(f"❌ 路径不存在: {src}")
                sys.exit(1)

            if src.is_file():
                dst = tmpdir / src.name
                shutil.copy2(src, dst)
                print(f"  📄 添加文件: {src.name}")
            elif src.is_dir():
                dst = tmpdir / src.name
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"  📁 添加目录: {src.name}")

        # 初始化 Git
        os.chdir(tmpdir)
        run_cmd(f'git init')
        run_cmd(f'git branch -m {branch}')

        # 添加 .gitignore（通用）
        gitignore = tmpdir / '.gitignore'
        if not gitignore.exists():
            gitignore.write_text(GITIGNORE_CONTENT)

        # 提交
        run_cmd('git add .')
        run_cmd(f'git -c user.name="OpenClaw Assistant" -c user.email="assistant@openclaw.ai" commit -m "{commit_msg}"')

        return str(tmpdir)

def push_branch(local_dir, remote_url, branch, force=False):
    """推送分支"""
    os.chdir(local_dir)
    run_cmd(f'git remote add origin {remote_url} 2>/dev/null || true')
    force_flag = '--force' if force else ''
    print(f"📤 推送分支: {branch}")
    run_cmd(f'git push -u origin {branch} {force_flag}')
    print(f"✅ 推送完成")

def create_pr(token, repo, head, base='main', title=None, body=None):
    """创建 PR"""
    owner, name = repo.split('/')
    # 检查已有 PR
    try:
        existing = github_request(f'https://api.github.com/repos/{repo}/pulls?head={owner}:{head}&base={base}&state=open', token)
        if existing:
            pr = existing[0]
            print(f"⚠️  已有 PR #{pr['number']}: {pr['title']}")
            return pr
    except:
        pass

    print(f"🔀 创建 PR: {head} → {base}")
    data = {
        'title': title or f'Merge {head} into {base}',
        'head': head,
        'base': base,
        'body': body or '自动创建 Pull Request，由 OpenClaw 助手部署。'
    }
    pr = github_request(f'https://api.github.com/repos/{repo}/pulls', token, method='POST', data=data)
    print(f"✅ PR 创建成功: {pr['html_url']} (#{pr['number']})")
    return pr

def merge_pr(token, repo, pr_number, method='squash'):
    """合并 PR"""
    print(f"🔀 合并 PR #{pr_number}...")
    data = {'merge_method': method}
    try:
        result = github_request(f'https://api.github.com/repos/{repo}/pulls/{pr_number}/merge', token, method='PUT', data=data)
        if result.get('merged'):
            print(f"✅ PR 已合并: #{pr_number}")
            return True
        else:
            print(f"⚠️  合并失败: {result.get('message', 'Unknown')}")
            return False
    except Exception as e:
        print(f"❌ 合并 PR 失败: {e}")
        return False

GITIGNORE_CONTENT = """# Deploy .gitignore
.env
*.key
*.pem
credentials.json
tokens.json
*.log
*.tmp
.DS_Store
__pycache__/
venv/
node_modules/
"""

def main():
    parser = argparse.ArgumentParser(description='灵活部署文件/目录到 GitHub')
    parser.add_argument('--repo', required=True, help='GitHub 仓库 (owner/repo)')
    parser.add_argument('--path', action='append', required=True, help='要部署的文件或目录路径（可多次指定）')
    parser.add_argument('--commit-msg', default='Deploy files', help='Git 提交信息')
    parser.add_argument('--force', action='store_true', help='强制推送（谨慎使用）')

    # 模式相关参数
    parser.add_argument('--mode', choices=['direct', 'feature'], default='direct',
                        help='部署模式: direct(直接推送到指定分支), feature(先推送到开发分支再PR到主分支)')
    parser.add_argument('--branch', default='main', help='目标分支 (direct 模式用, 默认 main)')
    parser.add_argument('--dev-branch', help='开发分支 (feature 模式用，默认 openclaw)')
    parser.add_argument('--base-branch', default='main', help='基础分支 (feature 模式用，默认 main)')
    parser.add_argument('--no-pr', action='store_true', help='不创建 PR (direct 模式)')
    parser.add_argument('--auto-merge', action='store_true', help='自动合并 PR (feature 模式)')

    args = parser.parse_args()

    token = check_token()

    # 模式判断
    if args.mode == 'feature':
        dev_branch = args.dev_branch or 'openclaw'
        base_branch = args.base_branch
        print(f"🚀 模式: FEATURE (先推送到 {dev_branch}，再 PR 到 {base_branch})")
        target_branch = dev_branch
        create_pr_flag = True  # feature 模式总是创建 PR
    else:
        target_branch = args.branch
        create_pr_flag = not args.no_pr
        print(f"🚀 模式: DIRECT (直接推送到 {target_branch})")

    print(f"   仓库: {args.repo}")
    print(f"   路径: {', '.join(args.path)}")
    print(f"   创建 PR: {'是' if create_pr_flag else '否'}")

    # 1. 确保仓库存在
    ensure_repo(token, args.repo)

    # 2. Feature 模式需要确保 base 分支存在
    if args.mode == 'feature':
        print(f"\n📋 确保基础分支存在: {base_branch}")
        ensure_branch(token, args.repo, base_branch)
        # 检查 dev 分支是否存在，如果存在且需要强制推送，需要特殊处理
    else:
        # Direct 模式也需要确保目标分支存在（推送时会自动创建）
        pass

    # 3. 准备 Git 仓库
    print("\n📦 准备 Git 仓库...")
    local_dir = setup_git_repo(args.path, target_branch, args.commit_msg)

    # 4. 推送
    print("\n📤 推送代码...")
    remote_url = f'https://github.com/{args.repo}.git'
    push_branch(local_dir, remote_url, target_branch, force=args.force)

    # 5. 创建 PR（如果需要）
    if create_pr_flag and target_branch != base_branch:
        print("\n🔀 创建 Pull Request...")
        pr = create_pr(token, args.repo, target_branch, base_branch)

        # 6. 自动合并（可选）
        if args.auto_merge and pr:
            print("\n⚡ 自动合并 PR...")
            merge_pr(token, args.repo, pr['number'])
    elif create_pr_flag:
        print("\n✅ 目标分支就是基础分支，无需 PR")
    else:
        print("\n✅ 跳过 PR 创建")

    print("\n🎉 部署完成！")

if __name__ == '__main__':
    main()
