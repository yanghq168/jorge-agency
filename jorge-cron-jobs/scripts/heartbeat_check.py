#!/usr/bin/env python3
"""
高频心跳检查 v1.0
每30分钟检查远程服务器核心服务
发现问题立即飞书告警
"""

import subprocess
import re
from datetime import datetime

SSH_KEY = "/root/.ssh/jorge_server"
HOST = "ai-worker@82.156.225.39"
TARGET = "ou_b38c2eefcb9e3efa1a08f81b73af91c7"

SERVICES = {
    "Nginx": "nginx",
    "MySQL": "mariadb|mysql",
    "Redis": "redis-server",
    "Java后端": "jorge-ai-demo",
}

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout.strip(), r.returncode
    except:
        return "", 1

def send_feishu(content):
    result = subprocess.run(
        [
            "/root/.nvm/versions/node/v22.22.0/bin/openclaw", "message", "send",
            "--channel", "feishu", "--target", TARGET, "--message", content,
        ],
        capture_output=True, text=True,
    )
    return result.returncode == 0

def check_services():
    stdout, rc = run_cmd(f"ssh -i {SSH_KEY} -o ConnectTimeout=10 -o StrictHostKeyChecking=no {HOST} 'ps aux' 2>/dev/null")
    
    if rc != 0:
        msg = f"🔴 服务器失联\n\n无法连接: {HOST}\n时间: {datetime.now().strftime('%H:%M')}\n\n🦞 权权管家告警中心"
        send_feishu(msg)
        return 1
    
    failed = []
    for name, pattern in SERVICES.items():
        if not re.search(pattern, stdout, re.IGNORECASE):
            failed.append(name)
    
    if failed:
        msg = f"🔴 服务异常告警 · {datetime.now().strftime('%H:%M')}\n\n以下服务未运行:\n"
        for f in failed:
            msg += f"  • {f}\n"
        msg += "\n🦞 权权管家告警中心"
        send_feishu(msg)
        return 1
    
    return 0

def main():
    exit_code = check_services()
    now = datetime.now().strftime('%H:%M')
    if exit_code == 0:
        print(f"✅ [{now}] 远程服务器全部正常")
    else:
        print(f"❌ [{now}] 发现异常，已发送告警")
    return exit_code

if __name__ == '__main__':
    import sys
    sys.exit(main())
