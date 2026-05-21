#!/bin/bash
# SKILL自动备份脚本
# 每天自动备份 OpenClaw SKILL 到 GitHub

set -e

SKILL_DIR="/root/.openclaw/workspace/skills"
REPO_DIR="/tmp/jorge-skills"
REPO_URL="https://github.com/yanghq168/jorge-skills.git"
BACKUP_LOG="/var/log/skill-backup.log"

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$BACKUP_LOG"
}

log "=== SKILL备份开始 ==="

# 确保仓库存在
if [ ! -d "$REPO_DIR/.git" ]; then
    log "克隆仓库..."
    rm -rf "$REPO_DIR"
    git clone "$REPO_URL" "$REPO_DIR"
fi

# 进入仓库
cd "$REPO_DIR"

# 拉取最新更新
git pull origin main

# 更新SKILL文件
log "复制SKILL文件..."
rm -rf skills/
cp -r "$SKILL_DIR" ./skills/

# 更新README中的日期
DATE=$(date '+%Y_%m_%d')
sed -i "s/Updated_[0-9]\{4\}_[0-9]\{2\}_[0-9]\{2\}/Updated_$DATE/g" README.md
sed -i "s/备份时间.*$/备份时间: $(date '+%Y-%m-%d')/g" README.md

# 添加并提交
git add -A
if git diff --cached --quiet; then
    log "无变更，跳过提交"
else
    git commit -m "🔄 自动备份: $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    log "✅ 备份完成并推送"
fi

log "=== SKILL备份结束 ==="
