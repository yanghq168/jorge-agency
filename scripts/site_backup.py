#!/usr/bin/env python3
"""
全站备份脚本 v1.0
备份内容：
1. crontab配置
2. 环境变量/PATH
3. 关键配置文件
4. skills目录
5. 推送到GitHub
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
BACKUP_DIR = WORKSPACE / "backup"
GITHUB_REPO = "https://github.com/yanghq168/jorge-ai-repository"


def run_cmd(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=30)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1


def backup_crontab():
    """备份crontab"""
    stdout, rc = run_cmd("sudo crontab -l")
    if rc != 0:
        return False, "无法读取crontab"
    
    backup_file = BACKUP_DIR / "crontab.txt"
    with open(backup_file, 'w') as f:
        f.write(stdout + "\n")
    return True, backup_file


def backup_env():
    """备份环境变量"""
    env_file = BACKUP_DIR / "environment.txt"
    lines = [
        f"# 备份时间: {datetime.now().isoformat()}",
        f"PATH={os.environ.get('PATH', '')}",
        f"HOME={os.environ.get('HOME', '')}",
        f"USER={os.environ.get('USER', '')}",
        "",
        "# Node版本",
    ]
    
    node_v, rc = run_cmd("node --version")
    if rc == 0:
        lines.append(f"NODE_VERSION={node_v}")
    
    npm_v, rc = run_cmd("npm --version")
    if rc == 0:
        lines.append(f"NPM_VERSION={npm_v}")
    
    java_v, rc = run_cmd("java -version 2>&1 | head -1")
    if rc == 0:
        lines.append(f"JAVA_VERSION={java_v}")
    
    with open(env_file, 'w') as f:
        f.write("\n".join(lines) + "\n")
    
    return True, env_file


def backup_configs():
    """备份关键配置文件"""
    configs = [
        WORKSPACE / "skills" / "daily-report" / "config.json",
        WORKSPACE / "skills" / "ai-news-daily" / "config" / "feishu.json",
        WORKSPACE / "skills" / "ai-news-daily" / "config" / "email.json",
    ]
    
    config_dir = BACKUP_DIR / "configs"
    config_dir.mkdir(exist_ok=True)
    
    for cfg in configs:
        if cfg.exists():
            target = config_dir / cfg.name
            with open(cfg, 'r') as src, open(target, 'w') as dst:
                dst.write(src.read())
    
    return True, config_dir


def backup_skills_list():
    """备份技能清单"""
    skills_file = BACKUP_DIR / "skills_manifest.json"
    skills_dir = WORKSPACE / "skills"
    
    manifest = {
        "backup_time": datetime.now().isoformat(),
        "skills": [],
    }
    
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir():
                meta = d / "_meta.json"
                info = {"name": d.name, "path": str(d.relative_to(WORKSPACE))}
                if meta.exists():
                    try:
                        with open(meta, 'r') as f:
                            info['meta'] = json.load(f)
                    except:
                        pass
                manifest["skills"].append(info)
    
    with open(skills_file, 'w') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    return True, skills_file


def git_push():
    """推送到GitHub"""
    repo_dir = WORKSPACE / "jorge-ai-repository"
    
    # 如果仓库不存在，clone
    if not (repo_dir / ".git").exists():
        stdout, rc = run_cmd(f"git clone {GITHUB_REPO} {repo_dir}", cwd=WORKSPACE)
        if rc != 0:
            return False, f"克隆仓库失败: {stdout}"
    
    # 同步备份文件到仓库
    backup_repo_dir = repo_dir / "backup"
    backup_repo_dir.mkdir(exist_ok=True)
    
    # 复制备份文件
    for item in BACKUP_DIR.iterdir():
        if item.is_file():
            target = backup_repo_dir / item.name
            with open(item, 'r') as src, open(target, 'w') as dst:
                dst.write(src.read())
        elif item.is_dir():
            target = backup_repo_dir / item.name
            target.mkdir(exist_ok=True)
            for sub in item.iterdir():
                if sub.is_file():
                    t = target / sub.name
                    with open(sub, 'r') as src, open(t, 'w') as dst:
                        dst.write(src.read())
    
    # git操作
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    run_cmd("git add .", cwd=repo_dir)
    stdout, rc = run_cmd(f'git commit -m "auto backup: {now}"', cwd=repo_dir)
    
    if rc != 0 and "nothing to commit" not in stdout:
        return False, f"git commit失败: {stdout}"
    
    stdout, rc = run_cmd("git push origin main", cwd=repo_dir)
    if rc != 0:
        return False, f"git push失败: {stdout}"
    
    return True, "GitHub推送成功"


def main():
    BACKUP_DIR.mkdir(exist_ok=True)
    
    results = []
    
    ok, msg = backup_crontab()
    results.append(("crontab", ok, msg))
    
    ok, msg = backup_env()
    results.append(("环境变量", ok, msg))
    
    ok, msg = backup_configs()
    results.append(("配置文件", ok, msg))
    
    ok, msg = backup_skills_list()
    results.append(("技能清单", ok, msg))
    
    # GitHub推送
    ok, msg = git_push()
    results.append(("GitHub推送", ok, msg))
    
    # 输出报告
    print(f"📦 全站备份 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("─" * 30)
    for name, ok, msg in results:
        status = "✅" if ok else "❌"
        print(f"{status} {name}: {msg}")
    
    all_ok = all(r[1] for r in results)
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
