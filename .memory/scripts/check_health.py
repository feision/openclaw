#!/usr/bin/env python3
"""
记忆系统健康检查
快速验证数据库状态和基本信息
"""

import sys
sys.path.insert(0, '.memory')
from memory_manager import MemoryManager

def main():
    mm = MemoryManager('.memory')
    stats = mm.get_stats()

    print(f"总记忆数: {stats['total_memories']}")
    print(f"分类统计: {stats['by_category']}")
    print(f"当前任务: {stats['current_task']}")

    mm.close()

if __name__ == "__main__":
    main()
