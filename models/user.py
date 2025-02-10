# /www/wwwroot/air_emergency_response/models/user.py
from . import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)  # 新增字段:哈希密码
    salt = db.Column(db.String(32), nullable=False) # 新增字段: 盐值
    role_level = db.Column(db.Integer, nullable=False)
