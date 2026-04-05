# ⚡ 灵活部署工具

提供两种部署方式：
- `deploy/github_deploy.py` - **全能工具**，支持 Direct（直接推送）和 Feature（开发分支工作流）两种模式
- `deploy/deploy_f.py` - **开发分支工作流专用脚本**，参数更简洁，适合日常开发

两者都能快速推送**指定文件或目录**到 GitHub。

---

## 🎯 为什么需要这个？

- 你每次工作的内容可能只是 workspace 的一部分
- 有时只需推送单个文件，有时是某个目录
- 不想每次打包整个 workspace

这个工具让你精确控制要推送的内容，并支持两种工作流模式。

---

## 🚀 快速开始

### 1️⃣ 配置 Token

```bash
export GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### 2️⃣ 基本用法

```bash
cd /home/node/.openclaw/workspace/openclaw-github-workflow-skills
python3 deploy/github_deploy.py \
  --repo feision/openclaw \
  --branch openclaw \
  --path SOUL.md \
  --path USER.md \
  --path MEMORY.md
```

---

## 📝 使用场景

### 场景 A: 直接推送（Direct 模式）

直接推送到指定分支（如 `main`），可选的创建 PR：

```bash
python3 deploy/github_deploy.py \
  --repo feision/openclaw \
  --branch main \
  --path README.md \
  --commit-msg "Update README" \
  --no-pr  # 不创建 PR，直接推送
```

### 场景 B: 开发分支工作流（Feature 模式）⭐ 推荐用于频繁开发

先推送到**开发分支**（如 `openclaw`），再创建 PR 合并到**主分支**（`main`）：

```bash
python3 deploy/github_deploy.py \
  --repo feision/openclaw \
  --dev-branch openclaw \
  --base-branch main \
  --mode feature \
  --path SOUL.md \
  --path USER.md \
  --path MEMORY.md \
  --commit-msg "Update user configs"
```

**输出示例**：
```
🚀 模式: FEATURE (先推送到 openclaw，再 PR 到 main)
📋 确保基础分支存在: main
✅ 分支已存在: main
📦 准备 Git 仓库...
  📄 添加文件: SOUL.md
  📄 添加文件: USER.md
📤 推送分支: openclaw
✅ 推送完成
🔀 创建 Pull Request...
✅ PR 创建成功: https://github.com/feision/openclaw/pull/1 (#1)
🎉 部署完成！
```

### 场景 C: 自动合并 PR

使用 `--auto-merge` 自动合并 PR（谨慎）：

```bash
python3 deploy/github_deploy.py \
  --repo feision/openclaw \
  --dev-branch openclaw \
  --mode feature \
  --path SOUL.md \
  --auto-merge
```

### 场景 D: 强制推送

当需要覆盖开发分支时使用 `--force`：

```bash
python3 deploy/github_deploy.py \
  --repo feision/openclaw \
  --dev-branch openclaw \
  --mode feature \
  --path SOUL.md \
  --force
```

### 场景 F: 开发分支工作流专用脚本（简化版）⭐

如果你只需要**开发分支工作流**（开发分支→PR→主分支）的简化操作，使用专门的脚本：

```bash
python3 deploy/deploy_f.py \
  --repo feision/openclaw \
  --dev-branch feature/lobster \
  --base-branch main \
  --path SOUL.md \
  --path USER.md \
  --path MEMORY.md \
  --commit-msg "Update configs"
```

**`deploy_f.py` 特点**:
- 只做**开发分支工作流**，无需 `--mode` 参数
- 自动创建 PR（不可关闭）
- 参数更直观，适合作为常用命令别名
- 可配合 `--auto-merge` 自动合并（谨慎）
- 支持 `--force` 强制推送

**输出示例**:
```
🚀 开发分支工作流: 先推送到 feature/lobster，再 PR 到 main
   仓库: feision/openclaw
   路径: SOUL.md, USER.md, MEMORY.md
📋 确保基础分支存在: main
✅ 分支已存在: main
📦 准备 Git 仓库...
  📄 添加文件: SOUL.md
  📄 添加文件: USER.md
📤 推送分支: feature/lobster
✅ 推送完成
🔀 创建 Pull Request...
✅ PR 创建成功: https://github.com/feision/openclaw/pull/1 (#1)
🎉 开发分支工作流部署完成！
```

> 💡 **建议**: 日常开发使用 `deploy_f.py`，复杂场景（如直接推送、不创建 PR）使用 `github_deploy.py`。

---

## 🔧 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--repo` | ✅ | GitHub 仓库名，如 `feision/openclaw` |
| `--path` | ✅ | 要推送的文件或目录路径（可重复指定多个） |
| `--commit-msg` | ❌ | Git 提交信息，默认 "Deploy files" |
| `--force` | ❌ | 强制推送（谨慎使用） |

### 模式相关参数

| 参数 | 模式 | 说明 |
|------|------|------|
| `--mode` | 通用 | 部署模式: `direct`(默认) 或 `feature` |
| `--branch` | direct | 目标分支（默认 `main`） |
| `--dev-branch` | feature | 开发分支（默认 `openclaw`） |
| `--base-branch` | feature | 基础分支（默认 `main`） |
| `--no-pr` | direct | 不创建 PR，直接推送到目标分支 |
| `--auto-merge` | feature | 自动合并 PR（需 PR 创建成功） |

---

## 🔄 两种模式对比

| 特性 | DIRECT 模式 | FEATURE 模式 |
|------|-------------|--------------|
| **推送目标** | 直接推送到 `--branch` | 先推送到 `--dev-branch` |
| **PR 创建** | 可选（`--no-pr` 关闭） | 自动创建（`--dev-branch` → `--base-branch`） |
| **适用场景** | 快速修复、文档更新、直接推送到 main | 功能开发、多次迭代、需要代码审查 |
| **历史追溯** | 修改直接在 main，难区分 | 开发分支有独立历史，PR 合并后仍可追溯 |

> 💡 **提示**: 如果你主要使用**开发分支工作流**，可以直接用 `deploy/deploy_f.py`，参数更简洁。

---

## ⚠️ 注意事项

1. **Token 权限**: `GITHUB_TOKEN` 需要 `repo` 权限（完全控制仓库）
2. **强制推送**: `--force` 会覆盖远程历史，仅在你明确知道后果时使用
3. **路径存在性**: 所有 `--path` 必须存在，否则报错
4. **分支保护**: 如果目标分支有保护规则（如需要 PR），请使用 `--mode feature`
5. **PR 限制**: 创建 PR 要求基础分支存在
6. **Feature 模式自动创建分支**: 如果 `--dev-branch` 不存在，会自动从 `--base-branch` 创建

---

## 📚 相关链接

- 完整工作流教程: `../COMPLETE_WORKFLOW.md`
- 环境配置: `../SETUP_GUIDE.md`
- 错误处理: `../ERROR_HANDLING.md`

---

**一句话总结：现在你可以选择"直接推"或"先开发再 PR"，让代码管理更清晰。** 🎯
