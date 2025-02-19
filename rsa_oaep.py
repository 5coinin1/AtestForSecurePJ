import os
import hashlib
import gmpy2
import random

def is_prime(n, k=10):
    """Kiểm tra số nguyên tố bằng thuật toán Miller-Rabin."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(bits=1024):
    """Sinh số nguyên tố lớn với độ dài bits."""
    while True:
        num = random.getrandbits(bits) | (1 << bits - 1) | 1
        if is_prime(num):
            return num

def generate_key_pair(bits=2048):
    """Tạo cặp khóa RSA (public key và private key)."""
    p = generate_large_prime(bits // 2)
    q = generate_large_prime(bits // 2)
    
    N = p * q
    phi = (p - 1) * (q - 1)
    
    e = 65537  # Giá trị công khai tiêu chuẩn
    d = gmpy2.invert(e, phi)  # Tính d = e^(-1) mod phi
    
    public_key = (N, e)
    private_key = (N, int(d))  # Convert d về int để dễ sử dụng

    return private_key, public_key

def sha256(data):
    return hashlib.sha256(data).digest()

def mgf1(seed, length):
    output = b""
    counter = 0
    while len(output) < length:
        counter_bytes = counter.to_bytes(4, 'big')
        output += sha256(seed + counter_bytes)
        counter += 1
    return output[:length]

def oaep_pad(message, key_size):
    k = key_size // 8
    hash_len = 32
    ps_len = k - len(message) - 2 * hash_len - 2
    if ps_len < 0:
        raise ValueError("Message quá dài để padding với OAEP!")
    ps = b'\x00' * ps_len
    db = sha256(b"") + ps + b'\x01' + message
    seed = os.urandom(hash_len)
    db_mask = mgf1(seed, k - hash_len - 1)
    masked_db = bytes(a ^ b for a, b in zip(db, db_mask))
    seed_mask = mgf1(masked_db, hash_len)
    masked_seed = bytes(a ^ b for a, b in zip(seed, seed_mask))
    return b'\x00' + masked_seed + masked_db

def oaep_unpad(padded_message):
    hash_len = 32
    k = len(padded_message)
    if padded_message[0] != 0x00:
        raise ValueError("Sai padding!")
    masked_seed = padded_message[1:1 + hash_len]
    masked_db = padded_message[1 + hash_len:]
    seed_mask = mgf1(masked_db, hash_len)
    seed = bytes(a ^ b for a, b in zip(masked_seed, seed_mask))
    db_mask = mgf1(seed, k - hash_len - 1)
    db = bytes(a ^ b for a, b in zip(masked_db, db_mask))
    expected_hash = sha256(b"")
    if db[:hash_len] != expected_hash:
        raise ValueError("Sai padding!")
    index = db.find(b'\x01', hash_len)
    if index == -1:
        raise ValueError("Sai padding!")
    return db[index + 1:].decode()

def encrypt(plaintext, public_key, key_size):
    N, e = public_key
    padded_message = oaep_pad(plaintext.encode(), key_size)
    num_repr = int.from_bytes(padded_message, 'big')
    ciphertext = gmpy2.powmod(num_repr, e, N)
    return int(ciphertext)

def decrypt(ciphertext, private_key, key_size):
    N, d = private_key
    num_repr = gmpy2.powmod(ciphertext, d, N)
    padded_message = int(num_repr).to_bytes(key_size // 8, 'big')
    return oaep_unpad(padded_message)

if __name__ == '__main__':
    private_key, public_key = generate_key_pair()
    key_size = 2048
    key = "mysecretkey"
    encrypted_key = encrypt(key, public_key, key_size)
    print("Encrypted Key:", encrypted_key)
    decrypted_key = decrypt(encrypted_key, private_key, key_size)
    print("Decrypted Key:", decrypted_key)
