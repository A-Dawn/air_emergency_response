from . import db

class SecurityCheck(db.Model):
    __tablename__ = 'security_checks'
    check_id = db.Column(db.Integer, primary_key=True)  # 安全检查ID
    check_record = db.Column(db.Text, nullable=False)  # 检查记录
    issue_tracking = db.Column(db.Text, nullable=False)  # 问题跟踪
    improvement_status = db.Column(db.Integer, nullable=False)  # 改进建议状态
    evaluation_report = db.Column(db.Text, nullable=True)  # 评估报告