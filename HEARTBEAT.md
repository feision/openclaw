# HEARTBEAT.md Template

```markdown
# HEARTBEAT.md - 定期检查任务列表

## 触发条件
- 每隔约 30 分钟自动执行（具体间隔由 OpenClaw 系统调度）
- 每次会话开始时也会读取此文件作为参考

## 检查任务（每次 heartbeat）

### 📡 GitHub 相关
- [ ] 检查 GitHub 通知（mentions, PR review requests, issue assignments）
- [ ] 检查是否有新的 Issue 或 PR 需要关注
- [ ] 检查 CI/CD 状态（是否有构建失败）
- [ ] 检查 Star/Follow 通知（可选）

### 📧 通信渠道
- [ ] 检查未读重要消息（Telegram/Slack/Email - 需配置插件）
- [ ] 检查是否有需要回复的对话

### ⏰ 日历与时间
- [ ] 查看今天和明天的日程事件（15分钟内提醒）
- [ ] 检查是否有即将到期的任务

### 💻 系统状态（如适用）
- [ ] 检查服务器健康状态（CPU、内存、磁盘）
- [ ] 检查服务运行状态（Docker, Workers, VPS）
- [ ] 检查日志错误（关键服务）

### 🌤️ 环境信息
- [ ] 获取当地天气（今天/明天）
- [ ] 特殊天气提醒（暴雨、台风等）

### 📊 项目进度
- [ ] 检查活跃项目的最近进展（git log、 Issue 更新）
- [ ] 检查是否有阻塞任务需要处理

### 📚 教程同步
- [ ] 检查 `openclaw-github-workflow-skills` 仓库更新（独立仓库）
- [ ] 如有更新，拉取到本地（路径: `openclaw-github-workflow-skills/`）
- [ ] 更新 MEMORY.md 中的学习资源摘要（如需）

## 响应行为
- 如果有紧急事项 → 立即发送通知给用户
- 如果一切正常 → 回复 `HEARTBEAT_OK`（不打扰用户）
- 如果需要用户决策 → 提供选项并询问
- 如果教程有更新 → 发送简短通知（"教程已更新，请查看"）

## 备注
- 所有检查应在 10 秒内完成，避免耗时操作
- 涉及网络请求需设置超时
- 避免频繁调用同一 API（GitHub Rate Limit: 5000/hr）
```
