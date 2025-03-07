from flask import Blueprint, request, jsonify
from models import db, Incident, Department, EventType, IncidentStatus, User
from utils.jwt_utils import token_required, role_required
from datetime import datetime
import bleach
incident = Blueprint('incident', __name__)
# 辅助函数：用于检查用户是否可以修改事件状态
def can_modify_incident(user, incident):
    """
    检查用户是否可以修改事件状态,根据Status和Role进行判断,抽取出来可以⽅便后续维护和功能添加
    """
    if user.role_level == -1 or user.role_level == 0:
        return True  # 管理员和领导⼩组有权修改所有事件
    if incident.submitted_by_user_id == user.user_id:  # 提交⼈
        if incident.status == IncidentStatus.DRAFT or incident.status == IncidentStatus.DEPARTMENT_REJECTED:
            return True
    # 部门领导⻆⾊
    if user.role_level == 2 and incident.status == IncidentStatus.SUBMITTED_DEPARTMENT_REVIEW:
        # 只有当事件状态为 SUBMITTED_DEPARTMENT_REVIEW 时，部⻔领导才能修改
            return True
    # 指挥中⼼⻆⾊
    if user.role_level == 1 and incident.status in [
            IncidentStatus.DEPARTMENT_APPROVED,
            IncidentStatus.PENDING_COMMAND_CENTER
    ]:
            return True
    return False
# 添加以下配置
ALLOWED_TAGS = ['b', 'i', 'u', 'strong', 'em', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'ul', 'ol', 'li']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title'], 'abbr': ['title'], 'acronym': ['title']}
def clean_html(text):
        return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
"""
tags:
  - 事件管理
"""
# 审批通过
@incident.route('/incidents/<int:incident_id>/department-approve', methods=['POST'])
@token_required
@role_required([2])  # 只有部门领导可以访问
def department_approve_incident(current_user, incident_id):
    """
    openapi:
      summary: 部门审批通过事件
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
          description: 事件已批准
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 事件已批准!
        '400':
          description: 事件状态不正确，无法批准
        '401':
          description: 未授权
        '403':
          description: 无权限执行此操作
        '404':
          description: 事件不存在
    """
    incident = Incident.query.get_or_404(incident_id)
    if incident.status != IncidentStatus.SUBMITTED_DEPARTMENT_REVIEW:
        return jsonify({'message': '事件状态不正确，⽆法批准!'}), 400
    if not can_modify_incident(current_user, incident):
        return jsonify({'message': '⽆权限执⾏此操作'}), 403
    incident.status = IncidentStatus.DEPARTMENT_APPROVED
    db.session.commit()
    return jsonify({'message': '事件已批准!'}), 200
"""
tags:
  - 事件管理
"""
# 打回
@incident.route('/incidents/<int:incident_id>/department-reject', methods=['POST'])
@token_required
@role_required([2])  # 只有部门领导可以访问
def department_reject_incident(current_user, incident_id):
    """
    openapi:
      summary: 部门驳回事件
      security:
        - bearerAuth: []
      parameters:
        - name: incident_id
          in: path
          required: true
          description: 事件ID
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                rejection_reason:
                  type: string
                  description: 驳回原因
              required:
                - rejection_reason
      responses:
        '200':
          description: 事件已驳回
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 事件已驳回!
        '400':
          description: 请提供驳回原因 或 事件状态不正确，无法驳回
        '401':
          description: 未授权
        '403':
          description: 无权限执行此操作
        '404':
          description: 事件不存在
    """
    # 假设前端通过JSON传递驳回原因
    data = request.get_json()
    rejection_reason = data.get('rejection_reason')
    if not rejection_reason:
        return jsonify({'message': '请提供驳回原因!'}), 400
    incident = Incident.query.get_or_404(incident_id)
    if incident.status != IncidentStatus.SUBMITTED_DEPARTMENT_REVIEW:
            return jsonify({'message': '事件状态不正确，⽆法驳回!'}), 400
    if not can_modify_incident(current_user, incident):
        return jsonify({'message': '⽆权限执⾏此操作'}), 403
    incident.status = IncidentStatus.DEPARTMENT_REJECTED
    incident.rejection_reason = rejection_reason  # 记录驳回原因
    db.session.commit()
    return jsonify({'message': '事件已驳回!'}), 200
