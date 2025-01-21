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