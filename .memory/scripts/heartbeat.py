#!/usr/bin/env python3
# OpenClaw Memory System - Heartbeat Handler
# 每次 OpenClaw 心跳时自动执行，负责记忆系统的日常维护

import sys
import subprocess
import os
import json
from datetime import datetime, timedelta

WORKSPACE = '/home/node/.openclaw/workspace'
STATE_FILE = f'{WORKSPACE}/.memory/working/heartbeat_state.json'
LOG_FILE = f'{WORKSPACE}/.memory/logs/heartbeat.log'

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'last_sync': None, 'last_maintenance': None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def log_message(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")

def should_run(last_run, interval_hours):
    if not last_run:
        return True
    try:
        last = datetime.fromisoformat(last_run)
        return datetime.now() - last > timedelta(hours=interval_hours)
    except:
        return True

def run_command(cmd, description):
    print(f"\n[{datetime.now().strftime('%H:%M')}] {description}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30,
            cwd=WORKSPACE, env={**os.environ, 'PYTHONUNBUFFERED': '1'}
        )
        if result.returncode == 0:
            print(f"✅ 完成")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()[:200]}")
            log_message(f"{description} - 成功")
            return True
        else:
            print(f"❌ 失败: {result.stderr.strip()[:200]}")
            log_message(f"{description} - 失败: {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 超时（>30秒）")
        log_message(f"{description} - 超时")
        return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        log_message(f"{description} - 异常: {str(e)}")
        return False

def check_database_health():
    """调用独立健康检查脚本"""
    return run_command("python3 .memory/scripts/check_health.py", "数据库健康检查")

def main():
    print("=" * 60)
    print("  OpenClaw Memory System - Heartbeat Check")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    state = load_state()
    tasks_run = 0
    tasks_success = 0

    # 1. 每日同步索引（间隔 24 小时）
    if should_run(state.get('last_sync'), interval_hours=24):
        tasks_run += 1
        if run_command("python3 .memory/scripts/sync.py", "同步 MEMORY.md 索引"):
            tasks_success += 1
            state['last_sync'] = datetime.now().isoformat()
    else:
        last = datetime.fromisoformat(state['last_sync'])
        next_run = last + timedelta(hours=24)
        print(f"\n⏭️  跳过索引同步（下次: {next_run.strftime('%m-%d %H:%M')}）")

    # 2. 每周维护（间隔 168 小时 = 7 天）
    if should_run(state.get('last_maintenance'), interval_hours=168):
        tasks_run += 1
        if run_command("python3 .memory/scripts/maintenance.py", "每周维护（清理+合并）"):
            tasks_success += 1
            state['last_maintenance'] = datetime.now().isoformat()
    else:
        last = datetime.fromisoformat(state['last_maintenance'])
        next_run = last + timedelta(days=7)
        print(f"\n⏭️  跳过每周维护（下次: {next_run.strftime('%m-%d %H:%M')}）")

    # 3. 数据库健康检查（每次心跳都执行）
    tasks_run += 1
    if check_database_health():
        tasks_success += 1

    # 保存状态
    save_state(state)

    # 总结
    print("\n" + "=" * 60)
    print(f"  ✅ 心跳完成 | 成功 {tasks_success}/{tasks_run} 个任务")
    print("=" * 60)

    if tasks_success == tasks_run:
        print("\nHEARTBEAT_OK")
        return 0
    else:
        print(f"\n⚠️  部分任务失败，详情见日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())
