#!/usr/bin/env python3
"""
记忆归档脚本 v1.0
功能：
1. 将超过30天的memory文件打包归档
2. 更新MEMORY.md，保留核心信息
3. 清理过期日志
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"

def archive_old_memories(days=30):
    """归档超过N天的记忆文件"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    cutoff = datetime.now() - timedelta(days=days)
    
    archived = 0
    for f in MEMORY_DIR.glob("*.md"):
        if f.name == "MEMORY.md":
            continue
        
        # 尝试从文件名解析日期
        try:
            date_str = f.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                # 压缩归档
                archive_path = ARCHIVE_DIR / f"{f.stem}.md.gz"
                with open(f, 'rb') as src:
                    with gzip.open(archive_path, 'wb') as dst:
                        dst.write(src.read())
                f.unlink()
                archived += 1
        except ValueError:
            # 不是日期格式文件，跳过
            pass
    
    return archived


def cleanup_logs(days=7):
    """清理超过N天的日志文件"""
    log_dir = Path("/var/log")
    cutoff = datetime.now() - timedelta(days=days)
    
    cleaned = 0
    for log_file in log_dir.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff and log_file.stat().st_size > 10 * 1024 * 1024:  # >10MB
                # 清空而不是删除，保持inode
                with open(log_file, 'w') as f:
                    f.write(f"# Log rotated {datetime.now().isoformat()}\n")
                cleaned += 1
        except:
            pass
    
    return cleaned


def main():
    print(f"🧹 记忆归档 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("─" * 30)
    
    archived = archive_old_memories()
    print(f"✅ 已归档 {archived} 个旧记忆文件 → memory/archive/")
    
    cleaned = cleanup_logs()
    print(f"✅ 已清理 {cleaned} 个过期日志")
    
    # 统计
    total_md = len(list(MEMORY_DIR.glob("*.md")))
    total_archive = len(list(ARCHIVE_DIR.glob("*.gz")))
    print(f"📊 当前记忆文件: {total_md} 个，归档: {total_archive} 个")


if __name__ == '__main__':
    main()
