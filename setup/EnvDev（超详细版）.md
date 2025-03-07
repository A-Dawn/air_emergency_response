---

### **《民航应急响应系统》Ubuntu 22.04 超详细部署文档**

---

#### **一、服务器环境初始化**  
**1. 操作系统验证**  
```bash
# 1.1 确认系统版本
lsb_release -a
# 预期输出：
# No LSB modules are available.
# Distributor ID: Ubuntu
# Description:    Ubuntu 22.04.3 LTS
# Release:        22.04
# Codename:       jammy

# 1.2 更新系统（耗时约5-10分钟）
sudo apt update && sudo apt upgrade -y && sudo reboot
```

**2. 创建部署专用用户（非root操作，提高安全性）**  
```bash
# 2.1 创建用户
sudo adduser deployer  # 按提示设置密码
sudo usermod -aG sudo deployer  # 赋予sudo权限

# 2.2 切换到deployer用户（后续操作均在此用户下执行）
su - deployer
```

---

#### **二、依赖安装（逐行执行）**  
**1. 安装基础工具**  
```bash
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    tree \
    htop \
    ufw
```

**2. 安装Python环境**  
```bash
# Ubuntu 22.04 默认Python版本为3.10
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev
```

**3. 安装MySQL数据库**  
```bash
# 3.1 安装MySQL
sudo apt install -y mysql-server

# 3.2 启动并验证
sudo systemctl start mysql
sudo systemctl status mysql  # 应显示 active (running)

# 3.3 安全初始化（交互式操作）
sudo mysql_secure_installation
# 按提示操作：
# 1. 设置root密码（建议复杂密码如：Air@Emergency2024!）
# 2. 移除匿名用户？ → Y
# 3. 禁止远程root登录？ → Y
# 4. 移除测试数据库？ → Y
# 5. 刷新权限表？ → Y
```

**4. 安装Nginx**  
```bash
sudo apt install -y nginx
sudo systemctl start nginx
```

---

#### **三、项目部署（精确到文件路径）**  
**1. 创建项目目录**  
```bash
sudo mkdir -p /www/wwwroot
sudo chown -R deployer:deployer /www/wwwroot  # 关键权限设置！
cd /www/wwwroot
```

**2. 克隆代码仓库**  
```bash
# 假设仓库地址为 git@github.com:yourname/air_emergency_response.git
git clone git@github.com:yourname/air_emergency_response.git
cd air_emergency_response

# 验证目录结构
tree -L 1
# 应显示：
# .
# ├── app.py
# ├── config.py
# ├── models
# ├── routes
# ├── utils
# └── requirements.txt
```

**3. 配置Python虚拟环境**  
```bash
# 3.1 创建虚拟环境（必须位于项目根目录）
python3 -m venv venv

# 3.2 激活环境
source venv/bin/activate  # 激活后提示符变为 (venv)

# 3.3 验证Python路径
which python  # 应显示：/www/wwwroot/air_emergency_response/venv/bin/python
```

**4. 安装Python依赖**  
```bash
# 4.1 升级pip
pip install --upgrade pip

# 4.2 安装依赖（耗时约2-5分钟）
pip install -r requirements.txt

# 4.3 验证关键库版本
pip list | grep -E "flask|gmssl"
# 预期输出：
# Flask           2.0.3
# gmssl           3.2.2
```

---

#### **四、数据库配置（详细SQL操作）**  
**1. 创建专用数据库用户**  
```bash
# 登录MySQL（使用之前设置的root密码）
sudo mysql -u root -p

-- 执行SQL命令
CREATE DATABASE air_emergency 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

CREATE USER 'air_db_user'@'localhost' 
    IDENTIFIED BY '--------------';

GRANT ALL PRIVILEGES ON air_emergency.* 
    TO 'air_db_user'@'localhost';

FLUSH PRIVILEGES;
EXIT;
```

**2. 验证数据库连接**  
```bash
mysql -u air_db_user -p air_emergency
# 输入密码后应进入MySQL命令行
mysql> SHOW TABLES;  # 此时应无表
mysql> EXIT;
```

---

#### **五、环境变量与配置文件**  
**1. 创建.env文件（敏感信息保护）**  
##### 注意！.env已经被废除使用！
```bash
nano /www/wwwroot/air_emergency_response/.env
```
内容如下（按实际修改）：  
```ini
# ==== 数据库配置 ====
DATABASE_URL=mysql+pymysql://air_db_user:---------!@localhost/air_emergency

# ==== JWT配置 ====
JWT_SECRET_KEY=YourSuperSecretKey_32BytesLong!

# ==== SM2私钥 ====
SM2_PRIVATE_KEY=308193020100301...  # 完整HEX格式私钥

# ==== 业务参数 ====
MAX_FAILED_ATTEMPTS=5
BAN_DURATION=300
```

**2. 设置文件权限**  
```bash
chmod 600 .env  # 仅允许所有者读写
```

---

#### **六、服务部署与启动**  
**1. 初始化数据库表**  
```bash
flask shell
>>> from app import db
>>> db.create_all()  # 创建所有表
>>> exit()

# 验证表是否生成
mysql -u air_db_user -p air_emergency -e "SHOW TABLES;"
# 应显示 users, incidents 等表
```

