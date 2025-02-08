from flask import Blueprint, request, jsonify, current_app
from models.user import User
from models.login_attempt import LoginAttempt
from utils.jwt_utils import generate_jwt_token, decode_jwt_token
from utils.sm_utils import load_server_sm2_private_key  # 导入 load_server_sm2_private_key
from functools import wraps
import datetime
from models import db

auth = Blueprint('auth', __name__)

# 从配置读取
MAX_FAILED_ATTEMPTS = 5
BAN_DURATION = 300

def token_required(f):
    """Token验证装饰器 (强制校验 SM2 私钥)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少 Token!'}), 401

        try:
            # 从 utils 中获取SM2私钥
            sm2_private_key = load_server_sm2_private_key()
        except ValueError as e:
            return jsonify({'message': str(e)}, 500)  # 返回具体的错误信息

        # 解密并验证 Token
        user_id = decode_jwt_token(
            encrypted_token=token,
            secret_key=current_app.config['JWT_SECRET_KEY'],
            sm2_private_key=sm2_private_key  # 传入私钥
        )

        # 处理验证结果
        if isinstance(user_id, str):
            return jsonify({'message': user_id}), 401  # 返回错误信息

        current_user = User.query.filter_by(user_id=user_id).first()
        if not current_user:
            return jsonify({'message': '用户不存在!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@auth.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    #  注意:  此版本仍然存在 安全隐患!   请确保在生产环境中, 永远不要返回用户的私钥!
    data = request.get_json()
    username = data.get('username')
    public_key = data.get('sm2_public_key')   #要求用户提供 公钥

    if not username:
        return jsonify({'message': '用户名不能为空!'}), 400

    if not public_key:
        return jsonify({'message': 'SM2 公钥不能为空!'}), 400

    # 检查用户是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户已存在!'}), 400

    new_user = User(
        username=username,
        sm2_public_key=public_key,  # 使用用户提供的公钥
        role_level=data.get('role_level', 0)  # 默认角色等级
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功!'}), 201  # 只返回成功消息

@auth.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    username = data.get('username')
    ip_address = request.remote_addr

    # 检查账户是否被锁定
    if is_user_banned(username):
        return jsonify({'message': '账户已锁定,请5分钟后重试!'}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        record_failed_attempt(username, ip_address)
        return jsonify({'message': '用户不存在!'}), 404

    # 此处应添加实际密码验证逻辑

    # 生成 Token
    token = generate_jwt_token(user, current_app.config['JWT_SECRET_KEY'])
    record_successful_attempt(username, ip_address)
    return jsonify({'token': token}), 200

@auth.route('/refresh-token', methods=['POST'])
@token_required
def refresh_token(current_user):
    """刷新 Token 接口"""
    new_token = generate_jwt_token(current_user, current_app.config['JWT_SECRET_KEY'])
    return jsonify({'token': new_token}), 200

# ------------------ 工具函数 ------------------
def record_attempt(username, ip_address, success):
    """记录登录尝试"""
    user = User.query.filter_by(username=username).first()
    if user:
        attempt = LoginAttempt(
            user_id=user.user_id,
            success=success,
            ip_address=ip_address
        )
        db.session.add(attempt)
        db.session.commit()

def record_successful_attempt(username, ip_address):
    """记录成功登录"""
    record_attempt(username, ip_address, True)

def record_failed_attempt(username, ip_address):
    """记录失败登录"""
    record_attempt(username, ip_address, False)

def is_user_banned(username):
    """检查用户是否被锁定"""
    user = User.query.filter_by(username=username).first()
    if not user:
        return False

    # 计算锁定时间窗口
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=BAN_DURATION)
    failed_attempts = LoginAttempt.query.filter(
        LoginAttempt.user_id == user.user_id,
        LoginAttempt.success == False,
        LoginAttempt.attempt_time >= cutoff_time
    ).count()

    return failed_attempts >= MAX_FAILED_ATTEMPTS
