import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from aes import encrypt_cfb, decrypt_cfb

def generate_key_pair():
    """Tạo cặp khóa RSA (public key và private key)."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_private_key(private_key, file_path):
    """Lưu private key vào file."""
    with open(file_path, 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )


def load_private_key(file_path):
    """Tải private key từ file."""
    with open(file_path, 'rb') as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )


def save_public_key(public_key, file_path):
    """Lưu public key vào file."""
    with open(file_path, 'wb') as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def load_public_key(file_path):
    """Tải public key từ file."""
    with open(file_path, 'rb') as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )


def encrypt_file(file_path: str, public_key, output_path: str) -> None:
    """Mã hóa file bằng public key."""
    # Tạo salt và key ngẫu nhiên để mã hóa file
    salt = os.urandom(16)
    key = os.urandom(32)

    # Đọc nội dung file gốc
    with open(file_path, 'rb') as f:
        plaintext = f.read()

    # Mã hóa nội dung file bằng AES
    iv = os.urandom(16)  # Khởi tạo vector IV
    ciphertext = encrypt_cfb(plaintext, key, iv)

    # Mã hóa key AES bằng public key RSA
    encrypted_key = public_key.encrypt(
        key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Lưu file mã hóa (bao gồm salt, IV, encrypted_key và ciphertext)
    with open(output_path, 'wb') as f:
        f.write(salt + iv + encrypted_key + ciphertext)


def decrypt_file(file_path: str, private_key, output_path: str) -> None:
    """Giải mã file bằng private key."""
    # Đọc file mã hóa
    with open(file_path, 'rb') as f:
        data = f.read()

    # Trích xuất các phần từ file mã hóa
    salt = data[:16]
    iv = data[16:32]
    encrypted_key = data[32:288]  # Độ dài encrypted_key là 256 bytes (RSA 2048-bit)
    ciphertext = data[288:]

    # Giải mã key AES bằng private key RSA
    key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Giải mã nội dung file bằng AES-CFB
    plaintext = decrypt_cfb(ciphertext, key, iv)

    # Lưu file gốc
    with open(output_path, 'wb') as f:
        f.write(plaintext)
