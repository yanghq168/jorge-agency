#!/bin/bash
# Agency Agents Backup Script
# 每天自动备份 agents 到 jorge-agency 仓库并发送邮件通知

set -e

REPO_DIR="/tmp/jorge-agency"
SOURCE_DIR="/root/.openclaw/workspace/agency-agents"
BACKUP_DIR="$REPO_DIR/agents"
README_FILE="$REPO_DIR/README.md"
LOG_FILE="/tmp/agency-backup.log"
EMAIL_TO="${AGENCY_BACKUP_EMAIL:-}"  # 从环境变量读取邮箱

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# 克隆或更新仓库
setup_repo() {
    log "设置仓库..."
    if [ -d "$REPO_DIR/.git" ]; then
        cd "$REPO_DIR"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
    else
        rm -rf "$REPO_DIR"
        gh repo clone jorge-agency "$REPO_DIR"
    fi
    
    cd "$REPO_DIR"
    # 确保git配置存在
    git config user.email "quanquan@backup.local" 2>/dev/null || true
    git config user.name "权权管家(仓库)" 2>/dev/null || true
}

# 生成分类名称（中文映射）
get_category_name() {
    local en_name=$1
    case "$en_name" in
        "academic") echo "📚 学术研究" ;;
        "design") echo "🎨 设计创意" ;;
        "engineering") echo "💻 工程开发" ;;
        "finance") echo "💰 金融财务" ;;
        "game-development") echo "🎮 游戏开发" ;;
        "marketing") echo "📢 市场营销" ;;
        "paid-media") echo "💵 付费媒体" ;;
        "product") echo "📱 产品管理" ;;
        "project-management") echo "📊 项目管理" ;;
        "sales") echo "💼 销售业务" ;;
        "spatial-computing") echo "🥽 空间计算" ;;
        "specialized") echo "🔧 专业领域" ;;
        "strategy") echo "🎯 战略规划" ;;
        "support") echo "🎧 客户支持" ;;
        "testing") echo "🧪 测试质检" ;;
        *) echo "$en_name" ;;
    esac
}

