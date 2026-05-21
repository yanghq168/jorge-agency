#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音图文【围炉家常】每日内容生成器
每晚22:30运行，生成抖音图文（和公众号同主题，但更尖锐、更短、更扎心）
通过 openclaw infer model run 调用 Kimi 生成内容
发送邮件至 569545015@qq.com
发件人：权权管家（抖音）
"""

import json
import random
import re
import smtplib
import ssl
import subprocess
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==================== 配置 ====================
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "569545015@qq.com"
SMTP_PASS = "iylylmwnitbbbebi"
TO_EMAIL = "569545015@qq.com"
MODEL = "kimi-coding/k2p5"

LOG_FILE = "/var/log/douyin-daily.log"

# ==================== 主题轮换库（和公众号一致）====================
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
SYSTEM_PROMPT = """你是一位专做"家庭人情关系"图文抖音的文案高手。
目标受众：45岁以上下沉市场用户。
风格要求：①文案极度口语化，像拉家常；②前3句必须抓人，要么扎心要么共鸣；③总字数控制在150-250字，适合手机一屏读完；④配图要"有故事感"，像老照片或生活抓拍。"""


def get_today_topic():
    """根据日期选择今日主题（和公众号脚本一致）"""
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
            timeout=120,
        )

        if result.returncode != 0:
            print(f"LLM调用失败: {result.stderr}", file=sys.stderr)
            return None

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


def generate_douyin_content(topic, date_str):
    """生成抖音图文内容"""
    user_prompt = f"""今天是 {date_str}，请为抖音号【围炉家常】生成一条图文内容。

【要求】
1. 主题与当天公众号文章主题一致，但角度更尖锐、更短、更扎心。
2. 主题方向：{topic}
3. 输出格式必须严格如下：

===
【抖音文案】（150-250字，口语化，前3句必须有钩子，如"你有没有发现...""说实话...""人这辈子最寒心的，不是外人..."）

【配图描述】（1张，9:16竖版，GPT IMAGE2英文提示词，要求：生活场景、情绪饱满、像真实抓拍、无文字无水印，适合抖音图文轮播首图）

【BGM建议】（给出1个抖音热门BGM风格，如"伤感钢琴+雨声""老歌《常回家看看》片段"）

【话题标签】#亲戚关系 #家庭情感 #人到中年 #人间真实
===

