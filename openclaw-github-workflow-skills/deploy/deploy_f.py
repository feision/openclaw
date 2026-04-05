#!/usr/bin/env python3
"""
F 方案专用脚本 - 先推送子分支，再 PR 合并到主分支

适用于频繁开发：清晰区分"新修改"与"旧代码"，便于恢复、审计、多人协作。

用法:
  python3 deploy_f.py \
    --repo feision/openclaw \
    --dev-branch feature/your-name \
    --base-branch main \
    --path SOUL.md \
    --path USER.md \
    --commit-msg "Add user configs"

参数:
  --repo          GitHub 仓库 (必填)
  --dev-branch    开发分支名称 (默认: openclaw)
  --base-branch   基础分支 (默认: main)
  --path          要推送的文件或目录 (可多次指定)
  --commit-msg    Git 提交信息 (默认: "Deploy via F-scheme")
  --auto-merge    自动合并 PR (谨慎使用)
  --force         强制推送开发分支 (谨慎使用)

示例:
  # 推送多个文件到 feature/lobster 分支，并 PR 到 main
  python3 deploy_f.py \
    --repo feision/openclaw \
    --dev-branch feature/lobster \
    --path SOUL.md --path USER.md --path MEMORY.md \
    --commit-msg "Update memory and configs"

  # 强制更新开发分支（覆盖历史）
  python3 deploy_f.py \
    --repo feision/openclaw \
    --dev-branch feature/new-ui \
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

def ensure_repo(token, repo):
    """确保仓库存在"""
    try:
        github_request(f'https://api.github.com/repos/{repo}', token)
        return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"🔄 创建仓库: {repo}")
            name = repo.split('/')[-1]
            data = {'name': name, 'description': 'Deployed via F-scheme', 'private': False}
            result = github_request('https://api.github.com/user/repos', token, method='POST', data=data)
            print(f"✅ 仓库创建成功: {result['html_url']}")
            return True
        else:
            raise

def ensure_branch(token, repo, branch, from_branch):
    """确保分支存在，如不存在则从 from_branch 创建"""
    try:
        github_request(f'https://api.github.com/repos/{repo}/branches/{branch}', token)
        return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"🔄 创建分支: {branch} (基于 {from_branch})")
            branch_info = github_request(f'https://api.github.com/repos/{repo}/branches/{from_branch}', token)
            sha = branch_info['commit']['sha']
            data = {'ref': f'refs/heads/{branch}', 'sha': sha}
            github_request(f'https://api.github.com/repos/{repo}/git/refs', token, method='POST', data=data)
            print(f"✅ 分支创建成功: {branch}")
            return True
        else:
            raise

def setup_git_repo(target_paths, branch, commit_msg):
    """在临时目录创建 Git 仓库"""
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 临时工作区: {tmpdir}")
        tmpdir = Path(tmpdir)

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

        os.chdir(tmpdir)
        run_cmd(f'git init')
        run_cmd(f'git branch -m {branch}')

        gitignore = tmpdir / '.gitignore'
        if not gitignore.exists():
            gitignore.write_text("""# F-scheme deploy
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
""")

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

def create_pr(token, repo, head, base='main'):
    """创建 PR"""
    owner, name = repo.split('/')
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
        'title': f'Merge {head} into {base}',
        'head': head,
        'base': base,
        'body': f'自动创建 Pull Request，由 OpenClaw 助手通过 F 方案部署。\n\n---\nDev-branch: `{head}`\nBase-branch: `{base}`'
    }
    pr = github_request(f'https://api.github.com/repos/{repo}/pulls', token, method='POST', data=data)
    print(f"✅ PR 创建成功: {pr['html_url']} (#{pr['number']})")
    return pr

def merge_pr(token, repo, pr_number):
    """合并 PR"""
    print(f"🔀 合并 PR #{pr_number}...")
    data = {'merge_method': 'squash'}
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

def main():
    parser = argparse.ArgumentParser(description='F 方案专用部署脚本')
    parser.add_argument('--repo', required=True, help='GitHub 仓库 (owner/repo)')
    parser.add_argument('--dev-branch', default='openclaw', help='开发分支 (默认: openclaw)')
    parser.add_argument('--base-branch', default='main', help='基础分支 (默认: main)')
    parser.add_argument('--path', action='append', required=True, help='要部署的文件或目录 (可多次指定)')
    parser.add_argument('--commit-msg', default='Deploy via F-scheme', help='提交信息')
    parser.add_argument('--auto-merge', action='store_true', help='自动合并 PR')
    parser.add_argument('--force', action='store_true', help='强制推送')
    args = parser.parse_args()

    token = check_token()

    print(f"🚀 F 方案: 先推送到 {args.dev_branch}，再 PR 到 {args.base_branch}")
    print(f"   仓库: {args.repo}")
    print(f"   路径: {', '.join(args.path)}")

    # 1. 确保仓库和基础分支存在
    ensure_repo(token, args.repo)
    print(f"\n📋 确保基础分支存在: {args.base_branch}")
    ensure_branch(token, args.repo, args.base_branch, args.base_branch)

    # 2. 准备 Git 仓库
    print("\n📦 准备 Git 仓库...")
    local_dir = setup_git_repo(args.path, args.dev_branch, args.commit_msg)

    # 3. 推送到开发分支
    print("\n📤 推送代码到开发分支...")
    remote_url = f'https://github.com/{args.repo}.git'
    push_branch(local_dir, remote_url, args.dev_branch, force=args.force)

    # 4. 创建 PR
    print("\n🔀 创建 Pull Request...")
    pr = create_pr(token, args.repo, args.dev_branch, args.base_branch)

    # 5. 自动合并（可选）
    if args.auto_merge and pr:
        print("\n⚡ 自动合并 PR...")
        merge_pr(token, args.repo, pr['number'])

    print("\n🎉 F 方案部署完成！")
    print("💡 如需继续开发，可在开发分支上迭代；完成后再次运行此脚本推送。")

if __name__ == '__main__':
    main()