# 生成 README.md (确保UTF-8编码)
generate_readme() {
    log "生成 README.md..."
    
    local total_agents=$(find "$SOURCE_DIR" -name "*.md" | wc -l)
    local categories=$(find "$SOURCE_DIR" -type d -not -path "$SOURCE_DIR" | sort)
    local backup_time=$(date '+%Y-%m-%d %H:%M:%S')
    local category_count=$(echo "$categories" | wc -l)
    
    # 用 Python 生成 README 确保 UTF-8 正常
    python3 - "$SOURCE_DIR" "$total_agents" "$category_count" "$backup_time" << 'PYEOF'
import os, sys, glob, re

source_dir = sys.argv[1]
total_agents = sys.argv[2]
category_count = sys.argv[3]
backup_time = sys.argv[4]

category_map = {
    "academic": "📚 学术研究",
    "design": "🎨 设计创意",
    "engineering": "💻 工程开发",
    "finance": "💰 金融财务",
    "game-development": "🎮 游戏开发",
    "marketing": "📢 市场营销",
    "paid-media": "💵 付费媒体",
    "product": "📱 产品管理",
    "project-management": "📊 项目管理",
    "sales": "💼 销售业务",
    "spatial-computing": "🥽 空间计算",
    "specialized": "🔧 专业领域",
    "strategy": "🎯 战略规划",
    "support": "🎧 客户支持",
    "testing": "🧪 测试质检",
}

def read_agent_meta(path):
    name = desc = emoji = ""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith('name:'):
                name = line.split(':', 1)[1].strip()
            elif line.startswith('description:'):
                desc = line.split(':', 1)[1].strip()[:80]
            elif line.startswith('emoji:'):
                emoji = line.split(':', 1)[1].strip()
            if name and desc and emoji:
                break
    if not name:
        name = os.path.splitext(os.path.basename(path))[0]
    if not emoji:
        emoji = "🤖"
    if not desc:
        desc = "暂无描述"
    return emoji, name, desc

lines = []
lines.append("# 🦞 Jorge 的 AI Agent 军团")
lines.append("")
lines.append("> **权权管家(仓库)** 自动维护的 Agent 备份中心")
lines.append("")
lines.append(f"![Agent 数量](https://img.shields.io/badge/Agent-{total_agents}-10b981?style=flat-square)")
lines.append(f"![最后备份](https://img.shields.io/badge/最后备份-{backup_time}-059669?style=flat-square)")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 📋 目录")
lines.append("")
lines.append("- [简介](#-简介)")
lines.append("- [Agent 分类清单](#-agent-分类清单)")
lines.append("- [如何使用](#-如何使用)")
lines.append("- [更新记录](#-更新记录)")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 📝 简介")
lines.append("")
lines.append("本仓库是 **Jorge** 的 AI Agent 集合备份中心。每个 Agent 都是一个专门化的 AI 角色，具备特定的专业技能、个性特征和工作流程。")
lines.append("")
lines.append("### 当前统计")
lines.append("")
lines.append("| 指标 | 数量 |")
lines.append("|------|------|")
lines.append(f"| 📦 Agent 总数 | **{total_agents}** 个 |")
lines.append(f"| 📁 分类数量 | **{category_count}** 个 |")
lines.append("| 🔄 备份频率 | 每日 02:00 |")
lines.append("| 📧 变更通知 | 自动邮件 |")
lines.append("")
lines.append("### 什么是 Agent？")
lines.append("")
lines.append("Agent（智能代理）是具备以下特征的 AI 角色：")
lines.append("- **专业身份** - 明确的职业角色和专业领域")
lines.append("- **个性特征** - 独特的性格、语气和表达方式")
lines.append("- **核心使命** - 清晰的职责范围和工作目标")
lines.append("- **记忆系统** - 上下文保持和经验积累能力")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 🤖 Agent 分类清单")
lines.append("")

# 遍历分类目录
for cat_dir in sorted(glob.glob(os.path.join(source_dir, "*/"))):
    cat_name = os.path.basename(os.path.dirname(cat_dir))
    display = category_map.get(cat_name, cat_name)
    agents = sorted(glob.glob(os.path.join(cat_dir, "*.md")))
    count = len(agents)
    if count == 0:
        continue
    lines.append(f"### {display}（{count} 个）")
    lines.append("")
    lines.append("| 角色名称 | 职责描述 |")
    lines.append("|---------|---------|")
    for agent_file in agents:
        emoji, name, desc = read_agent_meta(agent_file)
        lines.append(f"| {emoji} **{name}** | {desc}... |")
    lines.append("")

# 根目录独立 agent
root_agents = sorted(glob.glob(os.path.join(source_dir, "*.md")))
if root_agents:
    lines.append(f"### 📌 独立 Agent（{len(root_agents)} 个）")
    lines.append("")
    lines.append("| 角色名称 | 职责描述 |")
    lines.append("|---------|---------|")
    for agent_file in root_agents:
        emoji, name, desc = read_agent_meta(agent_file)
        lines.append(f"| {emoji} **{name}** | {desc}... |")
    lines.append("")

lines.append("---")
lines.append("")
lines.append("## 📖 如何使用")
lines.append("")
lines.append("### 查看 Agent 详情")
lines.append("")
lines.append("每个分类目录中包含完整的 Agent 定义文件（`.md`），结构如下：")
lines.append("")
lines.append("```yaml")
lines.append("---")
lines.append("name: Agent 名称")
lines.append("description: 职责描述")
lines.append("color: 主题色")
lines.append("emoji: 表情符号")
lines.append("vibe: 个性标签")
lines.append("---")
lines.append("```")
lines.append("")
lines.append("内容包含：")
lines.append("- **🧠 角色定义** - 专业技能、个性特征、记忆系统")
lines.append("- **🎯 核心使命** - 职责范围、工作目标")
lines.append("- **⚙️ 工作流程** - 具体的执行步骤和方法")
lines.append("- **💾 记忆系统** - 上下文保持和经验积累")
lines.append("")
lines.append("### 目录结构说明")
lines.append("")
lines.append("```")
lines.append("agents/")
lines.append("├── academic/          # 📚 学术研究 - 人类学、地理学、心理学等")
lines.append("├── design/            # 🎨 设计创意 - UI/UX、品牌、视觉设计")
lines.append("├── engineering/       # 💻 工程开发 - 前端、后端、AI、DevOps")
lines.append("├── finance/           # 💰 金融财务 - 会计、投资、税务")
lines.append("├── game-development/  # 🎮 游戏开发 - 游戏设计、关卡设计、音频")
lines.append("├── marketing/         # 📢 市场营销 - 社媒、SEO、内容创作")
lines.append("├── paid-media/        # 💵 付费媒体 - 广告投放、效果追踪")
lines.append("├── product/           # 📱 产品管理 - 产品经理、用户研究")
lines.append("├── project-management/# 📊 项目管理 - 项目协调、流程优化")
lines.append("├── sales/             # 💼 销售业务 - 销售策略、客户管理")
lines.append("├── spatial-computing/ # 🥽 空间计算 - AR/VR、VisionOS")
lines.append("├── specialized/       # 🔧 专业领域 - 法律、医疗、招聘等垂直领域")
lines.append("├── strategy/          # 🎯 战略规划 - 商业策略、执行方案")
lines.append("├── support/           # 🎧 客户支持 - 客服、运维支持")
lines.append("└── testing/           # 🧪 测试质检 - QA、性能测试、安全测试")
lines.append("```")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 📝 更新记录")
lines.append("")
lines.append("### 📅 最近备份")
lines.append("")
lines.append(f"- **备份时间**: {backup_time}")
lines.append(f"- **Agent 总数**: {total_agents} 个")
lines.append(f"- **分类数量**: {category_count} 个")
lines.append("")
lines.append("---")
lines.append("")
lines.append("*本仓库由 🦞 **权权管家(仓库)** 自动维护*")
lines.append("")
lines.append("[![GitHub](https://img.shields.io/badge/GitHub-jorge--agency-181717?style=flat-square&logo=github)](https://github.com/yanghq168/jorge-agency)")

with open("/tmp/jorge-agency/README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
PYEOF

    log "README.md 生成完成"
}

# 同步 agents 文件
sync_agents() {
    log "同步 agents 文件..."
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    
    # 使用 rsync 进行增量同步
    if command -v rsync &> /dev/null; then
        rsync -av --delete "$SOURCE_DIR/" "$BACKUP_DIR/"
    else
        # 如果没有 rsync，使用 cp
        rm -rf "$BACKUP_DIR"
        cp -r "$SOURCE_DIR" "$BACKUP_DIR"
    fi
    
    log "同步完成"
}

# 检查变更
check_changes() {
    cd "$REPO_DIR"
    
    # 检查是否有提交历史
    if ! git rev-parse --git-dir > /dev/null 2>&1 || [ -z "$(git rev-list -n 1 --all 2>/dev/null)" ]; then
        log "新仓库，需要首次提交"
        return 0
    fi
    
    # 检查是否有变更
    if git diff --quiet && git diff --staged --quiet && [ -z "$(git status --porcelain)" ]; then
        log "没有检测到变更，跳过提交"
        return 1
    fi
    
    return 0
}

# 提交变更
commit_changes() {
    cd "$REPO_DIR"
    
    local date_str=$(date '+%Y-%m-%d')
    local time_str=$(date '+%H:%M:%S')
    
    log "提交变更..."
    
    git add -A
    git commit -m "🔄 自动备份: $date_str $time_str

- 更新 Agent 定义
- 同步 README.md
- 备份时间: $time_str

🦞 权权管家(仓库) 自动提交" 2>/dev/null || {
        log "没有新变更需要提交"
        return 0
    }
    
    # 使用 token 推送
    local token=$(gh auth token)
    git push https://x-access-token:${token}@github.com/yanghq168/jorge-agency.git HEAD
    
    log "提交完成"
}

