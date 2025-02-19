# routes/summary.py
from flask import Blueprint, request, jsonify
from models import db, Summary, Incident, User
from utils.jwt_utils import token_required, role_required

summary = Blueprint('summary', __name__)

"""
tags:
  - 事件总结
"""
# 创建事件总结（安全管理员）
@summary.route('/summaries/create', methods=['POST'])
@token_required
@role_required([3])  # 只有安全管理员可以访问
def create_summary(current_user):
    """
    openapi:
      summary: 创建事件总结（安全管理员）
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Summary'
      responses:
        '201':
          description: 事件总结创建成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 事件总结创建成功!
        '400':
          description: 缺少必要参数!
        '401':
          description: 未授权
        '403':
            description: "权限不足"
        '404':
          description: 事件不存在
    """
    data = request.get_json()
    incident_id = data.get('incident_id')
    content = data.get('content')
    event_type = data.get('event_type')
    security_level = data.get('security_level')

    if not all([incident_id, content, event_type, security_level]):
        return jsonify({'message': '缺少必要参数!'}), 400

    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({'message': '事件不存在!'}), 404

    new_summary = Summary(
        incident_id=incident_id,
        user_id=current_user.user_id,
        content=content,
        event_type = event_type,
        security_level = security_level
    )
    db.session.add(new_summary)
    db.session.commit()
    return jsonify({'message': '事件总结创建成功!'}), 201

"""
tags:
  - 事件总结
"""

# 获取事件总结
@summary.route('/summaries/<int:incident_id>', methods=['GET'])
@token_required
def get_summary(current_user, incident_id):
    """
    openapi:
      summary: 获取事件总结
      security:
        - bearerAuth: []
      parameters:
        - name: incident_id
          in: path
          required: true
          description: 事件ID
          schema:
            type: integer
      responses:
        '200':
          description: 成功返回事件总结
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Summary'
        '401':
          description: 未授权
        '404':
          description: 未找到事件总结
    """
    summary = Summary.query.filter_by(incident_id=incident_id).first()
    if not summary:
        return jsonify({'message': '未找到事件总结!'}), 404
    summary_data = {
          'summary_id': summary.summary_id,
          'incident_id': summary.incident_id,
          'user_id': summary.user_id,
          'content': summary.content,
          'event_type': summary.event_type,
          'security_level':summary.security_level
       }
    return jsonify(summary_data), 200
"""
tags:
  - 事件总结
"""
# 审批总结（部门领导）
@summary.route('/summaries/<int:summary_id>/approve', methods=['POST'])
@token_required
@role_required([2])  # 只有部门领导可以访问
def approve_summary(current_user, summary_id):
    """
    openapi:
      summary: 审批事件总结 (部门领导)
      security:
        - bearerAuth: []
      parameters:
        - name: summary_id
          in: path
          required: true
          description: 总结ID
          schema:
            type: integer
      responses:
        '200':
          description: 总结审批通过
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 总结审批通过!
        '400':
          description: 总结状态不正确，无法审批
        '401':
          description: 未授权
        '403':
            description: "权限不足"
        '404':
          description: 未找到事件总结
    """
    summary = Summary.query.get(summary_id)
    if not summary:
        return jsonify({'message': '未找到事件总结!'}), 404

    # 只有待审批的总结才能被审批
    if summary.summary_status != 1:
        return jsonify({'message': '总结状态不正确，无法审批!'}), 400

    summary.summary_status = 2 # 2: 审批通过
    db.session.commit()
    return jsonify({'message': '总结审批通过!'}), 200
"""
tags:
  - 事件总结
"""
# 拒绝总结（部门领导）
@summary.route('/summaries/<int:summary_id>/reject', methods=['POST'])
@token_required
@role_required([2])  # 只有部门领导可以访问
def reject_summary(current_user, summary_id):
    """
    openapi:
      summary: 拒绝事件总结 (部门领导)
      security:
        - bearerAuth: []
      parameters:
        - name: summary_id
          in: path
          required: true
          description: 总结ID
          schema:
            type: integer
      responses:
        '200':
          description: 总结审批拒绝
          content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: 总结审批拒绝!
        '400':
            description: "总结状态不正确，无法拒绝"
        '401':
          description: 未授权
        '403':
            description: "权限不足"
        '404':
          description: 未找到事件总结
    """
    summary = Summary.query.get(summary_id)
    if not summary:
        return jsonify({'message': '未找到事件总结!'}), 404

    # 只有待审批的总结才能被拒绝
    if summary.summary_status != 1:
        return jsonify({'message': '总结状态不正确，无法拒绝!'}), 400
    summary.summary_status = 3  # 3: 审批拒绝
    db.session.commit()
    return jsonify({'message': '总结审批拒绝!'}), 200