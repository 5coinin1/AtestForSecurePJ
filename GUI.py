import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import sys
import io

# Thay đổi mã hóa đầu ra của stdout thành utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# URL của server Flask (phải thay đổi nếu sử dụng server khác)
UPLOAD_URL = "https://atestforsecurepj.onrender.com/client"
DOWNLOAD_URL = "https://atestforsecurepj.onrender.com/download"

def upload_file():
    """Tải lên file lên server."""
    file_path = filedialog.askopenfilename(title="Chọn file để tải lên")
    public_key_path = filedialog.askopenfilename(title="Chọn file public key")

    if file_path and public_key_path:
        try:
            # Mở file và public key
            files = {
                'file': open(file_path, 'rb'),
                'public_key': open(public_key_path, 'rb')
            }

            # Gửi file lên server
            response = requests.post(UPLOAD_URL, files=files)

            # Kiểm tra phản hồi từ server
            if response.status_code == 200:
                messagebox.showinfo("Thành công", "File đã được tải lên thành công!")
            else:
                messagebox.showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải lên file: {str(e)}")
        finally:
            files['file'].close()
            files['public_key'].close()

def download_file():
    """Tải file từ server xuống."""
    file_key = tk.simpledialog.askstring("Key", "Nhập key file:")
    private_key_path = filedialog.askopenfilename(title="Chọn file private key")

    if file_key and private_key_path:
        try:
            # Mở private key
            private_key_file = open(private_key_path, 'rb')

            # Gửi yêu cầu tải file từ server với key và private key
            files = {'private_key': private_key_file}
            params = {'key': file_key}

            # Gửi yêu cầu tải file
            response = requests.get(DOWNLOAD_URL, files=files, params=params)

            # Kiểm tra phản hồi từ server
            if response.status_code == 200:
                file_name = "downloaded_file"  # Tên file được tải về từ server
                with open(file_name, 'wb') as f:
                    f.write(response.content)

                messagebox.showinfo("Thành công", f"File đã được tải xuống và lưu dưới tên {file_name}")
            else:
                messagebox.showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải xuống file: {str(e)}")
        finally:
            private_key_file.close()

# Tạo GUI
def create_gui():
    root = tk.Tk()
    root.title("Ứng dụng Tải Lên và Tải Xuống File")

    # Tạo button upload
    upload_btn = tk.Button(root, text="Tải lên file", command=upload_file)
    upload_btn.pack(pady=10)

    # Tạo button download
    download_btn = tk.Button(root, text="Tải xuống file", command=download_file)
    download_btn.pack(pady=10)

    # Chạy ứng dụng GUI
    root.mainloop()

# Chạy ứng dụng
if __name__ == "__main__":
    create_gui()
