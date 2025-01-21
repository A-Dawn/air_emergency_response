from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .emergency_plan import EmergencyPlan
from .incident import Incident
from .security_check import SecurityCheck
from .work_log import WorkLog
from .system_log import SystemLog
from .login_attempt import LoginAttempt