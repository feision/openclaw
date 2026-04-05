# OpenClaw GitHub Workflow Tutorial - 完整指南

> 本项目面向 OpenClaw AI 助手，系统化讲解如何使用 GitHub API 进行仓库、分支、文件、PR 等操作，包含权限处理、错误恢复与完整工作流示例，适合快速上手与生产实践。

## ⚡ 5分钟快速开始（必读）

### 1️⃣ 选择认证方式并设置环境变量（只需要做一次）

```bash
# 方案 A: Maton Gateway (OAuth 托管)
export MATON_API_KEY="your_maton_key"

# 方案 B: GitHub Personal Access Token (直接 API)
export GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

**建议**: 将上述 `export` 命令加入 `~/.bashrc` 或 `~/.zshrc`，这样每次终端启动自动加载，无需重复设置。

### 2️⃣ 验证连接

根据你选择的方案，运行对应的测试脚本：

```bash
# Maton Gateway
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://gateway.maton.ai/github/user')
req.add_header('Authorization', f'Bearer {os.environ.get("MATON_API_KEY", "")}')
try:
    user = json.load(urllib.request.urlopen(req))
    print(f"✅ Connected as: {user['login']}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF

# GitHub PAT
python3 <<'EOF'
import urllib.request, json, os
req = urllib.request.Request('https://api.github.com/user')
req.add_header('Authorization', f'token {os.environ.get("GITHUB_TOKEN", "")}')
try:
    user = json.load(urllib.request.urlopen(req))
    print(f"✅ Connected as: {user['login']}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF
```

### 3️⃣ 执行你的第一个 GitHub 操作

**如果你刚创建了新仓库并需要上传完整 workspace**，请务必先阅读:

**[COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md) ⭐ 完整工作流教程**

这部教程详细记录了一次真实的工作流（包括分支策略、常见坑、解决方案），帮你避免 PR 失败和分支混乱问题。

基础操作（创建仓库、上传文件）也可见 [QUICK_START.md](QUICK_START.md)。

---

## 📚 文档导航

- **[COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md)** ⭐ **新推荐** - 完整工作流：创建仓库 → 上传文件 → 合并分支（实战记录）
- **SETUP_GUIDE.md** - 详细配置步骤（含环境变量设置、Token 管理）
- **QUICK_START.md** - 5分钟快速上手（基础操作示例）
- **PERMISSION_TROUBLESHOOTING.md** - OpenClaw 权限问题实战记录（包含 `exec security=full ask=off` 的使用、常见错误解决、分支管理最佳实践）
- **ERROR_HANDLING.md** - GitHub Token 与 Maton Gateway 错误处理指南
- **USER_CASES.md** - 使用案例与场景
- **SUMMARY.md** - 内容概要

## 🎯 核心技能

本仓库提供 OpenClaw AI 助手使用 GitHub API 的完整技能包，包括：

1. **认证方式**
   - GitHub Token（直接 API）
   - Maton Gateway（托管 OAuth）
   - **环境变量管理**: `MATON_API_KEY` / `GITHUB_TOKEN`

2. **常用操作**
   - 仓库管理（创建、删除、分支）
   - 文件操作（读取、上传、更新）
   - Issue 与 PR 管理
   - 协作与评审

3. **权限处理**
   - `exec security=full ask=off` 绕过 OpenClaw 安全限制
   - 处理 401/403/409 等错误
   - Rate Limit 管理

4. **安全最佳实践**
   - 避免敏感信息泄露（Token 不要硬编码）
   - 使用环境变量存储凭证
   - 分支清理与管理
   - Token 过期与刷新策略

## 🚀 快速开始

```bash
# 1. 设置环境变量
export MATON_API_KEY="your_maton_key"
export GITHUB_TOKEN="your_github_token"

# 2. 运行示例脚本
python3 github_setup.py
```

详细步骤请阅读 [QUICK_START.md](QUICK_START.md)

## 🔧 常见问题

**Q: exec 命令被拒绝怎么办？**
A: 使用 `/exec security=full ask=off <command>`

**Q: 文件上传后显示 base64 乱码？**
A: 使用 Contents API 而非 low-level Git API，详见 [PERMISSION_TROUBLESHOOTING.md](PERMISSION_TROUBLESHOOTING.md)

**Q: GitHub 返回 409 Conflict？**
A: 检查内容是否包含敏感信息（Token），移除后重试

更多问题请查看 [ERROR_HANDLING.md](ERROR_HANDLING.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📖 许可

MIT License

---

*本助手使用的模型：`openrouter/stepfun/step-3.5-flash:free`（默认模型）*
