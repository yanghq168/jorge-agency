#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量翻译 Agent description - 后台执行版
处理全部166个文件，完成后通知
"""

import os
import re
import glob
import json
import time
import subprocess
from pathlib import Path

AGENTS_DIR = "/root/.openclaw/workspace/agency-agents"
SCRIPT_DIR = "/root/.openclaw/workspace/scripts"

# 翻译映射表（预定义常用翻译，减少API调用）
TRANSLATION_CACHE = {}

def get_all_md_files():
    """获取所有 markdown 文件"""
    pattern = os.path.join(AGENTS_DIR, "**/*.md")
    files = glob.glob(pattern, recursive=True)
    return sorted(files)

def extract_description(filepath):
    """提取 description 字段"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None, None, None
        
        front_matter = match.group(1)
        rest_content = content[match.end():]
        
        desc_match = re.search(r'^description:\s*(.+)$', front_matter, re.MULTILINE)
        if not desc_match:
            return None, None, None
        
        desc = desc_match.group(1).strip()
        
        # 检查是否已中文
        if any('\u4e00' <= char <= '\u9fff' for char in desc):
            return None, None, None
        
        return filepath, desc, (front_matter, rest_content)
    except Exception as e:
        print(f"❌ 读取失败 {filepath}: {e}")
        return None, None, None

def translate_with_kimi(text):
    """使用 Kimi API 翻译"""
    import requests
    
    api_key = os.getenv("KIMI_API_KEY", "")
    if not api_key:
        # 如果没有API key，使用规则翻译
        return rule_based_translate(text)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "kimi-k2.5",
        "messages": [
            {
                "role": "system",
                "content": "将以下英文描述翻译成简洁专业的中文（60字以内），保留关键技术术语如AI、API、UI等。只返回译文，不解释。"
            },
            {"role": "user", "content": text}
        ],
        "temperature": 0.3,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(
            "https://api.kimi.com/coding/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip().strip('"').strip("'")
    except Exception as e:
        print(f"  API错误: {e}")
        return rule_based_translate(text)

def rule_based_translate(text):
    """基于规则的简单翻译（备用方案）"""
    # 常见模式替换
    replacements = {
        "Expert in": "专家",
        "Expert ": "专家",
        "specializing in": "专注于",
        "specialist": "专家",
        "specialist in": "专家",
        "specializing": "专注于",
        "focused on": "专注于",
        "building": "构建",
        "development": "开发",
        "design": "设计",
        "optimization": "优化",
        "management": "管理",
        "analysis": "分析",
        "strategy": "策略",
        "marketing": "营销",
        "engineering": "工程",
        "security": "安全",
        "data": "数据",
        "AI": "AI",
        "ML": "机器学习",
        "API": "API",
        "UI": "UI",
        "UX": "UX",
        "SEO": "SEO",
        "DevOps": "DevOps",
        "automation": "自动化",
        "cloud": "云",
        "frontend": "前端",
        "backend": "后端",
        "mobile": "移动",
        "web": "Web",
        "application": "应用",
        "system": "系统",
        "platform": "平台",
        "service": "服务",
        "integration": "集成",
        "testing": "测试",
        "deployment": "部署",
        "monitoring": "监控",
        "performance": "性能",
        "scalable": "可扩展",
        "modern": "现代",
        "intelligent": "智能",
    }
    
    # 简单替换
    result = text
    for en, cn in replacements.items():
        result = result.replace(en, cn)
    
    # 如果结果太长，截断
    if len(result) > 80:
        result = result[:77] + "..."
    
    return result

def update_file(filepath, new_desc):
    """更新文件中的 description"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 description
        new_content = re.sub(
            r'^(description:\s*).+$',
            r'\1' + new_desc,
            content,
            flags=re.MULTILINE
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"❌ 写入失败 {filepath}: {e}")
        return False

def run_backup():
    """运行备份脚本"""
    try:
        result = subprocess.run(
            ["/root/.openclaw/workspace/scripts/agency-backup.sh"],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def notify_user(message):
    """通知用户（通过创建标记文件）"""
    with open("/tmp/agency_translation_done.txt", "w", encoding='utf-8') as f:
        f.write(message)
    print(f"\n{'='*60}")
    print(message)
    print(f"{'='*60}")

def main():
    print("🦞 开始批量翻译 Agent descriptions...")
    print("="*60)
    
    files = get_all_md_files()
    print(f"找到 {len(files)} 个文件\n")
    
    # 收集待翻译项
    to_translate = []
    for filepath in files:
        fp, desc, _ = extract_description(filepath)
        if fp and desc:
            to_translate.append((fp, desc))
    
    total = len(to_translate)
    print(f"需要翻译: {total} 个文件\n")
    
    if total == 0:
        notify_user("✅ 没有需要翻译的文件")
        return
    
    # 批量翻译
    success_count = 0
    fail_count = 0
    
    for i, (filepath, desc) in enumerate(to_translate, 1):
        filename = os.path.basename(filepath)
        print(f"[{i}/{total}] {filename}")
        print(f"      原文: {desc[:60]}...")
        
        # 翻译
        translated = translate_with_kimi(desc)
        if translated:
            print(f"      译文: {translated[:60]}...")
            
            # 更新文件
            if update_file(filepath, translated):
                success_count += 1
                print(f"      ✅ 已更新")
            else:
                fail_count += 1
                print(f"      ❌ 更新失败")
        else:
            fail_count += 1
            print(f"      ❌ 翻译失败")
        
        # 每10个暂停一下，避免API限制
        if i % 10 == 0:
            print(f"\n  ⏸️  已处理 {i} 个，暂停2秒...\n")
            time.sleep(2)
    
    print("\n" + "="*60)
    print(f"翻译完成: {success_count} 成功, {fail_count} 失败")
    
    # 运行备份
    print("\n🔄 正在运行备份脚本...")
    backup_ok, backup_output = run_backup()
    
    if backup_ok:
        print("✅ 备份完成")
    else:
        print(f"⚠️ 备份可能有问题: {backup_output[:200]}")
    
    # 通知
    message = f"""🦞 Agent Description 翻译完成

统计:
- 总文件: {len(files)}
- 翻译: {success_count} 个
- 失败: {fail_count} 个
- 备份: {'成功' if backup_ok else '失败'}

仓库地址: https://github.com/yanghq168/jorge-agency
"""
    notify_user(message)

if __name__ == "__main__":
    main()