"""
tags:
  - 事件管理
"""
# 提交指挥中心
@incident.route('/incidents/<int:incident_id>/command-center-submit', methods=['POST'])
@token_required
@role_required([2])  # 只有部门领导可以访问
def command_center_submit_incident(current_user, incident_id):
    """
    openapi:
        summary: 部门提交事件至指挥中心
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
            description: 提交指挥中心成功
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: 提交指挥中⼼成功!
          '400':
            description: 当前状态无法提交至指挥中心
          '401':
            description: 未授权
          '403':
           description: 无权限执行此操作
          '404':
            description: 事件不存在
    """
    incident = Incident.query.get_or_404(incident_id)
    if incident.status != IncidentStatus.DEPARTMENT_APPROVED:
        return jsonify({'message': '当前状态⽆法提交⾄指挥中⼼'}), 400
    if not can_modify_incident(current_user, incident):
        return jsonify({'message': '⽆权限执⾏此操作'}), 403
    incident.status = IncidentStatus.PENDING_COMMAND_CENTER
    db.session.commit()
    #这里可以不发送通知给指挥中心,因为上面审批通过的时候已经发过了
    return jsonify({'message': '提交指挥中⼼成功!'}), 200
"""
tags:
  - 事件管理
"""
@incident.route('/incidents/<int:incident_id>/command-center-resolve', methods=['POST'])
@token_required
@role_required([1])   #只有指挥中心可以访问
def command_center_resolve_incident(current_user, incident_id):
    """
    openapi:
      summary: 指挥中心处理事件
      security:
        - bearerAuth: []
      parameters:
          - name: incident_id
            in: path
            required: true
            description: 事件ID
            schema:
              type: integer
      requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  resolution_measures:
                    type: string
                    description: 解决措施
      responses:
        '200':
          description: 指挥中心处理完成
          content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: 指挥中⼼处理完成!
        '400':
          description:  请填写解决措施! 或 当前状态⽆法解决!
        '401':
          description: 未授权
        '403':
          description: 无权限执行此操作
        '404':
          description: 事件不存在
    """
    data = request.get_json()
    resolution_measures = data.get('resolution_measures')
    incident_info = data.get('incident_info')  # 获取新的事件内容
    if not resolution_measures:
         return jsonify({'message': '请填写解决措施!'}), 400
    incident = Incident.query.get_or_404(incident_id)
    if incident.status != IncidentStatus.PENDING_COMMAND_CENTER:
      return jsonify({'message': '当前状态⽆法解决!'}), 400
    if not can_modify_incident(current_user, incident):
        return jsonify({'message': '⽆权限执⾏此操作'}), 403
    incident.status = IncidentStatus.COMMAND_CENTER_PROCESSED
    incident.resolution_measures = resolution_measures
    # 如果incident_info不为空， 则更新事件内容
    if incident_info:
        #  使用 bleach 进行编码转义  对数据库中的数据进行清洗
        cleaned_incident_info = clean_html(incident_info)
        incident.incident_info = cleaned_incident_info
    db.session.commit()
    return jsonify({'message': '指挥中⼼处理完成!'}), 200
