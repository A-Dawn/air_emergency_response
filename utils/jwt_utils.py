import jwt
from datetime import datetime, timedelta
from gmssl import sm2

def generate_jwt_token(user, secret_key):
    """
    生成JWT令牌（使用HS256算法签名，SM2公钥加密）
    """
    payload = {
        'user_id': user.user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    # 生成JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    # SM2加密
    sm2_crypt = sm2.CryptSM2(public_key=user.sm2_public_key)
    return sm2_crypt.encrypt(token.encode('utf-8'))

def decode_jwt_token(encrypted_token, secret_key, sm2_private_key):
    """
    解密并验证JWT令牌（需传入SM2私钥）
    """
    try:
        # SM2解密
        sm2_crypt = sm2.CryptSM2(private_key=sm2_private_key)
        decrypted_token = sm2_crypt.decrypt(encrypted_token).decode('utf-8')
        # JWT验证
        payload = jwt.decode(decrypted_token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except sm2.SM2Error as e:
        return f"解密失败: {str(e)}"
    except jwt.ExpiredSignatureError:
        return 'Token已过期，请重新登录'
    except jwt.InvalidTokenError:
        return 'Token不合法，请重新登录'