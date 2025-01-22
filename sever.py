from flask import Flask, request, jsonify, send_file
import os
import random
import string
import schedule
import time
from threading import Thread

app = Flask(__name__)

# Thư mục lưu file upload
UPLOAD_FOLDER = "./uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lưu mật khẩu hiện tại vào một file tạm hoặc database giả lập
PASSWORD_FILE = "password.txt"

# Khóa token ủy quyền
CLIENT_TOKEN = "your_client_token"

# Hàm tạo mật khẩu ngẫu nhiên
def generate_password(length=8):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

# Thay đổi mật khẩu định kỳ
def update_password():
    new_password = generate_password()
    with open(PASSWORD_FILE, "w") as f:
        f.write(new_password)
    print(f"[INFO] Mat khau moi: {new_password}")

# Chạy hàm thay đổi mật khẩu theo lịch
def run_schedule():
    schedule.every(1).hours.do(update_password)  # Thay đổi mật khẩu mỗi 1 giờ
    while True:
        schedule.run_pending()
        time.sleep(1)

# Endpoint: Upload file
@app.route('/upload', methods=['POST'])
def upload_file():
    token = request.headers.get('Authorization')
    if not token or token != f"Bearer {CLIENT_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200

# Endpoint: Download file
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    token = request.headers.get('Authorization')
    if not token or token != f"Bearer {CLIENT_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)

# Endpoint: Lấy mật khẩu hiện tại
@app.route('/get_password', methods=['GET'])
def get_password():
    token = request.headers.get('Authorization')
    if not token or token != f"Bearer {CLIENT_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with open(PASSWORD_FILE, "r") as f:
            password = f.read()
        return jsonify({"password": password}), 200
    except FileNotFoundError:
        return jsonify({"error": "Password not found"}), 404

if __name__ == "__main__":
    # Tạo mật khẩu ban đầu nếu chưa có
    if not os.path.exists(PASSWORD_FILE):
        update_password()

    # Chạy lịch thay đổi mật khẩu trong một thread riêng
    schedule_thread = Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()

    # Chạy server Flask
    app.run(host="0.0.0.0", port=5000)
