# OpenClaw Memory System v2.0 - 部署与运维文档

> **版本**: 1.0
> **基于**: https://github.com/feision/agent-memory-manager
> **部署日期**: 2026-04-08
> **适用环境**: OpenClaw workspace (Linux)

---

## 📦 一、整体架构

```
OpenClaw Workspace (优化后)
├── SOUL.md                    # 身份/价值观（不变）
├── USER.md                    # 用户配置（不变）
├── MEMORY.md                  # 精简索引 (~70 行, ~230 tokens)
├── HEARTBEAT.md               # 心跳检查（已增强）
├── AGENTS.md                  # 启动规则（已升级 v2.0）
│
├── .memory/                   # 新增：结构化记忆存储
│   ├── memory.db              # SQLite 数据库（核心）
│   ├── config.json            # 记忆系统配置
│   ├── working/
│   │   └── session_state.json # 工作上下文（当前任务/目标）
│   ├── logs/                  # 原始日志归档（原 memory/ 目录）
│   │   ├── 2026-04-04-api-key-config.md
│   │   ├── 2026-04-05-0042.md
│   │   ├── 2026-04-05-reasoning-is-required-for-this.md
│   │   └── 2026-04-07-reasoning-is-required-for-this.md
│   └── scripts/               # 工具脚本
│       ├── init_memory.py     # 初始化导入（MEMORY.md → SQLite）
│       ├── query.py           # 查询记忆
│       ├── sync.py            # 同步索引（SQLite → MEMORY.md）
│       ├── maintenance.py     # 维护清理
│       └── test_startup.py    # 启动流程验证
│
└── agent-memory-manager/       #  upstream 仓库（参考用）
    ├── memory_manager.py       # 核心模块（已复制到 .memory/）
    ├── example_usage.py
    └── docs/
```

---

## 🚀 二、部署步骤（从零开始）

### **前置条件**

- ✅ Python 3.9+（测试环境：Python 3.11.2）
- ✅ 至少 10MB 可用磁盘空间
- ✅ OpenClaw 已正常运行（`openclaw` 命令可用）

---

### **步骤 1：克隆参考仓库（可选）**

```bash
cd /home/node/.openclaw/workspace
git clone https://github.com/feision/agent-memory-manager.git
```

**用途**：参考实现、更新核心模块时对照。

---

### **步骤 2：创建 `.memory/` 目录结构**

```bash
# 创建目录
mkdir -p .memory/working
mkdir -p .memory/scripts
mkdir -p .memory/logs

# 迁移旧日志
mv memory/*.md .memory/logs/

# 验证
tree .memory -L 2
```

**预期输出**：
```
.memory
├── logs
│   ├── 2026-04-04-api-key-config.md
│   ├── 2026-04-05-0042.md
│   ├── 2026-04-05-reasoning-is-required-for-this.md
│   └── 2026-04-07-reasoning-is-required-for-this.md
├── scripts
└── working
```

---

### **步骤 3：复制核心模块**

```bash
# 复制 memory_manager.py（核心）
cp agent-memory-manager/memory_manager.py .memory/

# 复制示例脚本到 scripts/（参考用）
cp agent-memory-manager/example_usage.py .memory/scripts/
```

**验证**：
```bash
ls -lh .memory/memory_manager.py
# 应为 -rw-r--r-- 1 ... 内存管理器文件
```

---

### **步骤 4：编写初始化脚本**

创建 `.memory/scripts/init_memory.py`（见附录 A 完整代码）。

**作用**：解析现有的 `MEMORY.md`，提取关键信息，导入 SQLite 数据库。

**运行**：
```bash
python3 .memory/scripts/init_memory.py
```

