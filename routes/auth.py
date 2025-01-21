from flask import Blueprint, request, jsonify, current_app
from models.user import User
from models.login_attempt import LoginAttempt
from utils.jwt_utils import generate_jwt_token, decode_jwt_token
from utils.sm_utils import generate_sm2_key_pair
from functools import wraps
from ... import db
import datetime

auth = Blueprint('auth', __name__)

# 最大失败次数
MAX_FAILED_ATTEMPTS = 5
# 禁止登录时间（秒）
BAN_DURATION = 300  # 5分钟

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

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户已存在!'}), 400
    private_key, public_key = generate_sm2_key_pair()
    new_user = User(username=username, sm2_public_key=public_key, role_level=data['role_level'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': '用户注册成功!', 'private_key': private_key}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        record_failed_attempt(username, request.remote_addr)
        return jsonify({'message': '用户不存在!'}), 404

    # 检查是否被禁止登录
    if is_user_banned(username):
        return jsonify({'message': '您的账户因多次失败尝试已暂时被禁止登录!'}), 403

    # 在此处添加实际的密码验证逻辑
    # 这里假设密码验证通过
    token = generate_jwt_token(user, current_app.config['JWT_SECRET_KEY'])
    record_successful_attempt(username, request.remote_addr)
    return jsonify({'token': token}), 200

def record_attempt(username, ip_address, success):
    user = User.query.filter_by(username=username).first()
    if user:
        new_attempt = LoginAttempt(user_id=user.user_id, success=success, ip_address=ip_address)
        db.session.add(new_attempt)
        db.session.commit()

def record_successful_attempt(username, ip_address):
    record_attempt(username, ip_address, True)

def record_failed_attempt(username, ip_address):
    record_attempt(username, ip_address, False)

def is_user_banned(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return False

    # 获取过去 BAN_DURATION 秒内的所有失败尝试
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=BAN_DURATION)
    failed_attempts = LoginAttempt.query.filter(
        LoginAttempt.user_id == user.user_id,
        LoginAttempt.success == False,
        LoginAttempt.attempt_time >= cutoff_time
    ).count()

    return failed_attempts >= MAX_FAILED_ATTEMPTS