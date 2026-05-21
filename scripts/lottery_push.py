#!/usr/bin/env python3
"""
彩票开奖号码推送 - 使用 huiniao API
每天晚上10:10检查并推送当天开奖的双色球/大乐透
使用统一邮件模板系统
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
import sys
from pathlib import Path

# 导入统一邮件模板（添加路径）
sys.path.insert(0, '/root/.openclaw/workspace/skills/daily-report')
from email_templates import create_lottery_email

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "569545015@qq.com"
SMTP_PASS = "iylylmwnitbbbebi"
TO_EMAIL = "569545015@qq.com"

# 彩票配置
LOTTERY_CONFIG = {
    'ssq': {
        'name': '双色球',
        'days': [1, 3, 6],  # 周二、四、日
        'api_type': 'ssq'
    },
    'dlt': {
        'name': '大乐透',
        'days': [0, 2, 5],  # 周一、三、六
        'api_type': 'dlt'
    }
}


def send_email(subject, html_content, text_content):
    """发送邮件"""
    msg = MIMEMultipart('alternative')
    from_header = Header('权权养的虾（投资）', 'utf-8')
    from_header.append(f'<{SMTP_USER}>', 'ascii')
    msg['From'] = from_header
    msg['To'] = TO_EMAIL
    msg['Subject'] = Header(subject, 'utf-8')
    
    # 添加纯文本版本（优先）
    text_part = MIMEText(text_content, 'plain', 'utf-8')
    msg.attach(text_part)
    
    # 添加HTML版本
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
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


def fetch_lottery_data(lottery_type):
    """从 huiniao API 获取彩票数据"""
    url = f"http://api.huiniao.top/interface/home/lotteryHistory?type={lottery_type}&page=1&limit=1"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        if data.get('code') == 1 and data.get('data'):
            last_data = data['data'].get('last', {})
            return last_data
    except Exception as e:
        print(f"获取 {lottery_type} 数据失败: {e}")
    
    return None


def parse_ssq(data):
    """解析双色球数据"""
    red_balls = [data.get('one'), data.get('two'), data.get('three'), 
                 data.get('four'), data.get('five'), data.get('six')]
    blue_ball = data.get('seven')
    
    return {
        'issue': data.get('code', ''),
        'red': ' '.join([f"{int(b):02d}" for b in red_balls if b]),
        'blue': f"{int(blue_ball):02d}" if blue_ball else '',
        'date': data.get('day', ''),
        'open_time': data.get('open_time', '')
    }


def parse_dlt(data):
    """解析大乐透数据"""
    front_balls = [data.get('one'), data.get('two'), data.get('three'), 
                   data.get('four'), data.get('five')]
    back_balls = [data.get('six'), data.get('seven')]
    
    return {
        'issue': data.get('code', ''),
        'front': ' '.join([f"{int(b):02d}" for b in front_balls if b]),
        'back': ' '.join([f"{int(b):02d}" for b in back_balls if b]),
        'date': data.get('day', ''),
        'open_time': data.get('open_time', '')
    }


def generate_lottery_html(results):
    """生成彩票HTML内容"""
    html = ''
    for item in results:
        html += f'''
        <div style="background: linear-gradient(135deg, #fdf2f2 0%, #fef9e7 100%); border-left: 4px solid #e74c3c; padding: 16px 20px; margin-bottom: 15px; border-radius: 0 8px 8px 0;">
            <div style="font-size: 16px; font-weight: 700; color: #c0392b; margin-bottom: 8px;">🎱 {item['type']} 第 {item['issue']} 期</div>
            <div style="font-size: 18px; font-weight: 600; color: #2c3e50; letter-spacing: 2px; margin: 12px 0;">{item['numbers']}</div>
            <div style="font-size: 12px; color: #7f8c8d;">开奖时间: {item['open_time']}</div>
        </div>'''
    return html


def main():
    """主函数"""
    today = datetime.now()
    weekday = today.weekday()
    date_str = today.strftime('%Y-%m-%d')
    
    print(f"🦞 检查 {date_str} 的彩票开奖...")
    
    results = []
    
    # 检查每种彩票
    for lottery_key, config in LOTTERY_CONFIG.items():
        if weekday in config['days']:
            print(f"  📌 今天有 {config['name']} 开奖")
            data = fetch_lottery_data(config['api_type'])
            
            if data:
                if lottery_key == 'ssq':
                    parsed = parse_ssq(data)
                    results.append({
                        'type': config['name'],
                        'issue': parsed['issue'],
                        'numbers': f"红球: {parsed['red']} | 蓝球: {parsed['blue']}",
                        'date': parsed['date'],
                        'open_time': parsed['open_time']
                    })
                else:
                    parsed = parse_dlt(data)
                    results.append({
                        'type': config['name'],
                        'issue': parsed['issue'],
                        'numbers': f"前区: {parsed['front']} | 后区: {parsed['back']}",
                        'date': parsed['date'],
                        'open_time': parsed['open_time']
                    })
            else:
                print(f"  ❌ 无法获取 {config['name']} 数据")
    
    if not results:
        print("今天没有开奖，跳过推送")
        return
    
    # 使用统一模板
    email = create_lottery_email("🎱 彩票开奖结果", f"每日开奖 · {date_str}")
    
    # 添加开奖结果区块
    lottery_html = generate_lottery_html(results)
    email.add_section("🎱 开奖号码", "🎱", lottery_html, highlight=True)
    
    # 添加统计栏
    email.add_stats_bar([
        {'icon': '📅', 'label': '日期', 'value': date_str},
        {'icon': '🎱', 'label': '开奖', 'value': f'{len(results)} 种'},
    ])
    
    # 生成HTML
    html_content = email.render()
    
    # 生成纯文本版本
    text_lines = [f"🎱 每日彩票开奖结果", f"📅 开奖日期：{date_str}", ""]
    
    for item in results:
        text_lines.append(f"【{item['type']}】第 {item['issue']} 期")
        text_lines.append(f"  {item['numbers']}")
        text_lines.append(f"  开奖时间：{item['open_time']}")
        text_lines.append("")
    
    text_lines.append("-" * 40)
    text_lines.append("🦞 由权权龙虾管家自动推送")
    text_lines.append("⚠️ 仅供参考，请以官方公告为准")
    
    text_content = '\n'.join(text_lines)
    print("\n" + text_content)
    
    # 发送邮件
    subject = f"🎱 彩票开奖 {date_str}"
    send_email(subject, html_content, text_content)


if __name__ == '__main__':
    main()
