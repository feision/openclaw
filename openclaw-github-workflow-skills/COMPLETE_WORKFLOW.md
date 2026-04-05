---

## 📝 实战记录（2025-04-05）

> 记录一次真实的 openclaw 仓库搭建过程，包括踩坑和解决方案。

### 场景

需要创建 `feision/openclaw` 仓库，采用 `main`（默认）+ `openclaw`（开发）双分支策略。本地已有完整 workspace 文件，目标是上传到 GitHub。

### 我的最初错误

1. **先创建 `openclaw` 再创建 `main`** → PR 失败（"No commits between main and openclaw"）
2. **分支名不一致**（本地 `master` vs 远程 `main`）
3. **使用孤儿分支** → 无共同历史

### 正确的最终流程（测试成功）

#### 步骤 1: 创建空仓库（GitHub UI）

- 访问 https://github.com/new
- 仓库名: `openclaw`
- **不要勾选** "Initialize this repository with a README"
- 创建 → 远程默认分支为 `main`

#### 步骤 2: 本地创建 `main` 占位并推送

```bash
mkdir openclaw-upload && cd openclaw-upload
git init
git branch -m main          # 关键：确保本地分支名与远程一致
echo "# OpenClaw" > README.md
git add . && git commit -m "Initial main - placeholder"
git remote add origin https://github.com/feision/openclaw.git
git push -u origin main     # ✅ 先推 main
```

#### 步骤 3: 从 `main` 创建 `openclaw` 分支

```bash
git checkout -b openclaw
```

#### 步骤 4: 上传完整文件（关键：保护 .git 目录）

```bash
# 安全方法：使用临时目录过滤 .git
TMPDIR=$(mktemp -d)
cp -r /home/node/.openclaw/workspace/* "$TMPDIR/"
find "$TMPDIR" -name ".git" -type d -exec rm -rf {} +
cp -r "$TMPDIR"/* .
rm -rf "$TMPDIR"

# 或者：克隆后直接替换（推荐）
git clone https://github.com/feision/openclaw.git workspace
cd workspace
git checkout -b openclaw
# 删除除 .git 外的所有文件
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} \;
# 复制完整 workspace 文件过来
cp -r /home/node/.openclaw/workspace/* .
find . -name ".git" -type d -exec rm -rf {} + 2>/dev/null  # 删除子目录的 .git
git add . && git commit -m "feat: 上传完整工作空间"
git push origin openclaw
```

#### 步骤 5: 创建 PR 并合并

- GitHub UI: https://github.com/feision/openclaw 会自动提示 "Compare & pull request"
- base: `main`, compare: `openclaw`
- 填写描述，创建 PR
- 审查后点击 "Merge pull request"

#### 关键命令验证

```bash
# 验证分支关系
git log --oneline main..openclaw   # 应有输出
git diff main...openclaw --stat    # 应显示新增文件

# 验证远程分支
git ls-remote origin
```

### 结果

✅ 仓库地址: https://github.com/feision/openclaw  
✅ 默认分支: `main`  
✅ 开发分支: `openclaw`（小写）  
✅ PR 成功创建并合并

### 注意事项

1. **分支顺序不能颠倒**：必须先有 `main`，才能创建 `openclaw` 并 PR
2. **分支名一致**：本地如果是 `master` 必须改成 `main`（或配置 GitHub 默认分支）
3. **避免嵌套 .git**：复制文件后务必删除子目录的 `.git`，否则会变成子模块
4. **保持 `.git` 完整**：操作时只删除**子目录**的 `.git`，顶层 `.git` 不能动
5. **验证后再 PR**：用 `git log main..openclaw` 确认有差异再创建 PR

---

**本次实战验证了 COMPLETE_WORKFLOW.md 中的流程，确保可一次成功。** 🎯
