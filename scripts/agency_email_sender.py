#!/usr/bin/env python3
"""
Agency Backup Email Sender
发送人: 权权管家(仓库)
"""

import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

def send_backup_email(to_email, subject_file, body_file):
    """发送备份通知邮件"""
    
    # 读取邮件内容
    with open(subject_file, 'r', encoding='utf-8') as f:
        subject = f.read().strip()
    
    with open(body_file, 'r', encoding='utf-8') as f:
        body = f.read()
    
    # 邮件配置 (使用环境变量或配置文件)
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_pass = os.getenv('SMTP_PASS', '')
    
    # 如果没有配置SMTP，直接打印到日志
    if not smtp_user or not smtp_pass:
        print("⚠️ SMTP 未配置，邮件内容如下:")
        print(f"主题: {subject}")
        print(f"内容:\n{body}")
        return True
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = Header('权权管家(仓库) <quanquan@backup.local>', 'utf-8')
        msg['To'] = Header(to_email, 'utf-8')
        
        # 纯文本版本
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # HTML 版本
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 20px; border-radius: 0 0 8px 8px; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
                .lobster {{ font-size: 24px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <span class="lobster">🦞</span> 权权管家(仓库) 备份报告
                </div>
                <div class="content">
                    <pre style="white-space: pre-wrap; font-family: inherit;">{body}</pre>
                </div>
                <div class="footer">
                    此邮件由 权权管家(仓库) 自动发送 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        
        print(f"✅ 邮件已发送到 {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 agency_email_sender.py <to_email> <subject_file> <body_file>")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject_file = sys.argv[2]
    body_file = sys.argv[3]
    
    success = send_backup_email(to_email, subject_file, body_file)
    sys.exit(0 if success else 1)
