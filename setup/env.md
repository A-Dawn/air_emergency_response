# 应急响应平台部署文档

## 概述
本文档提供了详细的步骤，以在Ubuntu 22.04上部署应急响应平台。部署过程包括安装依赖、配置环境、设置数据库、运行应用等步骤。

## 前提条件
1. 安装了Ubuntu 22.04的服务器或虚拟机。
2. 具有sudo权限的用户账户。
3. 已安装`git`（用于克隆代码库）。
4. 已安装`Python 3.8`或更高版本。
5. 已安装`pip`（Python包管理工具）。
6. 已安装`MySQL`或兼容的数据库服务器（如MariaDB）。

## 详细步骤

### 1. 更新系统包
首先，确保系统包是最新的。
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. 安装Python和pip
确保已安装Python 3.8或更高版本以及`pip`。
```bash
sudo apt install python3 python3-pip -y
```

### 3. 安装虚拟环境工具
使用`virtualenv`来管理Python虚拟环境。
```bash
sudo pip3 install virtualenv
```

### 4. 克隆项目代码
使用`git`克隆项目代码到服务器上。
```bash
git clone https://github.com/A-Dawn/air_emergency_response
cd air_emergency_response
```

### 5. 创建虚拟环境
创建并激活Python虚拟环境。
```bash
virtualenv venv
source venv/bin/activate
```

### 6. 安装项目依赖
安装项目所需的Python包。
```bash
pip install -r requirements.txt
```

#### 安装MySQL客户端库
如果使用MySQL数据库，确保安装`mysqlclient`库。
```bash
sudo apt-get install libmysqlclient-dev -y
pip install mysqlclient
```

### 7. 配置环境变量
在项目根目录下创建一个`.env`文件，用于存储敏感信息和配置参数。

```bash
nano .env
```

在`.env`文件中添加以下内容：
```plaintext
SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://air_user:your_password@localhost/air_emergency_response
JWT_SECRET_KEY=jwt_secret_key
```

#### 详细说明：
- **SECRET_KEY**: 用于加密Flask会话和其他安全相关功能的密钥。请使用随机生成的长字符串替换`your_secret_key`。
- **DATABASE_URL**: 数据库连接字符串。请替换`your_password`为实际的数据库密码。
- **JWT_SECRET_KEY**: 用于加密JWT令牌的密钥。请使用随机生成的长字符串替换`jwt_secret_key`。

保存并关闭文件。

### 8. 配置数据库
确保MySQL服务器已安装并运行。

#### 安装MySQL
如果尚未安装MySQL，可以使用以下命令安装：
```bash
sudo apt install mysql-server -y
```

#### 登录MySQL并创建数据库
```bash
sudo mysql -u root -p
```

在MySQL shell中执行以下命令：
```sql
CREATE DATABASE air_emergency_response;
CREATE USER 'air_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON air_emergency_response.* TO 'air_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 详细说明：
- **your_password**: 替换为您设置的实际数据库密码。

### 9. 初始化数据库
在虚拟环境中运行以下命令以初始化数据库。
```bash
export FLASK_APP=app.py
flask db init
flask db migrate
flask db upgrade
```

### 10. 启动Flask应用
在虚拟环境中启动Flask应用。
```bash
flask run --host=0.0.0.0 --port=5000
```

#### 使用Gunicorn和Nginx（可选）
为了提高性能和安全性，可以使用Gunicorn和Nginx来部署应用。

#### 安装Gunicorn
```bash
pip install gunicorn
```

#### 创建Gunicorn启动脚本
在项目根目录下创建一个`gunicorn-start.sh`脚本。
```bash
nano gunicorn-start.sh
```

在脚本中添加以下内容：
```bash
#!/bin/bash
cd /www/wwwroot/air_emergency_response
source venv/bin/activate
exec gunicorn --bind 0.0.0.0:5000 app:app
```

保存并关闭文件，然后赋予脚本执行权限。
```bash
chmod +x gunicorn-start.sh
```

#### 配置Nginx
安装Nginx。
```bash
sudo apt install nginx -y
```

创建一个Nginx配置文件。
```bash
sudo nano /etc/nginx/sites-available/air_emergency_response
```

在配置文件中添加以下内容：
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

保存并关闭文件，然后创建一个符号链接以启用配置。
```bash
sudo ln -s /etc/nginx/sites-available/air_emergency_response /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 详细说明：
- **your_domain_or_ip**: 替换为您的域名或服务器IP地址。

### 11. 设置防火墙
允许HTTP和HTTPS流量。
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 12. 配置日志文件
确保Flask和Gunicorn的日志文件正确配置。

在项目根目录下创建一个`logs`文件夹。
```bash
mkdir logs
```

### 13. 设置项目启动脚本
为了确保应用在服务器重启后自动启动，可以使用`systemd`服务。

创建一个`systemd`服务文件。
```bash
sudo nano /etc/systemd/system/air_emergency_response.service
```

在服务文件中添加以下内容：
```ini
[Unit]
Description=Air Emergency Response Flask Application
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/www/wwwroot/air_emergency_response
Environment="PATH=/www/wwwroot/air_emergency_response/venv/bin"
Environment="FLASK_APP=app.py"
ExecStart=/www/wwwroot/air_emergency_response/venv/bin/gunicorn --workers 3 --bind unix:air_emergency_response.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

#### 详细说明：
- **your_username**: 替换为运行应用的用户名。

保存并关闭文件，然后启动并启用服务。
```bash
sudo systemctl start air_emergency_response
sudo systemctl enable air_emergency_response
```

### 14. 配置Nginx以使用Gunicorn的Unix套接字
编辑Nginx配置文件。
```bash
sudo nano /etc/nginx/sites-available/air_emergency_response
```

修改内容如下：
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://unix:/www/wwwroot/air_emergency_response/air_emergency_response.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

保存并关闭文件，然后测试Nginx配置并重启Nginx。
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 总结

通过以上步骤，您应该能够在Ubuntu 22.04上成功部署应急响应平台，并请特别注意以下需要修改的部分：

1. **修改`.env`文件中的敏感信息**：
   - **SECRET_KEY**: 替换为随机生成的长字符串。
   - **DATABASE_URL**: 替换为实际的数据库用户和密码。
   - **JWT_SECRET_KEY**: 替换为随机生成的长字符串。

2. **MySQL配置**：
   - **your_password**: 替换为实际的数据库密码。

3. **Nginx配置**：
   - **your_domain_or_ip**: 替换为服务器IP地址（域名没买）。

4. **systemd服务配置**：
   - **your_username**: 替换为运行应用的用户名。

如果遇到任何问题，可以查看日志文件或查阅相关文档以进行故障排除。

