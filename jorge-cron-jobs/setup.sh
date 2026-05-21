#!/bin/bash
# =============================================================================
# jorge-cron-jobs 一键安装脚本
# 用途：新服务器快速复刻所有定时任务
# 运行方式：./setup.sh
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="/var/log"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  🦞 jorge-cron-jobs 一键安装脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# =============================================================================
# 1. 检查基础依赖
# =============================================================================
echo -e "${YELLOW}[1/8] 检查基础依赖...${NC}"

# 检查 python3
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ python3 未安装，请先安装 Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+' | head -1)
echo -e "${GREEN}✅ Python: ${PYTHON_VERSION}${NC}"

# 检查 openclaw
if ! command -v openclaw >/dev/null 2>&1; then
    echo -e "${RED}❌ openclaw 未安装${NC}"
    echo "   安装方式: npm install -g openclaw"
    echo "   或参考: https://docs.openclaw.ai"
    exit 1
fi
OPENCLAW_VERSION=$(openclaw --version | head -1)
echo -e "${GREEN}✅ OpenClaw: ${OPENCLAW_VERSION}${NC}"

# 检查 pip3
if ! command -v pip3 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ pip3 未安装，尝试安装...${NC}"
    apt-get update && apt-get install -y python3-pip 2>/dev/null || \
    yum install -y python3-pip 2>/dev/null || \
    dnf install -y python3-pip 2>/dev/null || {
        echo -e "${RED}❌ 无法自动安装 pip3，请手动安装${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✅ pip3 已安装${NC}"

# =============================================================================
# 2. 安装 Python 依赖
# =============================================================================
echo ""
echo -e "${YELLOW}[2/8] 安装 Python 依赖...${NC}"

pip3 install pyyaml 2>/dev/null || pip3 install --user pyyaml 2>/dev/null
echo -e "${GREEN}✅ pyyaml 已安装${NC}"

# =============================================================================
# 3. 创建日志目录
# =============================================================================
echo ""
echo -e "${YELLOW}[3/8] 创建日志目录...${NC}"

LOG_FILES=(
    "xiaohongshu-travel.log"
    "wechat-article-daily.log"
    "douyin-daily.log"
    "bithappy-email.log"
    "daily-report.log"
    "health-check.log"
    "site-backup.log"
    "memory-archive.log"
    "metrics.log"
    "weekly-report.log"
    "monthly-report.log"
    "heartbeat.log"
    "prediction.log"
)

for log_file in "${LOG_FILES[@]}"; do
    touch "${LOG_DIR}/${log_file}" 2>/dev/null || sudo touch "${LOG_DIR}/${log_file}" 2>/dev/null
    chmod 666 "${LOG_DIR}/${log_file}" 2>/dev/null || sudo chmod 666 "${LOG_DIR}/${log_file}" 2>/dev/null
done
echo -e "${GREEN}✅ 日志目录已创建 (${#LOG_FILES[@]} 个日志文件)${NC}"

# =============================================================================
# 4. 生成配置文件
# =============================================================================
echo ""
echo -e "${YELLOW}[4/8] 配置邮件和API...${NC}"

CONFIG_FILE="${SCRIPT_DIR}/config/config.yaml"
CONFIG_TEMPLATE="${SCRIPT_DIR}/config/config.yaml.template"

if [ ! -f "${CONFIG_FILE}" ]; then
    echo ""
    echo -e "${YELLOW}⚠️ 配置文件不存在，从模板生成...${NC}"
    
    # 复制模板
    cp "${CONFIG_TEMPLATE}" "${CONFIG_FILE}"
    
    # 提示用户填入密码
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  ⚠️ 请手动编辑配置文件填入密码${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "配置文件路径: ${CONFIG_FILE}"
    echo ""
    echo "需要填入的信息："
    echo "  1. QQ邮箱授权码（不是登录密码）"
    echo "     获取方式：QQ邮箱设置 → 账户 → 生成授权码"
    echo ""
    echo "编辑命令:"
    echo "  vim ${CONFIG_FILE}"
    echo "  或 nano ${CONFIG_FILE}"
    echo ""
    echo -e "${YELLOW}填入完成后，按 Enter 继续...${NC}"
    read -r
else
    echo -e "${GREEN}✅ 配置文件已存在: ${CONFIG_FILE}${NC}"
fi

# 验证配置文件
if command -v python3 >/dev/null 2>&1; then
    python3 -c "import yaml; yaml.safe_load(open('${CONFIG_FILE}')); print('✅ 配置文件格式正确')" 2>/dev/null || {
        echo -e "${RED}❌ 配置文件格式错误，请检查 YAML 语法${NC}"
        exit 1
    }
fi

# =============================================================================
# 5. 检查 OpenClaw 模型配置
# =============================================================================
echo ""
echo -e "${YELLOW}[5/8] 检查 OpenClaw 模型配置...${NC}"

if openclaw config get auth 2>/dev/null | grep -q "kimi-coding"; then
    echo -e "${GREEN}✅ Kimi 模型已配置${NC}"
else
    echo -e "${YELLOW}⚠️ Kimi 模型未配置${NC}"
    echo ""
    echo "配置方式:"
    echo "  1. 运行: openclaw configure"
    echo "  2. 选择 kimi-coding"
    echo "  3. 填入 API Key"
    echo ""
    echo -e "${YELLOW}配置完成后，按 Enter 继续...${NC}"
    read -r
fi

# 测试模型调用
echo ""
echo -e "${YELLOW}测试模型调用...${NC}"
if openclaw infer model run --prompt "hi" --model kimi-coding/k2p5 --json >/dev/null 2>&1; then
    echo -e "${GREEN}✅ 模型调用正常${NC}"
else
    echo -e "${YELLOW}⚠️ 模型调用测试失败，可能需要重新配置 API Key${NC}"
fi

# =============================================================================
# 6. 安装定时任务
# =============================================================================
echo ""
echo -e "${YELLOW}[6/8] 安装定时任务...${NC}"

crontab_file="${SCRIPT_DIR}/crontab.txt"

if [ -f "${crontab_file}" ]; then
    # 读取现有 crontab（避免覆盖其他任务）
    existing_crontab=$(crontab -l 2>/dev/null || true)
    
    # 过滤掉旧的 jorge-cron-jobs 任务（如果有）
    filtered_crontab=$(echo "${existing_crontab}" | grep -v "jorge-cron-jobs/scripts" | grep -v "xiaohongshu-travel-daily" | grep -v "wechat-article-daily" | grep -v "douyin-daily" | grep -v "bithappy_email_pro" | grep -v "site_backup" | grep -v "memory_archive" | grep -v "collect_metrics" | grep -v "heartbeat_check" | grep -v "failure_prediction" | grep -v "health_check" | grep -v "daily_report" | grep -v "weekly_report" | grep -v "monthly_report" | grep -v "push_feishu" | grep -v "skill-backup")
    
    # 适配路径：将 crontab.txt 中的路径替换为当前实际路径
    adapted_crontab=$(sed "s|/root/.openclaw/workspace/jorge-cron-jobs|${SCRIPT_DIR}|g; s|/root/.openclaw/workspace/scripts|${SCRIPT_DIR}/scripts|g; s|/root/.openclaw/workspace/skills/daily-report|${SCRIPT_DIR}/scripts|g" "${crontab_file}")
    
    # 合并
    new_crontab="${filtered_crontab}

# ============================================
# jorge-cron-jobs 定时任务
# 项目路径: ${SCRIPT_DIR}
# 安装时间: $(date '+%Y-%m-%d %H:%M:%S')
# ============================================
${adapted_crontab}"
    
    # 安装
    echo "${new_crontab}" | crontab -
    echo -e "${GREEN}✅ 定时任务已安装${NC}"
    echo ""
    echo "已安装的任务:"
    crontab -l | grep -A 100 "jorge-cron-jobs" | tail -n +2 | head -30
else
    echo -e "${RED}❌ crontab.txt 不存在${NC}"
    exit 1
fi

# =============================================================================
# 7. 运行测试
# =============================================================================
echo ""
echo -e "${YELLOW}[7/8] 运行测试...${NC}"

echo ""
echo -e "${BLUE}测试1: 小红书旅游攻略脚本...${NC}"
cd "${SCRIPT_DIR}/scripts" && python3 xiaohongshu-travel-daily.py 2>&1 && echo -e "${GREEN}✅ 小红书脚本测试通过${NC}" || echo -e "${YELLOW}⚠️ 小红书脚本测试失败（可能是邮件配置问题）${NC}"

echo ""
echo -e "${BLUE}测试2: 抖音图文脚本...${NC}"
cd "${SCRIPT_DIR}/scripts" && python3 douyin-daily.py 2>&1 && echo -e "${GREEN}✅ 抖音脚本测试通过${NC}" || echo -e "${YELLOW}⚠️ 抖音脚本测试失败${NC}"

# =============================================================================
# 8. 完成
# =============================================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "项目路径: ${SCRIPT_DIR}"
echo "日志目录: ${LOG_DIR}"
echo "配置文件: ${CONFIG_FILE}"
echo ""
echo "定时任务已安装，查看命令:"
echo "  crontab -l"
echo ""
echo "查看日志:"
echo "  tail -f ${LOG_DIR}/xiaohongshu-travel.log"
echo "  tail -f ${LOG_DIR}/wechat-article-daily.log"
echo "  tail -f ${LOG_DIR}/douyin-daily.log"
echo ""
echo -e "${BLUE}🦞 暴躁小龙虾提示：记得把 config/config.yaml 的密码填好！${NC}"
