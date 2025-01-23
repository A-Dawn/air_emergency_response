from flask import Blueprint, request, jsonify, current_app
from models.user import User
from models.login_attempt import LoginAttempt
from utils.jwt_utils import generate_jwt_token, decode_jwt_token
from utils.sm_utils import generate_sm2_key_pair
from functools import wraps
import datetime
from .. import db

auth = Blueprint('auth', __name__)

# 登录失败最大尝试次数（从配置读取）
MAX_FAILED_ATTEMPTS = 5
# 账户锁定时间（秒）
BAN_DURATION = 300

def token_required(f):
    """Token验证装饰器（强制校验SM2私钥）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少Token!'}), 401

        # 从配置中获取SM2私钥（必须通过环境变量配置！）
        sm2_private_key = current_app.config.get('SM2_PRIVATE_KEY')
        if not sm2_private_key:
            return jsonify({'message': '系统配置异常，请联系管理员!'}), 500

        # 解密并验证Token
        user_id = decode_jwt_token(
            encrypted_token=token,
            secret_key=current_app.config['JWT_SECRET_KEY'],
            sm2_private_key=sm2_private_key  # 修复：传入私钥
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
    """用户注册接口（临时方案，需客户端配合生成密钥对）"""
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'message': '用户名不能为空!'}), 400

    # 检查用户是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'message': '用户已存在!'}), 400

    # 生成SM2密钥对（正式环境应由客户端生成！此处仅为临时方案）
    private_key, public_key = generate_sm2_key_pair()
    new_user = User(
        username=username,
        sm2_public_key=public_key,
        role_level=data.get('role_level', 0)  # 默认角色等级
    )
    db.session.add(new_user)
    db.session.commit()

    # 警告：正式环境不应返回私钥！需客户端自行生成密钥对
    # return jsonify({'message': '注册成功', 'private_key': private_key}), 201
    return jsonify({'message': '注册成功（请联系管理员获取密钥）'}), 201  # 临时占位

@auth.route('/login', methods=['POST'])
def login():
    """用户登录接口（需补充密码验证逻辑）"""
    data = request.get_json()
    username = data.get('username')
    ip_address = request.remote_addr

    # 检查账户是否被锁定
    if is_user_banned(username):
        return jsonify({'message': '账户已锁定，请5分钟后重试!'}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        record_failed_attempt(username, ip_address)
        return jsonify({'message': '用户不存在!'}), 404

    # 此处应添加实际密码验证逻辑（示例仅作占位）
    # if not validate_password(data['password'], user.password_hash):
    #     record_failed_attempt(username, ip_address)
    #     return jsonify({'message': '密码错误!'}), 401

    # 生成Token
    token = generate_jwt_token(user, current_app.config['JWT_SECRET_KEY'])
    record_successful_attempt(username, ip_address)
    return jsonify({'token': token}), 200

@auth.route('/refresh-token', methods=['POST'])
@token_required
def refresh_token(current_user):
    """刷新Token接口"""
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