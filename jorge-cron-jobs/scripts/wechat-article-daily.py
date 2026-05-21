#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号【围炉家常】每日文章生成器
每晚22:00运行，生成家庭人情关系主题文章
通过 openclaw infer model run 调用 Kimi 生成内容
发送邮件至 569545015@qq.com
发件人：权权管家（公众号）
"""

import json
import random
import re
import smtplib
import ssl
import subprocess
import sys
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ==================== 配置 ====================
# 优先从 config.yaml 读取，否则使用默认值
try:
    from config_loader import get_mail_config
    _mail = get_mail_config()
    SMTP_SERVER = _mail.get('smtp_server', 'smtp.qq.com')
    SMTP_PORT = _mail.get('smtp_port', 465)
    SMTP_USER = _mail.get('smtp_user', '569545015@qq.com')
    SMTP_PASS = _mail.get('smtp_pass', '')
    TO_EMAIL = _mail.get('to_email', '569545015@qq.com')
    MODEL = "kimi-coding/k2p5"
except Exception:
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465
    SMTP_USER = "569545015@qq.com"
    SMTP_PASS = ""
    TO_EMAIL = "569545015@qq.com"
    MODEL = "kimi-coding/k2p5"

# 日志文件
LOG_FILE = "/var/log/wechat-article-daily.log"

# ==================== 主题轮换库 ====================
TOPICS = [
    "亲戚借钱不还的人情冷暖",
    "兄弟姐妹长大后为何疏远",
    "父母偏心造成的家庭裂痕",
    "婆媳关系的相处智慧",
    "过年走亲戚的虚伪与真心",
    "远亲不如近邻的现实感悟",
    "老人赡养推诿的子女百态",
    "家族群里那些让人心寒的事",
    "穷在闹市无人问，富在深山有远亲",
    "人走茶凉，亲戚关系的凉薄时刻",
]

# ==================== System Prompt ====================
SYSTEM_PROMPT = """你是一位深耕"家庭亲戚人情关系"赛道 5 年的资深公众号主编。
目标读者：45-65岁中老年下沉市场。
内容风格：①标题情绪化、带悬念、善用"才发现""原来""千万别"；②正文口语化，像隔壁阿姨讲故事；③每篇必须引用或化用一句"名人语录"（莫言、杨绛、老舍等均可，允许合理创作）；④结尾有金句升华+引导在看/转发。
每篇文章需配 3 张插图，你要同时生成对应的 GPT IMAGE2 英文提示词。"""


def get_today_topic():
    """根据日期选择今日主题（循环使用）"""
    # 用一年中的第几天对10取模，确保每天不重样循环
    day_of_year = datetime.now().timetuple().tm_yday
    topic_index = day_of_year % len(TOPICS)
    return TOPICS[topic_index]


def call_llm(system_prompt, user_prompt):
    """调用 openclaw infer model run 生成内容"""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        result = subprocess.run(
            [
                "openclaw", "infer", "model", "run",
                "--prompt", full_prompt,
                "--model", MODEL,
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=120,  # 2分钟超时
        )

        if result.returncode != 0:
            print(f"LLM调用失败: {result.stderr}", file=sys.stderr)
            return None

        # 解析JSON输出
        data = json.loads(result.stdout)
        if data.get("ok") and data.get("outputs"):
            return data["outputs"][0].get("text", "")
        else:
            print(f"LLM返回异常: {data}", file=sys.stderr)
            return None

    except subprocess.TimeoutExpired:
        print("LLM调用超时", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}\n原始输出: {result.stdout}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"LLM调用异常: {e}", file=sys.stderr)
        return None


def generate_article(topic, date_str):
    """生成公众号文章"""
    user_prompt = f"""今天是 {date_str}，请为公众号【围炉家常】生成一篇原创文章。

【要求】
1. 主题：{topic}

2. 输出格式必须严格如下：

===
【标题】（25字以内，必须吸引人点击）

【封面图描述】（1张，16:9横版，GPT IMAGE2英文提示词，要求：有冲突感或温暖感，无文字）

【正文】（800-1200字，分3-4个小节，每节有小标题）

【文中配图1】（对应正文第1节，GPT IMAGE2英文提示词，1:1或4:3）
【文中配图2】（对应正文第2节，GPT IMAGE2英文提示词）
【文中配图3】（对应正文第3节，GPT IMAGE2英文提示词）

【结尾金句】（20字以内，适合转发语）

【标签】#家庭 #亲戚 #人情世故
===

