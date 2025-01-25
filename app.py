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
from cryptography.hazmat.backends import default_backend

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
    """
    Hàm này đọc public key từ file và trả về đối tượng public key.
    """
    # Tạo đường dẫn file tạm thời để lưu public key
    public_key_path = os.path.join(UPLOAD_FOLDER, secure_filename(public_key_file.filename))

    # Lưu file public key vào thư mục tạm
    public_key_file.save(public_key_path)

    # Mở và đọc file public key
    with open(public_key_path, 'rb') as key_file:
        # Sử dụng cryptography để tải khóa công khai từ file PEM
        public_key = serialization.load_pem_public_key(
            key_file.read(),  # Đọc nội dung public key
            backend=default_backend()
        )
    return public_key

@app.route('/upload', methods=['POST'])
def upload_file():
    # Kiểm tra xem yêu cầu có chứa file và public_key không
    if 'file' not in request.files:
        return jsonify({"error": "Không có file trong yêu cầu"}), 400

    if 'public_key' not in request.files:
        return jsonify({"error": "Không có public key trong yêu cầu"}), 400

    # Lấy file và public_key từ yêu cầu
    file = request.files['file']
    public_key_file = request.files['public_key']

    # Kiểm tra xem file có được chọn hay không
    if file.filename == '':
        return jsonify({"error": "Không có file được chọn"}), 400

    # Lưu file tải lên vào thư mục tạm thời trên server
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(file_path)

    # Lưu public key vào hệ thống tệp
    public_key = load_public_key_from_file(public_key_file)

    # Tạo key đặc biệt cho file
    key = generate_key()

    # Mã hóa file bằng public key
    encrypted_file_path = file_path + '.enc'
    encrypt_file(file_path=file_path, public_key=public_key, output_path=encrypted_file_path)

    # Lưu thông tin vào cơ sở dữ liệu mà không cần mật khẩu
    file_record = FileRecord(file_name=file.filename, file_path=encrypted_file_path, key=key)
    db.session.add(file_record)
    db.session.commit()

    return jsonify({"message": "File đã được mã hóa và tải lên thành công!", "key": key})

@app.route('/download', methods=['GET'])
def download_file():
    file_key = request.args.get('key')
    private_key_file = request.files.get('private_key')  # Nhận private key từ client

    if not file_key or not private_key_file:
        return jsonify({"error": "Vui lòng cung cấp key và private key"}), 400

    # Tìm kiếm bản ghi file trong cơ sở dữ liệu
    file_record = FileRecord.query.filter_by(key=file_key).first()
    if not file_record:
        return jsonify({"error": "Không tìm thấy file với key này"}), 404

    # Lưu private key tạm thời và load key từ file
    private_key = load_private_key_from_file(private_key_file)

    # Tạo file giải mã tạm thời
    decrypted_file_path = file_record.file_path.replace('.enc', '.decrypted')

    # Giải mã file bằng private key RSA và khóa AES
    try:
        decrypt_file(file_path=file_record.file_path, private_key=private_key, output_path=decrypted_file_path)
    except Exception as e:
        return jsonify({"error": "Sai private key hoặc file không hợp lệ"}), 403

    # Trả về file đã giải mã cho client
    return send_file(decrypted_file_path, as_attachment=True)

# Hàm để tải private key từ file
def load_private_key_from_file(private_key_file):
    """Load private key từ file (PEM format)."""
    private_key = serialization.load_pem_private_key(
        private_key_file.read(),
        password=None  # Không có mật khẩu bảo vệ key
    )
    return private_key

@app.route('/client', methods=['GET', 'POST'])
def client():
    if request.method == 'POST':
        file = request.files.get('file')
        public_key_file = request.files.get('public_key')

        # Kiểm tra xem file và public key có tồn tại không
        if not file or not public_key_file:
            return jsonify({"error": "Thiếu file hoặc public key"}), 400

        # Lưu file và public key lên server
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        public_key_path = os.path.join(UPLOAD_FOLDER, secure_filename(public_key_file.filename))

        file.save(file_path)
        public_key_file.save(public_key_path)

        # Đọc public key từ file đã tải lên
        public_key = load_public_key_from_file(public_key_file)

        # Tạo key cho file
        key = generate_key()

        # Mã hóa file bằng public key
        encrypted_file_path = file_path + '.enc'
        encrypt_file(file_path=file_path, public_key=public_key, output_path=encrypted_file_path)

        # Lưu thông tin vào cơ sở dữ liệu
        file_record = FileRecord(file_name=file.filename, file_path=encrypted_file_path, key=key)
        db.session.add(file_record)
        db.session.commit()

        return jsonify({"message": "File đã được mã hóa và tải lên thành công!", "key": key})

    return '''
        <form method="post" enctype="multipart/form-data">
            <label for="file">Chọn file tải lên:</label>
            <input type="file" name="file" id="file" /><br>
            <label for="public_key">Chọn Public Key:</label>
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
            <li>
                <form action="/download" method="get" enctype="multipart/form-data">
                    <label for="key">Nhập key:</label>
                    <input type="text" name="key" id="key" required><br>
                    <label for="private_key">Chọn private key RSA:</label>
                    <input type="file" name="private_key" id="private_key" required><br>
                    <input type="submit" value="Tải xuống file">
                </form>
            </li>
        </ul>
    '''

if __name__ == '__main__':
    app.run(debug=True)
