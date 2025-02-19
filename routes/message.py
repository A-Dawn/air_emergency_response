from flask import Blueprint, request, jsonify
from models import db, Message, User
from utils.jwt_utils import token_required, role_required

message = Blueprint('message', __name__)
"""
tags:
  - 消息
"""
# 获取当前用户的收件箱
@message.route('/messages', methods=['GET'])
@token_required
def get_my_messages(current_user):
    """
    openapi:
      summary: 获取当前用户的收件箱
      security:
        - bearerAuth: []
      responses:
        '200':
          description: 成功返回消息列表
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Message'
        '401':
          description: 未授权
    """
    messages = Message.query.filter_by(recipient_id=current_user.user_id).order_by(Message.sent_at.desc()).all()
    message_list = []
    for msg in messages:
        message_data = {
             'message_id': msg.message_id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.username, # 发送者姓名/用户名
            'incident_id': msg.incident_id,
            'content': msg.content,
            'is_read': msg.is_read,
            'sent_at': msg.sent_at.isoformat()
        }
        message_list.append(message_data)
    return jsonify(message_list), 200
"""
tags:
  - 消息
"""
#  标记消息为已读
@message.route('/messages/<int:message_id>/read', methods=['POST'])
@token_required
def mark_message_as_read(current_user, message_id):
    """
    openapi:
      summary: 标记消息为已读
      security:
        - bearerAuth: []
      parameters:
        - name: message_id
          in: path
          required: true
          description: 消息ID
          schema:
            type: integer
      responses:
        '200':
          description: 消息已标记为已读
          content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: 消息已标记为已读!
        '401':
          description: 未授权
        '403':
            description:  您无权操作此消息!
        '404':
            description: 未找到该消息!
    """
    message = Message.query.get(message_id)
    if not message:
         return jsonify({'message': '未找到该消息!'}),404
    if message.recipient_id != current_user.user_id:
        return jsonify({'message': '您无权操作此消息!'}),403
    message.is_read = True
    db.session.commit()
    return jsonify({'message': '消息已标记为已读!'}), 200

# 发送消息 (内部函数，不直接暴露为 API 接口)
def send_message(sender_id, recipient_id, incident_id, content):
    new_message = Message(sender_id=sender_id, recipient_id=recipient_id, incident_id=incident_id, content=content)
    db.session.add(new_message)
    db.session.commit()
    return new_message