from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .emergency_plan import EmergencyPlan
# 确保导⼊ Incident 和 IncidentStatus
from .incident import Incident, IncidentStatus
from .security_check import SecurityCheck
from .work_log import WorkLog
from .system_log import SystemLog
from .login_attempt import LoginAttempt
from .event_type import EventType
from .department import Department  # 确保导⼊ Department
from .summary import Summary  # 确保导⼊ Summary
from .message import Message  # 导⼊ Message

# 定义incident和department的多对多表
incident_departments = db.Table('incident_departments',
    db.Column('incident_id', db.Integer, db.ForeignKey('incidents.incident_id'), primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey('departments.department_id'), primary_key=True)
)
