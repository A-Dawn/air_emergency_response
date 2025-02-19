from . import db  # 确保从 models/__init__.py 导入 db

class EventType(db.Model):
    __tablename__ = 'event_types'
    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), nullable=False)
    is_aviation = db.Column(db.Boolean, default=False)  # 是否航空事件

    def __repr__(self):
        return f'<EventType {self.type_name}>'
"""
components:
  schemas:
    EventType:
      type: object
      properties:
        type_id:
          type: integer
          description: 事件类型ID
        type_name:
          type: string
          description: 事件类型名称
        is_aviation:
          type: boolean
          description: 是否航空事件
          default: false
      required:
        - type_name
"""