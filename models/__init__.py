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