请严格按上述格式输出，不要添加任何额外说明。"""

    return call_llm(SYSTEM_PROMPT, user_prompt)


def parse_content(raw_text):
    """解析LLM生成的内容"""
    result = {
        "caption": "",
        "image_prompt": "",
        "bgm": "",
        "tags": "",
        "raw": raw_text,
    }

    if not raw_text:
        return result

    caption_match = re.search(r'【抖音文案】\s*(.+?)(?=\n【|$)', raw_text, re.DOTALL)
    if caption_match:
        result["caption"] = caption_match.group(1).strip()

    image_match = re.search(r'【配图描述】\s*(.+?)(?=\n【|$)', raw_text, re.DOTALL)
    if image_match:
        result["image_prompt"] = image_match.group(1).strip()

    bgm_match = re.search(r'【BGM建议】\s*(.+?)(?=\n【|$)', raw_text)
    if bgm_match:
        result["bgm"] = bgm_match.group(1).strip()

    tags_match = re.search(r'【话题标签】\s*(.+?)(?=\n|$)', raw_text)
    if tags_match:
        result["tags"] = tags_match.group(1).strip()

    return result


def generate_email_html(parsed, topic, date_str):
    """生成邮件HTML"""
    caption = parsed.get("caption") or "文案生成中..."
    image_prompt = parsed.get("image_prompt") or ""
    bgm = parsed.get("bgm") or ""
    tags = parsed.get("tags") or "#亲戚关系 #家庭情感 #人到中年 #人间真实"

    # 文案换行处理
    caption_html = caption.replace("\n", "<br>")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; background: #fafafa; margin: 0; padding: 20px; }}
.container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; }}
.header h1 {{ color: white; margin: 0; font-size: 22px; font-weight: 700; }}
.header .subtitle {{ color: rgba(255,255,255,0.7); margin-top: 8px; font-size: 14px; }}
.meta {{ padding: 16px 30px; background: #f8f9fa; border-bottom: 1px solid #eee; font-size: 13px; color: #666; display: flex; justify-content: space-between; }}
.section {{ padding: 24px 30px; border-bottom: 1px solid #f0f0f0; }}
.section:last-child {{ border-bottom: none; }}
.section-title {{ font-size: 17px; font-weight: 700; color: #333; margin-bottom: 16px; display: flex; align-items: center; }}
.section-title .icon {{ margin-right: 8px; font-size: 20px; }}
.caption-box {{ background: #f0f0f0; border-radius: 12px; padding: 20px; font-size: 15px; line-height: 1.8; color: #222; }}
.prompt-box {{ background: #f8f9fa; border-radius: 10px; padding: 16px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.7; color: #555; border-left: 4px solid #ff0050; word-break: break-all; }}
.bgm-box {{ background: #fff3e0; border-radius: 10px; padding: 16px; font-size: 14px; color: #e65100; border-left: 4px solid #ff9800; }}
.tags {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 16px 30px; background: #fafafa; }}
.tag {{ display: inline-block; background: #ff0050; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
.footer {{ background: #fafafa; padding: 20px; text-align: center; font-size: 12px; color: #999; }}
.stats {{ display: flex; gap: 16px; padding: 16px 30px; background: #fafafa; font-size: 13px; color: #666; justify-content: space-around; text-align: center; }}
.stats .stat {{ flex: 1; }}
.stats .stat-num {{ font-size: 20px; font-weight: 700; color: #ff0050; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🎵 围炉家常 · 抖音图文</h1>
    <div class="subtitle">{date_str} · 今日主题：{topic}</div>
  </div>

  <div class="meta">
    <span>📌 主题：{topic}</span>
    <span>🕥 生成时间：{datetime.now().strftime('%H:%M')}</span>
  </div>

  <div class="stats">
    <div class="stat"><div class="stat-num">{len(caption)}</div><div>文案字数</div></div>
    <div class="stat"><div class="stat-num">1</div><div>配图</div></div>
    <div class="stat"><div class="stat-num">9:16</div><div>竖版</div></div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">📝</span>抖音文案</div>
    <div class="caption-box">
      {caption_html}
    </div>
    <div style="font-size: 12px; color: #999; margin-top: 10px;">
      💡 提示：前3句必须有钩子，适合手机一屏读完
    </div>
  </div>

  <div class="section">
    <div class="cover-section">
      <div style="font-size: 14px; font-weight: 600; color: #ff0050; margin-bottom: 8px;">🎨 配图提示词（ChatGPT image2 / DALL-E 3）</div>
      <div style="font-size: 12px; color: #999; margin-bottom: 8px;">9:16 竖版 · 生活场景 · 情绪饱满 · 无文字无水印</div>
      <div class="prompt-box">{image_prompt}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">🎵</span>BGM建议</div>
    <div class="bgm-box">{bgm}</div>
  </div>

  <div class="tags">
    {''.join(f'<span class="tag">{t.strip()}</span>' for t in tags.split() if t.strip())}
  </div>

  <div class="footer">
    <div>🦞 权权管家（抖音）每日推送</div>
    <div style="margin-top: 4px;">每晚10点半，一条扎心的家庭人情图文</div>
  </div>
</div>
</body>
</html>"""
    return html


def send_email(subject, html_body):
    """发送邮件"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        sender_name_b64 = "=?utf-8?b?5p2D5p2D5YW755qE566h5a6277yI6ZuF6Jm277yJ?="
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

    log(f"开始生成抖音图文 | 日期: {date_str}")

    # 选择和公众号一致的主题
    topic = get_today_topic()
    log(f"今日主题: {topic}")

    # 生成内容
    log("正在调用LLM生成抖音图文...")
    raw_content = generate_douyin_content(topic, date_str)

    if not raw_content:
        log("❌ 内容生成失败，发送错误通知邮件")
        error_html = f"""<html><body>
<h2>❌ 抖音图文生成失败</h2>
<p>日期：{date_str}</p>
<p>主题：{topic}</p>
<p>错误：LLM调用失败或无返回</p>
<p>请检查 openclaw infer model run 是否正常工作</p>
</body></html>"""
        send_email(f"❌ 围炉家常抖音图文生成失败 | {date_str}", error_html)
        sys.exit(1)

    log(f"✅ LLM返回 {len(raw_content)} 字符")

    # 解析内容
    parsed = parse_content(raw_content)
    log(f"解析结果: 文案={len(parsed['caption'])}字, 配图={'✅' if parsed['image_prompt'] else '❌'}, BGM={'✅' if parsed['bgm'] else '❌'}")

    # 检查文案字数
    caption_len = len(parsed.get("caption", ""))
    if caption_len < 100 or caption_len > 350:
        log(f"⚠️ 文案字数异常: {caption_len}字 (期望150-250字)")

    # 生成邮件
    html = generate_email_html(parsed, topic, date_str)

    # 发送邮件
    subject = f"🎵 围炉家常抖音 | {topic} | {date_str}"
    success = send_email(subject, html)

    if success:
        log(f"✅ 邮件已发送 | 主题: {topic}")
    else:
        log("❌ 邮件发送失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
