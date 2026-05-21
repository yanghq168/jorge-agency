# 项目环境配置文档

## 🖥️ 服务器信息

| 项目 | 值 |
|------|-----|
| IP | 82.156.225.39 |
| SSH端口 | 22 |
| 操作系统 | TencentOS Server 3.1 (RHEL 8) |
| 内存 | 4G (可用3.1G) |
| 磁盘 | 50G (已用5.2G, 可用42G) |
| Swap | 2G |

## 🔐 数据库配置

### MySQL (MariaDB 10.3)
- **root密码**: `Jorge@2026!`
- **应用用户**: `jorge_app`
- **应用密码**: `App@2026!Pass`
- **数据库名**: `jorge_project`
- **字符集**: utf8mb4

### Redis 5.0
- **密码**: `Redis@2026!`
- **监听**: 127.0.0.1:6379

## 🛠️ 已安装环境

| 软件 | 版本 | 用途 |
|------|------|------|
| Node.js | 18.20.8 | 前端/后端运行时 |
| NPM | 10.8.2 | 包管理 |
| Python | 3.6.8 | 脚本/后端 |
| MariaDB | 10.3.39 | 数据库 |
| Redis | 5.0.3 | 缓存/会话 |
| Nginx | 1.14.1 | Web服务器/反向代理 |
| Git | 2.43.5 | 版本控制 |

## 📁 项目目录

```
/var/www/jorge-project/
├── backend/    # 后端代码
├── frontend/   # 前端代码
└── logs/       # 日志目录
```

## 🚀 服务状态

| 服务 | 状态 | 命令 |
|------|------|------|
| MariaDB | ✅ 运行中 | `sudo systemctl start/stop/restart mariadb` |
| Redis | ✅ 运行中 | `sudo systemctl start/stop/restart redis` |
| Nginx | ✅ 运行中 | `sudo systemctl start/stop/restart nginx` |

## 📝 快速测试

```bash
# 测试MySQL
mysql -u jorge_app -pApp@2026!Pass -e "SELECT 1;" jorge_project

# 测试Redis
redis-cli -a Redis@2026! ping

# 测试Nginx
curl http://localhost
```

## ⚠️ 安全提醒

- root密码只有你掌握
- ai-worker用户通过SSH密钥认证
- 所有数据库已设置密码
- 建议定期更新系统和软件

---
*配置完成时间: 2026-04-23*