**预期输出**：
```
============================================================
  OpenClaw 记忆初始化 v2
============================================================

📖 解析 MEMORY.md ...
   提取到 11 条记忆

🗄️  初始化 SQLite 数据库 ...
   数据库已创建/连接

📥 导入记忆 ...
   [1/11] [identity] Name: 龙虾 (Lobster)
   ...
✅ 初始化完成！
   总记忆数 : 11
   分类分布 : {'decision': 2, 'experience': 1, ...}
```

---

### **步骤 5：验证数据导入**

```bash
# 查询测试
python3 .memory/scripts/query.py "GitHub"
python3 .memory/scripts/query.py "模型"

# 启动流程验证
python3 .memory/scripts/test_startup.py
```

**预期输出**：
```
============================================================
  OpenClaw 启动流程验证 v2.0
============================================================

1️⃣  加载 SOUL.md...
   ✅ 身份: 龙虾 (Lobster) - Owner & Architect

...

✅ **启动加载完成**
   总上下文 tokens: ~1262
```

---

### **步骤 6：生成精简 MEMORY.md**

```bash
python3 .memory/scripts/sync.py
```

**效果**：
- 原 `MEMORY.md`：305 行 → 新：74 行
- Token 占用：~1500 → ~230（节省 85%）

**验证**：
```bash
wc -l MEMORY.md  # 应输出 74
head -30 MEMORY.md
```

---

### **步骤 7：更新 AGENTS.md 和 HEARTBEAT.md**

**AGENTS.md** 修改部分：
-  Session Startup 改为 v2.0（轻量/完整两种模式）
-  加入 Memory System v2.0 说明（分层架构、分类标签、写入规范）

**HEARTBEAT.md** 修改部分：
-  增加记忆维护任务（每日 sync、每周 maintenance）

**我已替你完成，直接推送即可**。

---

### **步骤 8：同步到远程仓库**

```bash
# 在 workspace 根目录执行
# 1. 复制修改的文件到 openclaw 仓库
cp AGENTS.md openclaw/AGENTS.md
cp HEARTBEAT.md openclaw/HEARTBEAT.md
cp MEMORY.md openclaw/MEMORY.md
cp README.md openclaw/README.md  # 后续添加

# 2. 提交并推送（使用 openclaw 分支）
cd openclaw
git add -A
git commit -m "feat: upgrade memory system v2.0"
git checkout -b openclaw
git push -u origin openclaw

# 3. 合并到 main
git checkout main
git merge openclaw --no-edit
git push origin main

# 4. 清理分支
git branch -d openclaw
git push origin --delete openclaw
```

---

## 🔧 三、常见问题与排错

### **问题 1：`init_memory.py` 运行报 `IndexError`**

**现象**：
```
IndexError: no such group
```

**原因**：正则表达式匹配 `MEMORY.md` 的 Markdown 结构时，匹配模式与文件实际结构不符。

**解决**：
1. 检查 `MEMORY.md` 的标题格式（是否使用 `## 🦞 身份信息` 而非 `## 身份信息`）
2. 修改 `parse_memory_md()` 中的正则模式，用 `extract_section()` 函数更稳健提取
3. 我已修复脚本，使用 `extract_section()` 按标题精确提取

---

### **问题 2：`query.py` 检索结果为空或乱码**

**现象**：查询关键词无结果，或结果内容不完整。

**原因**：
- 数据库 `memory.db` 未建立 BM25 索引
- 导入的记忆条目内容过短或分类错误

**解决**：
```bash
# 重新初始化数据库
rm .memory/memory.db
python3 .memory/scripts/init_memory.py

# 验证索引构建
python3 -c "
import sys
sys.path.insert(0, '.memory')
from memory_manager import MemoryManager
mm = MemoryManager('.memory')
print('Total:', mm.get_stats()['total_memories'])
results = mm.search('GitHub', top_k=3)
print('Results:', len(results))
"
```

---

### **问题 3：`sync.py` 生成的 MEMORY.md 内容为空**

**现象**：`MEMORY.md` 文件大小异常小（< 500 字符）。

