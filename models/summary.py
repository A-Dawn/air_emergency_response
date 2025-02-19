# models/summary.py
from . import db
from datetime import datetime
from sqlalchemy_utils import EncryptedType  # 导入 EncryptedType
from flask import current_app  # 导入 current_app
from sqlalchemy import TypeDecorator, String
import hashlib

class StringEncoded(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.encode('utf-8')
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.decode('utf-8')
        return value

# class 为Summary设置sm4加解密
class SM4EncryptedType(TypeDecorator):
    impl = StringEncoded
    cache_ok = True

    def __init__(self, key, *args, **kwargs):
        self.key = key
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            from utils.sm_utils import encrypt_sm4
            value = encrypt_sm4(self.key, value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            from utils.sm_utils import decrypt_sm4
            value = decrypt_sm4(self.key, value)
        return value

class Summary(db.Model):
    __tablename__ = 'summaries'
    summary_id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.incident_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(SM4EncryptedType(key=hashlib.sha256(b'content').hexdigest()), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    incident = db.relationship('Incident', backref=db.backref('summaries', lazy=True))
    user = db.relationship('User', backref=db.backref('summaries', lazy=True))
    #  新增字段
    event_type = db.Column(db.String(100), nullable=False)  # 应急事件类型
    security_level = db.Column(db.String(50), nullable=False)  # 安全等级
    summary_status = db.Column(db.Integer, default=1)  # 1:待审批, 2:审批通过, 3:审批拒绝

    def __repr__(self):
        return f'<Summary {self.summary_id}>'

"""
components:
  schemas:
    Summary:
      type: object
      properties:
        summary_id:
          type: 
          description: 总结ID
        incident_id:
          type: integer
          description: 事件ID
        user_id:
          type: integer
          description: 用户ID
        content:
          type: string
          description: 总结内容 (SM4加密)
        created_at:
          type: string
          format: date-time
          description: 创建时间
        event_type:
          type: string
          description: 应急事件类型
        security_level:
          type: string
          description: 安全等级
        summary_status:
          type: integer
          description: 总结状态 (1-待审批, 2-审批通过, 3-审批拒绝)
          default: 1
      required:
        - incident_id
        - user_id
        - content
        - event_type
        - security_level
"""