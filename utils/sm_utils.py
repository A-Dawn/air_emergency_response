import os
from gmssl import sm2, sm4, func
from secrets import randbits
from flask import current_app

def load_server_sm2_private_key():
    """从环境变量加载服务器 SM2 私钥"""
    private_key = current_app.config.get('SM2_PRIVATE_KEY')
    if not private_key:
        raise ValueError("SM2_PRIVATE_KEY 未配置!")  # 关键: 抛出异常
    return private_key

def generate_sm4_key():
    """生成16字节的SM4密钥"""
    return os.urandom(16).hex()  # 返回16字节的十六进制字符串

def encrypt_sm4(data, key):
    """使用SM4-CBC加密数据，返回IV+密文"""
    sm4_crypt = sm4.CryptSM4()
    key_bytes = bytes.fromhex(key)  # 将十六进制字符串转换为字节
    if len(key_bytes) != 16:
        raise ValueError("SM4 key必须为16字节")
    iv = os.urandom(16)  # 生成随机IV
    sm4_crypt.set_key(key_bytes, sm4.SM4_ENCRYPT)
    encrypted_data = sm4_crypt.crypt_cbc(iv, data.encode())
    return iv + encrypted_data  # 返回IV和密文组合

def decrypt_sm4(encrypted_data_with_iv, key):
    """从IV+密文中使用SM4-CBC解密数据"""
    sm4_crypt = sm4.CryptSM4()
    key_bytes = bytes.fromhex(key)
    if len(key_bytes) != 16:
        raise ValueError("SM4 key必须为16字节")
    iv = encrypted_data_with_iv[:16]  # 提取前16字节作为IV
    encrypted_data = encrypted_data_with_iv[16:]
    sm4_crypt.set_key(key_bytes, sm4.SM4_DECRYPT)
    decrypted_data = sm4_crypt.crypt_cbc(iv, encrypted_data)
    return decrypted_data.decode()

