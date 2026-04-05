# GitHub Token 错误处理指南

## 🔍 快速诊断：环境变量是否已正确设置？

在执行任何 GitHub API 操作前，请先运行：

```bash
# 检查 Maton Gateway
echo "MATON_API_KEY: ${MATON_API_KEY:0:10}..."

# 检查 GitHub PAT
echo "GITHUB_TOKEN: ${GITHUB_TOKEN:0:10}..."
```

如果输出为空或只显示冒号，说明环境变量未设置。请参考 README.md 或 SETUP_GUIDE.md 完成配置。

---

## Token 错误的常见场景

### 1. 401 Unauthorized (认证失败)
```bash
HTTP Error 401: Unauthorized
```

**原因**:
- Token 已过期或被撤销
- Token 权限不足
- Token 格式错误
- Maton API Key 无效

**解决方案**:
1. **检查 Token 格式**: GitHub Token 应该是 `ghp_` 开头，Maton API Key 不同
2. **验证 Token**: 运行 `test_connection.py` 脚本
3. **重新生成 Token**: 访问 https://github.com/settings/tokens
4. **更新环境变量**: `export GITHUB_TOKEN="new_token"`

### 2. 422 Unprocessable Entity (参数错误)
```bash
HTTP Error 422: Unprocessable Entity
```

**原因**:
- 文件已存在（如 auto_init 创建的 README.md）
- 请求参数格式错误
- 缺少必要字段

**解决方案**:
```python
# 避免 auto_init: True
repo_data = {
    "name": "test-repo",
    "description": "Test",
    "private": False,
    "auto_init": False  # 改为 False
}
```

### 3. 403 Forbidden (权限不足)
```bash
HTTP Error 403: Forbidden
```

**原因**:
- Token 权限不足（缺少 repo、issues 等权限）
- 仓库访问限制
- GitHub API 版本不支持

**解决方案**:
1. **检查 Token 权限**: GitHub Token 需要相应权限
2. **重新生成 Token**: 选择所需权限
3. **检查仓库权限**: 确认有访问权限

## 调试工具

使用 `test_connection.py` 脚本：
```bash
python3 test_connection.py
```

输出示例：
```
Testing API key...
✓ API key is valid
✓ GitHub connection successful
Authenticated as: feision
```

## Token 管理最佳实践

### 1. 安全存储
```bash
# 在私密会话中设置环境变量
export GITHUB_TOKEN="your_token"
export MATON_API_KEY="your_maton_key"

# 不要在群聊中暴露 Token
```

### 2. 权限管理
GitHub Token 所需权限：
- **repo** - 仓库操作（创建、删除、更新）
- **issues** - Issue 管理
- **pull_requests** - PR 管理
- **workflow** - Actions 工作流

### 3. 定期更新
Token 有效期：
- GitHub Token 通常 90 天
- Maton API Key 通常更长
定期检查并更新

### 4. 错误处理流程
```python
import urllib.request, json, os

try:
    response = urllib.request.urlopen(req)
    result = json.load(response)
except urllib.request.HTTPError as e:
    if e.code == 401:
        print("Token 失效，请更新 Token")
    elif e.code == 403:
        print("权限不足，请检查 Token 权限")
    elif e.code == 422:
        print("请求参数错误，请检查输入")
```

## Maton Gateway 特定错误

### 1. 缺少 GitHub OAuth 连接
Maton Gateway 需要额外步骤：
```python
# 1. 创建 GitHub 连接
data = json.dumps({'app': 'github'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {MATON_API_KEY}')

# 2. 打开返回的 URL 完成 GitHub OAuth 授权
print(f"授权 URL: {result['connection']['url']}")

# 3. 等待授权完成后再使用
```

### 2. Maton API Key 失效
检查步骤：
```bash
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
try:
    response = urllib.request.urlopen(req)
    print("✓ Maton API Key 有效")
except:
    print("✗ Maton API Key 无效")
EOF
```

## GitHub API vs Maton Gateway 区别

### GitHub API（直接连接）
```python
# 使用 GitHub Token
req = urllib.request.Request('https://api.github.com/user')
req.add_header('Authorization', f'Bearer {GITHUB_TOKEN}')
```

**优点**:
- 直接连接，速度快
- 无需额外授权
- 简单易用

**缺点**:
- 需要在代码中处理 Token
- Token 安全风险

### Maton Gateway（github-api 技能）
```python
# 使用 Maton Gateway
req = urllib.request.Request('https://gateway.maton.ai/github/user')
req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
```

**优点**:
- OAuth 授权流程
- Token 不直接暴露
- 支持多应用连接

