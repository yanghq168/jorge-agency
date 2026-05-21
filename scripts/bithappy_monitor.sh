#!/bin/bash
# Bithappy 理财监控主脚本 - 每小时执行

set -e

echo "🦞 [$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取 Bithappy 理财数据..."

# 打开页面
agent-browser open https://bithappy.xyz/products 2>/dev/null
sleep 3

# 点击理财看板
agent-browser click "text=理财看板" 2>/dev/null
sleep 3

# 获取快照
agent-browser snapshot > /tmp/bithappy_snapshot.txt 2>/dev/null

# 关闭浏览器
agent-browser close 2>/dev/null

# 分析数据
python3 /root/.openclaw/workspace/scripts/analyze_bithappy.py /tmp/bithappy_snapshot.txt > /tmp/bithappy_report.txt

echo "✅ 分析完成，报告已保存到 /tmp/bithappy_report.txt"
