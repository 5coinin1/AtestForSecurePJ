from flask import Flask, request, render_template, send_from_directory
import os

app = Flask(__name__)

# Thư mục lưu trữ file upload
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Trang chủ: Form upload file
@app.route('/')
def index():
    return render_template('index.html')

# Xử lý upload file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return f"File {file.filename} uploaded successfully!"

# Download file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
