#!/bin/bash
# Bithappy 理财监控 - 完整脚本版

set -e

REPORT_FILE="/tmp/bithappy_report_$(date +%Y%m%d_%H%M).txt"
LOG_FILE="/tmp/bithappy_cron.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取..." >> "$LOG_FILE"

# 打开页面
agent-browser open https://bithappy.xyz/products &>/dev/null || {
    echo "❌ 打开页面失败" >> "$LOG_FILE"
    exit 1
}

sleep 3

# 点击理财看板 - 先用 snapshot 获取 ref
SNAPSHOT=$(agent-browser snapshot -i 2>/dev/null)
REF=$(echo "$SNAPSHOT" | grep "理财看板" | grep -oE '\[ref=e[0-9]+\]' | head -1 | tr -d '[]' | sed 's/ref=//')

if [ -z "$REF" ]; then
    echo "❌ 找不到理财看板按钮" >> "$LOG_FILE"
    agent-browser close &>/dev/null
    exit 1
fi

agent-browser click "$REF" &>/dev/null
sleep 3

# 获取完整快照
agent-browser snapshot > /tmp/bithappy_snapshot.txt 2>/dev/null
agent-browser close &>/dev/null

# 分析并生成报告
if [ -f /tmp/bithappy_snapshot.txt ]; then
    python3 /root/.openclaw/workspace/scripts/analyze_bithappy.py /tmp/bithappy_snapshot.txt > "$REPORT_FILE"
    echo "✅ 报告已生成: $REPORT_FILE" >> "$LOG_FILE"
    cat "$REPORT_FILE"
else
    echo "❌ 快照文件不存在" >> "$LOG_FILE"
    exit 1
fi
