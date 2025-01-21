import jwt
from datetime import datetime, timedelta
from gmssl import sm2

def generate_jwt_token(user, secret_key):
    # 生成JWT令牌
    payload = {
        'user_id': user.user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    sm2_crypt = sm2.CryptSM2(public_key=user.sm2_public_key)
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    # 使用SM2公钥加密令牌
    return sm2_crypt.encrypt(token.encode('utf-8'))

def decode_jwt_token(token, secret_key):
    # 解码JWT令牌
    sm2_crypt = sm2.CryptSM2()
    decrypted_token = sm2_crypt.decrypt(token).decode('utf-8')
    try:
        payload = jwt.decode(decrypted_token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return 'Token已过期，请重新登录'
    except jwt.InvalidTokenError:
        return 'Token不合法，请重新登录'