# HEARTBEAT.md - 定期检查任务

## ⚠️ 重要：定时任务存储位置

**所有定时任务通过 `root` 用户系统 crontab 管理，不在 `openclaw cron` 中！**

运行 `openclaw cron list` 只会显示 openclaw 内部任务（目前只有 `agency-agents-backup`），**不会显示系统 crontab 里的任务**。

查看系统定时任务的正确命令：
```bash
sudo crontab -l
```

## 当前定时任务清单

| 时间 | 任务 | 脚本路径 |
|------|------|----------|
| 7:00 | 晨间新闻简报 (AI+区块链) | `daily-report/morning_news.py` |
| 8:50 | AI新闻抓取 | `ai-news-daily/run.sh` |
| 9:00 | AI新闻推送到飞书 | `ai-news-daily/push_feishu.py` |
| 0,9,12,15,18,21 点 | Bithappy理财监控 | `scripts/bithappy_email_pro.py` |
| 19:00 | 每日个人日报邮件 | `daily-report/daily_report.py` |
| 21:00 | 晚间新闻晚报 (AI+区块链) | `daily-report/evening_news.py` |
| 每2小时 | 加密货币监控 | `daily-report/crypto_monitor.py` |
| 每天3:00 | 技能备份 | `scripts/skill-backup.sh` |

## 每两天检查项

- [ ] **检查定时任务状态** - 运行 `sudo crontab -l` 确认所有任务存在
- [ ] **检查任务运行状态** - 查看日志文件确认 Last Run 正常：
  - `/var/log/ai-news.log`
  - `/var/log/daily-report.log`
  - `/var/log/bithappy-email.log`
  - `/var/log/morning-news.log`
  - `/var/log/evening-news.log`
  - `/var/log/crypto-monitor.log`
- [ ] **检查 AI 新闻抓取状态** - 查看 `skills/ai-news-daily/data/fetch.log`
- [ ] **有问题主动报告** - 如果发现 error 或长时间未运行，立即通知 jorge

---
*上次检查: 2026-04-25*
