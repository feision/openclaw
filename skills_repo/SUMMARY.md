# OpenClaw GitHub 工作流技能总结

## 使用的技能和工具

### 1. GitHub API Skill (github-api)

**核心功能**:
- 完整的 GitHub REST API 访问
- 通过 Maton Gateway 进行 OAuth 认证
- 无需直接处理 GitHub Token 的安全管理

**位置**: `~/.openclaw/workspace/skills/github-api/SKILL.md`

**认证方式**: 
- 在 Maton.ai 创建 API Key
- 设置环境变量: `export MATON_API_KEY="your_api_key"`
- 创建 GitHub OAuth 连接

**API 端点**: `https://gateway.maton.ai/github/{native-api-path}`

### 2. Shell 命令工具 (exec)

**用途**:
- 执行 Python 脚本调用 API
- 测试连接和验证 Token
- 运行自动化脚本

**示例**:
```bash
exec "python3 github_automation.py"
```

### 3. 文件操作工具 (read/write/edit)

**用途**:
- 读取和写入代码文件
- 创建配置文件
- 编辑脚本和文档

**示例**:
```bash
write "/path/to/file.py" "Python code content"
```

### 4. 环境变量管理

**用途**:
- 安全存储 API Token
- 在会话中临时设置环境变量
- 避免硬编码敏感信息

**示例**:
```bash
export MATON_API_KEY="your_api_key"
```

## GitHub 操作流程指南

### 第一步：配置认证

1. **获取 Maton API Key**:
   - 访问 https://maton.ai
   - 注册账号并获取 API Key
   - 设置环境变量

2. **创建 GitHub OAuth 连接**:
```python
python3 <<'EOF'
import urllib.request, json, os
data = json.dumps({'app': 'github'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
result = json.load(urllib.request.urlopen(req))
print(f"Open URL to authorize: {result['connection']['url']}")
EOF
```

3. **验证连接**:
```python
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://gateway.maton.ai/github/user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
user = json.load(urllib.request.urlopen(req))
print(f"Authenticated as: {user['login']}")
EOF
```

### 第二步：常用操作

#### 创建仓库
```python
data = json.dumps({
    "name": "my-repo",
    "description": "My repository",
    "private": False
}).encode()

req = urllib.request.Request('https://gateway.maton.ai/github/user/repos', data=data, method='POST')
```

#### 上传文件
```python
import base64
encoded_content = base64.b64encode(content.encode()).decode()

upload_data = json.dumps({
    "message": "Add file",
    "content": encoded_content,
    "branch": "main"
}).encode()

req = urllib.request.Request('https://gateway.maton.ai/github/repos/{owner}/{repo}/contents/{path}', 
                            data=upload_data, method='PUT')
```

#### 创建 Issue
```python
data = json.dumps({
    "title": "Bug report",
    "body": "Description",
    "labels": ["bug"]
}).encode()

req = urllib.request.Request('https://gateway.maton.ai/github/repos/{owner}/{repo}/issues', 
                            data=data, method='POST')
```

#### 创建 Pull Request
```python
data = json.dumps({
    "title": "Feature",
    "body": "Changes",
    "head": "feature-branch",
    "base": "main"
}).encode()

req = urllib.request.Request('https://gateway.maton.ai/github/repos/{owner}/{repo}/pulls', 
                            data=data, method='POST')
```

### 第三步：集成到 OpenClaw

1. **创建自动化脚本**:
```python
#!/usr/bin/env python3
import urllib.request, json, os, base64

def github_request(url, method='GET', data=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    if data:
        req.add_header('Content-Type', 'application/json')
    return json.load(urllib.request.urlopen(req))
```

2. **自动化任务**:
   - 定期检查 Issues
   - 自动创建项目模板
   - 代码变更监控
   - PR 自动化审查

## 安全注意事项

1. **Token 保护**: GitHub Token 只能在私密会话中使用
2. **权限最小化**: 只授予必要的权限（repo, issues 等）
3. **环境变量**: 使用环境变量存储敏感信息
4. **定期更新**: Token 定期更新减少风险
5. **日志清理**: 避免在日志中留下敏感信息

## 故障排查

### 常见错误

| 错误代码 | 原因 | 解决方案 |
|---------|------|----------|
| 401 | API Key 无效 | 检查 MATON_API_KEY 是否正确 |
| 403 | 权限不足 | 重新授权 GitHub OAuth 连接 |
| 404 | 资源不存在 | 检查 URL 路径是否正确 |
| 422 | 验证失败 | 检查请求参数格式 |
| 429 | 速率限制 | 等待后重试 |

### 调试步骤

1. **检查环境变量**:
```bash
echo $MATON_API_KEY
```

2. **验证 API Key**:
```python
python3 test_connection.py
```

3. **检查 GitHub OAuth 连接**:
访问 https://ctrl.maton.ai/connections

4. **验证 API 调用**:
```python
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://gateway.maton.ai/github/user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
user = json.load(urllib.request.urlopen(req))
print(f"Connected: {user['login']}")
EOF
```

## 最佳实践

1. **模块化脚本**: 将常用操作封装为函数
2. **错误处理**: 添加异常处理和重试机制
3. **日志记录**: 记录重要的操作结果
4. **测试先行**: 先测试小范围操作，再扩展
5. **备份策略**: 重要操作前备份当前状态

## 资源链接

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [Maton Gateway Documentation](https://docs.maton.ai)
- [OpenClaw Skills Documentation](https://docs.openclaw.ai)
- [GitHub Token Management](https://github.com/settings/tokens)
- [GitHub OAuth Apps](https://github.com/settings/developers)

---

**总结**: OpenClaw GitHub 工作流提供了强大的自动化能力，通过 Maton Gateway 实现安全便捷的 API 访问，结合 exec、文件操作等工具，可以实现完整的 GitHub 管理自动化。