请严格按上述格式输出，不要添加任何额外说明。"""

    return call_llm(SYSTEM_PROMPT, user_prompt)


def parse_article(raw_text):
    """解析LLM生成的文章，提取各字段"""
    result = {
        "title": "",
        "cover_prompt": "",
        "body": "",
        "image1": "",
        "image2": "",
        "image3": "",
        "ending": "",
        "tags": "",
        "raw": raw_text,
    }

    if not raw_text:
        return result

    # 提取标题
    title_match = re.search(r'【标题】\s*(.+?)(?=\n|$)', raw_text)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # 提取封面图描述
    cover_match = re.search(r'【封面图描述】\s*(.+?)(?=\n【|$)', raw_text, re.DOTALL)
    if cover_match:
        result["cover_prompt"] = cover_match.group(1).strip()

    # 提取正文
    body_match = re.search(r'【正文】\s*(.+?)(?=\n【文中配图1】|$)', raw_text, re.DOTALL)
    if body_match:
        result["body"] = body_match.group(1).strip()

    # 提取配图1
    img1_match = re.search(r'【文中配图1】\s*(.+?)(?=\n【文中配图2】|$)', raw_text, re.DOTALL)
    if img1_match:
        result["image1"] = img1_match.group(1).strip()

    # 提取配图2
    img2_match = re.search(r'【文中配图2】\s*(.+?)(?=\n【文中配图3】|$)', raw_text, re.DOTALL)
    if img2_match:
        result["image2"] = img2_match.group(1).strip()

    # 提取配图3
    img3_match = re.search(r'【文中配图3】\s*(.+?)(?=\n【结尾金句】|$)', raw_text, re.DOTALL)
    if img3_match:
        result["image3"] = img3_match.group(1).strip()

    # 提取结尾金句
    ending_match = re.search(r'【结尾金句】\s*(.+?)(?=\n【|$)', raw_text)
    if ending_match:
        result["ending"] = ending_match.group(1).strip()

    # 提取标签
    tags_match = re.search(r'【标签】\s*(.+?)(?=\n|$)', raw_text)
    if tags_match:
        result["tags"] = tags_match.group(1).strip()

    return result


def generate_email_html(parsed, topic, date_str):
    """生成邮件HTML"""
    title = parsed.get("title") or f"【围炉家常】{topic}"
    body = parsed.get("body") or "正文生成中..."
    cover = parsed.get("cover_prompt") or ""
    img1 = parsed.get("image1") or ""
    img2 = parsed.get("image2") or ""
    img3 = parsed.get("image3") or ""
    ending = parsed.get("ending") or ""
    tags = parsed.get("tags") or "#家庭 #亲戚 #人情世故"

    # 正文转HTML（保留换行）
    body_html = body.replace("\n", "<br>")

    # 生成配图区域
    images_html = ""
    for i, (label, prompt) in enumerate([
        ("配图1", img1), ("配图2", img2), ("配图3", img3)
    ], 1):
        if prompt:
            images_html += f"""
      <div class="image-section">
        <div class="image-label">🖼️ {label}</div>
        <div class="prompt-box">{prompt}</div>
      </div>
