# utils/sm_utils.py
import os
from gmssl import sm3, func  # 导入 gmssl 库
import binascii
import hashlib

def encrypt_sm3(data, salt):
    """使用 SM3 算法对数据进行哈希 (加盐)"""
    salted_data = salt + data
    #  将字符串转换为字节串
    bytes_data = [x for x in salted_data.encode('utf-8')]
     #  创建 SM3 对象
    sm3_hash = sm3.sm3_hash(bytes_data)
    return sm3_hash

def generate_salt(length=16):
    """生成指定长度的随机盐值"""
    return os.urandom(length).hex()  # 返回 16 进制字符串

# 加密功能
def encrypt_sm4(key, data, iv):
    """SM4加密 (CBC模式)"""
    from gmssl import sm4
    sm4_crypt = sm4.CryptSM4()
    sm4_crypt.set_key(key.encode('utf-8'), sm4.SM4_ENCRYPT)
    encrypt_data = sm4_crypt.crypt_cbc(iv.encode('utf-8'), data.encode('utf-8'))
    return binascii.hexlify(encrypt_data).decode('utf-8')

# 解密功能
def decrypt_sm4(key, data, iv):
    """SM4解密 (CBC模式)"""
    from gmssl import sm4
    sm4_crypt = sm4.CryptSM4()
    sm4_crypt.set_key(key.encode('utf-8'), sm4.SM4_DECRYPT)
    # 首先将十六进制字符串转换为字节数组
    data = binascii.unhexlify(data)
    decrypt_data = sm4_crypt.crypt_cbc(iv.encode('utf-8'), data)
    return decrypt_data.decode('utf-8')

# 加载服务器 SM2 私钥
def load_server_sm2_private_key(pem_path, password=None):
    """
    加载 SM2 私钥 (PEM 格式)
    :param pem_path: 私钥文件路径
    :param password: 私钥密码 (如果私钥已加密)
    :return: SM2 私钥对象
    """
    from gmssl import sm2
    with open(pem_path, 'rb') as f:
        key = f.read()
    if password:
        password = password.encode('utf-8')
    private_key = sm2.CryptSM2(private_key=key, public_key=None)  #  只需要私钥
    return private_key
