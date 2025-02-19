# /www/wwwroot/air_emergency_response/models/login_attempt.py
from . import db

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)  # 尝试记录ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 用户ID
    attempt_time = db.Column(db.DateTime, default=db.func.current_timestamp())  # 尝试时间
    success = db.Column(db.Boolean, nullable=False)  # 尝试是否成功
    ip_address = db.Column(db.String(50), nullable=False)  # 尝试IP地址

    def __repr__(self):
        return f'<LoginAttempt {self.id}>'

"""
components:
  schemas:
    LoginAttempt:
      type: object
      properties:
        id:
          type: integer
          description: 尝试记录ID
        user_id:
          type: integer
          description: 用户ID
        attempt_time:
          type: string
          format: date-time
          description: 尝试时间
        success:
          type: boolean
          description: 尝试是否成功
        ip_address:
          type: string
          description: 尝试IP地址
      required:
        - user_id
        - success
        - ip_address
"""