"""
tags:
  - 事件管理
"""
# 下发应急⼩组
@incident.route('/incidents/<int:incident_id>/issue-emergency-team', methods=['POST'])
@token_required
@role_required([1])  # 只有指挥中心可以访问
def issue_emergency_team(current_user, incident_id):
    """
    openapi:
      summary: 指挥中心下发应急小组
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
          description: 已下发应急小组
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 已下发应急⼩组!
        '400':
          description: 当前状态无法下发应急小组
        '401':
          description: 未授权
        '403':
          description: 无权限执行此操作
        '404':
          description: 事件不存在
    """
    incident = Incident.query.get_or_404(incident_id)
    if incident.status != IncidentStatus.COMMAND_CENTER_PROCESSED:
        return jsonify({'message': '当前状态⽆法下发应急⼩组!'}), 400
    if not can_modify_incident(current_user, incident):
        return jsonify({'message': '⽆权限执⾏此操作'}), 403
    incident.status = IncidentStatus.ISSUED_EMERGENCY_TEAM
    db.session.commit()
    return jsonify({'message': '已下发应急⼩组!'}), 200
"""
tags:
  - 事件管理
"""
# 完结
@incident.route('/incidents/<int:incident_id>/resolve', methods=['POST'])
@token_required
@role_required([1])  # 只有指挥中心可以访问，根据实际情况调整
def resolve_incident(current_user, incident_id):
    """
    openapi:
      summary: 完结事件
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
          description: 事件已完结
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 事件已完结!
        '400':
          description: 当前状态无法完结
        '401':
          description: 未授权
        '403':
          description: 无权限执行此操作
        '404':
          description: 事件不存在
    """
    incident = Incident.query.get_or_404(incident_id)
    # 只有在下发应急⼩组后才能完结
    if incident.status != IncidentStatus.ISSUED_EMERGENCY_TEAM:
        return jsonify({'message': '当前状态⽆法完结!'}), 400
    if not can_modify_incident(current_user, incident):
         return jsonify({'message': '⽆权限执⾏此操作'}), 403
    incident.status = IncidentStatus.RESOLVED
    incident.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': '事件已完结!'}), 200
"""
tags:
  - 事件管理
"""
# 关闭
@incident.route('/incidents/<int:incident_id>/close', methods=['POST'])
@token_required
@role_required([0, -1])  # 只有领导⼩组和管理员可以访问
def close_incident(current_user, incident_id):
    """
    openapi:
      summary: 关闭事件
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
          description: 事件已关闭
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 事件已关闭!
        '400':
          description: 当前状态无法关闭
        '401':
          description: 未授权
        '403':
          description: 无权限执行此操作
        '404':
          description: 事件不存在
    """
    incident = Incident.query.get_or_404(incident_id)
    if incident.status != IncidentStatus.RESOLVED:
        return jsonify({'message': '当前状态⽆法关闭!'}), 400
    if not can_modify_incident(current_user, incident):
        return jsonify({'message': '⽆权限执⾏此操作'}), 403
    incident.status = IncidentStatus.CLOSED
    incident.closed_at = datetime.utcnow() #记录关闭时间
    db.session.commit()
    return jsonify({'message': '事件已关闭!'}), 200
"""
tags:
  - 事件管理
"""
@incident.route('/incidents/<int:incident_id>', methods=['GET'])
@token_required
def get_incident(current_user, incident_id):
    """
    openapi:
      summary: 获取事件详情
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
          description: 成功返回事件信息
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Incident'
        '401':
          description: 未授权
        '404':
          description: 事件不存在
    """
    incident = Incident.query.get_or_404(incident_id)
    #只要登录了， 就可以查看事件
    incident_data = {
      'incident_id': incident.incident_id,
      'incident_info': incident.incident_info,
      'process_status': incident.process_status,
      'response_log':incident.response_log,
      'incident_level': incident.incident_level,
      'is_aviation': incident.is_aviation,
      'event_type_id': incident.event_type_id,
      'attachment_url': incident.attachment_url,
      'submitted_by_user_id': incident.submitted_by_user_id,
      'status': incident.status.name, # 返回枚举名称
      'rejection_reason': incident.rejection_reason,
      'resolution_measures': incident.resolution_measures,
      'closed_at': incident.closed_at.isoformat() if incident.closed_at else None,
      'resolved_at': incident.resolved_at.isoformat() if incident.resolved_at else None,
    }
    return jsonify(incident_data), 200
