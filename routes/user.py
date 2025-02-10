from flask import Blueprint, request, jsonify, current_app
from models.user import User
from utils.jwt_utils import generate_jwt_token, decode_jwt_token
from utils.sm_utils import load_server_sm2_private_key  # load 私钥
from functools import wraps
from models import db

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
    """创建用户 (仅管理员)"""
    if current_user.role_level != 1:
        return jsonify({'message': '权限不足!'}), 403

    data = request.get_json()
    username = data['username']
    public_key = data['sm2_public_key']  # 客户端生成的公钥
    role_level = data['role_level']

    if not username:
        return jsonify({'message': '用户名不能为空!'}), 400
    if not public_key:
        return jsonify({'message': 'SM2公钥不能为空!'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户已存在!'}), 400

    new_user = User(username=username, sm2_public_key=public_key, role_level=role_level)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': '用户注册成功!'}), 201  # 不返回私钥!

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
