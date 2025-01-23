from gmssl import sm2

def generate_sm2_key_pair():
    # 生成SM2密钥对
    sm2_crypt = sm2.CryptSM2()
    private_key = sm2_crypt.private_key
    public_key = sm2_crypt.public_key
    return private_key, public_key

def encrypt_sm4(data, key):
    # 使用SM4加密数据
    sm4_crypt = sm2.CryptSM4()
    encrypted_data = sm4_crypt.encrypt(data.encode(), key.encode(), iv=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    return encrypted_data

def decrypt_sm4(encrypted_data, key):
    # 使用SM4解密数据
    sm4_crypt = sm2.CryptSM4()
    decrypted_data = sm4_crypt.decrypt(encrypted_data, key.encode(), iv=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    return decrypted_data.decode()