from flask import Flask, request, jsonify, send_file
import os
import io
import uuid
from cryptography.fernet import Fernet
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình thư mục lưu trữ file và database
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
db = SQLAlchemy(app)

# Model database
class FileRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(36), unique=True, nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    encryption_key = db.Column(db.String(44), nullable=False)  # 44 ký tự của Fernet key
    share_key = db.Column(db.String(10), unique=True, nullable=False)

# Khởi tạo database
with app.app_context():
    db.create_all()

# Route upload file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Tạo thông tin cho file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    encryption_key = Fernet.generate_key().decode()
    share_key = str(uuid.uuid4())[:10]  # Tạo key chia sẻ (10 ký tự)

    # Mã hóa file trước khi lưu
    cipher = Fernet(encryption_key)
    encrypted_data = cipher.encrypt(file.read())
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)

    # Lưu thông tin vào database
    new_file = FileRecord(
        file_id=file_id,
        file_path=file_path,
        encryption_key=encryption_key,
        share_key=share_key
    )
    db.session.add(new_file)
    db.session.commit()

    return jsonify({'share_key': share_key})

# Route download file
@app.route('/download/<share_key>', methods=['GET'])
def download_file(share_key):
    # Tìm file dựa trên share_key
    file_record = FileRecord.query.filter_by(share_key=share_key).first()
    if not file_record:
        return jsonify({'error': 'File not found'}), 404

    # Giải mã file
    cipher = Fernet(file_record.encryption_key)
    with open(file_record.file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)

    # Gửi file về client
    return send_file(
        io.BytesIO(decrypted_data),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='downloaded_file'
    )

if __name__ == '__main__':
    app.run(debug=True)
