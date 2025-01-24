import requests

# Địa chỉ server
SERVER_URL = 'http://127.0.0.1:5000'

# Hàm tải file lên server
def upload_file(filepath):
    url = f"{SERVER_URL}/upload"
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f)}
        response = requests.post(url, files=files)
        print(response.json())

# Hàm tải file về từ server
def download_file(filename):
    url = f"{SERVER_URL}/download?filename={filename}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'downloaded_{filename}', 'wb') as f:
            f.write(response.content)
        print(f"File {filename} downloaded successfully!")
    else:
        print(response.json())

# Thử tải lên và tải xuống file
if __name__ == '__main__':
    # Thay đổi với file của bạn
    upload_file('your_file.txt')  # Thay thế với đường dẫn đến file bạn muốn tải lên
    download_file('your_file.txt.enc')  # Tải về file đã mã hóa
