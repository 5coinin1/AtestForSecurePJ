import os
import hashlib
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

from encryption_utils import encrypt_file, decrypt_file

# Cấu hình ứng dụng Flask và kết nối với cơ sở dữ liệu PostgreSQL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://forsecurity_user:t5maPyNZCK4qN5PbZC6KHN7YRugOxaeb@dpg-cu8bq0aj1k6c739t1gt0-a.oregon-postgres.render.com/forsecurity'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Khởi tạo thư mục lưu file
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model cơ sở dữ liệu
class FileRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(100), unique=True, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Khởi tạo database
with app.app_context():
    db.create_all()

# Hàm tạo key đặc biệt cho file
def generate_key():
    return hashlib.sha256(os.urandom(16)).hexdigest()

# Hàm tạo mật khẩu cho file
def generate_password():
    return hashlib.sha256(os.urandom(16)).hexdigest()

# Đảm bảo xử lý tên file an toàn và hỗ trợ Unicode
def safe_filename(filename):
    return secure_filename(filename).encode('utf-8').decode('utf-8')

# Hàm để tải public key từ file
def load_public_key_from_file(public_key_file):
    with open(public_key_file, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())
    return public_key

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Không có file trong yêu cầu"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Không có file được chọn"}), 400

    # Đường dẫn file mã hóa
    encrypted_file_path = os.path.join(UPLOAD_FOLDER, file.filename + '.enc')

    # Mã hóa file bằng password
    password = generate_password()
    encrypt_file(file_path=file, password=password, output_path=encrypted_file_path)

    # Tạo key cho file
    key = generate_key()

    # Lưu thông tin file vào cơ sở dữ liệu
    file_record = FileRecord(file_name=file.filename, file_path=encrypted_file_path, password=password, key=key)
    db.session.add(file_record)
    db.session.commit()

    return jsonify({"message": "File đã được mã hóa và tải lên thành công!", "key": key, "password": password})

@app.route('/download', methods=['GET'])
def download_file():
    file_key = request.args.get('key')
    password = request.args.get('password')

    if not file_key or not password:
        return jsonify({"error": "Vui lòng cung cấp key và password"}), 400

    file_record = FileRecord.query.filter_by(key=file_key).first()
    if not file_record:
        return jsonify({"error": "Không tìm thấy file với key này"}), 404

    # File giải mã sẽ được tạo tạm thời
    decrypted_file_path = file_record.file_path.replace('.enc', '.decrypted')

    # Giải mã file
    try:
        decrypt_file(file_path=file_record.file_path, password=password, output_path=decrypted_file_path)
    except Exception as e:
        return jsonify({"error": "Sai password hoặc file không hợp lệ"}), 403

    return send_file(decrypted_file_path, as_attachment=True)

@app.route('/client', methods=['GET', 'POST'])
def client():
    """
    Client app - Giao diện tải lên và tải xuống file từ server.
    """
    if request.method == 'POST':
        file = request.files['file']
        public_key_file = request.files['public_key']  # Nhận public key

        if file and public_key_file:
            # Lưu file tạm thời vào thư mục trên server
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Lưu public key
            public_key = load_public_key_from_file(public_key_file)

            # Tạo key cho file
            key = generate_key()

            # Mã hóa file
            password = generate_password()
            encrypted_file_path = file_path + '.enc'
            encrypt_file(file_path=file_path, public_key=public_key, password=password, output_path=encrypted_file_path)

            # Lưu thông tin vào cơ sở dữ liệu
            file_record = FileRecord(file_name=file.filename, file_path=encrypted_file_path, password=password, key=key)
            db.session.add(file_record)
            db.session.commit()

            # Trả về thông tin file đã upload
            return jsonify({"message": "File đã được mã hóa và tải lên thành công!", "key": key, "password": password})

    return '''
        <form method="post" enctype="multipart/form-data">
            <label for="file">Chọn file tải lên:</label>
            <input type="file" name="file" id="file" /><br>
            <label for="public_key">Chọn Public Key (PEM):</label>
            <input type="file" name="public_key" id="public_key" /><br>
            <input type="submit" value="Tải lên file" />
        </form>
    '''

@app.route('/')
def index():
    """
    Trang chủ app - Dành cho client hoặc bất kỳ nội dung nào khác
    """
    return '''
        <h1>Ứng dụng Tải Lên và Tải Xuống File</h1>
        <p>Chào mừng bạn đến với ứng dụng quản lý file của chúng tôi!</p>
        <ul>
            <li><a href="/client">Tải lên file</a></li>
            <li><a href="/download?key=YOUR_KEY_HERE&password=YOUR_PASSWORD_HERE">Tải xuống file bằng key</a></li>
        </ul>
    '''

if __name__ == '__main__':
    app.run(debug=True)
