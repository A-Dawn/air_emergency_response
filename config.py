import os

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost/air_emergency')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置（必须通过环境变量设置！）
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # SM2私钥配置（必须通过环境变量设置！）
    SM2_PRIVATE_KEY = os.getenv('SM2_PRIVATE_KEY')  # 示例：'308193020100301...'

    # 密钥加密配置
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # 邮箱配置 (用于发送密码重置邮件等)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')  #  SMTP 服务器地址
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587)) # SMTP 端口
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'# 是否使用 TLS
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'# 是否使用 SSL
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'server_email@example.com')  # 邮箱用户名
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'server_email_password') # 邮箱密码或授权码
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'server_email@example.com')   # 默认发件人邮箱

    # 其他参数
    MAX_FAILED_ATTEMPTS = 5 # 登录失败锁定阈值
    BAN_DURATION = 300 # 锁定时间（秒）