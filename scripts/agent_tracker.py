#!/usr/bin/env python3
"""
Agent 优化追踪系统
记录所有 Agent 文件的变更历史
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

AGENTS_DIR = Path("/root/.openclaw/workspace/agency-agents")
TRACKING_FILE = Path("/root/.openclaw/workspace/data/agent_tracking.json")


def get_file_hash(filepath):
    """计算文件MD5哈希"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


def load_tracking_data():
    """加载追踪数据"""
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'agents': {},  # agent_name: {hash, last_modified, optimizations: []}
        'last_check': None
    }


def save_tracking_data(data):
    """保存追踪数据"""
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def check_agent_changes():
    """检查 Agent 文件变更"""
    data = load_tracking_data()
    today = datetime.now().strftime('%Y-%m-%d')
    changes = []
    
    if not AGENTS_DIR.exists():
        return changes
    
    for md_file in AGENTS_DIR.rglob("*.md"):
        relative_path = md_file.relative_to(AGENTS_DIR)
        agent_key = str(relative_path)
        current_hash = get_file_hash(md_file)
        
        if agent_key not in data['agents']:
            # 新 Agent
            data['agents'][agent_key] = {
                'hash': current_hash,
                'first_seen': today,
                'optimizations': []
            }
            changes.append({
                'agent': agent_key,
                'type': '新增',
                'date': today,
                'description': '新安装 Agent'
            })
        elif data['agents'][agent_key]['hash'] != current_hash:
            # 有变更
            data['agents'][agent_key]['hash'] = current_hash
            data['agents'][agent_key]['optimizations'].append({
                'date': today,
                'description': '文件内容更新'
            })
            changes.append({
                'agent': agent_key,
                'type': '优化',
                'date': today,
                'description': '内容更新优化'
            })
    
    data['last_check'] = datetime.now().isoformat()
    save_tracking_data(data)
    
    return changes


def get_today_optimizations():
    """获取今日优化记录"""
    data = load_tracking_data()
    today = datetime.now().strftime('%Y-%m-%d')
    optimizations = []
    
    for agent_key, agent_data in data['agents'].items():
        # 检查首次安装日期
        if agent_data.get('first_seen') == today:
            optimizations.append({
                'agent': Path(agent_key).stem.replace('-', ' ').title(),
                'type': '新增',
                'description': '新安装 Agent'
            })
        
        # 检查今日优化
        for opt in agent_data.get('optimizations', []):
            if opt['date'] == today:
                optimizations.append({
                    'agent': Path(agent_key).stem.replace('-', ' ').title(),
                    'type': '优化',
                    'description': opt['description']
                })
    
    return optimizations


if __name__ == '__main__':
    changes = check_agent_changes()
    print(f"检测到 {len(changes)} 个变更")
    for change in changes:
        print(f"  - {change['agent']}: {change['type']}")
