# /www/wwwroot/air_emergency_response/routes/user.py
from flask import Blueprint, request, jsonify, current_app
from models.user import User
from utils.jwt_utils import generate_jwt_token, decode_jwt_token
from utils.sm_utils import generate_sm2_key_pair
from functools import wraps
from .. import db

user = Blueprint('user', __name__)

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

@user.route('/users', methods=['POST'])
@token_required
def create_user(current_user):
    if current_user.role_level != 1:
        return jsonify({'message': '权限不足!'}), 403
    data = request.get_json()
    username = data['username']
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户已存在!'}), 400
    private_key, public_key = generate_sm2_key_pair()
    new_user = User(username=username, sm2_public_key=public_key, role_level=data['role_level'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': '用户注册成功!', 'private_key': private_key}), 201

@user.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message': '用户不存在!'}), 404
    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'role_level': user.role_level
    }), 200