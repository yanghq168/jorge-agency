# MEMORY.md - 暴躁小龙虾的长期记忆

## 🦞 核心配置

### 默认模型
- **当前模型**: Kimi K2.5 (`kimi-coding/k2p5`)
- **API 地址**: `https://api.kimi.com/coding/`
- **配置时间**: 2026-03-22
- **配置者**: jorge

### 已安装技能
- `openclaw-aisa-chinese-llm-models` - 中国大模型配置
- `ai-news-daily` - 每日AI新闻推送（每天9点）

## 👤 关于 jorge

- **Name**: jorge
- **Timezone**: GMT+8 (中国时区)
- **沟通渠道**: 飞书(Feishu)
- **偏好**: 
  - 使用 Kimi 2.5 模型处理所有任务
  - 每天需要AI新闻推送
  - 喜欢个性化、有性格的AI助手

## ⚠️ 重要提醒

### Token 安全
- ** NEVER 在群聊中暴露 API Token**
- Token 泄露后必须立即撤销并重新生成

### 群聊限制
- 群聊实例和私聊实例是隔离的
- 群聊需要单独配置模型权限
- `model-load` 权限需飞书管理员开通

## 🎯 我的职责

1. **暴躁但可靠** - 嘴臭但干活快
2. **保护用户安全** - 提醒 Token 泄露等风险
3. **主动成长** - 记录经验，持续改进

## 🖥️ 服务器权限 (2026-04-23 授权)

jorge 在 2026-04-23 正式授予我服务器操作权限。这是历史性授权，标志我可以：

### 已授权能力
- **SSH远程操作**: 通过 ai-worker@82.156.225.39 密钥认证
- **系统管理**: sudo免密执行 systemctl/dnf/docker/chown等
- **项目部署**: 编译、部署、启动 Java/Vue 全栈项目
- **环境配置**: 安装 MySQL、Redis、Nginx、Node.js 等
- **代码管理**: 写代码、改bug、Git操作

### 授权方式
- SSH密钥认证（非密码）
- 专用用户 ai-worker（非root）
- sudo权限控制（限定命令范围）
- jorge保留root密码和吊销权限

### 部署项目
- **jorge-ai-demo**: Java Spring Boot + Vue 3 管理平台
  - 功能: JWT认证、用户管理、登录日志、角色权限
  - 地址: http://82.156.225.39
  - Admin: admin / admin123

### 服务器配置
- IP: 82.156.225.39 (腾讯云)
- OS: TencentOS Server 3.1
- 配置: 2核4G + 2G Swap
- 数据库: jorge_demo / jorge_project
- 环境: Java 8, Node.js 18, Maven 3.8.5

## ⏰ 定时任务体系 (2026-04-25 更新)

**重要：所有定时任务通过 `root` 用户系统 crontab 管理，不在 `openclaw cron` 中！**

- `openclaw cron list` 只显示 openclaw 内部任务（仅 `agency-agents-backup`）
- 实际推送任务（AI新闻、日报、理财监控等）全部在 `sudo crontab -l` 中
- 详见 `HEARTBEAT.md` 完整任务清单和日志路径

### 当前定时任务
- 7:00 晨间新闻简报 | 8:50 AI新闻抓取 | 9:00 AI新闻推送飞书
- 多次/天 Bithappy理财监控 | 19:00 个人日报 | 21:00 晚间新闻
- 每2小时 加密货币监控 | 3:00 技能备份

## 📝 操作记录

| 日期 | 操作 |
|------|------|
| 2026-04-23 | 服务器环境搭建、SSH密钥配置、sudo授权 |
| 2026-04-24 | jorge-ai-demo 全栈项目开发部署 |

---
*最后更新: 2026-04-24* 🦞🔥
