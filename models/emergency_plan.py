# /www/wwwroot/air_emergency_response/models/emergency_plan.py
from . import db

class EmergencyPlan(db.Model):
    __tablename__ = 'emergency_plans'
    plan_id = db.Column(db.Integer, primary_key=True)  # 应急预案ID
    plan_details = db.Column(db.Text, nullable=False)  # 应急预案详情
    version = db.Column(db.String(20), nullable=False)  # 版本号
    status = db.Column(db.Integer, nullable=False)  # 状态

"""
components:
  schemas:
    EmergencyPlan:
      type: object
      properties:
        plan_id:
          type: integer
          description: 应急预案ID
        plan_details:
          type: string
          description: 应急预案详情
        version:
          type: string
          description: 版本号
        status:
          type: integer
          description: 状态 (例如：1-草稿, 2-已发布, 3-已废弃)
      required:
        - plan_details
        - version
        - status
"""