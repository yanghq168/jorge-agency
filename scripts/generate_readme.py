#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成 README.md，确保 UTF-8 编码正确
"""

import os
import re
import glob

AGENTS_DIR = "/root/.openclaw/workspace/agency-agents"
REPO_DIR = "/tmp/jorge-agency"

def get_category_name(en_name):
    """分类名称映射"""
    mapping = {
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
    return mapping.get(en_name, en_name)

def extract_agent_info(filepath):
    """提取 agent 信息"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None, None, None
        
        front_matter = match.group(1)
        
        name_match = re.search(r'^name:\s*(.+)$', front_matter, re.MULTILINE)
        desc_match = re.search(r'^description:\s*(.+?)$', front_matter, re.MULTILINE | re.DOTALL)
        emoji_match = re.search(r'^emoji:\s*(.+)$', front_matter, re.MULTILINE)
        
        name = name_match.group(1).strip() if name_match else os.path.basename(filepath)[:-3]
        desc = desc_match.group(1).strip() if desc_match else "暂无描述"
        emoji = emoji_match.group(1).strip() if emoji_match else "🤖"
        
        # 截断描述
        if len(desc) > 60:
            desc = desc[:57] + "..."
        
        return name, desc, emoji
    except Exception as e:
        return None, None, None

def generate_readme():
    """生成 README.md"""
    
    # 统计
    all_files = glob.glob(os.path.join(AGENTS_DIR, "**/*.md"), recursive=True)
    total_agents = len(all_files)
    
    categories = []
    for d in os.listdir(AGENTS_DIR):
        full_path = os.path.join(AGENTS_DIR, d)
        if os.path.isdir(full_path):
            categories.append(d)
    categories.sort()
    
    from datetime import datetime
    backup_time = datetime.now().strftime('%Y.%m.%d')
    # shields.io badge: 使用下划线代替点号，避免解析问题
    badge_date = backup_time.replace('.', '_')
    
    # 构建 README 内容
    lines = []
    lines.append("# 🦞 Jorge 的 AI Agent 军团")
    lines.append("")
    lines.append("> **权权管家(仓库)** 自动维护的 Agent 备份中心")
    lines.append("")
    lines.append(f"![Agents](https://img.shields.io/badge/Agents-{total_agents}-10b981?style=flat-square)")
    lines.append(f"![Updated](https://img.shields.io/badge/Updated-{badge_date}-059669?style=flat-square)")
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
    lines.append(f"| 📁 分类数量 | **{len(categories)}** 个 |")
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
    
    # 处理每个分类
    for category in categories:
        category_path = os.path.join(AGENTS_DIR, category)
        md_files = glob.glob(os.path.join(category_path, "*.md"))
        md_files.sort()
        
        if not md_files:
            continue
        
        category_name = get_category_name(category)
        lines.append(f"### {category_name}（{len(md_files)} 个）")
        lines.append("")
        lines.append("| 角色名称 | 职责描述 |")
        lines.append("|---------|---------|")
        
        for md_file in md_files:
            name, desc, emoji = extract_agent_info(md_file)
            if name:
                lines.append(f"| {emoji} **{name}** | {desc} |")
        
        lines.append("")
    
    # 根目录下的文件
    root_files = glob.glob(os.path.join(AGENTS_DIR, "*.md"))
    if root_files:
        lines.append(f"### 📌 独立 Agent（{len(root_files)} 个）")
        lines.append("")
        lines.append("| 角色名称 | 职责描述 |")
        lines.append("|---------|---------|")
        
        for md_file in root_files:
            name, desc, emoji = extract_agent_info(md_file)
            if name:
                lines.append(f"| {emoji} **{name}** | {desc} |")
        
        lines.append("")
    
    # 使用说明
    lines.append("---")
    lines.append("")
    lines.append("## 📖 如何使用")
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
    lines.append("---")
    lines.append("")
    lines.append("## 📝 更新记录")
    lines.append("")
    lines.append("### 📅 最近备份")
    lines.append("")
    lines.append(f"- **备份时间**: {backup_time}")
    lines.append(f"- **Agent 总数**: {total_agents} 个")
    lines.append(f"- **分类数量**: {len(categories)} 个")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本仓库由 🦞 **权权管家(仓库)** 自动维护*")
    lines.append("")
    
    # 写入文件，确保 UTF-8
    readme_path = os.path.join(REPO_DIR, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ README.md 已生成: {readme_path}")
    print(f"   总 Agent: {total_agents}")
    print(f"   分类数: {len(categories)}")

if __name__ == "__main__":
    generate_readme()
