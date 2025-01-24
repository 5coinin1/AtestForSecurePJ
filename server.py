from flask import Flask, request, jsonify
import os
from cryptography.fernet import Fernet
import json

app = Flask(__name__)

# Đường dẫn thư mục lưu trữ file
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tạo và lưu key mã hóa
def generate_key():
    return Fernet.generate_key()

# Giải mã file khi tải xuống
def decrypt_file(filename, key):
    with open(filename, 'rb') as f:
        encrypted_data = f.read()
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data

# Mã hóa file khi tải lên
def encrypt_file(filename, key):
    with open(filename, 'rb') as f:
        file_data = f.read()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(file_data)
    encrypted_filename = f'{filename}.enc'
    with open(encrypted_filename, 'wb') as f:
        f.write(encrypted_data)
    return encrypted_filename

# API để tải file lên
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        key = generate_key()  # Tạo key mới cho file này
        encrypted_filename = encrypt_file(file.filename, key)
        file_path = os.path.join(UPLOAD_FOLDER, encrypted_filename)
        file.save(file_path)
        
        # Lưu key vào database (hoặc file JSON)
        with open(f'{encrypted_filename}.key', 'wb') as keyfile:
            keyfile.write(key)
        
        return jsonify({"message": "File uploaded successfully", "filename": encrypted_filename}), 200
    return jsonify({"message": "No file uploaded"}), 400

# API để tải file xuống
@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if filename:
        keyfile_path = f'{UPLOAD_FOLDER}/{filename}.key'
        encrypted_file_path = f'{UPLOAD_FOLDER}/{filename}'
        
        if os.path.exists(encrypted_file_path) and os.path.exists(keyfile_path):
            with open(keyfile_path, 'rb') as keyfile:
                key = keyfile.read()
                
            decrypted_data = decrypt_file(encrypted_file_path, key)
            response = jsonify(decrypted_data)
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        return jsonify({"message": "File not found or key missing"}), 404
    return jsonify({"message": "No filename specified"}), 400

if __name__ == '__main__':
    app.run(debug=True)
