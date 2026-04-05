# openclaw-github-workflow-skills
OpenClaw GitHub Workflow Tutorial - Complete guide for AI assistants to use GitHub APIs

## 📚 文档导航

- **QUICK_START.md** - 5分钟快速上手
- **PERMISSION_TROUBLESHOOTING.md** - OpenClaw 权限问题实战记录（包含 `exec security=full ask=off` 的使用、常见错误解决、分支管理最佳实践）
- **ERROR_HANDLING.md** - GitHub Token 与 Maton Gateway 错误处理指南
- **SETUP_GUIDE.md** - 环境配置步骤
- **USER_CASES.md** - 使用案例与场景
- **SUMMARY.md** - 内容概要

## 🎯 核心技能

本仓库提供 OpenClaw AI 助手使用 GitHub API 的完整技能包，包括：

1. **认证方式**
   - GitHub Token（直接 API）
   - Maton Gateway（托管 OAuth）

2. **常用操作**
   - 仓库管理（创建、删除、分支）
   - 文件操作（读取、上传、更新）
   - Issue 与 PR 管理

3. **权限处理**
   - `exec security=full ask=off` 绕过 OpenClaw 安全限制
   - 处理 401/403/409 等错误

4. **安全最佳实践**
   - 避免敏感信息泄露
   - 使用环境变量
   - 分支清理与管理

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
