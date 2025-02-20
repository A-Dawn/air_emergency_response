# models/incident.py
from . import db
from datetime import datetime
from enum import Enum
from flask import current_app  # 导入 current_app
from sqlalchemy import TypeDecorator, String
import hashlib
from utils.sm_utils import encrypt_sm4,decrypt_sm4 # 确保在这里导入

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

class Incident(db.Model):
    __tablename__ = 'incidents'
    incident_id = db.Column(db.Integer, primary_key=True)
    # 增加了长度限制，并且在数据库层面限制不能为空
    incident_info = db.Column(db.String(2048), nullable=False)
    process_status = db.Column(db.String(255))
    response_log = db.Column(db.Text)
    incident_level = db.Column(db.Integer)
    is_aviation = db.Column(db.Boolean, default=False) # 增加默认值
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_types.type_id'), nullable=False) # 数据库层面限制外键不能为空
    attachment_url = db.Column(db.String(255))
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False) # 数据库层面限制外键不能为空
    # 增加default值
    status = db.Column(db.Enum(IncidentStatus), default=IncidentStatus.DRAFT)
    rejection_reason = db.Column(db.Text)
    resolution_measures = db.Column(db.Text)
    closed_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    # 和event_type表建立relationship关系
    event_type = db.relationship('EventType', backref='incidents')
    # 和user表建立relationship关系
    submitted_by = db.relationship('User', backref='incidents')
    # 和department建立多对多的relationship关系
    departments = db.relationship('Department', secondary='incident_departments', backref=db.backref('incidents', lazy='dynamic'))
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
