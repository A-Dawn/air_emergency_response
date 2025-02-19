# /www/wwwroot/air_emergency_response/routes/security_check.py
from flask import Blueprint, request, jsonify, current_app
from models.security_check import SecurityCheck
from functools import wraps
from models.user import User
from utils.jwt_utils import decode_jwt_token
from models import db

security_check = Blueprint('security_check', __name__)

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
    - 安全检查
"""
@security_check.route('/security-checks', methods=['POST'])
@token_required
def create_security_check(current_user):
    """
    openapi:
      summary: 创建安全检查记录
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SecurityCheck'
      responses:
        '201':
          description: 安全检查记录创建成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 安全检查记录创建成功!
        '401':
          description: 未授权
    """
    data = request.get_json()
    new_check = SecurityCheck(
        check_record=data['check_record'],
        issue_tracking=data['issue_tracking'],
        improvement_status=data['improvement_status'],
        evaluation_report=data.get('evaluation_report', '')
    )
    db.session.add(new_check)
    db.session.commit()
    return jsonify({'message': '安全检查记录创建成功!'}), 201

"""
  tags:
    - 安全检查
"""
@security_check.route('/security-checks/<int:check_id>', methods=['GET'])
@token_required
def get_security_check(current_user, check_id):
    """
    openapi:
      summary: 获取安全检查记录
      security:
        - bearerAuth: []
      parameters:
        - name: check_id
          in: path
          required: true
          description: 安全检查记录ID
          schema:
            type: integer
      responses:
        '200':
          description: 成功返回安全检查记录信息
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SecurityCheck'
        '401':
          description: 未授权
        '404':
          description: 安全检查记录不存在
    """
    check = SecurityCheck.query.filter_by(check_id=check_id).first()
    if not check:
        return jsonify({'message': '安全检查记录不存在!'}), 404
    return jsonify({
        'check_id': check.check_id,
        'check_record': check.check_record,
        'issue_tracking': check.issue_tracking,
        'improvement_status': check.improvement_status,
        'evaluation_report': check.evaluation_report
    }), 200