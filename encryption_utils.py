import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes) -> bytes:
    """Tạo khóa mã hóa từ password và salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_file(file_path: str, password: str, output_path: str) -> None:
    """Mã hóa file bằng password."""
    # Tạo salt và khởi tạo khóa
    salt = os.urandom(16)
    key = derive_key(password, salt)

    # Đọc nội dung file gốc
    with open(file_path, 'rb') as f:
        plaintext = f.read()

    # Mã hóa nội dung
    iv = os.urandom(16)  # Khởi tạo vector IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Lưu file mã hóa (bao gồm salt và IV)
    with open(output_path, 'wb') as f:
        f.write(salt + iv + ciphertext)

def decrypt_file(file_path: str, password: str, output_path: str) -> None:
    """Giải mã file bằng password."""
    # Đọc file mã hóa
    with open(file_path, 'rb') as f:
        data = f.read()

    # Trích xuất salt, IV và nội dung mã hóa
    salt = data[:16]
    iv = data[16:32]
    ciphertext = data[32:]

    # Tạo lại khóa từ password và salt
    key = derive_key(password, salt)

    # Giải mã nội dung
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Lưu file gốc
    with open(output_path, 'wb') as f:
        f.write(plaintext)
