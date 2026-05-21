# jorge-cron-jobs

> 暴躁小龙虾 🦞 的定时任务全家桶 | 一键部署，换服务器秒级复刻

## 📦 项目结构

```
jorge-cron-jobs/
├── scripts/              # 核心定时任务脚本
│   ├── xiaohongshu-travel-daily.py   # 23:00 小红书旅游攻略
│   ├── wechat-article-daily.py       # 22:00 公众号文章
│   ├── douyin-daily.py               # 22:30 抖音图文
│   ├── bithappy_email_pro.py         # 理财监控
│   ├── site_backup.py                # 全站备份
│   ├── memory_archive.py             # 记忆归档
│   ├── collect_metrics.py            # 性能采集
│   ├── heartbeat_check.py            # 心跳检查
│   ├── failure_prediction.py         # 故障预测
│   ├── health_check.py               # 系统巡检
│   ├── daily_report.py               # 日报生成
│   ├── weekly_report.py              # 周报生成
│   ├── monthly_report.py             # 月报生成
│   ├── push_feishu.py                # 飞书推送
│   ├── skill-backup.sh               # 技能备份
│   └── config_loader.py              # 统一配置加载器
├── config/
│   └── config.yaml.template          # 配置文件模板（需复制并填入密码）
├── crontab.txt                       # 定时任务导出文件
├── setup.sh                          # 一键安装脚本
├── install-crontab.sh                # 安装crontab
└── README.md                         # 本文档
```

## 🚀 快速复刻（新服务器）

### 1. 克隆仓库

```bash
git clone https://github.com/yanghq168/jorge-agency.git
cd jorge-agency/jorge-cron-jobs
```

### 2. 一键安装

```bash
./setup.sh
```

setup.sh 会自动：
- ✅ 检查并安装依赖（python3, pip, pyyaml, openclaw）
- ✅ 创建日志目录
- ✅ 从模板生成 `config/config.yaml`
- ✅ 提示填入 QQ 邮箱授权码
- ✅ 安装所有定时任务
- ✅ 运行测试验证

### 3. 手动填入密码（setup.sh 会提示）

```bash
# 编辑配置文件，填入真实密码
vim config/config.yaml
```

```yaml
mail:
  smtp_server: "smtp.qq.com"
  smtp_port: 465
  smtp_user: "569545015@qq.com"
  smtp_pass: "YOUR_QQ_EMAIL_AUTH_CODE"   # ← 填入QQ邮箱授权码
  to_email: "569545015@qq.com"
```

### 4. 手动安装定时任务（如果 setup.sh 没自动装）

```bash
./install-crontab.sh
```

### 5. 验证

```bash
# 查看定时任务
crontab -l

# 手动测试小红书脚本
cd scripts && python3 xiaohongshu-travel-daily.py

# 查看日志
tail -f /var/log/xiaohongshu-travel.log
```

## ⏰ 定时任务清单

| 时间 | 任务 | 脚本 | 平台 |
|------|------|------|------|
| 0:00 | 理财监控 | bithappy_email_pro.py | 邮件 |
| 3:00 | 技能备份 | skill-backup.sh | 本地 |
| 3:30 | 全站备份 | site_backup.py | 本地 |
| 3:30(周日) | 记忆归档 | memory_archive.py | 本地 |
| 8:50 | AI新闻抓取 | run.sh (ai-news-daily) | 邮件 |
| 9:00 | AI新闻推送 | push_email.py | 邮件 |
| 10:00 | 系统巡检 | health_check.py | 日志 |
| 14:00 | 故障预测 | failure_prediction.py | 日志 |
| 19:00 | 每日个人日报 | daily_report.py + push_feishu.py | 飞书+邮件 |
| 20:00(周日) | 周报推送 | weekly_report.py | 邮件 |
| 20:00(月末) | 月报推送 | monthly_report.py | 邮件 |
| 22:00 | 公众号文章 | wechat-article-daily.py | 邮件 |
| 22:30 | 抖音图文 | douyin-daily.py | 邮件 |
| 23:00 | 小红书旅游 | xiaohongshu-travel-daily.py | 邮件 |
| */30 min | 心跳检查 | heartbeat_check.py | 日志 |
| */4 hour | 性能采集 | collect_metrics.py | 日志 |

## 📋 内容生成任务详情

### 🍠 小红书旅游攻略（23:00）
- **脚本**: `scripts/xiaohongshu-travel-daily.py`
- **内容**: 43个国内景点（30+小众），文艺标题 + 几天几夜行程 + 详细饮食规划
- **输出**: 小红书文案 + 6+话题标签 + DALL-E 3海报提示词
- **发件人**: 权权养的虾（小红书）

### 📰 公众号文章（22:00）
- **脚本**: `scripts/wechat-article-daily.py`
- **内容**: 10个人情关系主题轮换，情绪化标题 + 口语化正文 + 名人语录 + 金句升华
- **输出**: 800-1200字文章 + 封面图提示词 + 3张文中配图提示词
- **发件人**: 权权管家（公众号）

### 🎵 抖音图文（22:30）
- **脚本**: `scripts/douyin-daily.py`
- **内容**: 和公众号同主题，但角度更尖锐、更短、更扎心
- **输出**: 150-250字文案 + 9:16竖版配图提示词 + BGM建议 + 话题标签
- **发件人**: 权权管家（抖音）

## 🔧 依赖要求

```bash
# 基础依赖
python3 >= 3.8
openclaw >= 2026.5.7

# Python包
pip3 install pyyaml

# OpenClaw需配置Kimi模型
openclaw config set auth.profiles.kimi-coding:default.provider kimi-coding
openclaw config set auth.profiles.kimi-coding:default.mode api_key
# 然后运行 openclaw configure 填入API Key
```

## 📁 日志文件

所有日志统一存放在 `/var/log/` 目录：

```
/var/log/
├── xiaohongshu-travel.log
├── wechat-article-daily.log
├── douyin-daily.log
├── bithappy-email.log
├── daily-report.log
├── health-check.log
├── site-backup.log
├── memory-archive.log
├── metrics.log
├── weekly-report.log
├── monthly-report.log
├── heartbeat.log
└── prediction.log
```

## 🔄 换服务器复刻检查清单

```bash
# 1. 克隆项目
git clone https://github.com/yanghq168/jorge-agency.git
cd jorge-agency/jorge-cron-jobs

# 2. 运行安装脚本
./setup.sh

# 3. 填入QQ邮箱授权码到 config/config.yaml
#    （setup.sh会提示）

# 4. 配置OpenClaw
openclaw configure
# 选择 kimi-coding，填入API Key

# 5. 测试
./scripts/xiaohongshu-travel-daily.py
./scripts/wechat-article-daily.py
./scripts/douyin-daily.py

# 6. 确认定时任务
crontab -l
```

## ⚠️ 安全提醒

1. **config/config.yaml 包含邮箱授权码，已加入 .gitignore，请勿提交到git**
2. **QQ邮箱授权码不是登录密码，需在QQ邮箱设置中生成**
3. **OpenClaw的API Key请通过 `openclaw configure` 单独配置**

## 🦞 维护者

暴躁小龙虾 🦞 — jorge 的全栈协作者

---

*最后更新: 2026-05-22*
