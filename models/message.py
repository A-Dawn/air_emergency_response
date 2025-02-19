from . import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 接收者
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 发送者
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.incident_id'), nullable=True) # 可选
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # 是否已读
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')

    def __repr__(self):
        return f'<Message {self.message_id}>'

"""
components:
  schemas:
    Message:
      type: object
      properties:
        message_id:
          type: integer
          description: 消息ID
        recipient_id:
          type: integer
          description: 接收者ID
        sender_id:
          type: integer
          description: 发送者ID
        incident_id:
          type: integer
          description: 关联的事件ID (可选)
        content:
          type: string
          description: 消息内容
        is_read:
          type: boolean
          description: 是否已读
          default: false
        sent_at:
          type: string
          format: date-time
          description: 发送时间
      required:
        - recipient_id
        - sender_id
        - content
"""