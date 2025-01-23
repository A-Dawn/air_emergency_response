# /www/wwwroot/air_emergency_response/models/user.py
from . import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)  # 用户ID
    username = db.Column(db.String(50), unique=True, nullable=False)  # 用户名
    sm2_public_key = db.Column(db.Text, nullable=False)  # SM2公钥
    role_level = db.Column(db.Integer, nullable=False)  # 用户角色等级