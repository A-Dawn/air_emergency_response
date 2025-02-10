import jwt
from datetime import datetime, timedelta

def generate_jwt_token(user, secret_key):
    """生成 JWT 令牌"""
    payload = {
        'user_id': user.user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    # 使用 HS256 算法签名 JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def decode_jwt_token(token, secret_key):
    """验证 JWT 令牌"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return 'Token 已过期,请重新登录'
    except jwt.InvalidTokenError:
        return 'Token 不合法,请重新登录'