**缺点**:
- 需要额外授权步骤
- 依赖 Maton 服务

## Token 错误恢复流程

### 步骤 1: 诊断错误类型
```bash
python3 error_diagnosis.py
```

### 步骤 2: 验证 Token
```bash
# GitHub Token 验证
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://api.github.com/user')
req.add_header('Authorization', f'Bearer {os.environ["GITHUB_TOKEN"]}')
response = urllib.request.urlopen(req)
user = json.load(response)
print(f"GitHub Token 有效: {user['login']}")
EOF

# Maton API Key 验证
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
response = urllib.request.urlopen(req)
connections = json.load(response)
print(f"Maton API Key 有效: {len(connections)} 个连接")
EOF
```

### 步骤 3: 生成新 Token

**GitHub Token**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择所需权限
4. 复制新 Token
5. 更新环境变量

**Maton API Key**:
1. 访问 https://maton.ai
2. 登录账号
3. 获取 API Key
4. 更新环境变量

### 步骤 4: 更新配置文件
```bash
# 更新 TOOLS.md
echo "GitHub Token: YOUR_NEW_TOKEN" >> TOOLS.md

# 更新环境变量
export GITHUB_TOKEN="YOUR_NEW_TOKEN"
export MATON_API_KEY="YOUR_NEW_KEY"
```

## 示例：完整错误处理脚本

```python
#!/usr/bin/env python3
"""
GitHub Token Error Handler
"""

import urllib.request
import json
import os
import sys

def diagnose_error():
    """诊断 Token 错误"""
    github_token = os.environ.get("GITHUB_TOKEN")
    maton_key = os.environ.get("MATON_API_KEY")
    
    print("Diagnosing token issues...")
    
    if github_token:
        print(f"GitHub Token: {github_token[:10]}...")
        
        # Test GitHub Token
        try:
            req = urllib.request.Request('https://api.github.com/user')
            req.add_header('Authorization', f'Bearer {github_token}')
            req.add_header('User-Agent', 'OpenClaw-Test')
            
            response = urllib.request.urlopen(req)
            user = json.load(response)
            print(f"✓ GitHub Token valid: {user['login']}")
        except Exception as e:
            print(f"✗ GitHub Token invalid: {e}")
            print("  Solution: Regenerate token at https://github.com/settings/tokens")
    
    if maton_key:
        print(f"Maton API Key: {maton_key[:10]}...")
        
        # Test Maton API Key
        try:
            req = urllib.request.Request('https://ctrl.maton.ai/connections')
            req.add_header('Authorization', f'Bearer {maton_key}')
            
            response = urllib.request.urlopen(req)
            connections = json.load(response)
            print(f"✓ Maton API Key valid: {len(connections)} connections")
            
            github_connections = [c for c in connections if c.get('app') == 'github']
            if github_connections:
                print(f"✓ GitHub connection exists")
            else:
                print(f"✗ GitHub connection missing")
                print("  Solution: Create GitHub connection at https://ctrl.maton.ai/connections")
        except Exception as e:
            print(f"✗ Maton API Key invalid: {e}")
            print("  Solution: Get new key at https://maton.ai")
    
    if not github_token and not maton_key:
        print("✗ No tokens found")
        print("  Solution: Set GITHUB_TOKEN or MATON_API_KEY environment variables")

def main():
    """主诊断流程"""
    diagnose_error()
    
    print("\n=== Summary ===")
    print("GitHub API: Direct token authentication")
    print("Maton Gateway: OAuth with Maton API key")
    print("\nRecommended actions:")
    print("1. Verify token format and permissions")
    print("2. Regenerate token if expired")
    print("3. Update environment variables")
    print("4. Test with simple API call")

if __name__ == "__main__":
    main()
```

## 常见错误快速修复

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 401 | Token 无效 | 重新生成 GitHub Token |
| 401 | Maton Key 无效 | 获取新 Maton API Key |
| 403 | 权限不足 | 添加 repo/issues 权限 |
| 422 | 参数错误 | 检查请求格式 |
| 404 | 资源不存在 | 检查 URL/路径 |
| 429 | 速率限制 | 等待后重试 |

## 结论

Token 错误通常可以通过以下步骤解决：
1. **诊断错误类型** - 401、403、422 等
2. **验证 Token 有效性** - 测试 API 连接
3. **重新生成 Token** - GitHub 或 Maton
4. **更新环境变量** - 确保正确设置
5. **测试简单操作** - 验证修复成功

最重要的是 **不要在群聊中暴露 Token**，只在私密会话中使用。