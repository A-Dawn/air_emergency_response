from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from forms import EventTypeForm
from models import db, EventType  # 确保从 models 导入 EventType
from utils.jwt_utils import token_required, role_required  # 确保 utils 路径正确

event_type = Blueprint('event_type', __name__)
"""
tags:
  - 事件类型
"""
@event_type.route('/admin/event-types', methods=['GET'])
@token_required
@role_required([0, -1])  # 只有全局管理员和领导小组可以访问
def list_event_types(current_user):
    """
    openapi:
      summary: 获取所有事件类型（管理员）
      security:
        - bearerAuth: []
      responses:
        '200':
          description: 返回所有事件类型
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/EventType'
        '401':
          description: 未授权
        '403':
          description: 权限不足
    """
    event_types = EventType.query.all()
    return jsonify([{'type_id': et.type_id, 'type_name': et.type_name, 'is_aviation': et.is_aviation} for et in event_types])

"""
tags:
  - 事件类型
"""
@event_type.route('/admin/event-types/create', methods=['GET', 'POST'])
@token_required
@role_required([0, -1])  # 只有全局管理员和领导小组可以访问
def create_event_type(current_user):
    """
    openapi:
      summary: 创建事件类型（管理员）
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EventType'
      responses:
        '201':
          description: 事件类型创建成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 事件类型创建成功!
        '400':
            description: 事件类型创建失败
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    errors:
                      type: object
                      description: 错误信息
        '401':
          description: 未授权
        '403':
          description: 权限不足
    """
    form = EventTypeForm()
    if form.validate_on_submit():
        type_name = form.type_name.data
        is_aviation = form.is_aviation.data
        new_event_type = EventType(type_name=type_name, is_aviation=is_aviation)
        db.session.add(new_event_type)
        db.session.commit()
        return jsonify({'message': '事件类型创建成功!'}), 201
    return jsonify({'errors': form.errors}), 400  # 返回错误信息
"""
tags:
  - 事件类型
"""
@event_type.route('/admin/event-types/<int:type_id>/update', methods=['GET', 'POST'])
@token_required
@role_required([0, -1])  # 只有全局管理员和领导小组可以访问
def update_event_type(current_user, type_id):
    """
      openapi:
        summary: 更新事件类型（管理员）
        security:
          - bearerAuth: []
        parameters:
          - name: type_id
            in: path
            required: true
            description: 事件类型ID
            schema:
              type: integer
        requestBody:
          required: true
          content:
              application/json:
                schema:
                    $ref: '#/components/schemas/EventType'
        responses:
          '200':
            description: 事件类型更新成功
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: 事件类型更新成功!
          '400':
            description: 事件类型更新失败
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    errors:
                      type: object
                      description: 错误信息
          '401':
            description: 未授权
          '403':
            description: 权限不足
          '404':
            description: 事件类型不存在
    """
    event_type = EventType.query.get_or_404(type_id)
    form = EventTypeForm(obj=event_type)  # 使用 obj 参数初始化表单
    if form.validate_on_submit():
        event_type.type_name = form.type_name.data
        event_type.is_aviation = form.is_aviation.data
        db.session.commit()
        return jsonify({'message': '事件类型更新成功!'}), 200
    return jsonify({'errors': form.errors}), 400  # 返回错误信息

"""
tags:
  - 事件类型
"""
@event_type.route('/admin/event-types/<int:type_id>/delete', methods=['POST'])
@token_required
@role_required([0, -1])  # 只有全局管理员和领导小组可以访问
def delete_event_type(current_user, type_id):
    """
    openapi:
      summary: 删除事件类型（管理员）
      security:
        - bearerAuth: []
      parameters:
        - name: type_id
          in: path
          required: true
          description: 事件类型ID
          schema:
            type: integer
      responses:
        '200':
          description: 事件类型删除成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 事件类型删除成功!
        '401':
          description: 未授权
        '403':
          description: 权限不足
        '404':
          description: 事件类型不存在
    """
    event_type = EventType.query.get_or_404(type_id)
    db.session.delete(event_type)
    db.session.commit()
    return jsonify({'message': '事件类型删除成功!'}), 200