#!/bin/bash
# 批量抓取8个B站视频信息并生成Markdown文档

VIDEOS=(
    "BV1KVsHznEyU|TikTok跨境电商从0-1入门教程"
    "BV1XcEtzcEii|亚马逊跨境电商从0-1"
    "BV1RYqHYnEw8|虾皮Shopee跨境电商从0-1"
    "BV1YzpgeiE1X|外贸副业从0-1"
    "BV1Xq4y1L7Ry|打破内卷·8个低门槛副业"
    "BV1vV411j7QE|打工人剥削老板指南"
    "BV1sV411q7Q8|史上最骚微商指南"
    "BV1Py4y1s7wK|如何3秒钟看出一个人的实力"
)

for video in "${VIDEOS[@]}"; do
    IFS='|' read -r bvid title <<< "$video"
    echo "Fetching $bvid..."
    
    curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$bvid" > "/tmp/$bvid.json"
    
    python3 << EOF
import json

with open("/tmp/$bvid.json") as f:
    data = json.load(f)

if data.get('code') == 0:
    v = data['data']
    duration_min = v['duration'] // 60
    duration_sec = v['duration'] % 60
    
    desc = v.get('desc', '') or '暂无简介'
    tags = [t['tag_name'] for t in v.get('tags', [])[:15]]
    tags_str = ', '.join(tags) if tags else '暂无标签'
    
    content = f"""# {v['title']}

> **视频来源**: [Bilibili - 统一的奸商之路](https://www.bilibili.com/video/{v['bvid']})
> **UP主**: 统一的奸商之路（150万关注）
> **发布时间**: {v.get('pubdate', '未知')}
> **视频时长**: {duration_min}分{duration_sec}秒
> **播放量**: {v['stat']['view']:,} | **弹幕**: {v['stat']['danmaku']:,} | **点赞**: {v['stat']['like']:,}
> **硬币**: {v['stat']['coin']:,} | **收藏**: {v['stat']['favorite']:,} | **分享**: {v['stat']['share']:,}

---

## 📌 视频简介

{desc}

---

## 🏷️ 相关标签

{tags_str}

---

## 📝 内容大纲（待补充）

### 第一部分：[待补充]
- [ ] 要点1
- [ ] 要点2
- [ ] 要点3

### 第二部分：[待补充]
- [ ] 要点1
- [ ] 要点2
- [ ] 要点3

### 第三部分：[待补充]
- [ ] 要点1
- [ ] 要点2
- [ ] 要点3

---

## 💡 核心知识点（待补充）

> 观看视频后在此记录关键知识点...

---

## 🔗 相关资源（待补充）

> 记录视频中提到的工具、网站、联系方式等...

---

## 🎯 行动清单（待补充）

- [ ] 行动项1
- [ ] 行动项2
- [ ] 行动项3

---

*本文档由AI自动整理创建 | 框架生成时间: $(date +%Y-%m-%d)*
*⚠️ 视频具体内容需结合实际观看后补充*
"""
    
    filename = f"{v['bvid']}-{title}.md"
    with open(f"/root/.openclaw/workspace/tiktok-docs/{filename}", "w") as f:
        f.write(content)
    print(f"Created: {filename}")
else:
    print(f"Error fetching {v['bvid']}: {data.get('message', 'Unknown error')}")
EOF

done

echo "All done! Files created in /root/.openclaw/workspace/tiktok-docs/"
ls -la /root/.openclaw/workspace/tiktok-docs/
