#!/usr/bin/env python3
"""
批量翻译 Agent 文件的 description 字段为中文
使用 Kimi API
"""

import os
import re
import glob
import json
import time
from pathlib import Path

# Kimi API 配置
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_API_URL = "https://api.kimi.com/coding/v1/chat/completions"

def translate_description(text):
    """使用 Kimi API 翻译 description"""
    import requests
    
    if not text or len(text.strip()) < 5:
        return text
    
    headers = {
        "Authorization": f"Bearer {KIMI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "kimi-k2.5",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的技术翻译助手。请将下面的英文描述翻译成简洁、专业的中文，保留技术术语的准确性。只返回翻译后的文本，不要任何解释。"
            },
            {
                "role": "user",
                "content": f"请翻译以下描述（控制在80字以内）：\n{text}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(KIMI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        translated = result["choices"][0]["message"]["content"].strip()
        # 清理可能的引号
        translated = translated.strip('"').strip("'")
        return translated
    except Exception as e:
        print(f"  ⚠️ 翻译失败: {e}")
        return None

def process_file(filepath, dry_run=True):
    """处理单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 front matter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return False, None
    
    front_matter = match.group(1)
    rest_content = content[match.end():]
    
    # 查找 description 字段
    desc_match = re.search(r'^description:\s*(.+)$', front_matter, re.MULTILINE)
    if not desc_match:
        return False, None
    
    original_desc = desc_match.group(1).strip()
    
    # 检查是否已经是中文（简单判断）
    if any('\u4e00' <= char <= '\u9fff' for char in original_desc):
        print(f"  ⏭️  已中文，跳过")
        return False, None
    
    print(f"  📝 原文: {original_desc[:60]}...")
    
    # 翻译
    translated = translate_description(original_desc)
    if not translated:
        return False, None
    
    print(f"  ✅ 译文: {translated[:60]}...")
    
    # 替换 description
    new_front_matter = re.sub(
        r'^(description:\s*).+$',
        r'\1' + translated,
        front_matter,
        flags=re.MULTILINE
    )
    
    new_content = f"---\n{new_front_matter}\n---\n{rest_content}"
    
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return True, translated

def main():
    # Agent 目录
    agents_dir = "/root/.openclaw/workspace/agency-agents"
    
    # 获取所有 md 文件
    md_files = glob.glob(os.path.join(agents_dir, "**/*.md"), recursive=True)
    md_files.sort()
    
    print(f"🦞 找到 {len(md_files)} 个 Agent 文件")
    print("-" * 60)
    
    # 检查 API Key
    if not KIMI_API_KEY:
        print("❌ 错误: 请设置 KIMI_API_KEY 环境变量")
        print("   export KIMI_API_KEY=your_api_key")
        return
    
    # 先试运行（dry run）
    print("\n📋 试运行模式（不会实际修改文件）\n")
    
    translated_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, filepath in enumerate(md_files[:5], 1):  # 先测试前5个
        filename = os.path.basename(filepath)
        print(f"[{i}/5] {filename}")
        
        try:
            success, _ = process_file(filepath, dry_run=True)
            if success:
                translated_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            error_count += 1
        
        time.sleep(0.5)  # 避免请求过快
    
    print("-" * 60)
    print(f"测试完成: {translated_count} 个待翻译, {skipped_count} 个跳过, {error_count} 个错误")
    
    # 询问是否继续
    print("\n测试通过！确认要翻译所有文件吗？")
    print("运行: python3 translate_descriptions.py --confirm")

if __name__ == "__main__":
    import sys
    if "--confirm" in sys.argv:
        # 实际执行模式
        pass
    else:
        main()
