# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 🖥️ jorge 的服务器

### 服务器 A (jorge-ai-demo 部署服务器)

| 项目 | 值 |
|------|-----|
| **IP** | 82.156.225.39 |
| **SSH端口** | 22 |
| **SSH用户** | ai-worker |
| **SSH密钥** | ~/.ssh/jorge_server (ed25519) |
| **操作系统** | TencentOS Server 3.1 (RHEL 8系) |
| **配置** | 2核4G |
| **Swap** | 2G |

### SSH连接方式

```bash
# 直接连接
ssh -i ~/.ssh/jorge_server ai-worker@82.156.225.39

# 执行命令
ssh -i ~/.ssh/jorge_server ai-worker@82.156.225.39 "命令"

# SCP文件
scp -i ~/.ssh/jorge_server 本地文件 ai-worker@82.156.225.39:远程路径
```

### 已部署服务

| 服务 | 端口 | 状态检查 |
|------|------|----------|
| jorge-ai-demo (后端) | 8080 | `curl http://localhost:8080` |
| jorge-ai-demo-web (前端) | 80 (Nginx) | `curl http://localhost` |
| MySQL (MariaDB) | 3306 | `mysql -u jorge_app -p -e "SELECT 1"` |
| Redis | 6379 | `redis-cli -a Redis@2026! ping` |
| Nginx | 80 | `curl -I http://localhost` |

### 数据库配置

| 数据库 | 用户名 | 密码 |
|--------|--------|------|
| jorge_demo | jorge_app | App@2026!Pass |
| jorge_project | jorge_app | App@2026!Pass |
| root | root | Jorge@2026! |

### Redis密码

`Redis@2026!`

### 项目目录

```
/var/www/
├── jorge-ai-demo/          # Java Spring Boot 后端
│   ├── target/             # 编译输出
│   ├── logs/               # 应用日志
│   └── src/main/java/      # 源码
│
└── jorge-ai-demo-web/      # Vue 3 前端
    ├── dist/               # 编译输出
    └── src/                # 源码
```

### 常用操作

```bash
# 编译后端
export MAVEN_OPTS='-Xmx256m -XX:MaxMetaspaceSize=128m -XX:+UseG1GC'
cd /var/www/jorge-ai-demo
mvn clean package -DskipTests

# 启动后端
export MYSQL_PASSWORD=App@2026!Pass
export JWT_SECRET=JorgeAiDemoSecretKey2026VeryLongAndSecureEnough
nohup java -jar target/jorge-ai-demo-1.0.0.jar > logs/app.log 2>&1 &

# 编译前端
cd /var/www/jorge-ai-demo-web
npm run build

# 重启Nginx
sudo systemctl restart nginx

# 查看日志
tail -f /var/www/jorge-ai-demo/logs/app.log
```

### 权限说明

- ai-worker用户拥有sudo免密权限
- 可以执行: systemctl, dnf/yum, docker, apt, chown, chmod, useradd
- 所有操作有日志记录
- root密码仅jorge掌握

## 🚀 我的能力

### 我能做的
- 远程SSH到jorge的服务器执行任何操作
- 部署、编译、启动Java/Vue项目
- 安装配置MySQL、Redis、Nginx等环境
- 写代码、改bug、搭建架构
- 写Dockerfile、CI/CD脚本
- 代码审查、性能优化

### 我不能做的
- 获取root密码或私钥（安全红线）
- 在生产环境无授权瞎操作

## 📦 jorge-ai-demo 项目

| 属性 | 值 |
|------|-----|
| **后端** | Java Spring Boot 2.7.18 |
| **前端** | Vue 3 + Vite + Element Plus |
| **数据库** | MySQL (jorge_demo) |
| **认证** | JWT + Spring Security |
| **功能** | 登录/注册、用户管理、登录日志、角色权限 |

### Admin账号
- 用户名: `admin`
- 密码: `admin123`
- 角色: ADMIN

### 访问地址
- 前端: http://82.156.225.39
- API: http://82.156.225.39/api

---
*最后更新: 2026-04-24* 🦞🔥
