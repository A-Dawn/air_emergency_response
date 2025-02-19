# /www/wwwroot/air_emergency_response/routes/emergency_plan.py
from flask import Blueprint, current_app, request, jsonify
from models.emergency_plan import EmergencyPlan
from functools import wraps
from models.user import User
from utils.jwt_utils import decode_jwt_token
from models import db

emergency_plan = Blueprint('emergency_plan', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少Token!'}), 401
        user_id = decode_jwt_token(token, current_app.config['JWT_SECRET_KEY'])
        if isinstance(user_id, str):
            return jsonify({'message': user_id}), 401
        current_user = User.query.filter_by(user_id=user_id).first()
        if not current_user:
            return jsonify({'message': '用户不存在!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

"""
  tags:
    - 应急预案
"""
@emergency_plan.route('/emergency-plans', methods=['POST'])
@token_required
def create_emergency_plan(current_user):
    """
    openapi:
      summary: 创建应急预案
      description: 创建新的应急预案。
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EmergencyPlan'
      responses:
        '201':
          description: 应急预案创建成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 应急预案创建成功!
        '401':
          description: 未授权访问
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 缺少Token!
    """
    data = request.get_json()
    new_plan = EmergencyPlan(plan_details=data['plan_details'], version=data['version'], status=data['status'])
    db.session.add(new_plan)
    db.session.commit()
    return jsonify({'message': '应急预案创建成功!'}), 201

"""
  tags:
    - 应急预案
"""
@emergency_plan.route('/emergency-plans/<int:plan_id>', methods=['GET'])
@token_required
def get_emergency_plan(current_user, plan_id):
    """
    openapi:
      summary: 获取应急预案
      description: 根据ID获取指定的应急预案。
      security:
        - bearerAuth: []
      parameters:
        - name: plan_id
          in: path
          required: true
          description: 应急预案ID
          schema:
            type: integer
      responses:
        '200':
          description: 成功返回应急预案信息
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EmergencyPlan'
        '401':
          description: 未授权访问
        '404':
          description: 应急预案不存在
    """
    plan = EmergencyPlan.query.filter_by(plan_id=plan_id).first()
    if not plan:
        return jsonify({'message': '应急预案不存在!'}), 404
    return jsonify({
        'plan_id': plan.plan_id,
        'plan_details': plan.plan_details,
        'version': plan.version,
        'status': plan.status
    }), 200