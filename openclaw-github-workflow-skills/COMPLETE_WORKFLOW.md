# 🚀 完整工作流：创建仓库、上传文件、合并分支

> **场景**: 需要将本地 workspace 文件上传到新的 GitHub 仓库，采用 `main` + `Openclaw` 双分支策略
> **目标**: 一次性完成，避免 PR 失败、分支混乱
> **难度**: 中级
> **时间**: 10-15 分钟

---

## 📌 核心原则

1. **`main` 分支必须最早存在并推送**（即使只是占位 README）
2. **`Openclaw` 必须从 `main` 分支创建**，这样才有共同历史，PR 才能成功
3. **分支命名必须一致**：远程默认分支是 `main`，本地也必须叫 `main`（不是 `master`）
4. **先推 `main`，再推 `Openclaw`**，然后 PR `Openclaw` → `main`

---

## ⚠️ 常见错误（我的血泪教训）

### 错误 A: 先创建 `Openclaw` 再创建 `main`

**表现**: PR 失败，提示 "No commits between main and Openclaw"

**原因**: `main` 是从 `Openclaw` 分出来的，所有提交都在 `main` 历史中，PR 无新提交。

** fixes**: 删除本地 `Openclaw`，从 `main` 重新创建:
```bash
git checkout main
git branch -D Openclaw
git checkout -b Openclaw
# 添加文件、提交、推送
```

### 错误 B: 分支名不一致（本地 master vs 远程 main）

**表现**: 推送后远程出现两个分支（master 和 main），PR 失败

**原因**: `git init` 默认创建 `master`，但 GitHub 期望 `main`

**解决**: 本地立即改名:
```bash
git branch -m main  # 将 master 改为 main
```

### 错误 C: `main` 和 `Openclaw` 没有共同祖先

**表现**: PR 失败，提示 "Branch has no history in common with base"

**原因**: `main` 是孤儿分支（orphan），从零创建，而 `Openclaw` 是另一个孤儿分支，它们没有共同提交。

**解决**: 确保 `main` 先创建并推送，然后 `Openclaw` 从 `main` 创建。

---

## 🗺️ 步骤总览

```
1. 创建空仓库（GitHub UI 或 API）
2. 本地初始化，创建 main 分支（占位 README）
3. 推送 main 到远程
4. 基于 main 创建 Openclaw 分支
5. 在 Openclaw 分支添加所有文件，提交
6. 推送 Openclaw 到远程
7. 创建 PR: Openclaw → main
8. 在 GitHub 上合并 PR
```

---

## 🔧 详细步骤（带命令）

### 准备工作

```bash
# 1. 确保环境变量已设置
export GITHUB_TOKEN="your_personal_access_token"

# 2. 测试连接
python3 -c "
import urllib.request, json, os
token = os.environ.get('GITHUB_TOKEN')
req = urllib.request.Request('https://api.github.com/user')
req.add_header('Authorization', f'token {token}')
user = json.load(urllib.request.urlopen(req))
print(f'✅ Connected as {user[\"login\"]}')
"
```

---

### Step 1: 创建空仓库（GitHub）

**方式 A: GitHub UI**
1. 访问 https://github.com/new
2. 仓库名: `openclaw`
3. 不要勾选 "Initialize this repository with a README"
4. 创建

**方式 B: API (可选)**
```python
import urllib.request, json, os
token = os.environ['GITHUB_TOKEN']
data = json.dumps({'name': 'openclaw', 'private': False}).encode()
req = urllib.request.Request('https://api.github.com/user/repos', data=data, method='POST')
req.add_header('Authorization', f'token {token}')
req.add_header('Content-Type', 'application/json')
repo = json.load(urllib.request.urlopen(req))
print(repo['html_url'])
```

---

### Step 2: 本地初始化并创建 `main` 分支

```bash
# 工作目录
mkdir openclaw-upload && cd openclaw-upload

# 初始化 Git，并立即指定默认分支为 main
# (Git 默认可能是 master，必须改名)
git init
git branch -m main

# 创建占位 README（main 分支的初始内容）
cat > README.md << 'EOF'
# OpenClaw

AI 助手工作空间。

完整配置位于 `Openclaw` 分支，包含所有文档、技能和记忆。
EOF

# 提交到 main 分支
git add README.md
git -c user.name="OpenClaw Assistant" -c user.email="assistant@openclaw.ai" commit -m "Initial main - placeholder"
```

