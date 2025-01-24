import os
import hashlib
from flask import Flask, request, jsonify, send_file
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    API nhận file và tải lên server
    """
    if 'file' not in request.files:
        return jsonify({"error": "Không có file trong yêu cầu"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Không có file được chọn"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Tạo key và mật khẩu cho file
    key = generate_key()
    password = generate_password()

    # Lưu thông tin file vào cơ sở dữ liệu
    file_record = FileRecord(file_name=file.filename, file_path=file_path, password=password, key=key)
    db.session.add(file_record)
    db.session.commit()

    # Trả về phản hồi với key
    return jsonify({"message": "File đã được tải lên thành công", "key": key})

@app.route('/download', methods=['GET'])
def download_file():
    """
    API trả file về cho người dùng qua key đặc biệt
    """
    file_key = request.args.get('key')
    if not file_key:
        return jsonify({"error": "Cần cung cấp key"}), 400

    file_record = FileRecord.query.filter_by(key=file_key).first()
    if not file_record:
        return jsonify({"error": "File không tồn tại hoặc key không hợp lệ"}), 404

    # Trả về file
    return send_file(file_record.file_path)

@app.route('/client', methods=['GET', 'POST'])
def client():
    """
    Client app - Giao diện tải lên và tải xuống file từ server.
    """
    if request.method == 'POST':
        # Chỉ cần form upload file, không cần phải dùng requests
        file = request.files['file']
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            
            # Tạo key cho file
            key = generate_key()

            # Lưu thông tin file vào cơ sở dữ liệu (hoặc có thể làm theo logic riêng của bạn)
            file_record = FileRecord(file_name=file.filename, file_path=file_path, password=generate_password(), key=key)
            db.session.add(file_record)
            db.session.commit()

            # Trả về phản hồi với message và key
            response = jsonify({"message": "File đã được tải lên thành công", "key": key})
            return response

    return '''
        <form method="post" enctype="multipart/form-data">
            Chọn file tải lên: <input type="file" name="file" /><br>
            <input type="submit" value="Tải lên file" />
        </form>
    '''

@app.route('/files', methods=['GET'])
def list_files():
    """
    Liệt kê tất cả các file đã được tải lên server
    """
    files = FileRecord.query.all()
    if not files:
        return jsonify({"message": "Không có file nào được tải lên"}), 404

    file_list = []
    for file in files:
        file_list.append({
            "id": file.id,
            "file_name": file.file_name,
            "key": file.key,
            "last_updated": file.last_updated
        })

    return jsonify({"files": file_list})


@app.route('/')
def hello():
    response = jsonify(message="Chào bạn, server đang hoạt động tốt!")
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

def index():
    """
    Trang chủ app - Dành cho client hoặc bất kỳ nội dung nào khác
    """
    return '''
        <h1>Ứng dụng Tải Lên và Tải Xuống File</h1>
        <a href="/client">Tải lên file</a><br>
        <a href="/download?key=YOUR_KEY_HERE">Tải xuống file bằng key</a><br>
    '''

if __name__ == '__main__':
    app.run(debug=True)
import requests

@app.route('/connect_to_web', methods=['GET'])
def connect_to_web():
    # Gửi yêu cầu GET tới ứng dụng web trên Render
    response = requests.get('https://atestforsecurepj.onrender.com/some-endpoint')

    # Kiểm tra nếu yêu cầu thành công
    if response.status_code == 200:
        return response.json()  # Trả về dữ liệu JSON từ server
    else:
        return jsonify({"error": "Không thể kết nối tới web"}), 400
