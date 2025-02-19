import ctypes
import os

# Load thư viện C
lib_path = os.path.abspath("aes.so")  # Trên Windows đổi thành "aes.dll"
aes = ctypes.CDLL(lib_path)

# Khai báo kiểu dữ liệu
aes.encrypt_cfb.argtypes = (
    ctypes.POINTER(ctypes.c_uint8),  # plaintext
    ctypes.POINTER(ctypes.c_uint8),  # key
    ctypes.POINTER(ctypes.c_uint8),  # iv
    ctypes.POINTER(ctypes.c_uint8),  # ciphertext
    ctypes.c_int,  # length
)

def encrypt_cfb(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(key) != 32 or len(iv) != 16:
        raise ValueError("AES-256-CFB yêu cầu key 32 byte và IV 16 byte.")
    
    ciphertext = (ctypes.c_uint8 * len(plaintext))()
    
    aes.encrypt_cfb(
        (ctypes.c_uint8 * len(plaintext))(*plaintext),
        (ctypes.c_uint8 * 32)(*key),
        (ctypes.c_uint8 * 16)(*iv),
        ciphertext,
        len(plaintext)
    )
    
    return bytes(ciphertext)

aes.decrypt_cfb.argtypes = (
    ctypes.POINTER(ctypes.c_uint8),  # ciphertext
    ctypes.POINTER(ctypes.c_uint8),  # key
    ctypes.POINTER(ctypes.c_uint8),  # iv
    ctypes.POINTER(ctypes.c_uint8),  # plaintext
    ctypes.c_int,  # length
)

def decrypt_cfb(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(key) != 32 or len(iv) != 16:
        raise ValueError("AES-256-CFB yêu cầu key 32 byte và IV 16 byte.")
    
    plaintext = (ctypes.c_uint8 * len(ciphertext))()

    aes.decrypt_cfb(
        (ctypes.c_uint8 * len(ciphertext))(*ciphertext),
        (ctypes.c_uint8 * 32)(*key),
        (ctypes.c_uint8 * 16)(*iv),
        plaintext,
        len(ciphertext)
    )

    return bytes(plaintext)

# Kiểm thử
plaintext = b"1234567890123456"  # 16 byte
key = b"0123456789abcdef0123456789abcdef"  # 32 byte
iv = b"abcdefghijklmnop"  # 16 byte

ciphertext = encrypt_cfb(plaintext, key, iv)
print("Ciphertext:", ciphertext.hex())
