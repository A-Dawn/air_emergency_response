from . import db

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    log_id = db.Column(db.Integer, primary_key=True)  # 系统日志ID
    operation_type = db.Column(db.Integer, nullable=False)  # 操作类型
    operator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 操作员ID
    operation_content = db.Column(db.Text, nullable=False)  # 操作内容
    operation_result = db.Column(db.Integer, nullable=False)  # 操作结果
    ip_address = db.Column(db.String(50), nullable=False)  # IP地址
    operation_time = db.Column(db.DateTime, default=db.func.current_timestamp())  # 操作时间