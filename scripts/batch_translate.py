#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量翻译 Agent description 为中文
确保 UTF-8 编码
"""

import os
import re
import glob

AGENTS_DIR = "/root/.openclaw/workspace/agency-agents"

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
        
        # 匹配 front matter
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None, None
        
        front_matter = match.group(1)
        
        # 提取 description
        desc_match = re.search(r'^description:\s*(.+)$', front_matter, re.MULTILINE)
        if not desc_match:
            return None, None
        
        desc = desc_match.group(1).strip()
        
        # 检查是否已经是中文
        if any('\u4e00' <= char <= '\u9fff' for char in desc):
            return None, None
        
        return filepath, desc
    except Exception as e:
        print(f"❌ 读取失败 {filepath}: {e}")
        return None, None

def update_description(filepath, new_desc):
    """更新 description 字段"""
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
        
        # 写回文件，确保 UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"❌ 写入失败 {filepath}: {e}")
        return False

def main():
    print("🦞 扫描所有 Agent 文件...")
    
    files = get_all_md_files()
    print(f"找到 {len(files)} 个文件\n")
    
    # 收集所有需要翻译的 description
    to_translate = []
    for filepath in files:
        fp, desc = extract_description(filepath)
        if fp and desc:
            to_translate.append((fp, desc))
    
    print(f"需要翻译: {len(to_translate)} 个文件\n")
    
    if not to_translate:
        print("✅ 没有需要翻译的文件")
        return
    
    # 生成翻译任务列表
    print("=" * 60)
    print("请翻译以下内容（复制到AI助手进行批量翻译）:")
    print("=" * 60)
    
    for i, (fp, desc) in enumerate(to_translate, 1):
        filename = os.path.basename(fp)
        print(f"\n{i}. {filename}")
        print(f"   原文: {desc}")
    
    print("\n" + "=" * 60)
    print(f"\n共 {len(to_translate)} 条待翻译")
    print("翻译后按格式提供: 文件名|译文")

if __name__ == "__main__":
    main()
