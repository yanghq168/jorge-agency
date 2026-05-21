#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一配置加载器"""

import os
import yaml
from pathlib import Path

def load_config():
    """加载配置文件，优先查找顺序：
    1. 环境变量 JORGE_CRON_CONFIG 指定的路径
    2. 脚本同级目录的 config.yaml
    3. 上级目录 config/config.yaml
    4. 使用默认值
    """
    # 尝试各种路径
    possible_paths = []
    
    # 环境变量
    env_path = os.environ.get('JORGE_CRON_CONFIG')
    if env_path:
        possible_paths.append(Path(env_path))
    
    # 脚本所在目录
    script_dir = Path(__file__).parent
    possible_paths.append(script_dir / 'config.yaml')
    
    # 上级目录的 config/
    possible_paths.append(script_dir.parent / 'config' / 'config.yaml')
    
    # 再上级
    possible_paths.append(script_dir.parent.parent / 'config' / 'config.yaml')
    
    for path in possible_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                continue
    
    # 返回默认值
    return {}


def get_mail_config():
    """获取邮件配置"""
    config = load_config()
    mail = config.get('mail', {})
    return {
        'smtp_server': mail.get('smtp_server', 'smtp.qq.com'),
        'smtp_port': mail.get('smtp_port', 465),
        'smtp_user': mail.get('smtp_user', ''),
        'smtp_pass': mail.get('smtp_pass', ''),
        'to_email': mail.get('to_email', mail.get('smtp_user', '')),
    }


def get_openclaw_config():
    """获取OpenClaw配置"""
    config = load_config()
    openclaw = config.get('openclaw', {})
    return {
        'model': openclaw.get('model', 'kimi-coding/k2p5'),
    }


def get_paths():
    """获取路径配置"""
    config = load_config()
    paths = config.get('paths', {})
    return {
        'workspace': paths.get('workspace', '/root/.openclaw/workspace'),
        'logs': paths.get('logs', '/var/log'),
    }
