#!/usr/bin/env python3
"""
性能趋势收集脚本 v1.0
每天记录系统资源使用数据
用于周报/月报的趋势分析
"""

import os
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/root/.openclaw/workspace/memory/metrics")

def run_cmd(cmd):
    import subprocess
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip(), r.returncode
    except:
        return "", 1

def collect_metrics():
    """收集当前系统指标"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu": {},
        "memory": {},
        "disk": {},
        "load": {},
    }
    
    # CPU 使用率
    stdout, _ = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
    try:
        metrics["cpu"]["usage"] = float(stdout)
    except:
        metrics["cpu"]["usage"] = None
    
    # 内存
    stdout, _ = run_cmd("free -m | grep Mem")
    try:
        parts = stdout.split()
        metrics["memory"]["total_mb"] = int(parts[1])
        metrics["memory"]["used_mb"] = int(parts[2])
        metrics["memory"]["free_mb"] = int(parts[3])
        metrics["memory"]["available_mb"] = int(parts[6])
        metrics["memory"]["usage_pct"] = round(int(parts[2]) / int(parts[1]) * 100, 1)
    except:
        pass
    
    # 磁盘
    stdout, _ = run_cmd("df -h / | tail -1")
    try:
        parts = stdout.split()
        metrics["disk"]["total"] = parts[1]
        metrics["disk"]["used"] = parts[2]
        metrics["disk"]["available"] = parts[3]
        metrics["disk"]["usage_pct"] = int(parts[4].rstrip('%'))
    except:
        pass
    
    # Load average
    stdout, _ = run_cmd("cat /proc/loadavg")
    try:
        parts = stdout.split()
        metrics["load"]["1min"] = float(parts[0])
        metrics["load"]["5min"] = float(parts[1])
        metrics["load"]["15min"] = float(parts[2])
    except:
        pass
    
    # 进程数
    stdout, _ = run_cmd("ps aux | wc -l")
    try:
        metrics["processes"] = int(stdout.strip()) - 1
    except:
        metrics["processes"] = None
    
    return metrics


def collect_remote_metrics():
    """采集远程服务器指标"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "host": "82.156.225.39",
        "cpu": {},
        "memory": {},
        "disk": {},
        "load": {},
    }
    
    ssh_key = os.path.expanduser("~/.ssh/jorge_server")
    host = "ai-worker@82.156.225.39"
    
    # 负载
    stdout, rc = run_cmd(f"ssh -i {ssh_key} -o ConnectTimeout=10 -o StrictHostKeyChecking=no {host} 'cat /proc/loadavg' 2>/dev/null")
    if rc == 0:
        try:
            parts = stdout.split()
            metrics["load"]["1min"] = float(parts[0])
            metrics["load"]["5min"] = float(parts[1])
            metrics["load"]["15min"] = float(parts[2])
        except:
            pass
    
    # 内存
    stdout, rc = run_cmd(f"ssh -i {ssh_key} -o ConnectTimeout=10 -o StrictHostKeyChecking=no {host} 'free -m | grep Mem' 2>/dev/null")
    if rc == 0:
        try:
            parts = stdout.split()
            metrics["memory"]["total_mb"] = int(parts[1])
            metrics["memory"]["used_mb"] = int(parts[2])
            metrics["memory"]["free_mb"] = int(parts[3])
            metrics["memory"]["available_mb"] = int(parts[6])
            if metrics["memory"]["total_mb"] > 0:
                metrics["memory"]["usage_pct"] = round(int(parts[2]) / int(parts[1]) * 100, 1)
        except:
            pass
    
    # 磁盘
    stdout, rc = run_cmd(f"ssh -i {ssh_key} -o ConnectTimeout=10 -o StrictHostKeyChecking=no {host} 'df -h / | tail -1' 2>/dev/null")
    if rc == 0:
        try:
            parts = stdout.split()
            metrics["disk"]["total"] = parts[1]
            metrics["disk"]["used"] = parts[2]
            metrics["disk"]["available"] = parts[3]
            metrics["disk"]["usage_pct"] = int(parts[4].rstrip('%'))
        except:
            pass
    
    # 进程数
    stdout, rc = run_cmd(f"ssh -i {ssh_key} -o ConnectTimeout=10 -o StrictHostKeyChecking=no {host} 'ps aux | wc -l' 2>/dev/null")
    if rc == 0:
        try:
            metrics["processes"] = int(stdout.strip()) - 1
        except:
            pass
    
    return metrics


def save_metrics(metrics, remote_metrics=None):
    """保存指标到按日期组织的JSON文件"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REMOTE_DIR = DATA_DIR / "remote"
    REMOTE_DIR.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 本地数据
    file_path = DATA_DIR / f"{date_str}.json"
    data = []
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except:
            data = []
    data.append(metrics)
    with open(file_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 远程数据
    if remote_metrics:
        remote_path = REMOTE_DIR / f"{date_str}.json"
        remote_data = []
        if remote_path.exists():
            try:
                with open(remote_path, 'r') as f:
                    remote_data = json.load(f)
            except:
                remote_data = []
        remote_data.append(remote_metrics)
        with open(remote_path, 'w') as f:
            json.dump(remote_data, f, ensure_ascii=False, indent=2)
    
    return file_path


def get_trend_summary(days=7):
    """获取最近N天的趋势摘要"""
    summaries = []
    
    for i in range(days):
        date = datetime.now() - __import__('datetime').timedelta(days=i)
        file_path = DATA_DIR / f"{date.strftime('%Y-%m-%d')}.json"
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if data:
                    # 取当天的平均值
                    cpu_vals = [d["cpu"].get("usage", 0) for d in data if d.get("cpu")]
                    mem_vals = [d["memory"].get("usage_pct", 0) for d in data if d.get("memory")]
                    disk_vals = [d["disk"].get("usage_pct", 0) for d in data if d.get("disk")]
                    
                    summary = {
                        "date": date.strftime("%m-%d"),
                        "cpu_avg": round(sum(cpu_vals) / len(cpu_vals), 1) if cpu_vals else None,
                        "mem_avg": round(sum(mem_vals) / len(mem_vals), 1) if mem_vals else None,
                        "disk_avg": round(sum(disk_vals) / len(disk_vals), 1) if disk_vals else None,
                        "samples": len(data),
                    }
                    summaries.append(summary)
            except:
                pass
    
    return summaries


def main():
    print(f"📊 性能数据采集 · {datetime.now().strftime('%H:%M')}")
    
    # 本地
    metrics = collect_metrics()
    # 远程
    remote_metrics = collect_remote_metrics()
    
    file_path = save_metrics(metrics, remote_metrics)
    
    print(f"✅ 已保存: {file_path}")
    
    # 打印当前值
    cpu = metrics.get("cpu", {}).get("usage")
    mem = metrics.get("memory", {}).get("usage_pct")
    disk = metrics.get("disk", {}).get("usage_pct")
    load = metrics.get("load", {}).get("1min")
    
    print(f"  [本地] CPU:{cpu}% 内存:{mem}% 磁盘:{disk}% 负载:{load}")
    
    if remote_metrics.get("memory"):
        r_mem = remote_metrics["memory"].get("usage_pct")
        r_disk = remote_metrics["disk"].get("usage_pct")
        r_load = remote_metrics["load"].get("1min")
        print(f"  [远程] 内存:{r_mem}% 磁盘:{r_disk}% 负载:{r_load}")


if __name__ == '__main__':
    main()
