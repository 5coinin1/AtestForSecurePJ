import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
import pyperclip
import requests
import sys
import io

# Thay đổi mã hóa đầu ra của stdout thành utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# URL của server Flask (phải thay đổi nếu sử dụng server khác)
UPLOAD_URL = "https://atestforsecurepj.onrender.com/upload"
DOWNLOAD_URL = "https://atestforsecurepj.onrender.com/download"


def upload_file():
    """Tải lên file lên server."""
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
        with open(file_path, 'rb') as file, open(public_key_path, 'rb') as public_key:
            files = {'file': file, 'public_key': public_key}
            response = requests.post(UPLOAD_URL, files=files)

            if response.status_code == 200:
                # Lấy thông tin từ phản hồi của server
                response_data = response.json()
                key = response_data.get('key', None)

                if key:
                    # Sao chép key vào clipboard
                    pyperclip.copy(key)
                    
                    # Lưu key vào file
                    key_file_path = f"{file_path}.key.txt"
                    with open(key_file_path, 'w') as key_file:
                        key_file.write(key)
                    
                    messagebox.showinfo(
                        "Thành công",
                        f"File đã được tải lên thành công!\n"
                        f"Key: {key}\n\n"
                        f"Key đã được sao chép vào clipboard và lưu tại:\n{key_file_path}"
                    )
                else:
                    messagebox.showinfo("Thành công", "File đã được tải lên thành công nhưng không có key trả về.")
            else:
                messagebox.showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))

    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải lên file: {str(e)}")
def download_file():
    """Tải xuống file đã giải mã từ server."""
    # Nhập key từ người dùng
    file_key = simpledialog.askstring("Nhập Key", "Vui lòng nhập key:")
    if not file_key:
        messagebox.showerror("Lỗi", "Bạn chưa nhập key!")
        return

    # Chọn file private key
    messagebox.showinfo("Chọn Private Key", "Vui lòng chọn file private key (PEM).")
    private_key_path = filedialog.askopenfilename(title="Chọn file private key (PEM)")
    if not private_key_path:
        messagebox.showerror("Lỗi", "Bạn chưa chọn file private key!")
        return

    try:
        # Gửi yêu cầu tải file từ server
        with open(private_key_path, 'rb') as private_key_file:
            files = {'private_key': private_key_file}
            data = {'key': file_key}
            response = requests.post(DOWNLOAD_URL, data=data, files=files)

            if response.status_code == 200:
                # Lấy tên file gốc từ header Content-Disposition (nếu server cung cấp)
                content_disposition = response.headers.get('Content-Disposition', '')
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    # Nếu server không gửi tên file, dùng tên mặc định
                    filename = "downloaded_file.decrypted"

                # Bỏ đuôi `.decrypted` nếu có
                if filename.endswith('.decrypted'):
                    filename = filename.rsplit('.decrypted', 1)[0]

                # Hỏi người dùng nơi lưu file
                save_path = filedialog.asksaveasfilename(
                    title="Lưu file dưới tên...",
                    initialfile=filename,  # Gợi ý tên file gốc
                    defaultextension="." + filename.split('.')[-1],  # Gợi ý phần mở rộng gốc
                    filetypes=[("All Files", "*.*")]
                )
                if not save_path:
                    messagebox.showinfo("Hủy", "Bạn đã hủy lưu file.")
                    return

                # Lưu file tải xuống vào đường dẫn đã chọn
                with open(save_path, 'wb') as f:
                    f.write(response.content)

                # Thông báo thành công
                messagebox.showinfo("Thành công", f"Tải xuống file thành công!\nFile được lưu tại: {save_path}")
            else:
                # Hiển thị lỗi từ server (nếu có)
                messagebox.showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải xuống file: {str(e)}")

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
