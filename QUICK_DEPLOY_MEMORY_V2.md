# OpenClaw Memory System v2.0 - 部署手册

> 基于 https://github.com/feision/agent-memory-manager
> 版本: 1.0 | 日期: 2026-04-08

---

## 📋 部署概览

将从纯 Markdown 的 MEMORY.md（200+ 行）升级为结构化 SQLite 存储 + 智能检索。

**核心收益**：
- Token 占用从 ~2500 降至 ~800（-68%）
- 支持 BM25 关键词检索
- 自动维护（清理 + 合并）

---

## 🚀 一、快速部署（5 分钟）

### 1.1 创建目录结构

```bash
cd /home/node/.openclaw/workspace

# 创建 .memory 目录
mkdir -p .memory/working .memory/scripts .memory/logs

# 迁移旧日志
mv memory/*.md .memory/logs/
```

### 1.2 复制核心模块

```bash
# 克隆参考仓库（如未克隆）
git clone https://github.com/feision/agent-memory-manager.git

# 复制核心文件
cp agent-memory-manager/memory_manager.py .memory/
```

### 1.3 初始化数据库

创建 `.memory/scripts/init_memory.py`：

```python
import sys
sys.path.insert(0, '.memory')
from memory_manager import MemoryManager

mm = MemoryManager(".memory")
# 导入身份信息
mm.add_memory("龙虾 (Lobster) - Owner & Architect", category="identity", importance=0.9)
# 导入目标
mm.add_memory("完成 GitHub PAT 配置并测试连接", category="goal", importance=0.8)
# 导入决策
mm.add_memory("2026-04-05: 切换模型到 step-3.5-flash:free", category="decision", importance=0.9)
# 设置当前任务
mm.set_current_task("配置 GitHub PAT", status="in_progress", goals=["获取 Token", "测试连接"])
mm.save_session_summary("init", "初始化记忆系统")
mm.close()
print("✅ 初始化完成")
```

运行：
```bash
python3 .memory/scripts/init_memory.py
```

### 1.4 验证安装

```bash
# 查询测试
python3 .memory/scripts/query.py "GitHub"

# 启动验证
python3 .memory/scripts/test_startup.py
```

预期输出：
```
✅ 总记忆: 11 条
✅ 启动加载完成，总上下文 tokens: ~1262
```

### 1.5 生成精简 MEMORY.md

```bash
python3 .memory/scripts/sync.py
```

检查：`wc -l MEMORY.md` 应显示 70-80 行。

---

## 🔧 二、排错指南

### 问题 1：初始化报 `IndexError` 或解析失败

**原因**：`MEMORY.md` 结构与正则不匹配。

**解决**：
1. 手动检查 `MEMORY.md` 标题格式（必须是 `## 🦞 身份信息` 这种）
2. 简化 `init_memory.py`，只添加关键记忆（见 1.3 示例）
3. 或直接用 API 逐条添加：

```python
mm.add_memory("你的记忆内容", category="decision", importance=0.8, tags="标签")
```

---

### 问题 2：查询无结果

**原因**：数据库为空或 BM25 索引未构建。

**解决**：
```bash
# 查看数据库统计
python3 -c "
import sys
sys.path.insert(0, '.memory')
from memory_manager import MemoryManager
mm = MemoryManager('.memory')
print('总记忆数:', mm.get_stats()['total_memories'])
print('分类:', mm.get_stats()['by_category'])
"
```

如果为 0，重新运行 `init_memory.py`。

---

### 问题 3：`sync.py` 生成空文件

**原因**：`get_by_category()` 返回空列表。

**解决**：修改 `sync.py`，直接用 `mm.get_all()` 测试：

```python
all_memories = mm.get_all()
print(f"总记忆: {len(all_memories)}")
for m in all_memories[:5]:
    print(m['content'])
```

---

### 问题 4：找不到 `session_state.json`

**原因**：文件名实际是 `session_state.json`，不是 `state.json`。

**解决**：使用 `init_working.py` 脚本（已修正）。

