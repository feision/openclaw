# MEMORY.md - 长期记忆索引（自动生成）

> **说明**: 详细记忆已存储于 `.memory/memory.db`（共 11 条）
> 本文件为索引 + 摘要，用于快速恢复上下文
> 最后同步: 2026-04-08 23:18

---

## 📍 上次会话摘要

初始化记忆系统：将 MEMORY.md 结构化数据迁移到 SQLite 数据库，建立分类和索引。

---

## 🎯 当前活跃目标

- **任务**: 配置 GitHub PAT 完成连接
- **子目标**:
  - 获取 GitHub Token
  - 测试 API 连接
  - 验证仓库访问权限

---

## 📊 项目状态速览

| 状态 | 项目 |
|------|------|


---

## 🔑 关键决策（最近）

- [2026-04-05 01:11] 遭遇模型配置错误（多个模型不可用）
- [2026-04-05 01:11] 决定切换到 `openrouter/stepfun/step-3.5-flash:free`


---

## 🧠 经验教训（最近）

- 经验: 权限问题**（2026-04-04）
   - 错误：`exec security=full ask=off` 未正确配置
   - 解决：检查 age


---

## 📈 记忆统计

- **总记忆数**: 11 条
- **分类统计**: {'decision': 2, 'experience': 1, 'goal': 2, 'identity': 2, 'preference': 4}
- **下次维护**: 2026-04-15

---

## 🔧 工具命令

```bash
# 查询记忆
python .memory/scripts/query.py "关键词"

# 手动同步索引（本脚本）
python .memory/scripts/sync.py

# 记忆维护（清理+合并）
python .memory/scripts/maintenance.py
```

---


最后更新: 2026-04-08