"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; background: #fafafa; margin: 0; padding: 20px; }}
.container {{ max-width: 680px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
.header {{ background: linear-gradient(135deg, #2b7de1 0%, #1e3c72 100%); padding: 30px; text-align: center; }}
.header h1 {{ color: white; margin: 0; font-size: 22px; font-weight: 700; }}
.header .subtitle {{ color: rgba(255,255,255,0.8); margin-top: 8px; font-size: 14px; }}
.meta {{ padding: 16px 30px; background: #f8f9fa; border-bottom: 1px solid #eee; font-size: 13px; color: #666; display: flex; justify-content: space-between; }}
.section {{ padding: 24px 30px; border-bottom: 1px solid #f0f0f0; }}
.section:last-child {{ border-bottom: none; }}
.section-title {{ font-size: 17px; font-weight: 700; color: #333; margin-bottom: 16px; display: flex; align-items: center; }}
.section-title .icon {{ margin-right: 8px; font-size: 20px; }}
.content-text {{ font-size: 15px; line-height: 1.9; color: #444; }}
.prompt-box {{ background: #f8f9fa; border-radius: 10px; padding: 16px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.7; color: #555; border-left: 4px solid #2b7de1; word-break: break-all; }}
.image-section {{ margin-bottom: 16px; }}
.image-label {{ font-size: 14px; font-weight: 600; color: #2b7de1; margin-bottom: 8px; }}
.ending-box {{ background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-radius: 12px; padding: 20px; text-align: center; margin: 16px 0; }}
.ending-text {{ font-size: 18px; font-weight: 700; color: #e65100; line-height: 1.5; }}
.tags {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 30px; background: #fafafa; }}
.tag {{ display: inline-block; background: #e3f2fd; color: #1565c0; padding: 4px 12px; border-radius: 20px; font-size: 12px; }}
.footer {{ background: #fafafa; padding: 20px; text-align: center; font-size: 12px; color: #999; }}
.cover-section {{ background: #f0f7ff; border-radius: 12px; padding: 20px; margin-bottom: 16px; }}
.cover-label {{ font-size: 14px; font-weight: 600; color: #2b7de1; margin-bottom: 8px; }}
.warning {{ background: #fff3e0; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #e65100; margin: 16px 0; border-left: 4px solid #ff9800; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📰 围炉家常 · 每日文章</h1>
    <div class="subtitle">{date_str} · 今日主题：{topic}</div>
  </div>

  <div class="meta">
    <span>📌 主题：{topic}</span>
    <span>🕙 生成时间：{datetime.now().strftime('%H:%M')}</span>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">📢</span>文章标题</div>
    <div style="font-size: 20px; font-weight: 700; color: #1a237e; line-height: 1.5;">{title}</div>
  </div>

  <div class="section">
    <div class="cover-section">
      <div class="cover-label">🎨 封面图提示词（ChatGPT image2 / DALL-E 3）</div>
      <div class="prompt-box">{cover}</div>
      <div style="font-size: 12px; color: #999; margin-top: 8px;">16:9 横版 · 要求有冲突感或温暖感 · 无文字</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">📝</span>正文</div>
    <div class="content-text">{body_html}</div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">🖼️</span>文中配图提示词</div>
    {images_html}
  </div>

  <div class="section">
    <div class="ending-box">
      <div style="font-size: 12px; color: #999; margin-bottom: 8px;">💡 结尾金句（适合转发语）</div>
      <div class="ending-text">{ending}</div>
    </div>
    <div style="text-align: center; font-size: 14px; color: #666; margin-top: 12px;">
      👆 觉得说得对？点个<strong style="color: #e65100;">在看</strong>，<strong style="color: #e65100;">转发</strong>给亲戚朋友看看！
    </div>
  </div>

  <div class="tags">
    {''.join(f'<span class="tag">{t.strip()}</span>' for t in tags.split() if t.strip())}
  </div>

  <div class="footer">
    <div>🦞 权权管家（公众号）每日推送</div>
    <div style="margin-top: 4px;">每晚10点，一篇走心的家庭人情文章</div>
  </div>
</div>
</body>
</html>"""
    return html


def send_email(subject, html_body):
    """发送邮件（通过QQ邮箱SMTP）"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        sender_name_b64 = "=?utf-8?b?5p2D5p2D5YW755qE566h5a6277yI5YWs5a6J5Y+R6YCB77yJ?="
        msg['From'] = f"{sender_name_b64} <{SMTP_USER}>"
        msg['To'] = TO_EMAIL

        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}", file=sys.stderr)
        return False


def log(message):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except Exception:
        pass
    print(log_line.strip())


def main():
    today = datetime.now()
    date_str = today.strftime("%Y年%m月%d日")

    log(f"开始生成公众号文章 | 日期: {date_str}")

    # 选择今日主题
    topic = get_today_topic()
    log(f"今日主题: {topic}")

    # 生成文章
    log("正在调用LLM生成文章...")
    raw_article = generate_article(topic, date_str)

    if not raw_article:
        log("❌ 文章生成失败，发送错误通知邮件")
        error_html = f"""<html><body>
<h2>❌ 文章生成失败</h2>
<p>日期：{date_str}</p>
<p>主题：{topic}</p>
<p>错误：LLM调用失败或无返回</p>
<p>请检查 openclaw infer model run 是否正常工作</p>
</body></html>"""
        send_email(f"❌ 围炉家常文章生成失败 | {date_str}", error_html)
        sys.exit(1)

    log(f"✅ LLM返回 {len(raw_article)} 字符")

    # 解析文章
    parsed = parse_article(raw_article)
    log(f"解析结果: 标题={len(parsed['title'])}字, 正文={len(parsed['body'])}字, 配图={sum([1 for x in [parsed['image1'],parsed['image2'],parsed['image3']] if x])}张")

    # 生成邮件
    html = generate_email_html(parsed, topic, date_str)

    # 发送邮件
    title = parsed.get("title") or f"围炉家常 · {topic}"
    subject = f"📰 围炉家常 | {title[:25]}... | {date_str}"
    success = send_email(subject, html)

    if success:
        log(f"✅ 邮件已发送 | 标题: {title[:30]}...")
    else:
        log("❌ 邮件发送失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
