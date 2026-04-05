# MEMORY.md - 我的长期记忆

> 说明：这是 OpenClaw 助手的关键记忆文件，记录重要决策、偏好、项目状态和学习经验。每次会话都会读取此文件，因此要保持简洁且关键信息前置。

---

## 🦞 身份信息

- **Name:** 龙虾 (Lobster)
- **Role:** Owner & Architect
- **Description:** 专注于跨平台业务工作流与系统设计，强调模块化、自动化、隐私与权限的精细化管理。目标是打造一个高效、可靠、可扩展的数字化中介平台。
- **Vibe:** 务实、直接、有技术洁癖，不喜欢绕弯子
- **专注领域:** 网络协议与代理架构、Cloudflare Workers 与边缘计算、自托管基础设施、隐私与数据主权、前端工程与配置系统设计

---

## 👤 用户信息

- **Name:** 用户
- **Timezone:** Asia/Shanghai (UTC+8)
- **Communication style:** 务实、直接、技术性
- **Preferences:** 简洁回复，具体建议，不喜欢空泛评价

---

## 🎯 当前核心目标

1. **短期（2026-04）**
   - 完成 GitHub PAT 配置并测试连接
   - 掌握 OpenClaw GitHub Workflow Skills 的完整用法
   - 维护和优化 Node-magic-change-panel.js

2. **中期（2026-Q2）**
   - 开发跨平台简历管理系统
   - 实现角色与字段级访问控制
   - 构建创意与信息丰富的仪表盘

3. **长期**
   - 打造一个高效、可靠、可扩展的数字化中介平台
   - 自动化节点组管理与错误防护
   - 优化部署与资源利用

---

## 💼 项目状态（2026-04-05）

### ✅ 完成
- OpenClaw GitHub Workflow 教程仓库克隆
- 初始 USER.md 配置（增强版）

### 🔄 进行中
- GitHub 连接配置（等待用户提供 PAT）
- Node-magic-change-panel.js 的理解与维护
- 环境权限配置（Maton Gateway vs GitHub Token）

### ⏳ 待开始
- 使用 GitHub API 进行实际操作（上传文件、创建 PR 等）
- 规划 cron 自动化任务
- 配置邮件/日历集成

---

## 📝 重要决策与对话记录

### 2026-04-05 01:11
- 遭遇模型配置错误（多个模型不可用）
- 决定切换到 `openrouter/stepfun/step-3.5-flash:free`
- 用户提供了 Maton API Key，但未完成 OAuth 连接

### 2026-04-05 03:52
- 询问连接 GitHub 的方式
- 提供方案选择：Maton Gateway vs GitHub PAT
- 选择 B（GitHub PAT）
- **等待提供 PAT**

### 2026-04-05 03:57
- 用户询问"开机流程"改造方案
- 设计增强版 USER.md 模板
- 初始化 HEARTBEAT.md 任务列表
- 创建本 MEMORY.md 文件

---

## 🔧 技术要点（2026-04-05 更新）

### GitHub API 端点选择
- **列出所有仓库（含私有）**: `GET /user/repos` ✅
- **列出他人公开仓库**: `GET /users/{username}/repos` (仅公开) ❌
- 错误使用 `/users/feision/repos` 导致无法看到私有仓库
- 已在 `README.md` 和 `QUICK_START.md` 添加明确说明

---

## ⚙️ 偏好与约束

### 执行策略
- **主动性:** 遇到问题先尝试解决（搜索文档、试错），再向用户汇报
- **安全性:** 外部操作（邮件、推文等）必须先询问用户
- **可追溯性:** 重大操作前记录到 `memory/` 日志
- **资源保护:** 避免重复 API 调用，遵守 Rate Limits

### 代码风格
- **DRY 原则:** 避免重复代码
- **模块化:** 优先可维护性
- **注释清晰:** 关键逻辑必须注释
- **错误处理:** 完善的 try/catch 和用户反馈

