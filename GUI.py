import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
import requests
import sys
import io
import os

from encryption_utils import encrypt_file
from encryption_utils import decrypt_file
from app import load_public_key
from app import load_private_key

# Thay đổi mã hóa đầu ra của stdout thành utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# URL của server Flask (phải thay đổi nếu sử dụng server khác)
UPLOAD_URL = "https://atestforsecurepj.onrender.com/upload"
DOWNLOAD_URL = "https://atestforsecurepj.onrender.com/download"

def upload_file():
    """Tải lên file đã mã hóa lên server."""
    messagebox.showinfo("Chọn File", "Vui lòng chọn file để tải lên.")
    file_path = filedialog.askopenfilename(title="Chọn file để tải lên")
    if not file_path:
        messagebox.showerror("Lỗi", "Bạn chưa chọn file!")
        return

    messagebox.showinfo("Chọn Public Key", "Vui lòng chọn file public key.")
    public_key_path = filedialog.askopenfilename(title="Chọn file public key")
    if not public_key_path:
        messagebox.showerror("Lỗi", "Bạn chưa chọn file public key!")
        return

    try:
        # Đọc public key từ file
        with open(public_key_path, 'rb') as pub_key_file:
            public_key_pem = pub_key_file.read()
            public_key = load_public_key(public_key_pem)

        # Tạo tên file mã hóa
        encrypted_file_path = file_path + '.enc'

        # Mã hóa file trước khi tải lên
        encrypt_file(file_path=file_path, public_key=public_key, output_path=encrypted_file_path)

        # Gửi file đã mã hóa lên server
        with open(encrypted_file_path, 'rb') as encrypted_file:
            files = {'file': encrypted_file}
            response = requests.post(UPLOAD_URL, files=files)

            if response.status_code == 200:
                # Lấy key từ server nếu có
                key = response.json().get('key')
                if key:
                    # Lưu key vào file
                    with open("key.txt", "w") as key_file:
                        key_file.write(key)
                    messagebox.showinfo("Thành công", "File đã được mã hóa và tải lên thành công!")
            else:
                messagebox.showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))
        
        # Xóa file đã mã hóa sau khi tải lên (nếu không cần lưu)
        os.remove(encrypted_file_path)

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải lên file: {str(e)}")

def download_file():
    """Tải xuống và giải mã file."""
    messagebox.showinfo("Nhập ID File", "Vui lòng nhập ID của file để tải xuống.")
    file_id = filedialog.askstring("Nhập ID", "Nhập ID file bạn muốn tải xuống")
    if not file_id:
        messagebox.showerror("Lỗi", "ID file không hợp lệ!")
        return

    try:
        # Gửi yêu cầu tải xuống file
        response = requests.get(DOWNLOAD_URL + file_id)
        
        if response.status_code == 200:
            # Lưu file đã tải về
            encrypted_file_path = f"{file_id}.enc"
            with open(encrypted_file_path, 'wb') as f:
                f.write(response.content)
            
            # Chọn vị trí lưu file đã giải mã
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", title="Chọn nơi lưu file đã giải mã")
            if not save_path:
                messagebox.showerror("Lỗi", "Bạn chưa chọn vị trí lưu file!")
                return

            # Giải mã file đã tải xuống
            messagebox.showinfo("Giải mã", "Đang giải mã file...")
            private_key_path = filedialog.askopenfilename(title="Chọn private key")
            if not private_key_path:
                messagebox.showerror("Lỗi", "Bạn chưa chọn private key!")
                return

            # Đọc private key từ file
            with open(private_key_path, 'rb') as private_key_file:
                private_key_pem = private_key_file.read()
                private_key = load_private_key(private_key_pem)  # Giả sử có hàm load_private_key

            # Giải mã file
            decrypt_file(encrypted_file_path, private_key, save_path)

            # Xóa file mã hóa sau khi giải mã
            os.remove(encrypted_file_path)

            messagebox.showinfo("Thành công", "File đã được giải mã và lưu thành công!")

        else:
            messagebox.showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải và giải mã file: {str(e)}")
# Tạo GUI
def create_gui():
    root = tk.Tk()
    root.title("Ứng dụng Tải Lên và Tải Xuống File")

    # Tạo button upload
    upload_btn = tk.Button(root, text="Tải lên file", command=upload_file)
    upload_btn.pack(pady=10)

    # Tạo button download
    download_button = tk.Button(root, text="Tải xuống File", command=download_file)
    download_button.pack(pady=20)

    # Chạy ứng dụng GUI
    root.mainloop()

# Chạy ứng dụng
if __name__ == "__main__":
    create_gui()
