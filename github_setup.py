#!/usr/bin/env python3
"""
GitHub 连接测试与配置脚本
"""
import os
import sys
import json
import urllib.request

def test_matong_connection(api_key):
    """测试 Maton Gateway 连接"""
    print("🔍 测试 Maton Gateway 连接...")
    req = urllib.request.Request('https://gateway.maton.ai/github/user')
    req.add_header('Authorization', f'Bearer {api_key}')
    try:
        response = urllib.request.urlopen(req, timeout=10)
        user = json.load(response)
        print(f"✅ 连接成功！")
        print(f"   GitHub 用户: {user['login']}")
        print(f"   姓名: {user.get('name', '未设置')}")
        print(f"   Public repos: {user['public_repos']}")
        return True, user
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False, None

def list_repos(api_key):
    """列出用户的仓库"""
    print("\n📦 获取仓库列表...")
    req = urllib.request.Request('https://gateway.maton.ai/github/user/repos?per_page=100')
    req.add_header('Authorization', f'Bearer {api_key}')
    try:
        response = urllib.request.urlopen(req, timeout=10)
        repos = json.load(response)
        for i, repo in enumerate(repos[:20], 1):  # 只显示前20个
            print(f"  {i}. {repo['full_name']}")
            if repo['description']:
                print(f"     📝 {repo['description']}")
            print(f"     🔗 {repo['html_url']}")
            print(f"     ⭐ {repo['stargazers_count']} | 🍴 {repo['forks_count']}")
            print()
        if len(repos) > 20:
            print(f"  ... 还有 {len(repos) - 20} 个仓库")
        return repos
    except Exception as e:
        print(f"❌ 获取仓库失败: {e}")
        return []

def create_file_in_repo(api_key, owner, repo, path, content, message="Update file", branch="main"):
    """在仓库中创建或更新文件"""
    print(f"\n📝 上传文件: {path} -> {owner}/{repo}")
    # 先获取文件信息（如果存在）
    url = f'https://gateway.maton.ai/github/repos/{owner}/{repo}/contents/{path}'
    req_get = urllib.request.Request(url)
    req_get.add_header('Authorization', f'Bearer {api_key}')
    sha = None
    try:
        response = urllib.request.urlopen(req_get, timeout=10)
        file_info = json.load(response)
        sha = file_info.get('sha')
        print(f"   ℹ️ 文件已存在，将更新")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"   ℹ️ 文件不存在，将创建")
        else:
            print(f"   ⚠️ 检查文件时出错: {e}")
            return False

    # 上传文件
    import base64
    encoded = base64.b64encode(content.encode()).decode()
    data = {
        "message": message,
        "content": encoded,
        "branch": branch
    }
    if sha:
        data["sha"] = sha

    req_put = urllib.request.Request(url, data=json.dumps(data).encode(), method='PUT')
    req_put.add_header('Authorization', f'Bearer {api_key}')
    req_put.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req_put, timeout=10)
        result = json.load(response)
        print(f"   ✅ 上传成功！")
        print(f"   🔗 {result['content']['html_url']}")
        return True
    except Exception as e:
        print(f"   ❌ 上传失败: {e}")
        if hasattr(e, 'read'):
            print(f"   详情: {e.read().decode()}")
        return False

def main():
    # 获取 API Key
    api_key = os.environ.get('MATON_API_KEY')
    if not api_key:
        print("❌ 请设置环境变量 MATON_API_KEY")
        print("   例如: export MATON_API_KEY='your_key_here'")
        sys.exit(1)

    # 1. 测试连接
    success, user = test_matong_connection(api_key)
    if not success:
        sys.exit(1)

    # 2. 列出仓库
    repos = list_repos(api_key)

    # 3. 交互式选择仓库（简单起见，硬编码目标）
    # 这里你可以修改为让用户输入
    target_owner = user['login']
    target_repo = input("👉 请输入要操作的目标仓库名 (回车跳过创建测试): ").strip()
    if not target_repo:
        print("跳过文件上传测试")
        return

    # 4. 测试上传一个简单的 README
    test_content = f"""# {target_repo}

This repository is managed by OpenClaw + Maton Gateway.

Created at: {json.dumps(user, ensure_ascii=False)}
"""
    path = "README_OPENCLAW.md"
    create_file_in_repo(api_key, target_owner, target_repo, path, test_content,
                        message="Add OpenClaw test file")

if __name__ == "__main__":
    main()