### 沟通风格
- **简洁:** 用最少的语言传达核心信息
- **技术化:** 可按需深入技术细节
- **结构化:** 复杂信息使用列表/表格
- **Emoji:** 适当使用表情提升可读性（仅非正式场景）

---

## 🧠 关键经验

1. **权限问题**（2026-04-04）
   - 错误：`exec security=full ask=off` 未正确配置
   - 解决：检查 agent 的 auth-profiles.json，确保权限开
   - 教训：操作 GitHub API 前先测试基础连接

2. **模型切换**（2026-04-05）
   - 错误：多个模型（anthropic/gemini-*, qwen/*）不可用
   - 解决：切换回默认的 `openrouter/stepfun/step-3.5-flash:free`
   - 教训：需要建立模型可用性监控机制

3. **Maton Gateway 认证流程**
   - 仅提供 API Key 不够，需要先在 maton.ai 完成 OAuth
   - 创建 Connection API 需要额外步骤
   - 备用方案：GitHub PAT 更直接

---

## 📊 环境配置

- **OpenClaw 版本:** 2026.3.31
- **Runtime:** agent=main | host=service-69d174f33b70d614c66fa39e-7b5dcf9455-vchkq
- **Default Model:** openrouter/stepfun/step-3.5-flash:free
- **Channel:** telegram
- **Workspace:** `/home/node/.openclaw/workspace`

---

## 🔗 外部服务凭证（示例 - 实际需加密）

| 服务 | 类型 | 状态 | 备注 |
|------|------|------|------|
| GitHub | PAT | ❓ 待提供 | 需要 `repo` + `read:org` 权限 |
| Maton | API Key | ✅ 已提供 | OAuth 连接未完成 |
| OpenRouter | API Key | ✅ 已配置 | 使用环境变量 `OPENROUTER_API_KEY` |

---

## ⏭️ 待办事项（待转移到任务系统）

- [ ] 等待用户提供 GitHub PAT 并测试连接
- [ ] 验证 `Node-magic-change-panel.js` 的功能完整性
- [ ] 设计并实现 cron 自动化任务（周一计划、周五总结）
- [ ] 配置邮件/日历集成插件（如需）
- [ ] 定期清理 `memory/` 文件，合并到本文件

---

## 📅 最近会话记录

- **2026-04-05 00:42** - 用户询问 GitHub 连接，开始配置
- **2026-04-05 01:11** - 模型故障，系统错误
- **2026-04-05 00:38-00:41** - 简短问候对话
- **2026-04-05 03:52** - 重启会话，继续 GitHub 连接任务
- **2026-04-05 03:57** - 讨论"开机流程"改造
- **2026-04-05 06:35** - 用户询问"在吗"
- **2026-04-05 06:36** - 获得授权更新配置文件

---

## 📚 重要学习资源

### OpenClaw GitHub Workflow Skills
**仓库**: https://github.com/feision/openclaw-github-workflow-skills  
**用途**: GitHub API 操作、分支管理、PR 流程的完整教程  
**本地路径**: `openclaw-github-workflow-skills/`（独立仓库，需单独克隆）

#### 推荐阅读顺序（必读）
1. **COMPLETE_WORKFLOW.md** ⭐ - 完整工作流（实战记录，含错误排查）
2. **SETUP_GUIDE.md** - 环境配置（Token 设置、认证）
3. **QUICK_START.md** - 5分钟快速上手
4. **PERMISSION_TROUBLESHOOTING.md** - OpenClaw 权限问题处理（`exec security=full ask=off`）
5. **ERROR_HANDLING.md** - 错误诊断与解决

#### 关键命令速查
- 设置 Token: `export GITHUB_TOKEN="ghp_..."`
- 测试连接: `python3 example_scripts/test_connection.py`
- 文件上传: 使用 GitHub Contents API（Base64 编码）
- 权限绕过: `exec security=full ask=off <command>`

#### 分支策略（核心）
- `main` - 默认稳定分支
- `openclaw` - 开发分支（从 main 创建）
- PR 流程: openclaw → main

---

**记住：遇到 GitHub 操作问题，先读 COMPLETE_WORKFLOW.md！** 🎯


