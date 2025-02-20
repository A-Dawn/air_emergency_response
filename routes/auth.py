from flask import Blueprint, request, jsonify
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
    # 计算锁定时间窗口
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
"""
  tags:
    - 认证
"""
@auth.route('/login', methods=['POST'])
def login():
    """
    openapi:
      summary: 用户登录
      description: 用户登录接口，验证用户名和密码，返回 JWT 令牌。
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: 用户名
                password:
                  type: string
                  description: 密码
              required:
                - username
                - password
      responses:
        '200':
          description: 登录成功，返回 JWT 令牌
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                    description: JWT 令牌
        '401':
          description: 密码错误
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 密码错误!
        '403':
          description: 账户已锁定
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 账户已锁定,请稍后重试!
        '404':
          description: 用户不存在
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 用户不存在!
        '500':
          description: 服务器内部错误 (Salt 为空)
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: 用户数据异常,请联系管理员!
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    ip_address = request.remote_addr
    # 检查账户是否被锁定
    if is_user_banned(username):
        return jsonify({'message': '账户已锁定,请稍后重试!'}), 403
    user = User.query.filter_by(username=username).first()
    if not user:
        record_failed_attempt(username, ip_address)
        return jsonify({'message': '用户不存在!'}), 404
    # 确保salt存在
    if user.salt is None:
        print("Error: Salt is None!") # 打印错误日志
        return jsonify({'message': '用户数据异常,请联系管理员!'}), 500
    # 使用 SM3 对用户输入的密码和盐值进行哈希处理
    salt = user.salt
    salted_password = password + salt
    message = [x for x in salted_password.encode('utf-8')]
    hashed_password = sm3.sm3_hash(message)
    hashed_password_hex = binascii.hexlify(bytes(hashed_password)).decode('utf-8')
    # 比较哈希密码
    if user.hashed_password != hashed_password_hex:
        record_failed_attempt(username, ip_address)
        return jsonify({'message': '密码错误!'}), 401
    # 密码验证通过,生成 Token
    token = generate_jwt_token(user, current_app.config['JWT_SECRET_KEY'])
    record_successful_attempt(username, ip_address)
    return jsonify({'token': token}), 200
