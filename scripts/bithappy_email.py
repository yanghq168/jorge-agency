#!/usr/bin/env python3
"""
Bithappy 理财监控 - 邮件版
抓取数据并发送邮件报告
"""

import subprocess
import time
import re
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 邮件配置 (从 daily-report 同步)
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "569545015@qq.com"
SMTP_PASS = "iylylmwnitbbbebi"
TO_EMAIL = "569545015@qq.com"

def send_email(subject, content, html_content=None):
    """发送邮件"""
    msg = MIMEMultipart('alternative')
    # 使用中文发件人名称
    from_header = Header('权权养的虾（投资）', 'utf-8')
    from_header.append(f'<{SMTP_USER}>', 'ascii')
    msg['From'] = from_header
    msg['To'] = TO_EMAIL
    msg['Subject'] = Header(subject, 'utf-8')
    
    # 纯文本内容
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    # HTML 内容 (如果提供)
    if html_content:
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
        server.quit()
        print(f"✅ 邮件已发送至 {TO_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def run_browser():
    """运行浏览器抓取数据"""
    # 打开页面
    result = subprocess.run(
        ['agent-browser', 'open', 'https://bithappy.xyz/products'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 打开页面失败: {result.stderr}")
        return None
    
    time.sleep(3)
    
    # 获取 snapshot 找到理财看板按钮
    result = subprocess.run(
        ['agent-browser', 'snapshot', '-i'],
        capture_output=True, text=True
    )
    snapshot = result.stdout
    
    # 提取 ref
    ref_match = re.search(r'理财看板.*\[ref=(e\d+)\]', snapshot)
    if not ref_match:
        print("❌ 找不到理财看板按钮")
        subprocess.run(['agent-browser', 'close'], capture_output=True)
        return None
    
    ref = ref_match.group(1)
    
    # 点击理财看板
    result = subprocess.run(
        ['agent-browser', 'click', ref],
        capture_output=True, text=True
    )
    time.sleep(3)
    
    # 获取完整快照
    result = subprocess.run(
        ['agent-browser', 'snapshot'],
        capture_output=True, text=True
    )
    snapshot = result.stdout
    
    # 关闭浏览器
    subprocess.run(['agent-browser', 'close'], capture_output=True)
    
    return snapshot

def extract_products(text):
    """从快照文本提取产品信息"""
    products = []
    static_texts = re.findall(r'- StaticText "([^"]+)"', text)
    
    coins = ['BYUSDT', 'USDE', 'USDGO', 'WBTC', 'WETH', 'USDT', 'USDC', 'USDD', 'USD1', 'USDG']
    platforms = ['Bybit', 'Ethereal', 'Bitget', '币安钱包', '币安理财', '币安', '火币', 'OKX', 'Theo', 'Pendle']
    
    i = 0
    while i < len(static_texts):
        text_item = static_texts[i]
        
        if text_item in coins or text_item == 'U':
            coin = text_item if text_item != 'U' else 'U(稳定币)'
            platform = None
            apy = None
            time_left = None
            
            for j in range(i+1, min(i+20, len(static_texts))):
                next_text = static_texts[j]
                
                if not platform and next_text in platforms:
                    platform = next_text
                
                if not apy and re.match(r'\d+\.\d+%$', next_text):
                    apy = float(next_text.replace('%', ''))
                
                if not time_left:
                    if '剩余' in next_text and '天' in next_text:
                        time_left = next_text
                    elif next_text == '长期':
                        time_left = '长期'
                    elif next_text == '无固定结束时间':
                        time_left = '无固定结束'
                
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
    """分析产品并生成报告"""
    if not products:
        return "⚠️ 未能获取到理财数据"
    
    seen = set()
    unique_products = []
    for p in products:
        key = (p['coin'], p['platform'], p['apy'])
        if key not in seen:
            seen.add(key)
            unique_products.append(p)
    
    products = unique_products
    sorted_products = sorted(products, key=lambda x: x['apy'], reverse=True)
    
    lines = []
    lines.append("📊 理财看板分析报告")
    lines.append(f"⏰ 数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"📈 共发现 {len(products)} 个理财产品\n")
    
    high_yield = [p for p in sorted_products if p['apy'] >= 15]
    if high_yield:
        lines.append("🔥 高收益推荐 (≥15% 年化，风险较高)")
        for p in high_yield[:3]:
            lines.append(f"  • {p['coin']} @ {p['platform']} - {p['apy']}% ({p['time_left']})")
        lines.append("")
    
    medium_yield = [p for p in sorted_products if 8 <= p['apy'] < 15]
    if medium_yield:
        lines.append("💎 稳健收益推荐 (8-15% 年化)")
        for p in medium_yield[:4]:
            lines.append(f"  • {p['coin']} @ {p['platform']} - {p['apy']}% ({p['time_left']})")
        lines.append("")
    
    low_yield = [p for p in sorted_products if p['apy'] < 8]
    if low_yield:
        lines.append("🛡️ 保守收益 (<8% 年化)")
        for p in low_yield[:3]:
            lines.append(f"  • {p['coin']} @ {p['platform']} - {p['apy']}% ({p['time_left']})")
        lines.append("")
    
    lines.append("-" * 40)
    lines.append("💡 投资建议：")
    
    top = sorted_products[0] if sorted_products else None
    if top and top['apy'] >= 15:
        lines.append(f"1. 高风险高回报: {top['coin']} ({top['apy']}%) 收益最高，但注意风控")
    
    binance_products = [p for p in sorted_products if '币安' in p['platform']]
    if binance_products:
        best_binance = max(binance_products, key=lambda x: x['apy'])
        lines.append(f"2. 稳健选择: {best_binance['coin']} @ {best_binance['platform']} ({best_binance['apy']}%) 相对安全")
    
    lines.append("3. 注意期限: 部分产品即将到期，注意资金安排")
    lines.append("\n⚠️ 风险提示: 以上仅为信息整理，不构成投资建议。DeFi理财有风险！")
    
    return '\n'.join(lines)

def main():
    print("🦞 开始抓取 Bithappy 理财数据...")
    
    snapshot = run_browser()
    if not snapshot:
        print("❌ 数据抓取失败")
        return
    
    products = extract_products(snapshot)
    report = analyze_products(products)
    
    print("\n" + report)
    
    # 发送邮件
    subject = f"🦞 理财报告 {datetime.now().strftime('%m-%d %H:%M')}"
    send_email(subject, report)

if __name__ == '__main__':
    main()
