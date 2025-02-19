# models/incident.py
from . import db
from enum import Enum  # 导入枚举类型
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

class IncidentStatus(Enum):
    DRAFT = 1  # 待提交
    SUBMITTED_DEPARTMENT_REVIEW = 2  # 已提交待部门审批
    DEPARTMENT_APPROVED = 3  # 部门审批已通过
    DEPARTMENT_REJECTED = 4  # 部门审批已驳回
    PENDING_COMMAND_CENTER = 5  # 待指挥中心处理
    COMMAND_CENTER_PROCESSED = 6  # 指挥中心已处理
    ISSUED_EMERGENCY_TEAM = 7  # 已下发应急小组
    RESOLVED = 8  # 已解决
    CLOSED = 9  # 已关闭

#  定义关联表
incident_departments = db.Table('incident_departments',
    db.Column('incident_id', db.Integer, db.ForeignKey('incidents.incident_id'), primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey('departments.department_id'), primary_key=True)
)

# class 为Incident设置sm4加解密
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

class Incident(db.Model):
    __tablename__ = 'incidents'
    incident_id = db.Column(db.Integer, primary_key=True)
    incident_info = db.Column(SM4EncryptedType(key=hashlib.sha256(b'incident_info').hexdigest()), nullable=False)
    process_status = db.Column(db.Integer, nullable=False) #请告诉我这个字段的具体含义以及可能的状态值
    response_log = db.Column(db.Text, nullable=True)  # 允许为空
    incident_level = db.Column(db.Integer, nullable=False) #请告诉我这个字段的具体含义以及可能的状态值
    is_aviation = db.Column(db.Boolean, default=False)
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_types.type_id'), nullable=False)
    departments = db.relationship('Department', secondary=incident_departments, backref=db.backref('incidents', lazy='dynamic'))
    attachment_url = db.Column(db.String(255), nullable=True)
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    status = db.Column(db.Enum(IncidentStatus), default=IncidentStatus.DRAFT)  # 使用枚举类型，默认状态为 DRAFT
    rejection_reason = db.Column(db.Text, nullable=True)  # 驳回原因
    resolution_measures = db.Column(db.Text, nullable=True)  # 解决方案
    closed_at = db.Column(db.DateTime, nullable=True) # 关闭时间
    resolved_at = db.Column(db.DateTime, nullable=True) # 解决时间

    def __repr__(self):
        return f'<Incident {self.incident_id}>'

"""
components:
  schemas:
    Incident:
      type: object
      properties:
        incident_id:
          type: integer
          description: 事件ID
        incident_info:
          type: string
          description: 事件详细信息 (SM4加密)
        process_status:
          type: integer
          description: "处理状态"
        response_log:
          type: string
          description: 响应日志
        incident_level:
          type: integer
          description: "事件等级"
        is_aviation:
          type: boolean
          description: 是否航空事件
          default: false
        event_type_id:
          type: integer
          description: 事件类型ID
        attachment_url:
          type: string
          description: 附件URL
        submitted_by_user_id:
          type: integer
          description: 提交用户ID
        status:
          type: string
          description: 事件状态
          enum:
            - DRAFT
            - SUBMITTED_DEPARTMENT_REVIEW
            - DEPARTMENT_APPROVED
            - DEPARTMENT_REJECTED
            - PENDING_COMMAND_CENTER
            - COMMAND_CENTER_PROCESSED
            - ISSUED_EMERGENCY_TEAM
            - RESOLVED
            - CLOSED
        rejection_reason:
          type: string
          description: 驳回原因
        resolution_measures:
          type: string
          description: 解决方案
        closed_at:
          type: string
          format: date-time
          description: 关闭时间
        resolved_at:
          type: string
          format: date-time
          description: 解决时间
        departments:
          type: array
          items:
            $ref: '#/components/schemas/Department'
      required:
        - incident_info
        - process_status
        - incident_level
        - event_type_id
"""