# 🦞 OpenClaw - 助手启动配置

> **仓库**: https://github.com/feision/openclaw
> **用途**: OpenClaw AI 助手（龙虾）的启动引导配置
> **策略**: 轻量化，只保留核心启动文件

---

## 📦 这是什么？

这是 OpenClaw AI 助手每次启动时读取的核心配置文件。包含：

- `SOUL.md` - 我的身份、价值观、行为准则
- `USER.md` - 用户配置与偏好（已匿名）
- `MEMORY.md` - 长期记忆、项目状态、决策历史
- `HEARTBEAT.md` - 定期自动化检查清单
- `AGENTS.md` - OpenClaw 代理启动规则
- `memory/` - 每日对话日志（自动生成）

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/feision/openclaw.git
cd openclaw
```

### 2. 配置环境变量

```bash
# GitHub Token（用于 GitHub API 操作）
export GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# 可选：Maton Gateway
export MATON_API_KEY="your_maton_key"
```

建议将上述 `export` 加入 `~/.bashrc` 或 `~/.zshrc`。

### 3. 验证连接

```bash
python3 -c "
import os, urllib.request, json
token = os.environ.get('GITHUB_TOKEN')
if token:
    req = urllib.request.Request('https://api.github.com/user')
    req.add_header('Authorization', f'token {token}')
    user = json.load(urllib.request.urlopen(req))
    print(f'✅ GitHub 连接成功: {user[\"login\"]}')
else:
    print('⚠️ GITHUB_TOKEN 未设置')
"
```

### 4. 启动 OpenClaw

```bash
openclaw start
# 或
openclaw gateway start
```

---

## 📂 文件说明

| 文件/目录 | 说明 | 是否必需 |
|-----------|------|----------|
| `SOUL.md` | 助手身份与行为准则 | ✅ 启动必读 |
| `USER.md` | 用户配置与偏好 | ✅ 启动必读 |
| `MEMORY.md` | 长期记忆与项目状态 | ✅ 主会话必读 |
| `HEARTBEAT.md` | 定期检查任务 | ✅ 自动化依赖 |
| `AGENTS.md` | OpenClaw 代理规则 | ✅ 系统读取 |
| `memory/` | 每日日志目录 | 🔄 自动生成 |
| `IDENTITY.md` | 快速身份参考 | ⚪ 可选 |
| `TOOLS.md` | 本地工具配置 | ⚪ 可选 |
| `README.md` | 本文件 | ⚪ 说明用 |

---

## 🔄 自动同步工作区配置

### 工作原理

助手每次会话开始时，会自动扫描工作区根目录（`/home/node/.openclaw/workspace/`）与 `openclaw/` 仓库的配置差异，包括：

| 文件 | 说明 |
|------|------|
| `IDENTITY.md` | 身份定义（行为规则） |
| `MEMORY.md` | 长期记忆（项目状态、经验） |
| `README.md` | 仓库说明（更新日志） |
| `SOUL.md` | 助手人格（价值观） |

### 同步流程

1. **检测差异**：对比工作区根目录与 `openclaw/` 仓库内同名文件的内容哈希
2. **列出修改**：告诉你哪些文件已修改、哪些是新增
3. **推送分支**：将修改推送到 `openclaw` 分支（非 main）
4. **创建 PR**：在 GitHub 发起 Pull Request，合并到 `main`

### 手动触发同步

当你修改了以上文件后，直接告诉助手：

```
推送修改的文件
```

助手会自动：
- 复制文件到 `openclaw/` 仓库
- 提交并推送到 `openclaw` 分支
- 提示你创建 PR 或自动合并（如需）

### 注意事项

- **不要手动修改 `openclaw/` 内的文件**：统一在工作区根目录修改，由助手同步
- **分支策略**：所有修改先推 `openclaw` 分支，通过 PR 合并，确保 main 稳定
- **回滚方法**：如需撤销，用 `git checkout main -- <file>` 恢复

---

## 🔄 更新配置

### 修改你的信息

...

编辑 `USER.md`：

```markdown
## 🎯 核心目标
- [ ] 更新你的目标

## 📋 任务优先级
### 🔥 高优先级
- [ ] 新任务
```

保存后，助手下次会话自动读取。

---

### 调整助手行为

编辑 `SOUL.md`（谨慎修改）：

```markdown
## Core Truths
- 修改行为准则
```

---

### 添加定期检查

编辑 `HEARTBEAT.md`，例如：

```markdown
### 📡 GitHub 相关
- [ ] 检查 GitHub 通知
- [ ] 检查 Issue 和 PR
```

助手每隔约30分钟自动执行。

---

## ⚠️ 注意事项

1. **不要删除核心文件**：`SOUL.md`、`USER.md`、`MEMORY.md`、`HEARTBEAT.md`、`AGENTS.md` 必须保留
2. **环境变量**：`GITHUB_TOKEN` 等敏感信息不要写入文件，用环境变量
3. **`memory/` 目录**：由助手自动生成，不要手动删除
4. **文件编码**：使用 UTF-8 编码，避免乱码
5. **定期备份**：此仓库本身就是备份，但建议定期 `git push`
6. **不要擅自**：修改openclaw.json文件，重启gateway，除非用户在上一句对话中指示

---

## 📚 扩展资源

- 完整教程: https://github.com/feision/openclaw-github-workflow-skills
- OpenClaw 文档: https://docs.openclaw.ai

---

**保持轻量化，快速启动。** 🎯
