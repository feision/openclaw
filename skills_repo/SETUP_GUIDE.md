# GitHub Workflow Setup Guide

## 快速配置指南

### 第一步：获取 Maton API Key

1. 访问 https://maton.ai
2. 注册账号并登录
3. 在 Settings 页面获取 API Key
4. 保存 API Key

### 第二步：设置环境变量

```bash
export MATON_API_KEY="your_maton_api_key"
```

### 第三步：创建 GitHub 连接

运行连接测试脚本：

```bash
python3 test_connection.py
```

如果出现授权 URL，请打开该 URL 完成 GitHub OAuth 授权。

### 第四步：验证连接

运行用户信息测试：

```bash
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://gateway.maton.ai/github/user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
user = json.load(urllib.request.urlopen(req))
print(f"Connected as: {user['login']}")
EOF
```

### 第五步：测试基本操作

创建测试仓库：

```bash
python3 <<'EOF'
import urllib.request, json, os
data = json.dumps({
    "name": "openclaw-test-repo",
    "description": "Test repository for OpenClaw",
    "private": False,
    "auto_init": True
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/github/user/repos', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
result = json.load(urllib.request.urlopen(req))
print(f"Repository created: {result['full_name']}")
EOF
```

## 安装额外技能

### 使用 skillhub 安装 GitHub 相关技能

根据 AVAILABLE_SKILLS.md 中的技能列表，选择需要的技能：

```bash
# 基础 GitHub CLI 工具
skillhub install github

# 高级自动化
skillhub install github-automation-pro

# GitHub Actions 生成器
skillhub install github-actions-generator

# GitHub 趋势分析
skillhub install github-trending

# Issue 创建助手
skillhub install github-issue-creator
```

如果 skillhub 不可用，使用 clawhub：

```bash
clawhub install github
clawhub install github-automation-pro
clawhub install github-actions-generator
```

## 使用教程示例

### 运行基础自动化示例

```bash
python3 example_scripts/github_automation.py
```

### 运行高级自动化示例

```bash
python3 example_scripts/advanced_automation.py
```

### 使用连接测试工具

```bash
python3 example_scripts/test_connection.py
```

## 常见问题解决

### Q1: API Key 401 错误
检查 MATON_API_KEY 是否正确设置：
```bash
echo $MATON_API_KEY
```

### Q2: GitHub 连接问题
需要授权 GitHub OAuth 连接：
运行 `python3 test_connection.py` 获取授权 URL

### Q3: 权限不足
GitHub OAuth 需要授权必要的权限：
- repo
- issues
- pull requests
- 根据需求选择权限

### Q4: 速率限制
GitHub API 有速率限制：
```bash
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://gateway.maton.ai/github/rate_limit')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
limits = json.load(urllib.request.urlopen(req))
print(f"Remaining requests: {limits['resources']['core']['remaining']}")
EOF
```

### Q5: 文件上传失败
确保文件内容正确 Base64 编码：
```python
import base64
encoded_content = base64.b64encode(content.encode()).decode()
```

## 安全建议

1. **不要在群聊中暴露 Token**
2. **定期更换 Token**
3. **使用最小权限原则**
4. **敏感信息存储在环境变量中**
5. **及时撤销泄露的 Token**

## 下一步

1. 根据实际需求调整自动化脚本
2. 探索其他 GitHub 技能的功能
3. 创建自定义自动化流程
4. 分享使用经验到社区