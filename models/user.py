# models/user.py
from . import db
from datetime import datetime # 导入 datetime

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    role_level = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # 添加邮箱字段
    is_active = db.Column(db.Boolean, default=True)  # 添加 is_active 字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 添加创建时间
    # 新增：与 Department 模型建立外键关联   后续再用
    #  department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))
    #  department = db.relationship('Department', backref='users')

    def __repr__(self):
        return f'<User {self.username}>'

"""
components:
  schemas:
    User:
      type: object
      properties:
        user_id:
          type: integer
          description: 用户ID
        username:
          type: string
          description: 用户名
        hashed_password:
          type: string
          description: 加密后的密码 (SM3)
        salt:
          type: string
          description: 盐值
        role_level:
          type: integer
          description: |
            角色级别:
            - -1: 管理员
            - 0: 领导小组
            - 1: 指挥中心
            - 2: 部门领导
            - 3: 普通用户/安全管理员
        email:
          type: string
          format: email
          description: 邮箱
        is_active:
          type: boolean
          description: 是否激活
          default: true
        created_at:
          type: string
          format: date-time
          description: 创建时间
      required:
        - username
        - hashed_password
        - salt
        - role_level
        - email
"""