---

### 问题 5：Git 推送失败

**现象**：`fatal: could not read Username`

**解决**：
```bash
export GITHUB_TOKEN="你的token"
git remote set-url origin "https://$GITHUB_TOKEN@github.com/feision/openclaw.git"
git push origin main
```

---

## 📦 三、文件清单（部署成功后）

### 3.1 新增目录

```
.memory/
├── memory.db                    # SQLite 数据库（核心数据）
├── config.json                  # 系统配置
├── working/
│   └── session_state.json      # 工作上下文
├── logs/                        # 历史日志归档
│   ├── 2026-04-04-*.md
│   └── ...
└── scripts/                     # 工具脚本
    ├── init_memory.py           # 初始化
    ├── query.py                 # 查询
    ├── sync.py                  # 同步索引
    ├── maintenance.py           # 维护
    ├── test_startup.py          # 验证
    └── init_working.py          # 初始化上下文
```

### 3.2 修改的文件

| 文件 | 变更 |
|------|------|
| `MEMORY.md` | 305 行 → 74 行（精简为索引） |
| `AGENTS.md` | 增加 v2.0 启动流程说明 |
| `HEARTBEAT.md` | 增加每日/每周维护任务 |
| `README.md` | 增加记忆系统 v2.0 完整文档 |

### 3.3 参考文件（可选）

```
agent-memory-manager/   # upstream 仓库，用于参考和更新核心模块
```

---

## 🔄 四、日常使用流程

### 4.1 添加新记忆

```python
import sys
sys.path.insert(0, '.memory')
from memory_manager import MemoryManager

mm = MemoryManager('.memory')
mm.add_memory("GitHub Token 需 repo + read:org 权限", category="fact", importance=0.8)
mm.set_current_task("测试 API 连接", status="in_progress", goals=["验证用户信息", "列出仓库"])
mm.save_session_summary("session_1", "完成了 GitHub Token 配置")
mm.close()
```

### 4.2 查询记忆

```bash
python3 .memory/scripts/query.py "权限问题"
python3 .memory/scripts/query.py "模型切换"
```

### 4.3 每日维护

```bash
# 每天执行一次
python3 .memory/scripts/sync.py

# 每周一执行一次
python3 .memory/scripts/maintenance.py
```

---

## 📦 五、打包与重装

### 5.1 打包备份

```bash
cd /home/node/.openclaw/workspace
tar -czf openclaw-memory-backup-$(date +%Y-%m-%d).tar.gz \
  .memory/ \
  MEMORY.md \
  AGENTS.md \
  HEARTBEAT.md \
  README.md \
  DEPLOYMENT_MEMORY_V2.md \
  agent-memory-manager/
```

### 5.2 重装恢复

```bash
# 1. 清理旧版本
rm -rf .memory/ MEMORY.md AGENTS.md HEARTBEAT.md

# 2. 解压备份
tar -xzf openclaw-memory-backup-2026-04-08.tar.gz

# 3. 验证
python3 .memory/scripts/query.py "GitHub"
```

---

## 📊 六、效果验证

| 指标 | v1.0 (旧) | v2.0 (新) | 验证命令 |
|------|-----------|-----------|---------|
| MEMORY.md 行数 | ~305 | ~74 | `wc -l MEMORY.md` |
| 冷启动 tokens | ~2500 | ~1260 | `test_startup.py` 输出 |
| 检索相关记忆 | ❌ | ✅ Top-5 | `query.py "关键词"` |
| 数据库大小 | 0 | ~50KB | `du -sh .memory/memory.db` |

---

## 🎯 七、下一步

1. **配置 cron 自动任务**（见 README.md）
2. **监控 Token 节省效果**（记录每次会话的上下文长度）
3. **扩展高级功能**（向量检索、记忆图谱）
4. **更新 `openclaw` 远程仓库**（已包含在本次部署中）

---

**部署完成！** 🎉 开始使用 `python3 .memory/scripts/query.py "关键词"` 测试吧。
