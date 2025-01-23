import os

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost/air_emergency')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置（必须通过环境变量设置！）
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'insecure_default_key_请修改')
    
    # SM2私钥配置（必须通过环境变量设置！）
    SM2_PRIVATE_KEY = os.getenv('SM2_PRIVATE_KEY')  # 示例：'308193020100301...'
    
    # 其他参数
    MAX_FAILED_ATTEMPTS = 5  # 登录失败锁定阈值
    BAN_DURATION = 300       # 锁定时间（秒）