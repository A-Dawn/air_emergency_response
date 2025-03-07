import os
#from dotenv import load_dotenv  # 导入 load_dotenv

#dotenv_path = os.path.join(os.path.dirname(__file__), '.env')  # 相对于当前脚本的路径
#load_dotenv(dotenv_path)  # 加载 .env 文件中的环境变量

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost/air_emergency')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置（必须通过环境变量设置！）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY 环境变量未设置！")

    # SM2私钥配置（必须通过环境变量设置！）
    SM2_PRIVATE_KEY = os.environ.get('SM2_PRIVATE_KEY')
    if not SM2_PRIVATE_KEY:
        raise ValueError("SM2_PRIVATE_KEY 环境变量未设置！")

    # 密钥加密配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY 环境变量未设置！")

    # 邮箱配置 (用于发送密码重置邮件等)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    if not MAIL_SERVER:
        raise ValueError("MAIL_SERVER 环境变量未设置!")
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    if not MAIL_PORT:
        raise ValueError("MAIL_PORT 环境变量未设置!")
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    if not MAIL_USERNAME:
        raise ValueError("MAIL_USERNAME 环境变量未设置!")
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    if not MAIL_PASSWORD:
        raise ValueError("MAIL_PASSWORD 环境变量未设置!")
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    if not MAIL_DEFAULT_SENDER:
        raise ValueError("MAIL_DEFAULT_SENDER 环境变量未设置!")

    # 其他参数
    MAX_FAILED_ATTEMPTS = int(os.environ.get('MAX_FAILED_ATTEMPTS', 5))
    BAN_DURATION = int(os.environ.get('BAN_DURATION', 300))
