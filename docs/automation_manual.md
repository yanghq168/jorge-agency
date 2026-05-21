# 🦞 权权龙虾管家 - 自动化服务手册

> **最后更新**：2026年3月24日  
> **由**：暴躁小龙虾 🦞 生成  
> **服务对象**：jorge

---

## 📧 一、邮件自动化系统

### 1.1 每日邮件时间表

| 时间 | 邮件类型 | 内容说明 |
|------|----------|----------|
| **07:00** | 🌅 晨间新闻简报 | AI + 区块链新闻精选 |
| **19:00** | 🦞 工作日报 | 我的工作记录 + 邮件总结 |
| **20:00** | 📧 邮件日报 | QQ邮箱智能分类摘要 |
| **21:00** | 🌙 晚间新闻晚报 | AI + 区块链新闻精选 |

### 1.2 新闻来源

**AI新闻源：**
- 量子位 (qbitai.com)
- 机器之心 (jiqizhixin.com)
- 36氪 (36kr.com)
- TechCrunch AI

**区块链新闻源：**
- Odaily (odaily.news)
- PANews (panewslab.com)
- CoinDesk
- Cointelegraph

### 1.3 邮件日报分类

- 🔴 **重要/工作邮件** - 需要优先处理
- 💰 **财务/账单** - 银行、支付相关
- 👥 **社交网络** - LinkedIn、GitHub等
- 📰 **订阅/新闻** - Newsletter、RSS
- ⚙️ **系统通知** - 验证码、提醒
- 📢 **推广/广告** - 营销邮件

---

## 📊 二、合约交易监控系统

### 2.1 监控频率

**每2小时自动检查一次**，发送市场数据报告到邮箱

### 2.2 监控内容

| 功能 | 说明 | 数据来源 |
|------|------|----------|
| 📈 **价格预警** | 价格突破/跌破设定阈值 | Binance/CoinGecko |
| 💰 **资金费率** | 异常费率（>0.1%）提醒 | Binance Futures |
| 💥 **爆仓数据** | 大额爆仓记录 | Binance API |
| 📊 **持仓量** | 市场持仓变化 | Binance Futures |

### 2.3 当前价格预警配置

| 币种 | 突破价格 | 跌破价格 | 当前价格 | 状态 |
|------|----------|----------|----------|------|
| ETH | $2,500 | $1,700 | ~$2,140 | 🟢 监控中 |
| SOL | $150 | $80 | ~$90 | 🟢 监控中 |
| BGB | $2.5 | $1.5 | ~$2.03 | 🟢 监控中 |
| BTC | - | - | ~$70,400 | ⚪ 已暂停 |

---

## 🛠️ 三、已安装技能

### 3.1 核心技能

| 技能名称 | 功能描述 | 版本 |
|----------|----------|------|
| **agent-browser** | 无头浏览器自动化，网页截图/点击/表单填写 | 0.2.0 |
| **tavily-search** | AI优化搜索，深度研究、新闻查询 | 1.0.0 |
| **find-skills** | 技能发现和安装助手 | 0.1.0 |
| **skill-vetter** | 技能安全扫描，检测恶意代码和后门 | - |
| **email-daily-summary** | 邮件自动登录和每日摘要生成 | 0.1.0 |

### 3.2 已配置自动化脚本

| 脚本 | 功能 | 位置 |
|------|------|------|
| `daily_report.py` | 工作日报生成 | `/skills/daily-report/` |
| `morning_news.py` | 晨间新闻简报 | `/skills/daily-report/` |
| `evening_news.py` | 晚间新闻晚报 | `/skills/daily-report/` |
| `email_summary.py` | 邮件日报 | `/skills/daily-report/` |
| `crypto_monitor.py` | 合约市场监控 | `/skills/daily-report/` |

---

## ⚙️ 四、配置信息

### 4.1 邮件配置

- **发件人**：权权龙虾管家 🦞
- **邮箱**：569545015@qq.com
- **SMTP服务器**：smtp.qq.com:465 (SSL)
- **IMAP服务器**：imap.qq.com:993 (SSL)

### 4.2 定时任务（Crontab）

```
0  7  * * *  晨间新闻简报
0 19  * * *  工作日报
0 20  * * *  邮件日报
0 21  * * *  晚间新闻晚报
0 */2 * * *  合约市场监控
```

---

## 📝 五、使用指南

### 5.1 修改价格预警

编辑配置文件：
```bash
/root/.openclaw/workspace/skills/daily-report/crypto_alerts.json
```

示例配置：
```json
{
  "price_alerts": [
    {"symbol": "ETHUSDT", "above": 2500, "below": 1700},
    {"symbol": "SOLUSDT", "above": 150, "below": 80},
    {"symbol": "BGBUSDT", "above": 2.5, "below": 1.5}
  ],
  "funding_alerts": true,
  "liquidation_alerts": true
}
```

### 5.2 手动触发邮件

```bash
cd /root/.openclaw/workspace/skills/daily-report

# 工作日报
python3 daily_report.py --send

# 晨间新闻
python3 morning_news.py

# 合约监控
python3 crypto_monitor.py
```

### 5.3 查看日志

```bash
# 工作日报日志
tail -f /var/log/daily-report.log

# 合约监控日志
tail -f /var/log/crypto-monitor.log

# 邮件日报日志
tail -f /var/log/email-summary.log
```

---

## ⚠️ 六、免责声明

> **合约交易风险极高**，本系统仅提供数据监控和提醒服务：
> 
> 1. 不提供任何投资建议
> 2. 不保证盈利
> 3. 请只用亏得起的钱进行交易
> 4. 所有数据仅供参考，交易风险自负

---

## 📞 七、联系与支持

如需调整配置或添加新功能，随时联系：

- **暴躁小龙虾** 🦞
- **发件邮箱**：569545015@qq.com

---

## 📅 八、更新日志

### 2026-03-24
- ✅ 搭建完整邮件自动化系统
- ✅ 添加合约交易监控
- ✅ 配置价格预警（ETH/SOL/BGB）
- ✅ 安装技能：skill-vetter, email-daily-summary

---

*本手册由 权权龙虾管家 自动生成*  
*OpenClaw Daily Report System v1.0*  
*暴躁小龙虾 🦞 为您服务*
