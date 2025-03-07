from flask import Flask, Blueprint, request, jsonify
from models.user import User
from models.login_attempt import LoginAttempt
from utils.jwt_utils import generate_jwt_token
from flask import current_app
import binascii
from gmssl import sm3
import datetime
from models import db
import uuid  # 导入 uuid

auth = Blueprint('auth', __name__)
MAX_FAILED_ATTEMPTS = 5
BAN_DURATION = 300

def is_user_banned(username):
    """检查用户是否被锁定"""
    user = User.query.filter_by(username=username).first()
    if not user:
        return False

    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=BAN_DURATION)
    failed_attempts = LoginAttempt.query.filter(
        LoginAttempt.user_id == user.user_id,
        LoginAttempt.success == False,
        LoginAttempt.attempt_time >= cutoff_time
    ).count()
    return failed_attempts >= MAX_FAILED_ATTEMPTS

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


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    ip_address = request.remote_addr

    # 账户锁定检查
    if is_user_banned(username):
        return jsonify({'message': '账户已锁定,请稍后重试!'}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        record_failed_attempt(username, ip_address)
        return jsonify({'message': '用户不存在!'}), 404

    if user.salt is None:
        print("Error: Salt is None!")
        return jsonify({'message': '用户数据异常,请联系管理员!'}), 500

    salt = user.salt
    salted_password = salt + password
    message = [x for x in salted_password.encode('utf-8')]
    hashed_password_hex = sm3.sm3_hash(message)  # hashed_password 已经是字节串
    #hashed_password_hex = binascii.hexlify(hashed_password).decode('utf-8')  # 直接 hexlify

    # 比较哈希密码并添加匹配状态信息
    password_match = user.hashed_password == hashed_password_hex

    if not password_match:
        record_failed_attempt(username, ip_address)
        return jsonify({
            'message': '密码错误!',
            'password_match': password_match,  # 添加匹配状态
            'stored_hash': user.hashed_password, #方便比对
            'calculated_hash': hashed_password_hex
        }), 401

    # 密码验证通过,生成 Token
    token = generate_jwt_token(user, current_app.config['JWT_SECRET_KEY'])
    record_successful_attempt(username, ip_address)
    return jsonify({
        'token': token,
        'password_match': password_match  # 添加匹配状态
    }), 200
