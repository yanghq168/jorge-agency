#!/bin/bash
# bithappy 理财数据抓取脚本

# 打开页面并等待加载
agent-browser open https://bithappy.xyz/products
sleep 3

# 点击理财看板
agent-browser click "text=理财看板"
sleep 3

# 获取完整页面内容
agent-browser snapshot > /tmp/bithappy_snapshot.txt

# 关闭浏览器
agent-browser close

# 输出结果
cat /tmp/bithappy_snapshot.txt
