# models/incident.py
from . import db
from datetime import datetime
from enum import Enum
from flask import current_app  # 导入 current_app
from sqlalchemy import TypeDecorator, String
import hashlib
from utils.sm_utils import encrypt_sm4,decrypt_sm4 # 确保在这里导入

class IncidentStatus(Enum):
    DRAFT = 1
    SUBMITTED_DEPARTMENT_REVIEW = 2
    DEPARTMENT_APPROVED = 3
    DEPARTMENT_REJECTED = 4
    PENDING_COMMAND_CENTER = 5
    COMMAND_CENTER_PROCESSED = 6
    ISSUED_EMERGENCY_TEAM = 7
    RESOLVED = 8
    CLOSED = 9

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
