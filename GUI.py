import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
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
                messagebox.showinfo("Thành công", "File đã được tải lên thành công!")
            else:
                messagebox.showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải lên file: {str(e)}")

def download_file():
    """Tải xuống file đã giải mã từ server."""
    file_key = simpledialog.askstring("Nhập Key", "Vui lòng nhập key:")
    if not file_key:
        messagebox.showerror("Lỗi", "Bạn chưa nhập key!")
        return

    messagebox.showinfo("Chọn Private Key", "Vui lòng chọn file private key (PEM).")
    private_key_path = filedialog.askopenfilename(title="Chọn file private key (PEM)")
    if not private_key_path:
        messagebox.showerror("Lỗi", "Bạn chưa chọn file private key!")
        return

    try:
        # Hỏi tên và vị trí lưu file
        save_path = filedialog.asksaveasfilename(
            title="Lưu file dưới tên...",
            defaultextension=".decrypted",
            filetypes=[("Decrypted File", "*.decrypted"), ("All Files", "*.*")]
        )
        if not save_path:
            messagebox.showinfo("Hủy", "Bạn đã hủy lưu file.")
            return

        # Mở private key file
        with open(private_key_path, 'rb') as private_key_file:
            files = {'private_key': private_key_file}
            data = {'key': file_key}
            response = requests.post(DOWNLOAD_URL, data=data, files=files)

            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                messagebox.showinfo("Thành công", f"Tải xuống file thành công!\nFile được lưu tại: {save_path}")
            else:
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
