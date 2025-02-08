import jwt
from datetime import datetime, timedelta
from gmssl import sm2
from .sm_utils import load_server_sm2_private_key  # 确保正确导入

def generate_jwt_token(user, secret_key):
    """生成 JWT 令牌 (使用 HS256 算法签名, SM2 加密)"""
    payload = {
        'user_id': user.user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    # 生成 JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    # 加载服务器私钥
    sm2_private_key = load_server_sm2_private_key()
    sm2_crypt = sm2.CryptSM2(private_key=sm2_private_key)
    # 使用 SM2 加密整个 token
    encrypted_token = sm2_crypt.encrypt(token.encode('utf-8'))
    return encrypted_token

def decode_jwt_token(encrypted_token, secret_key, sm2_private_key):
    """解密并验证 JWT 令牌 (需传入 SM2 私钥)"""
    try:
        # 使用 SM2 解密
        sm2_crypt = sm2.CryptSM2(private_key=sm2_private_key)  # 使用传入的私钥
        decrypted_token = sm2_crypt.decrypt(encrypted_token).decode('utf-8')

        # 验证 JWT
        payload = jwt.decode(decrypted_token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except sm2.SM2Error as e:
        return f"SM2 解密失败: {str(e)}"
    except jwt.ExpiredSignatureError:
        return 'Token 已过期,请重新登录'
    except jwt.InvalidTokenError:
        return 'Token 不合法,请重新登录'


