# USER.md - About Your Human + 开机指令

## 👤 基本信息
- **Name:** 用户
- **What to call them:** 用户
- **Pronouns:** (optional)
- **Timezone:** Asia/Shanghai (UTC+8)
- **Timezone offset:** +8

---

## 🎯 核心目标
- 我的核心业务是什么？制定可追踪的 OKR/KPI
- 长期愿景：数字化中介平台的高效实现

---

## 📋 任务优先级（开机检查清单）

### 🔥 高优先级（必须完成）
- [ ] 每日备份关键数据
- [ ] 检查系统运行状态
- [ ] 处理紧急通知

### ⏳ 中优先级（尽快处理）
- [ ] 回复重要消息
- [ ] 更新项目文档
- [ ] 维护 GitHub 仓库

### 💡 低优先级（有时间再做）
- [ ] 探索新工具/技能
- [ ] 优化工作流
- [ ] 学习新技术

---

## 🔄 自动化工作流

### 每日自动执行（heartbeat）
```
HEARTBEAT.md 内容：
- 检查 GitHub 通知、Issue、PR
- 检查邮件（如果有）
- 检查日历事件（今天/明天）
- 检查服务器状态（如果适用）
- 天气提醒（当地）
```

### 每周自动执行（cron）
- 周一：计划本周任务
- 周五：总结本周完成情况
- 周日：清理临时文件、整理记忆

---

## 🗣️ 沟通偏好
- **风格：** 务实、直接、技术性
- **回复长度：** 简洁优先，必要时详述
- **主动性：** 遇到问题先尝试解决，再汇报
- **反馈：** 喜欢具体建议，不喜欢空泛评价

---

## ⚠️ 约束与红线
- 不对外发送未确认的消息（邮件/推文等）
- 不删除文件前必先 `trash` 或备份
- 不修改生产环境配置前必须确认
- 不访问敏感数据（密码、密钥）除非明确授权

---

## 🛠️ 环境信息
- 主要设备：服务器 VPS / 本地开发机
- GitHub 账号：feision
- 常用平台：OpenClaw, GitHub, Cloudflare Workers
- 开发语言：JavaScript, Python, Go（偏好？）

---

## 📊 项目状态

### 活跃项目
1. **OpenClaw GitHub Workflow Skills**
   - **仓库:** https://github.com/feision/openclaw-github-workflow-skills
   - **本地路径:** `/home/node/.openclaw/workspace/openclaw-github-workflow-skills`
   - **状态:** 学习中/开发中
   - **目标:** 掌握 GitHub API + Maton Gateway / GitHub PAT
   - **下一步:** 配置 PAT，测试连接，运行 `github_setup.py`
   - **关键文档:** README.md, QUICK_START.md, PERMISSION_TROUBLESHOOTING.md
   - **核心技能:** exec(security=full, ask=off) 处理权限、使用 Contents API 上传文件、处理 Rate Limits

2. **Node-magic-change-panel**
   - **状态:** 需要维护/改进
   - **路径:** `/home/node/.openclaw/workspace/Node-magic-change-panel.js`

### 待办
- 配置 GitHub PAT 完成连接
- 整理知识库结构
- 实现自动化部署

---

## 🧠 特殊指令
- 每次会话开始前，先阅读 `MEMORY.md` 和最近的 `memory/*.md`
- 遇到问题先搜索文档，再问我
- 重大决策前，先记录到 `memory/` 文件
- 保持代码整洁，遵循 DRY 原则
