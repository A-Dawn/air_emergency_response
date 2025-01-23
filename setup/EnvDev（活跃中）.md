---

### **《民航应急响应系统》Ubuntu 22.04 专属部署指南（详细版）**

---

#### **一、服务器环境准备**
**1. 操作系统确认**  
```bash
# 确认系统版本
cat /etc/os-release | grep "PRETTY_NAME"
# 预期输出：PRETTY_NAME="Ubuntu 22.04.3 LTS"
```

**2. 更新系统**  
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot  # 更新后重启
```

---

#### **二、依赖安装（逐步操作）**
**1. 安装基础工具**  
```bash
sudo apt install -y git curl wget unzip
```

**2. 安装Python环境**  
```bash
# Ubuntu 22.04 默认自带Python 3.10
sudo apt install -y python3-pip python3-venv
```

**3. 安装MySQL数据库**  
```bash
sudo apt install -y mysql-server

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 检查MySQL状态（确保显示“active (running)”）
sudo systemctl status mysql
```

**4. 安装Nginx（生产环境必需）**  
```bash
sudo apt install -y nginx
```

---

#### **三、项目部署（逐行操作）**
**1. 克隆代码（假设代码仓库为GitHub）**  
```bash
# 创建项目目录
sudo mkdir -p /opt/air_emergency
sudo chown -R $USER:$USER /opt/air_emergency  # 赋予当前用户权限

# 克隆代码（替换为实际仓库地址）
cd /opt/air_emergency
git clone -b main https://github.com/A-Dawn/air_emergency_response.git
```

**2. 创建虚拟环境**  
```bash
python3 -m venv venv
source venv/bin/activate  # 激活虚拟环境
# 激活后命令行提示符会显示 (venv)
```

**3. 安装Python依赖**  
```bash
# 确保在虚拟环境中（命令行开头有(venv)）
pip install -r requirements.txt
```

---

#### **四、MySQL配置（详细步骤）**
**1. 安全初始化MySQL（重要！）**  
```bash
sudo mysql_secure_installation
```
- 按提示操作：  
  - 设置root密码（建议高强度密码）  
  - 移除匿名用户：输入 `Y`  
  - 禁止远程root登录：输入 `Y`  
  - 移除测试数据库：输入 `Y`  
  - 重新加载权限表：输入 `Y`  

**2. 创建专用数据库和用户**  
```bash
# 登录MySQL（使用上一步设置的root密码）
sudo mysql -u root -p

-- 执行SQL命令
CREATE DATABASE air_emergency CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'air_user'@'localhost' IDENTIFIED BY 'StrongPass123!';
GRANT ALL PRIVILEGES ON air_emergency.* TO 'air_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**3. 验证数据库连接**  
```bash
mysql -u air_user -p air_emergency
# 输入密码后应成功进入MySQL命令行
```

---

#### **五、环境变量配置（关键步骤）**
**1. 创建.env文件**  
```bash
nano /opt/air_emergency/.env
```
内容如下（按实际修改）：  
```ini
DATABASE_URL=mysql+pymysql://air_user:StrongPass123!@localhost/air_emergency
JWT_SECRET_KEY=YourSecureKey123!  # 至少32位随机字符串
SM2_PRIVATE_KEY=308193020100301...  # 真实SM2私钥
```

**2. 设置文件权限（防止泄露）**  
```bash
chmod 600 /opt/air_emergency/.env  # 仅允许所有者读写
```

**3. 临时加载环境变量（测试用）**  
```bash
source .env
```

---

#### **六、服务启动与验证**
**1. 初始化数据库表**  
```bash
# 在项目目录下执行
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

**2. 启动开发服务器（仅测试用）**  
```bash
flask run --host=0.0.0.0 --port=5000
# 按Ctrl+C停止
```

**3. 配置生产服务（Systemd）**  
```bash
# 创建服务文件
sudo nano /etc/systemd/system/air_emergency.service
```
内容如下：  
```ini
[Unit]
Description=民航应急响应系统后端服务
After=network.target

[Service]
User=ubuntu  # 替换为实际用户名
Group=ubuntu
WorkingDirectory=/opt/air_emergency
EnvironmentFile=/opt/air_emergency/.env
ExecStart=/opt/air_emergency/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**4. 启动服务**  
```bash
sudo systemctl daemon-reload
sudo systemctl start air_emergency
sudo systemctl enable air_emergency  # 开机自启

# 检查状态（确保显示"active (running)"）
sudo systemctl status air_emergency
```

---

#### **七、Nginx反向代理配置**
**1. 基本配置**  
```bash
sudo nano /etc/nginx/sites-available/air_emergency
```
内容如下：  
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为实际域名或IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**2. 启用配置**  
```bash
sudo ln -s /etc/nginx/sites-available/air_emergency /etc/nginx/sites-enabled/
sudo nginx -t  # 检查配置语法
sudo systemctl restart nginx
```

**3. 防火墙放行**  
```bash
sudo ufw allow 80/tcp
sudo ufw allow 5000/tcp  # 开发调试用
sudo ufw enable
```

---

#### **八、常见问题排查**
**问题1：数据库连接失败**  
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查用户权限
mysql -u air_user -p
SHOW GRANTS FOR 'air_user'@'localhost';
```

**问题2：服务启动失败**  
```bash
# 查看完整日志
journalctl -u air_emergency -f --since "5 minutes ago"
```

**问题3：端口冲突**  
```bash
# 查看5000端口占用
sudo lsof -i :5000

# 如果被占用，修改app.py中的端口或终止冲突进程
kill -9 <PID>
```

---

#### **九、备份脚本（每日自动执行）**
**1. 创建备份脚本**  
```bash
sudo nano /opt/backup_script.sh
```
内容：  
```bash
#!/bin/bash
DATE=$(date +%F)
mysqldump -u air_user -p'StrongPass123!' air_emergency > /backup/air_emergency_$DATE.sql
tar -czvf /backup/air_emergency_$DATE.tar.gz /opt/air_emergency
find /backup -type f -mtime +30 -delete
```

**2. 设置定时任务**  
```bash
sudo crontab -e
# 添加以下内容（每天凌晨2点备份）
0 2 * * * /bin/bash /opt/backup_script.sh
```

---

### **附录：部署流程图**
```plaintext
[更新系统] → [安装依赖] → [配置MySQL]  
    ↓  
[克隆代码] → [设置虚拟环境] → [安装依赖]  
    ↓  
[配置环境变量] → [初始化数据库]  
    ↓  
[配置Systemd服务] → [启动服务]  
    ↓  
[配置Nginx] → [完成部署]
```
