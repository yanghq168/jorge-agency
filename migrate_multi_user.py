#!/usr/bin/env python3
"""
用户隔离记忆系统 - 迁移和设置脚本
将现有单用户配置迁移到多用户隔离模式
"""

import shutil
from pathlib import Path
from datetime import datetime
from skills.user_memory_manager import UserMemoryManager, get_memory_manager

def migrate_to_multi_user(default_user_id=None):
    """
    迁移到多用户隔离模式
    
    Args:
        default_user_id: 默认用户ID（可选，如果不提供则保持共享模式直到有新用户）
    """
    
    print("=" * 60)
    print("🦞 多用户记忆隔离系统 - 迁移工具")
    print("=" * 60)
    print()
    
    manager = get_memory_manager()
    workspace = Path("/root/.openclaw/workspace")
    
    # 检查是否已经有用户数据
    existing_users = manager.list_users()
    
    if existing_users:
        print(f"✅ 已有 {len(existing_users)} 个用户配置:")
        for user in existing_users:
            print(f"   - {user['user_id']}")
        print()
    
    # 如果有默认用户ID，迁移现有数据
    if default_user_id:
        print(f"📝 正在为用户 {default_user_id} 创建独立空间...")
        
        # 初始化用户
        manager.init_user(default_user_id, {
            "name": "jorge",
            "timezone": "GMT+8",
            "migrated_from_shared": True,
            "migrated_at": datetime.now().isoformat()
        })
        
        # 迁移现有记忆文件
        old_memory_dir = workspace / "memory"
        if old_memory_dir.exists():
            user_memory_dir = manager.get_user_dir(default_user_id) / "memory"
            
            print(f"📁 迁移记忆文件...")
            for memory_file in old_memory_dir.glob("*.md"):
                target = user_memory_dir / memory_file.name
                if not target.exists():
                    shutil.copy2(memory_file, target)
                    print(f"   ✓ {memory_file.name}")
        
        # 迁移MEMORY.md
        old_memory = workspace / "MEMORY.md"
        if old_memory.exists():
            user_memory = manager.get_user_longterm_memory(default_user_id)
            if not user_memory.exists() or user_memory.stat().st_size == 0:
                shutil.copy2(old_memory, user_memory)
                print(f"   ✓ MEMORY.md")
        
        # 迁移配置
        old_config = workspace / "skills" / "daily-report" / "config.json"
        if old_config.exists():
            import json
            with open(old_config, 'r') as f:
                email_config = json.load(f)
            
            user_config = manager.load_user_config(default_user_id)
            user_config["email"] = email_config.get("smtp_user")
            user_config["smtp_config"] = email_config
            manager.save_user_config(default_user_id, user_config)
            print(f"   ✓ 邮件配置")
        
        # 迁移合约预警配置
        old_crypto = workspace / "skills" / "daily-report" / "crypto_alerts.json"
        if old_crypto.exists():
            import json
            with open(old_crypto, 'r') as f:
                crypto_config = json.load(f)
            
            user_config = manager.load_user_config(default_user_id)
            user_config["crypto_alerts"] = crypto_config
            manager.save_user_config(default_user_id, user_config)
            print(f"   ✓ 合约预警配置")
        
        print()
        print(f"✅ 用户 {default_user_id} 数据迁移完成！")
        print()
    
    # 显示系统结构
    print("📂 多用户系统结构:")
    print(f"   {workspace}/")
    print(f"   ├── users/                    # 用户隔离目录")
    print(f"   │   ├── {{user_id_1}}/         # 用户1专属空间")
    print(f"   │   │   ├── memory/           # 每日记忆")
    print(f"   │   │   ├── config/           # 个人配置")
    print(f"   │   │   └── MEMORY.md         # 长期记忆")
    print(f"   │   ├── {{user_id_2}}/         # 用户2专属空间")
    print(f"   │   └── ...")
    print(f"   ├── skills/                   # 共享技能（代码）")
    print(f"   ├── docs/                     # 共享文档")
    print(f"   └── config/                   # 系统配置")
    print()
    
    print("🔒 隔离规则:")
    print("   ✓ 记忆隔离: 每个用户独立的memory/和MEMORY.md")
    print("   ✓ 配置隔离: 每个用户独立的config.json")
    print("   ✓ 技能数据隔离: 每个用户独立的技能数据")
    print("   ✓ 共享资源: skills/, docs/, tools/ 所有用户共享")
    print()
    
    print("=" * 60)
    print("迁移完成！系统已启用多用户隔离模式。")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    # 检查是否有用户ID参数
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        migrate_to_multi_user(user_id)
    else:
        print("用法: python3 migrate_multi_user.py <user_id>")
        print()
        print("示例:")
        print("  python3 migrate_multi_user.py ou_b38c2eefcb9e3efa1a08f81b73af91c7")
        print()
        
        # 询问是否继续
        response = input("是否要为当前用户 (ou_b38c2eefcb9e3efa1a08f81b73af91c7) 迁移? [y/N]: ")
        if response.lower() == 'y':
            migrate_to_multi_user("ou_b38c2eefcb9e3efa1a08f81b73af91c7")
