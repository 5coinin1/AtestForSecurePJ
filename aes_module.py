import ctypes
import os
import platform

# Load thư viện C
# Chọn thư viện phù hợp
if platform.system() == "Windows":
    lib_path = os.path.abspath("aes.dll")  # Windows dùng DLL
else:
    lib_path = os.path.abspath("aes.so")   # Linux dùng SO

aes = ctypes.CDLL(lib_path)  # Load thư viện C

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

