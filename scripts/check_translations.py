#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用AI能力批量翻译Agent描述
分批处理避免超时
"""

import os
import re
import glob
import json

AGENTS_DIR = "/root/.openclaw/workspace/agency-agents"

def get_files_needing_translation():
    """获取需要翻译的文件（中英混合的）"""
    pattern = os.path.join(AGENTS_DIR, "**/*.md")
    files = glob.glob(pattern, recursive=True)
    
    need_translate = []
    for filepath in sorted(files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                continue
            
            front_matter = match.group(1)
            desc_match = re.search(r'^description:\s*(.+?)$', front_matter, re.MULTILINE | re.DOTALL)
            if not desc_match:
                continue
            
            desc = desc_match.group(1).strip()
            
            # 检查是否包含英文单词（中英混合）
            # 如果同时有中文和明显的英文单词（超过3个字母的英文单词），则需要重新翻译
            has_chinese = bool(re.search(r'[\u4e00-\u9fff]', desc))
            english_words = re.findall(r'\b[a-zA-Z]{4,}\b', desc)
            
            if has_chinese and len(english_words) > 3:
                # 中英混合，需要重新翻译
                need_translate.append((filepath, desc))
            elif not has_chinese and english_words:
                # 纯英文，也需要翻译
                need_translate.append((filepath, desc))
                
        except Exception as e:
            print(f"❌ 读取失败 {filepath}: {e}")
    
    return need_translate

def update_description(filepath, new_desc):
    """更新文件中的 description"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 description
        new_content = re.sub(
            r'^(description:\s*).+$',
            r'\1' + new_desc,
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"❌ 写入失败 {filepath}: {e}")
        return False

if __name__ == "__main__":
    files = get_files_needing_translation()
    print(f"需要重新翻译: {len(files)} 个文件")
    print("\n文件列表:")
    for i, (fp, desc) in enumerate(files[:30], 1):
        print(f"{i}. {os.path.basename(fp)}")
        print(f"   当前: {desc[:80]}...")
