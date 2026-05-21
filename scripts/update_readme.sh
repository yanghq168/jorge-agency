#!/bin/bash
# 更新README并推送到GitHub
cd /tmp/jorge-agency
python3 /root/.openclaw/workspace/scripts/generate_readme.py
git add README.md
git commit -m "📝 更新README - $(date '+%Y-%m-%d %H:%M')"
git push https://x-access-token:$(gh auth token)@github.com/yanghq168/jorge-agency.git HEAD
echo "✅ README已更新并推送"