from . import db

class Incident(db.Model):
    __tablename__ = 'incidents'
    incident_id = db.Column(db.Integer, primary_key=True)  # 事件ID
    incident_info = db.Column(db.Text, nullable=False)  # 事件信息
    process_status = db.Column(db.Integer, nullable=False)  # 处理状态
    response_log = db.Column(db.Text, nullable=False)  # 响应日志
    incident_level = db.Column(db.Integer, nullable=False)  # 事件级别
    assigned_resources = db.Column(db.Text, nullable=True)  # 分配资源
    update_time = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间