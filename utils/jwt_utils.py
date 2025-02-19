# utils/jwt_utils.py
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import User  # 导入 User 模型

def generate_jwt_token(user, secret_key):
    """生成 JWT 令牌"""
    payload = {
        'user_id': user.user_id,
        'role_level': user.role_level,  #  添加角色信息
        'exp': datetime.utcnow() + timedelta(days=1)  # 过期时间为 1 天
    }
    # 使用 HS256 算法签名 JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def decode_jwt_token(token, secret_key):
    """验证 JWT 令牌"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token 已过期,请重新登录'
    except jwt.InvalidTokenError:
        return 'Token 无效,请重新登录'

def token_required(f):
    """Token 验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少 Token!'}), 401

        try:
            payload = decode_jwt_token(token, current_app.config['JWT_SECRET_KEY'])
            if isinstance(payload, str): #  token已过期或者⽆效
                return jsonify({'message': payload}), 401

            user_id = payload['user_id']
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({'message': '⽤户不存在!'}), 401

        except Exception as e:
            return jsonify({'message': 'Token 验证失败!' + str(e) }), 401
        # 将当前用户传递给被装饰的函数
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(role_levels):
    """
    权限控制装饰器，限制只有特定角色的用户才能访问
    :param role_levels: 允许访问的角色级别列表 (例如: [0, 1] 表示只有全局管理员和领导小组可以访问)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': '缺少Token!'}), 401

            try:
                payload = decode_jwt_token(token, current_app.config['JWT_SECRET_KEY'])

                if isinstance(payload, str): # token已过期或者⽆效
                   return jsonify({'message': payload}), 401

                user_id = payload['user_id']
                current_user = User.query.get(user_id)

                if not current_user:
                    return jsonify({'message': '用户不存在!'}), 401

                # 权限检查：管理员直接放⾏，否则检查⻆⾊级别是否在允许的列表中
                if current_user.role_level != -1 and current_user.role_level not in role_levels:
                    return jsonify({'message': '权限不⾜!'}), 403

            except Exception as e:
                return jsonify({'message': 'Token 验证失败!' + str(e)}), 401

            # 将当前用户传递给被装饰的函数
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator