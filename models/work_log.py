# /www/wwwroot/air_emergency_response/models/work_log.py
from . import db

class WorkLog(db.Model):
    __tablename__ = 'work_logs'
    log_id = db.Column(db.Integer, primary_key=True)  # 日志ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 用户ID
    log_content = db.Column(db.Text, nullable=False)  # 日志内容
    work_progress = db.Column(db.Integer, nullable=False)  # 工作进度
    file_references = db.Column(db.Text, nullable=True)  # 文件引用
    create_time = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    update_time = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间