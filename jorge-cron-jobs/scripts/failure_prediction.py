#!/usr/bin/env python3
"""
故障预测脚本 v1.0
基于历史性能数据预测未来风险
- 磁盘空间耗尽预测
- 内存不足预警
- 负载持续高位预警
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

METRICS_DIR = Path("/root/.openclaw/workspace/memory/metrics")

def load_recent_metrics(days=7, remote=False):
    """加载最近N天的性能数据"""
    data = []
    subdir = METRICS_DIR / "remote" if remote else METRICS_DIR
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        file_path = subdir / f"{date.strftime('%Y-%m-%d')}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    day_data = json.load(f)
                    for entry in day_data:
                        entry['_date'] = date.strftime('%m-%d')
                    data.extend(day_data)
            except:
                pass
    
    return data

def predict_disk_full(data, threshold=90):
    """预测磁盘何时会满"""
    if not data:
        return None
    
    disk_vals = [(i, d["disk"]["usage_pct"]) for i, d in enumerate(data) if d.get("disk") and d["disk"].get("usage_pct") is not None]
    if len(disk_vals) < 2:
        return None
    
    # 简单线性回归
    n = len(disk_vals)
    x = [i for i, _ in disk_vals]
    y = [v for _, v in disk_vals]
    
    avg_x = sum(x) / n
    avg_y = sum(y) / n
    
    # 斜率
    numerator = sum((xi - avg_x) * (yi - avg_y) for xi, yi in zip(x, y))
    denominator = sum((xi - avg_x) ** 2 for xi in x)
    
    if denominator == 0 or numerator == 0:
        return None
    
    slope = numerator / denominator
    
    if slope <= 0:
        return None  # 磁盘使用率在下降或不变
    
    # 预测达到阈值需要多少个点
    last_val = y[-1]
    remaining = threshold - last_val
    if remaining <= 0:
        return 0  # 已经超限
    
    steps = remaining / slope
    # 假设每个点间隔4小时
    hours = steps * 4
    days = hours / 24
    
    return round(days, 1)

def predict_memory_pressure(data, threshold=85):
    """预测内存何时会不足"""
    if not data:
        return None
    
    mem_vals = [(i, d["memory"]["usage_pct"]) for i, d in enumerate(data) if d.get("memory") and d["memory"].get("usage_pct") is not None]
    if len(mem_vals) < 2:
        return None
    
    x = [i for i, _ in mem_vals]
    y = [v for _, v in mem_vals]
    
    n = len(mem_vals)
    avg_x = sum(x) / n
    avg_y = sum(y) / n
    
    numerator = sum((xi - avg_x) * (yi - avg_y) for xi, yi in zip(x, y))
    denominator = sum((xi - avg_x) ** 2 for xi in x)
    
    if denominator == 0 or numerator <= 0:
        return None
    
    slope = numerator / denominator
    last_val = y[-1]
    remaining = threshold - last_val
    if remaining <= 0:
        return 0
    
    steps = remaining / slope
    hours = steps * 4
    days = hours / 24
    
    return round(days, 1)

def check_load_spike(data, threshold=2.0):
    """检查负载是否持续高位"""
    if not data:
        return None
    
    load_vals = [d["load"]["1min"] for d in data if d.get("load") and d["load"].get("1min") is not None]
    if not load_vals:
        return None
    
    high_count = sum(1 for l in load_vals if l > threshold)
    ratio = high_count / len(load_vals) if load_vals else 0
    
    if ratio > 0.5:
        avg_load = sum(load_vals) / len(load_vals)
        return round(avg_load, 2)
    
    return None

def generate_prediction_report():
    """生成预测报告"""
    lines = []
    lines.append(f"🔮 故障预测报告 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("─" * 30)
    lines.append("")
    
    # 本地预测
    local_data = load_recent_metrics(days=7, remote=False)
    if local_data:
        lines.append("🖥️ 本地服务器 (OpenClaw VM)")
        
        disk_days = predict_disk_full(local_data)
        if disk_days is not None:
            if disk_days == 0:
                lines.append("  🔴 磁盘已接近或超过阈值！")
            elif disk_days < 7:
                lines.append(f"  🟡 磁盘预计 {disk_days} 天后将满（>90%）")
            else:
                lines.append(f"  🟢 磁盘预计 {disk_days} 天后将满，尚有空间")
        
        mem_days = predict_memory_pressure(local_data)
        if mem_days is not None:
            if mem_days == 0:
                lines.append("  🔴 内存已接近或超过阈值！")
            elif mem_days < 3:
                lines.append(f"  🟡 内存预计 {mem_days} 天后将不足（>85%）")
            else:
                lines.append(f"  🟢 内存预计 {mem_days} 天后将不足")
        
        load_avg = check_load_spike(local_data)
        if load_avg:
            lines.append(f"  🟡 负载持续高位，平均: {load_avg}")
        
        lines.append("")
    
    # 远程预测
    remote_data = load_recent_metrics(days=7, remote=True)
    if remote_data:
        lines.append("🌐 远程服务器 (82.156.225.39)")
        
        disk_days = predict_disk_full(remote_data)
        if disk_days is not None:
            if disk_days == 0:
                lines.append("  🔴 磁盘已接近或超过阈值！")
            elif disk_days < 7:
                lines.append(f"  🟡 磁盘预计 {disk_days} 天后将满（>90%）")
            else:
                lines.append(f"  🟢 磁盘预计 {disk_days} 天后将满，尚有空间")
        
        mem_days = predict_memory_pressure(remote_data)
        if mem_days is not None:
            if mem_days == 0:
                lines.append("  🔴 内存已接近或超过阈值！")
            elif mem_days < 3:
                lines.append(f"  🟡 内存预计 {mem_days} 天后将不足（>85%）")
            else:
                lines.append(f"  🟢 内存预计 {mem_days} 天后将不足")
        
        load_avg = check_load_spike(remote_data)
        if load_avg:
            lines.append(f"  🟡 负载持续高位，平均: {load_avg}")
        
        lines.append("")
    
    if not local_data and not remote_data:
        lines.append("⚪ 数据不足，无法进行预测")
        lines.append("  需要至少2天以上的性能数据")
        lines.append("")
    
    lines.append("🦞 权权管家预测中心")
    
    return "\n".join(lines)

def send_feishu(content):
    import subprocess
    TARGET = "ou_b38c2eefcb9e3efa1a08f81b73af91c7"
    result = subprocess.run(
        [
            "/root/.nvm/versions/node/v22.22.0/bin/openclaw", "message", "send",
            "--channel", "feishu", "--target", TARGET, "--message", content,
        ],
        capture_output=True, text=True,
    )
    return result.returncode == 0

def main():
    report = generate_prediction_report()
    print(report)
    
    # 只在有预警时发送
    if "🔴" in report or "🟡" in report:
        print("\n" + "=" * 30 + "\n")
        send_feishu(report)
        print("✅ 预警已发送")
    else:
        print("\n✅ 无风险，静默完成")

if __name__ == '__main__':
    main()
