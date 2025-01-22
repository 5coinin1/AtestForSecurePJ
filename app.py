import os
import random
import string
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)

# Cấu hình database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static'
db = SQLAlchemy(app)

# Mô hình lưu trữ file trong database
class FileModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tạo database
db.create_all()

# Tạo mật khẩu ngẫu nhiên
def generate_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Nén file với mật khẩu
def zip_with_password(file_path, output_path, password):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.setpassword(password.encode())
        zipf.write(file_path, arcname=os.path.basename(file_path))

# Thay đổi mật khẩu định kỳ
def update_passwords():
    files = FileModel.query.all()
    for file in files:
        new_password = generate_password()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        zip_path = file_path.replace(".txt", ".zip")

        # Nén file với mật khẩu mới
        zip_with_password(file_path, zip_path, new_password)

        # Cập nhật mật khẩu trong database
        file.password = new_password
        db.session.commit()
    print("Updated passwords at", datetime.now())

# Scheduler để thay đổi mật khẩu mỗi 24 giờ
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_passwords, trigger="interval", hours=24)
scheduler.start()

# API: Tải file lên
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Lưu file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Tạo mật khẩu ban đầu
    password = generate_password()

    # Nén file
    zip_path = file_path.replace(".txt", ".zip")
    zip_with_password(file_path, zip_path, password)

    # Lưu thông tin vào database
    new_file = FileModel(filename=filename, password=password)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully", "filename": filename, "password": password})

# API: Gửi file về người dùng
@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file = FileModel.query.get(file_id)
    if not file:
        return jsonify({"error": "File not found"}), 404

    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename.replace(".txt", ".zip"))
    return send_file(zip_path, as_attachment=True)

# Dừng scheduler khi ứng dụng dừng
@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    scheduler.shutdown()

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