**原因**：
- `get_by_category()` 返回空列表
- 数据库中没有相应分类的记忆

**解决**：
1. 检查数据库内容：
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '.memory')
   from memory_manager import MemoryManager
   mm = MemoryManager('.memory')
   print('All memories:')
   for m in mm.get_all():
       print(f\"  [{m['category']}] {m['content'][:50]}\")
   "
   ```
2. 如果没有数据，重新运行 `init_memory.py`
3. 如果有数据，检查 `sync.py` 中的 `get_by_category()` 调用参数

---

### **问题 4：启动时找不到 `.memory/working/session_state.json`**

**现象**：
```
FileNotFoundError: [Errno 2] No such file or directory: '.memory/working/session_state.json'
```

**原因**：`init_working.py` 使用了错误的方法名（`_save_working_state()` 而非 `_save_working_context()`）。

**解决**：
```bash
# 修正脚本（已修复）
python3 .memory/scripts/init_working.py

# 验证文件生成
ls -lh .memory/working/
```

---

### **问题 5：Git push 失败（权限错误）**

**现象**：
```
fatal: could not read Username for 'https://github.com': No such device or address
```

**原因**：未配置 GitHub Token 或 token 无效。

**解决**：
```bash
# 方法 1：使用环境变量（推荐）
export GITHUB_TOKEN="ghp_xxxxxxxx"
git config credential.helper store

# 方法 2：配置远程 URL 带 token
git remote set-url origin "https://$GITHUB_TOKEN@github.com/feision/openclaw.git"

# 测试
git push origin main
```

---

### **问题 6：`test_startup.py` 报 `FileNotFoundError`**

**现象**：找不到 `.memory/working/state.json`。

**原因**：文件名实际是 `session_state.json`，脚本中写错了。

**解决**：使用我已更新的 `test_startup.py`（已修正文件名）。

---

### **问题 7：记忆检索相关性低**

**现象**：查询 "GitHub" 返回的记忆不相关。

**原因**：
- BM25 索引未正确构建
- 记忆内容过于简短或关键词不匹配

**解决**：
1. 增加记忆条数：
   ```python
   # 在 init_memory.py 中扩展解析逻辑
   # 或手动添加
   mm.add_memory("GitHub API 使用 GET /user/repos", category="fact", importance=0.8)
   ```
2. 调整 BM25 参数（`memory_manager.py` 中的 `k1`, `b`）
3. 重新导入数据库

---

### **问题 8：`maintenance.py` 运行报错**

**现象**：
```
AttributeError: 'MemoryManager' object has no attribute 'cleanup_old_memories'
```

**原因**：`memory_manager.py` 版本与 `maintenance.py` 不匹配。

**解决**：
1. 确保使用的是 `agent-memory-manager` 最新版本的核心模块
2. 更新 `.memory/memory_manager.py`：
   ```bash
   cp agent-memory-manager/memory_manager.py .memory/
   ```
3. 或实现缺失方法（参考 `docs/API.md`）

---

## 📋 四、验证清单

部署完成后，运行以下命令逐项检查：

```bash
# ✅ 1. 目录结构
tree .memory -L 2
# 期望：memory.db, working/, logs/, scripts/ 都存在

# ✅ 2. 数据库文件
ls -lh .memory/memory.db
# 期望：> 10KB

# ✅ 3. 工作上下文
cat .memory/working/session_state.json
# 期望：包含 current_task, active_goals, last_updated

# ✅ 4. 查询功能
python3 .memory/scripts/query.py "GitHub"
# 期望：返回至少 3 条相关记忆

# ✅ 5. 启动验证
python3 .memory/scripts/test_startup.py
# 期望：总上下文 tokens < 1500

# ✅ 6. MEMORY.md 大小
wc -l MEMORY.md
# 期望：60-80 行

# ✅ 7. 同步脚本
python3 .memory/scripts/sync.py
# 期望：无错误，MEMORY.md 更新

# ✅ 8. 维护脚本
python3 .memory/scripts/maintenance.py
# 期望：显示清理和合并数量

# ✅ 9. Git 状态
cd openclaw && git status
# 期望：工作区干净，无未提交修改

# ✅ 10. 远程仓库
git log origin/main -1 --oneline
# 期望：提交信息包含 "memory system v2.0"
```

---

## 📦 五、文件清单（成功部署后）

### **核心文件（必须备份）**

| 文件/目录 | 大小 | 说明 |
|-----------|------|------|
| `.memory/memory.db` | ~50KB | SQLite 数据库（**核心数据**） |
| `.memory/working/session_state.json` | ~1KB | 当前任务状态 |
| `.memory/logs/*.md` | ~20KB | 历史日志归档 |
| `MEMORY.md` | ~1KB | 精简索引文件 |
| `AGENTS.md` | ~8KB | 启动规则 v2.0 |
| `HEARTBEAT.md` | ~2KB | 心跳检查（增强） |
| `openclaw/` 目录 | ~80KB | 远程仓库本地副本 |

### **工具脚本（可重跑）**

```
.memory/scripts/
├── init_memory.py      # 初始化导入（从 MEMORY.md → SQLite）
├── query.py            # 查询工具
├── sync.py             # 同步索引（SQLite → MEMORY.md）
├── maintenance.py      # 维护清理
├── test_startup.py     # 启动验证
├── init_working.py     # 初始化工作上下文
└── example_usage.py    # 参考示例（来自 upstream）
```

---

## 📦 六、打包与重装

### **打包成功状态（用于备份/迁移）**

```bash
cd /home/node/.openclaw/workspace

# 创建备份目录
mkdir -p backup/$(date +%Y-%m-%d)

# 复制关键文件
cp -r .memory backup/$(date +%Y-%m-%d)/
cp MEMORY.md backup/$(date +%Y-%m-%d)/
cp AGENTS.md backup/$(date +%Y-%m-%d)/
cp HEARTBEAT.md backup/$(date +%Y-%m-%d)/
cp README.md backup/$(date +%Y-%m-%d)/
cp agent-memory-manager/ backup/$(date +%Y-%m-%d)/

# 压缩
tar -czf openclaw-memory-backup-$(date +%Y-%m-%d).tar.gz backup/$(date +%Y-%m-%d)/

# 上传到远程（可选）
# scp openclaw-memory-backup-*.tar.gz user@backup-server:/backups/
```

**备份文件清单**：
```
openclaw-memory-backup-2026-04-08.tar.gz
├── .memory/
│   ├── memory.db                # ⭐ 核心数据
│   ├── working/session_state.json
│   ├── logs/*.md
│   └── scripts/*.py
├── MEMORY.md
├── AGENTS.md
├── HEARTBEAT.md
├── README.md
└── agent-memory-manager/         # upstream 参考
```

---

### **重装步骤（从备份恢复）**

```bash
# 1. 清理现有（可选）
rm -rf .memory/
rm MEMORY.md AGENTS.md HEARTBEAT.md

# 2. 解压备份
tar -xzf openclaw-memory-backup-2026-04-08.tar.gz
cp -r backup/2026-04-08/* .

# 3. 验证
tree .memory -L 2
python3 .memory/scripts/query.py "GitHub"

# 4. 同步到远程（如有修改）
# 参考"步骤 8：同步到远程仓库"
```

---

## 🕐 七、自动化配置（cron）

添加以下 cron 任务（`crontab -e`）：

```cron
# 每日 02:00 同步 MEMORY.md 索引
0 2 * * * cd /home/node/.openclaw/workspace && /usr/bin/python3 .memory/scripts/sync.py

# 每周一 03:00 执行维护（清理 + 合并）
0 3 * * 1 cd /home/node/.openclaw/workspace && /usr/bin/python3 .memory/scripts/maintenance.py

# 每次 OpenClaw 启动时自动恢复工作上下文（已在 AGENTS.md 中定义，无需 cron）
```

---

## 📊 八、监控与指标

### **Token 节省监控**

创建 `monitor_token.py`：

```python
import json
from datetime import datetime

def log_token_usage(session_id, tokens_before, tokens_after):
    """记录每次会话的 token 使用情况"""
    log = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "tokens_without_memory_system": tokens_before,
        "tokens_with_memory_system": tokens_after,
        "savings_percent": (1 - tokens_after / tokens_before) * 100
    }
    with open('.memory/token_usage_log.jsonl', 'a') as f:
        f.write(json.dumps(log) + '\n')

# 示例：记录一次会话
log_token_usage("session_2026-04-08", 2500, 800)
```

查看统计：
```bash
python3 -c "
import json
logs = [json.loads(l) for l in open('.memory/token_usage_log.jsonl')]
avg = sum(l['savings_percent'] for l in logs) / len(logs)
print(f'平均 Token 节省: {avg:.1f}%')
"
```

---

## 🎯 九、快速命令速查

| 任务 | 命令 |
|------|------|
| 初始化数据库 | `python3 .memory/scripts/init_memory.py` |
| 查询记忆 | `python3 .memory/scripts/query.py "关键词"` |
| 同步索引 | `python3 .memory/scripts/sync.py` |
| 维护清理 | `python3 .memory/scripts/maintenance.py` |
| 启动验证 | `python3 .memory/scripts/test_startup.py` |
| 查看统计 | `python3 -c "import sys; sys.path.insert(0,'.memory'); from memory_manager import MemoryManager; print(MemoryManager('.memory').get_stats())"` |
| 清理重建 | `rm .memory/memory.db && python3 .memory/scripts/init_memory.py` |

---

## 📚 十、参考资源

- **Upstream 仓库**: https://github.com/feision/agent-memory-manager
- **API 文档**: `agent-memory-manager/docs/API.md`
- **开发指南**: `agent-memory-manager/docs/DEVELOPMENT.md`
- **OpenClaw 集成方案**: `agent-memory-manager/docs/OPENCLAW_INTEGRATION_PLAN.md`（本部署方案基于此）
- **远程仓库**: https://github.com/feision/openclaw
- **本地文档**: `openclaw/README.md` → "记忆系统 v2.0" 章节

---

## ✅ 十一、部署成功标志

完成部署后，应满足以下条件：

- [x] `.memory/memory.db` 存在且 > 10KB
- [x] `MEMORY.md` < 100 行
- [x] `python3 .memory/scripts/query.py "GitHub"` 返回至少 3 条结果
- [x] `python3 .memory/scripts/test_startup.py` 通过全部检查
- [x] `openclaw` 远程仓库 `main` 分支包含 v2.0 更新提交
- [x] `HEARTBEAT.md` 包含记忆维护任务
- [x] `AGENTS.md` 包含 v2.0 启动流程

**所有检查通过 → 部署成功！** 🎉

---

## 🆘 十二、获取帮助

如遇到本方案未覆盖的问题：

1. **查阅 upstream 文档**：
   ```bash
   cat agent-memory-manager/docs/DEVELOPMENT.md
   cat agent-memory-manager/docs/PLANNING.md
   ```

2. **查看核心模块注释**：
   ```bash
   less .memory/memory_manager.py  # 搜索 "class MemoryManager"
   ```

3. **运行示例对比**：
   ```bash
   python3 agent-memory-manager/example_usage.py
   ```

4. **提交 Issue**：
   - OpenClaw 问题：https://github.com/feision/openclaw/issues
   - Memory Manager 问题：https://github.com/feision/agent-memory-manager/issues

---

**文档版本**: 1.0
**最后更新**: 2026-04-08
**部署状态**: ✅ 已验证成功
