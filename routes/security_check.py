# /www/wwwroot/air_emergency_response/routes/security_check.py
from flask import Blueprint, request, jsonify, current_app
from models.security_check import SecurityCheck
from functools import wraps

from models.user import User
from utils.jwt_utils import decode_jwt_token
from .. import db

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

@security_check.route('/security-checks', methods=['POST'])
@token_required
def create_security_check(current_user):
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

@security_check.route('/security-checks/<int:check_id>', methods=['GET'])
@token_required
def get_security_check(current_user, check_id):
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