⚠️ **关键点**: GitHub 新建仓库的默认分支通常是 `main`（也可能是 `master`，取决于配置）。**必须保证本地初始化的分支与远程默认分支同名**。如果 `git init` 后默认是 `master`，必须用 `git branch -m main` 改名。

---

---

### Step 3: 推送 `main` 到远程

```bash
git remote add origin https://github.com/feision/openclaw.git
git push -u origin main
```

✅ 现在远程 `main` 分支已存在，且有一个简单的 README。

---

### Step 4: 基于 `main` 创建 `Openclaw` 分支

```bash
# 从 main 分支创建 Openclaw
git checkout -b Openclaw

# (此时 Openclaw 和 main 内容相同，都只有 README)
```

---

### Step 5: 在 `Openclaw` 分支添加所有文件

```bash
# 删除占位 README（会被覆盖）
rm README.md

# 复制你的 workspace 所有文件
# 注意: 排除嵌套的 .git 目录！
cp -r /home/node/.openclaw/workspace/* .
find . -name ".git" -type d -exec rm -rf {} + 2>/dev/null

# 添加 .gitignore（重要！防止敏感文件上传）
cat > .gitignore << 'EOF'
# OpenClaw workspace .gitignore
.openclaw/
**/.openclaw/
*.tmp *.log .env *.key *.pem
.DS_Store Thumbs.db
.vscode/ .idea/
__pycache__/ venv/ env/
node_modules/
credentials.json
EOF

# 可选：添加补充文档（如 PROJECT.md, USAGE.md）
# 如果还没有，创建它们：

cat > PROJECT.md << 'EOF'
# 🦞 OpenClaw 工作空间 - 项目总览
... 你的内容 ...
EOF

cat > USAGE.md << 'EOF'
# 📖 使用指南
... 你的内容 ...
EOF

# 提交所有文件
git add .
git commit -m "feat: 上传完整工作空间档案

- 身份配置 (SOUL.md, USER.md, IDENTITY.md)
- 记忆系统 (MEMORY.md + memory/)
- Heartbeat 自动化检查
- GitHub Workflow 教程
- 项目文档 (PROJECT.md, USAGE.md)
- 所有项目文件"
```

---

### Step 6: 推送 `Openclaw` 到远程

```bash
git push origin Openclaw
```

---

### Step 7: 验证并创建 Pull Request

**验证本地分支关系**（确保 `main` 有提交，`Openclaw` 有更新）:

```bash
# 1. 查看所有分支
git branch -a

# 2. 检查 main 的提交
git log --oneline main -1

# 3. 检查 Openclaw 相对于 main 的提交
git log --oneline main..Openclaw  # 应该有输出

# 4. 检查文件差异
git diff main...Openclaw --stat  # 应该显示你添加的文件
```

如果以上都正常，说明分支结构正确，可以创建 PR。

---

**方式 A: GitHub UI（推荐）**
1. 访问你的仓库 URL
2. 应该看到提示: "Openclaw had recent pushes less than a minute ago. Compare & pull request"
3. 点击 "Compare & pull request"
4. 确认:
   - base: `main`
   - compare: `Openclaw`
5. 填写 PR 描述，点击 "Create pull request"

**方式 B: API（自动化）**
```python
import urllib.request, json, os
token = os.environ['GITHUB_TOKEN']
pr_data = {
    'title': '🚀 初始化 OpenClaw 工作空间',
    'head': 'Openclaw',
    'base': 'main',
    'body': '请审查后合并到 main。'
}
req = urllib.request.Request(
    'https://api.github.com/repos/feision/openclaw/pulls',
    data=json.dumps(pr_data).encode(),
    method='POST'
)
req.add_header('Authorization', f'token {token}')
req.add_header('Content-Type', 'application/json')
pr = json.load(urllib.request.urlopen(req))
print(f'PR created: {pr["html_url"]}')
```

---

---

### Step 8: 合并 PR

1. 在 GitHub PR 页面，点击 "Merge pull request"
2. 可选: 删除 `Openclaw` 分支（清理）

---

## ⚠️ 常见错误与解决

### 错误 1: "No commits between main and Openclaw"

**原因**: `main` 是从 `Openclaw` 创建的，`Openclaw` 的所有提交都在 `main` 历史中，导致 PR 无新提交。

**表现**:
```bash
git log --oneline main..Openclaw  # 无输出
```