# 生成变更日志邮件内容
generate_changelog() {
    cd "$REPO_DIR"
    
    local date_str=$(date '+%Y-%m-%d')
    local changes=$(git diff --name-status HEAD~1 2>/dev/null || echo "首次提交")
    
    local email_subject="Agent 仓库备份通知 - $date_str"
    local email_body="🦞 权权管家(仓库) 备份报告

备份时间: $(date '+%Y-%m-%d %H:%M:%S')
仓库地址: https://github.com/yanghq168/jorge-agency

📊 本次变更:
$changes

📈 当前统计:
- Agent 总数: $(find "$BACKUP_DIR" -name "*.md" | wc -l) 个
- 分类数量: $(find "$BACKUP_DIR" -type d -not -path "$BACKUP_DIR" | wc -l) 个

---
此邮件由 权权管家(仓库) 自动发送
"
    
    echo "$email_body" > "/tmp/agency-backup-email.txt"
    echo "$email_subject" > "/tmp/agency-backup-subject.txt"
}

# 发送邮件通知
send_email_notification() {
    if [ -z "$EMAIL_TO" ]; then
        log "未配置邮箱，跳过邮件发送"
        log "如需接收邮件，请设置环境变量: export AGENCY_BACKUP_EMAIL=your@email.com"
        return 0
    fi
    
    log "发送邮件通知到 $EMAIL_TO..."
    
    if python3 /root/.openclaw/workspace/scripts/agency_email_sender.py "$EMAIL_TO" "/tmp/agency-backup-subject.txt" "/tmp/agency-backup-email.txt"; then
        log "✅ 邮件发送完成"
    else
        warn "邮件发送失败，但备份已完成"
    fi
}

# 主流程
main() {
    log "========== Agency Agents 备份开始 =========="
    
    setup_repo
    sync_agents
    generate_readme
    
    if check_changes; then
        commit_changes
        generate_changelog
        send_email_notification
        log "✅ 备份完成，变更已提交到 GitHub"
    else
        log "✅ 检查完成，无需更新"
    fi
    
    log "========== 备份流程结束 =========="
}

main "$@"
