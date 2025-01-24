import tkinter as tk
from tkinter import filedialog, messagebox
import requests

# URL của server
SERVER_URL = "http://127.0.0.1:5000"

def upload_file():
    # Chọn file
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    try:
        # Gửi file lên server
        with open(file_path, 'rb') as f:
            response = requests.post(f"{SERVER_URL}/upload", files={'file': f})
        response.raise_for_status()

        # Lấy key từ server
        share_key = response.json().get('share_key')
        if share_key:
            messagebox.showinfo("Thành công", f"Key chia sẻ: {share_key}")
        else:
            messagebox.showerror("Lỗi", "Không thể tải file lên")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

def download_file():
    # Nhập key
    share_key = key_entry.get()
    if not share_key:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập key")
        return

    try:
        # Gửi yêu cầu tải file
        response = requests.get(f"{SERVER_URL}/download/{share_key}", stream=True)
        response.raise_for_status()

        # Lưu file
        file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            messagebox.showinfo("Thành công", "File đã được tải xuống")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

# Giao diện Tkinter
root = tk.Tk()
root.title("File Upload/Download")

# Nút upload
upload_button = tk.Button(root, text="Tải file lên", command=upload_file)
upload_button.pack(pady=10)

# Nhập key
key_label = tk.Label(root, text="Nhập key để tải file:")
key_label.pack()
key_entry = tk.Entry(root)
key_entry.pack(pady=5)

# Nút download
download_button = tk.Button(root, text="Tải file xuống", command=download_file)
download_button.pack(pady=10)

# Chạy ứng dụng
root.mainloop()