**解决**:
- 正确的分支关系应该是: `main` 先存在 → `Openclaw` 基于 `main` 创建 → `Openclaw` 有新提交
- 如果已搞乱，删除本地 `Openclaw`，从 `main` 重新创建:
  ```bash
  git checkout main
  git branch -D Openclaw
  git checkout -b Openclaw
  # 然后添加文件、提交
  ```

---

### 错误 2: "Branch has no history in common with base"

**原因**: `main` 和 `Openclaw` 是孤儿分支（没有共同祖先）。

**表现**: 无法创建 PR，即使文件不同。

**解决**: 确保 `main` 分支先创建并推送，然后 `Openclaw` 从 `main` 创建。

---

### 错误 3: 嵌套的 .git 目录（子模块问题）

**原因**: 复制 workspace 时把子目录的 `.git` 也复制了。

**表现**: `git status` 显示 "adding embedded git repository"

**解决**: 上传前删除所有嵌套 `.git`:
```bash
find . -name ".git" -type d -exec rm -rf {} + 2>/dev/null
```

---

### 错误 4: `main` 和 `Openclaw` 内容相同，PR 显示无差异

**原因**: `main` 占位 README 太简单，`Openclaw` 更新的文件都已在 `main` 历史中。

**解决**: 保持 `main` 为极简占位，`Openclaw` 的提交必须是新的（不是从 `main` 复制历史）。详见错误 1。

---

## ✅ 检查清单（执行前核对）

- [ ] `GITHUB_TOKEN` 已设置并有效
- [ ] 远程仓库已创建（空的，无 README）
- [ ] 本地 `main` 分支已创建并推送（至少一个占位 README）
- [ ] 本地 `Openclaw` 分支从 `main` 创建（`git checkout -b Openclaw`）
- [ ] `Openclaw` 分支已添加所有文件并提交
- [ ] 已删除所有嵌套 `.git` 目录
- [ ] `.gitignore` 已配置，避免敏感文件
- [ ] 已推送 `Openclaw` 到远程
- [ ] PR 已创建且显示正确的文件差异
- [ ] PR 描述清晰，包含变更内容列表

---

## 🔍 验证流程

```bash
# 1. 检查本地分支
git branch -a

# 2. 检查提交差异
git log --oneline main..Openclaw  # 应该有输出

# 3. 检查远程分支
git ls-remote origin

# 4. 检查文件差异
git diff main...Openclaw --stat

# 5. 如果以上都正常，PR 应该成功
```

---

## 💡 最佳实践

1. **分支命名**: 使用 `Openclaw`（首字母大写）或 `feature/xxx`，一致即可
2. **COMMIT 信息**: 明确标注功能，如 `feat: 上传工作空间档案`
3. **README 占位**: `main` 的 README 仅说明详情见 `Openclaw` 分支
4. **敏感文件**: `.gitignore` 必须包含 `.env`, `*.key`, `credentials.json`
5. **环境变量**: 永远不要将 `GITHUB_TOKEN` 硬编码在任何文件
6. **PR 描述**: 包含完整变更列表，方便审查
7. **合并后**: 考虑删除 `Openclaw` 分支，保持 `main` 唯一

---

## 📚 扩展阅读

- GitHub Flow: https://guides.github.com/introduction/flow/
- Git 分支策略: https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
- OpenClaw 工作空间使用: 见 `PROJECT.md` 和 `USAGE.md`

---

## 🎯 快速命令脚本

```bash
#!/bin/bash
# 一键上传完整工作空间到新仓库（假设 main 已存在且占位）

set -e

# 1. 从 main 创建 Openclaw
git checkout main
git checkout -b Openclaw

# 2. 清理并复制文件
rm -rf *
cp -r /home/node/.openclaw/workspace/* .
find . -name ".git" -type d -exec rm -rf {} + 2>/dev/null

# 3. 添加 .gitignore 和补充文档
cat > .gitignore << 'EOF'
.openclaw/
**/.openclaw/
*.tmp *.log .env *.key
.DS_Store
__pycache__/
credentials.json
EOF

# 4. 提交
git add .
git commit -m "feat: 初始化工作空间档案"
git push origin Openclaw

echo "✅ Openclaw 分支已推送，请在 GitHub 创建 PR 合并到 main"
```

---

**记住: `main` 先建，`Openclaw` 后建，PR 自然成。** 🎉
