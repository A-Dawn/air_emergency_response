from . import db

class EmergencyPlan(db.Model):
    __tablename__ = 'emergency_plans'
    plan_id = db.Column(db.Integer, primary_key=True)  # 应急预案ID
    plan_details = db.Column(db.Text, nullable=False)  # 应急预案详情
    version = db.Column(db.String(20), nullable=False)  # 版本号
    status = db.Column(db.Integer, nullable=False)  # 状态