# GitHub Workflow Quick Start

## 5分钟快速上手

### 第1步：配置环境

```bash
# 设置 Maton API Key
export MATON_API_KEY="your_maton_api_key"
```

### 第2步：验证连接

```python
import urllib.request, json, os

req = urllib.request.Request('https://gateway.maton.ai/github/user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
response = urllib.request.urlopen(req)
user = json.load(response)
print(f"Connected to GitHub as: {user['login']}")
```

### 第3步：基本操作

#### 创建仓库
```python
import urllib.request, json, os

data = json.dumps({
    "name": "test-repo",
    "description": "Test repository",
    "private": False
}).encode()

req = urllib.request.Request('https://gateway.maton.ai/github/user/repos', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')

response = urllib.request.urlopen(req)
repo = json.load(response)
print(f"Repository created: {repo['full_name']}")
```

#### 上传文件
```python
import urllib.request, json, os, base64

content = "Hello, GitHub!"
encoded_content = base64.b64encode(content.encode()).decode()

data = json.dumps({
    "message": "Add hello.txt",
    "content": encoded_content,
    "branch": "main"
}).encode()

req = urllib.request.Request('https://gateway.maton.ai/github/repos/{owner}/{repo}/contents/hello.txt', data=data, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')

response = urllib.request.urlopen(req)
result = json.load(response)
print(f"File uploaded: {result['content']['path']}")
```

### 第4步：常用命令速查

#### 列出仓库
```bash
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://api.github.com/user/repos?per_page=20')
req.add_header('Authorization', f'token {os.environ["GITHUB_TOKEN"]}')
repos = json.load(urllib.request.urlopen(req))
for repo in repos:
    print(f"{repo['full_name']} - {repo['description']}")
EOF
```

> **重要**: 使用 `/user/repos` 而非 `/users/{username}/repos`，才能看到私有仓库。

#### 创建 Issue
```bash
python3 <<'EOF'
import urllib.request, json, os
data = json.dumps({
    "title": "Quick bug report",
    "body": "Found issue in code"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/github/repos/{owner}/{repo}/issues', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
issue = json.load(urllib.request.urlopen(req))
print(f"Issue created: #{issue['number']}")
EOF
```

---

## ⚡ 一键部署工具（推荐！）

如果你需要快速推送完整工作空间到 GitHub，使用我们封装的工具：

```bash
# 1. 配置 Token
export GITHUB_TOKEN="ghp_..."

# 2. 一键部署
cd /path/to/openclaw-github-workflow-skills
python3 deploy/github_deploy.py \
  --workspace /home/node/.openclaw/workspace \
  --repo feision/openclaw \
  --branch openclaw
```

### 主要功能
- ✅ 自动创建/验证仓库
- ✅ 清理并初始化 Git
- ✅ 推送代码到指定分支
- ✅ 自动创建 PR 合并到 main（可选）

### 参数
- `--workspace`: 工作空间路径
- `--repo`: GitHub 仓库 (owner/repo)
- `--branch`: 目标分支（默认 main）
- `--no-pr`: 不创建 PR，直接推送
- `--force`: 强制推送（谨慎）

📖 详细文档: `deploy/README.md`

---

### 第5步：集成到 OpenClaw

将以下脚本添加到你的 OpenClaw 工作流程中：

```bash
# 自动化 GitHub 操作脚本
#!/bin/bash

# 设置 API Key
export MATON_API_KEY="$MATON_API_KEY"

# 执行 GitHub 操作
python3 <<'EOF'
import urllib.request, json, os, sys

def github_request(url, method='GET', data=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    if data:
        req.add_header('Content-Type', 'application/json')
    return json.load(urllib.request.urlopen(req))

# 示例：创建仓库和上传文件
print("Starting GitHub automation...")

# 1. 创建仓库
repo_data = github_request('https://gateway.maton.ai/github/user/repos', 'POST', 
    json.dumps({"name": "auto-repo", "description": "Automated repo"}).encode())
print(f"Repository created: {repo_data['full_name']}")

# 2. 上传 README
import base64
content = base64.b64encode("# Auto-generated README\n\nThis repo was created automatically by OpenClaw.".encode()).decode()
upload_data = github_request(f'https://gateway.maton.ai/github/repos/{repo_data["owner"]["login"]}/{repo_data["name"]}/contents/README.md', 'PUT',
    json.dumps({"message": "Auto README", "content": content, "branch": "main"}).encode())
print(f"README uploaded")

print("Done!")
EOF
```

## 调试技巧

如果遇到问题，检查以下：

1. **API Key**: `echo $MATON_API_KEY`
2. **网络连接**: `curl -I https://gateway.maton.ai`
3. **权限**: GitHub Token 需要足够的权限（repo, issues, etc）
4. **URL格式**: 确保 URL 正确，不要包含 `api.github.com` 前缀

## 下一步

完成 Quick Start 后，你可以：

1. 学习更高级的操作（见 README.md）
2. 集成到你的自动化流程
3. 探索 GitHub API 的其他功能
4. 结合其他技能创建完整的 CI/CD 流程