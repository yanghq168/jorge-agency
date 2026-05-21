#!/usr/bin/env python3
"""
Bithappy 理财数据分析脚本 - 简化版
直接解析快照文本生成报告
"""

import re
from datetime import datetime

def extract_products(text):
    """从快照文本提取产品信息"""
    products = []
    
    # 查找所有 StaticText 行
    static_texts = re.findall(r'- StaticText "([^"]+)"', text)
    
    # 定义币种和平台的匹配
    coins = ['BYUSDT', 'USDE', 'USDGO', 'WBTC', 'WETH', 'USDT', 'USDC', 'USDD', 'USD1', 'USDG']
    platforms = ['Bybit', 'Ethereal', 'Bitget', '币安钱包', '币安理财', '币安', '火币', 'OKX', 'Theo', 'Pendle']
    
    i = 0
    while i < len(static_texts):
        text_item = static_texts[i]
        
        # 检查是否是币种
        if text_item in coins or text_item == 'U':
            coin = text_item if text_item != 'U' else 'U(稳定币)'
            
            # 查找平台 (通常在币种后面几个位置)
            platform = None
            apy = None
            time_left = None
            
            # 在接下来的20个文本项中查找
            for j in range(i+1, min(i+20, len(static_texts))):
                next_text = static_texts[j]
                
                # 查找平台
                if not platform and next_text in platforms:
                    platform = next_text
                
                # 查找收益率 (格式如: 50.00%)
                if not apy and re.match(r'\d+\.\d+%$', next_text):
                    apy = float(next_text.replace('%', ''))
                
                # 查找剩余时间
                if not time_left:
                    if '剩余' in next_text and '天' in next_text:
                        time_left = next_text
                    elif next_text == '长期':
                        time_left = '长期'
                    elif next_text == '无固定结束时间':
                        time_left = '无固定结束'
                
                # 如果找到平台、收益率和时间，或者遇到下一个币种，就停止
                if platform and apy:
                    break
            
            if platform and apy:
                products.append({
                    'coin': coin,
                    'platform': platform,
                    'apy': apy,
                    'time_left': time_left or '未知'
                })
        
        i += 1
    
    return products

def analyze_products(products):
    """分析产品并生成投资建议"""
    if not products:
        return "⚠️ 未能获取到理财数据，请检查网页是否有更新。"
    
    # 去重 (有时会有重复)
    seen = set()
    unique_products = []
    for p in products:
        key = (p['coin'], p['platform'], p['apy'])
        if key not in seen:
            seen.add(key)
            unique_products.append(p)
    
    products = unique_products
    
    # 按收益率排序
    sorted_products = sorted(products, key=lambda x: x['apy'], reverse=True)
    
    report = []
    report.append("📊 **Bithappy 理财看板分析报告**")
    report.append(f"⏰ 数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"📈 共发现 {len(products)} 个理财产品\n")
    
    # 高收益推荐 (>=15%)
    high_yield = [p for p in sorted_products if p['apy'] >= 15]
    if high_yield:
        report.append("🔥 **高收益推荐 (≥15% 年化，风险较高)**")
        for p in high_yield[:3]:
            report.append(f"  • **{p['coin']}** @ {p['platform']} - **{p['apy']}%** ({p['time_left']})")
        report.append("")
    
    # 稳健收益 (8-15%)
    medium_yield = [p for p in sorted_products if 8 <= p['apy'] < 15]
    if medium_yield:
        report.append("💎 **稳健收益推荐 (8-15% 年化，相对平衡)**")
        for p in medium_yield[:4]:
            report.append(f"  • **{p['coin']}** @ {p['platform']} - **{p['apy']}%** ({p['time_left']})")
        report.append("")
    
    # 保守收益 (<8%)
    low_yield = [p for p in sorted_products if p['apy'] < 8]
    if low_yield:
        report.append("🛡️ **保守收益 (<8% 年化，相对安全)**")
        for p in low_yield[:3]:
            report.append(f"  • **{p['coin']}** @ {p['platform']} - **{p['apy']}%** ({p['time_left']})")
        report.append("")
    
    # 投资建议
    report.append("---")
    report.append("💡 **投资建议：**")
    
    top = sorted_products[0] if sorted_products else None
    if top and top['apy'] >= 15:
        report.append(f"1. **高风险高回报**: {top['coin']} ({top['apy']}%) 收益最高，但注意风控")
    
    # 找出币安的产品 (通常较安全)
    binance_products = [p for p in sorted_products if '币安' in p['platform']]
    if binance_products:
        best_binance = max(binance_products, key=lambda x: x['apy'])
        report.append(f"2. **稳健选择**: {best_binance['coin']} @ {best_binance['platform']} ({best_binance['apy']}%) 相对安全")
    
    report.append("3. **注意期限**: 部分产品即将到期，注意资金安排")
    report.append("\n⚠️ **风险提示**: 以上仅为信息整理，不构成投资建议。DeFi理财有风险，请自行研究并控制仓位！")
    
    return '\n'.join(report)

if __name__ == '__main__':
    import sys
    
    snapshot_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/bithappy_snapshot.txt'
    
    try:
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        products = extract_products(text)
        report = analyze_products(products)
        print(report)
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
