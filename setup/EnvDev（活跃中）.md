---

### **《民航应急响应系统》Ubuntu 22.04 部署总结文档**

---

#### **一、部署前准备**
1. **服务器要求**  
   - Ubuntu 22.04 LTS  
   - 开放端口：`5000`（开发测试）、`443`（生产HTTPS）  
   - 依赖工具：`git`, `python3-pip`, `mysql-server`, `nginx`

2. **目录规范**  
   ```bash
   /www/wwwroot/air_emergency_response/  # 项目根目录（Git自动生成）
   ├── venv/           # Python虚拟环境
   ├── .env            # 环境变量文件
   ├── app.py          # 主程序入口
   └── (其他代码子目录) # 从Git克隆的代码结构
   ```

---

#### **二、核心部署步骤**
##### **1. 克隆代码**
```bash
sudo mkdir -p /www/wwwroot
sudo chown -R $USER:$USER /www/wwwroot  # 确保当前用户有权限
cd /www/wwwroot
git clone -b main https://github.com/A-Dawn/air_emergency_response.git
```

##### **2. 初始化虚拟环境**
```bash
cd /www/wwwroot/air_emergency_response
python3 -m venv venv
source venv/bin/activate  # 激活环境（后续操作需在虚拟环境中执行）
pip install -r requirements.txt
```

##### **3. 配置MySQL数据库**
```sql
-- 登录MySQL
sudo mysql -u root -p

-- 创建数据库和用户
CREATE DATABASE air_emergency CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'air_user'@'localhost' IDENTIFIED BY 'StrongPass123!';
GRANT ALL PRIVILEGES ON air_emergency.* TO 'air_user'@'localhost';
FLUSH PRIVILEGES;
```

##### **4. 设置环境变量**
```bash
nano /www/wwwroot/air_emergency_response/.env
```
内容示例：
```ini
DATABASE_URL=mysql+pymysql://air_user:StrongPass123!@localhost/air_emergency
JWT_SECRET_KEY=YourSecureKey123!
SM2_PRIVATE_KEY=308193020100301...
```

##### **5. 启动服务**
```bash
# 初始化数据库表
flask shell
>>> from app import db
>>> db.create_all()

# 配置Systemd服务
sudo nano /etc/systemd/system/air_emergency.service
```
服务文件内容：
```ini
[Unit]
Description=应急响应系统服务
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/www/wwwroot/air_emergency_response
EnvironmentFile=/www/wwwroot/air_emergency_response/.env
ExecStart=/www/wwwroot/air_emergency_response/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```
启动命令：
```bash
sudo systemctl daemon-reload
sudo systemctl start air_emergency
sudo systemctl enable air_emergency
```

##### **6. 配置Nginx反向代理**
```bash
sudo nano /etc/nginx/sites-available/air_emergency
```
内容示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/air_emergency /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

---

#### **三、验证与监控**
1. **服务状态检查**  
   ```bash
   sudo systemctl status air_emergency  # 应为active (running)
   curl -I http://localhost:5000        # 返回200 OK
   ```

2. **日志查看**  
   ```bash
   journalctl -u air_emergency -f       # 实时日志
   tail -f /var/log/nginx/access.log    # Nginx访问日志
   ```

---

#### **四、维护命令**
| 操作                 | 命令                                  |
|----------------------|---------------------------------------|
| 重启服务             | `sudo systemctl restart air_emergency` |
| 停止服务             | `sudo systemctl stop air_emergency`    |
| 备份数据库           | `mysqldump -u air_user -p air_emergency > backup.sql` |
| 更新代码             | `git pull && systemctl restart air_emergency` |

---

#### **五、常见问题排查**
| 问题现象             | 解决方案                              |
|----------------------|---------------------------------------|
| **数据库连接失败**   | 检查`.env`中的账号密码和MySQL权限     |
| **端口冲突**         | `sudo lsof -i :5000` 终止占用进程     |
| **Token解密失败**    | 确认`.env`中的`SM2_PRIVATE_KEY`格式正确 |
| **Nginx 502错误**    | 检查Gunicorn服务是否正常运行          |

---

### **附录：部署流程图**
```plaintext
[克隆代码] → [配置虚拟环境] → [安装依赖]  
    ↓  
[初始化数据库] → [设置环境变量]  
    ↓  
[启动Systemd服务] → [配置Nginx]  
    ↓  
[验证部署] → [完成]
```

按此文档操作可在 **20分钟内完成部署**，若有报错请优先检查路径和权限！