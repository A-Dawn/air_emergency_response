# /www/wwwroot/air_emergency_response/routes/__init__.py
from flask import Blueprint

auth = Blueprint('auth', __name__)
emergency_plan = Blueprint('emergency_plan', __name__)
incident = Blueprint('incident', __name__)
security_check = Blueprint('security_check', __name__)
user = Blueprint('user', __name__)

from .auth import *  # 导入认证路由
from .emergency_plan import *  # 导入应急预案路由
from .incident import *  # 导入事件路由
from .security_check import *  # 导入安全检查路由
from .user import *  # 导入用户路由