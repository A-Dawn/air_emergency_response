# /www/wwwroot/air_emergency_response/models/security_check.py
from . import db

class SecurityCheck(db.Model):
    __tablename__ = 'security_checks'
    check_id = db.Column(db.Integer, primary_key=True)  # 安全检查ID
    check_record = db.Column(db.Text, nullable=False)  # 检查记录
    issue_tracking = db.Column(db.Text, nullable=False)  # 问题跟踪
    improvement_status = db.Column(db.Integer, nullable=False)  # 改进建议状态
    evaluation_report = db.Column(db.Text, nullable=True)  # 评估报告

"""
components:
  schemas:
    SecurityCheck:
      type: object
      properties:
        check_id:
          type: integer
          description: 安全检查ID
        check_record:
          type: string
          description: 检查记录
        issue_tracking:
          type: string
          description: 问题跟踪
        improvement_status:
          type: integer
          description: 改进建议状态
        evaluation_report:
          type: string
          description: 评估报告
      required:
        - check_record
        - issue_tracking
        - improvement_status
"""