**2. 配置Systemd服务（生产环境必须）**  
```bash
sudo nano /etc/systemd/system/air_emergency.service
```
内容如下：  
```ini
[Unit]
Description=民航应急响应系统后端服务
After=network.target

[Service]
User=deployer
Group=deployer
WorkingDirectory=/www/wwwroot/air_emergency_response
# 移除 EnvironmentFile 行
# EnvironmentFile=/www/wwwroot/air_emergency_response/.env

# 添加 Environment 行，设置所有环境变量
Environment="DATABASE_URL=mysql+pymysql://air_db_user:XXXXXXXXX!@localhost/air_emergency"
Environment="JWT_SECRET_KEY=XXXXXXXXXXXXX"
Environment="SM2_PRIVATE_KEY=XXXXXXXXXXXXXXXXXXXX"
Environment="SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXX"
Environment="MAIL_SERVER=XXXXXXXXXXXXX"
Environment="MAIL_PORT=25"
Environment="MAIL_USE_TLS=true"
Environment="MAIL_USE_SSL=false"
Environment="MAIL_USERNAME=XXXXXXXXXXXXXXXX"
Environment="MAIL_PASSWORD=XXXXXXXXXXXX"
Environment="MAIL_DEFAULT_SENDER=XXXXXXXXXXXXXXXXXXX"
Environment="MAX_FAILED_ATTEMPTS=5"
Environment="BAN_DURATION=300"

ExecStart=/www/wwwroot/air_emergency_response/venv/bin/gunicorn \
    -w 4 \
    -b 0.0.0.0:5000 \
    --timeout 120 \
    app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**3. 启动服务**  
```bash
sudo systemctl daemon-reload
sudo systemctl start air_emergency
sudo systemctl enable air_emergency

# 检查状态（必须显示 active (running)）
sudo systemctl status air_emergency
```

---

#### **七、Nginx反向代理配置（含HTTPS）**  
**1. 生成SSL证书（以Let's Encrypt为例）**  
```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请证书（替换your-domain.com）
sudo certbot --nginx -d your-domain.com

# 证书路径示例：
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

**2. 配置Nginx**  
```bash
sudo nano /etc/nginx/sites-available/air_emergency
```
内容如下：  
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 安全增强配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件配置（如果有）
    location /static {
        alias /www/wwwroot/air_emergency_response/static;
        expires 30d;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;  # HTTP强制跳转HTTPS
}
```

**3. 启用配置**  
```bash
sudo ln -s /etc/nginx/sites-available/air_emergency /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

---

#### **八、防火墙与安全加固**  
**1. 配置UFW防火墙**  
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable            # 启用防火墙

# 验证规则
sudo ufw status
# 应显示：
# Status: active
# 22/tcp ALLOW Anywhere
# 80/tcp ALLOW Anywhere
# 443/tcp ALLOW Anywhere
```

**2. 定期安全更新**  
```bash
# 配置自动安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades  # 选择"Yes"
```

---

#### **九、验证部署**  
**1. 接口测试（使用curl）**  
```bash
# 测试根接口
curl -k https://your-domain.com
# 预期返回：{"message":"欢迎使用应急响应平台!"}

# 测试登录接口（示例）
curl -X POST https://your-domain.com/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test_admin"}'
# 预期返回包含加密Token
```

**2. 日志监控**  
```bash
# 实时查看服务日志
sudo journalctl -u air_emergency -f

# 查看Nginx访问日志
sudo tail -f /var/log/nginx/access.log
```

---

#### **十、维护与监控**  
**1. 服务管理命令**  
| 操作                 | 命令                                      |
|----------------------|-------------------------------------------|
| 启动服务             | `sudo systemctl start air_emergency`      |
| 停止服务             | `sudo systemctl stop air_emergency`       |
| 重启服务             | `sudo systemctl restart air_emergency`    |
| 查看状态             | `sudo systemctl status air_emergency`     |

**2. 备份策略**  
```bash
# 每日数据库备份（配置cron）
0 3 * * * mysqldump -u air_db_user -p'XXXXXXXXXXXXXX' air_emergency > /backup/db_$(date +\%F).sql

# 代码备份（每周日2点）
0 2 * * 7 tar -czvf /backup/code_$(date +\%F).tar.gz /www/wwwroot/air_emergency_response
```

---

#### **十一、故障排查手册**  
**问题1：数据库连接失败**  
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 验证用户权限
mysql -u air_db_user -p
SHOW GRANTS;  # 应显示对air_emergency数据库的权限

# 检查.env文件中的连接字符串
cat /www/wwwroot/air_emergency_response/.env | grep DATABASE_URL
```

**问题2：502 Bad Gateway**  
```bash
# 检查Gunicorn是否运行
ps aux | grep gunicorn

# 检查端口占用
sudo lsof -i :5000

# 查看错误日志
sudo journalctl -u air_emergency --since "10 minutes ago"
```

**问题3：SM2解密失败**  
```bash
# 验证私钥格式
cat /www/wwwroot/air_emergency_response/.env | grep SM2_PRIVATE_KEY
# 应为完整HEX字符串，如以3081开头

# 测试密钥对
python3 -c "from gmssl import sm2; sm2_crypt = sm2.CryptSM2(private_key='$(echo $SM2_PRIVATE_KEY)'); print('密钥验证通过')"
```

---

### **部署架构图**  
```plaintext
                   +---------------------+
                   |   Nginx (443/80)    |
                   +---------------------+
                          ↓ 反向代理
                   +---------------------+
                   | Gunicorn (127.0.0.1:5000) |
                   +---------------------+
                          ↓ Flask
                   +---------------------+
                   |   MySQL Database    |
                   +---------------------+
``` 

按此文档逐步操作，可确保系统在 **30分钟内完成部署**。若遇到问题，优先检查：  
1. 所有路径是否精确匹配  
2. 用户权限是否正确（特别是`/www/wwwroot`目录）  
3. 环境变量是否生效  
4. 服务日志中的错误提示