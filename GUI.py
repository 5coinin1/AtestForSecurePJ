import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
import pyperclip
import requests
import sys
import io
import os

from dotenv import load_dotenv
import customtkinter as ctk
from cryptography.hazmat.primitives import serialization
from encryption_utils import encrypt_file, decrypt_file, generate_key_pair, save_private_key, save_public_key

# Thay đổi mã hóa đầu ra của stdout thành utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()  # Tải các biến môi trường từ file .env

# URL của server Flask (phải thay đổi nếu sử dụng server khác)
UPLOAD_URL = os.environ.get("UPLOAD_URL")
DOWNLOAD_URL = os.environ.get("DOWNLOAD_URL")

# Hàm tải public key từ dữ liệu
def load_public_key(public_key_pem: bytes):
    return serialization.load_pem_public_key(public_key_pem, backend=None)

def custom_showinfo(title, message):
    """Hiển thị hộp thoại thông báo với CTkLabel, tự động xuống dòng với wraplength."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    # Tăng kích thước cửa sổ để chứa được nhiều nội dung hơn
    dialog.geometry("500x400")
    dialog.resizable(True, True)

    # Sử dụng CTkLabel với wraplength để tự động xuống dòng
    label = ctk.CTkLabel(dialog, text=message, font=("Helvetica", 14), wraplength=450)
    label.pack(pady=20, padx=20, fill="both", expand=True)

    button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, font=("Helvetica", 14))
    button.pack(pady=10)

    dialog.grab_set()
    dialog.wait_window()

def custom_showerror(title, message):
    """Hiển thị hộp thoại lỗi (Error) tùy chỉnh."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)

    label = ctk.CTkLabel(dialog, text=message, font=("Helvetica", 14), text_color="red")
    label.pack(pady=20, padx=20)

    button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, font=("Helvetica", 14))
    button.pack(pady=10)

    dialog.grab_set()
    dialog.wait_window()

def custom_askstring(title, prompt):
    """Hiển thị hộp thoại nhập chuỗi tùy chỉnh và trả về giá trị người dùng nhập."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)

    label = ctk.CTkLabel(dialog, text=prompt, font=("Helvetica", 14))
    label.pack(pady=10, padx=20)

    entry = ctk.CTkEntry(dialog, font=("Helvetica", 14))
    entry.pack(pady=10, padx=20, fill="x")

    result = {"value": None}

    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()

    ok_button = ctk.CTkButton(dialog, text="OK", command=on_ok, font=("Helvetica", 14))
    ok_button.pack(pady=10)

    dialog.grab_set()
    dialog.wait_window()
    return result["value"]

def upload_file():
    """Tải lên file đã mã hóa lên server."""
    # Sử dụng hộp thoại tuỳ chỉnh để thông báo cho người dùng
    custom_showinfo("Chọn File", "Vui lòng chọn file để tải lên.")
    file_path = filedialog.askopenfilename(title="Chọn file để tải lên")
    if not file_path:
        custom_showerror("Lỗi", "Bạn chưa chọn file!")
        return

    custom_showinfo("Chọn Public Key", "Vui lòng chọn file public key.")
    public_key_path = filedialog.askopenfilename(title="Chọn file public key")
    if not public_key_path:
        custom_showerror("Lỗi", "Bạn chưa chọn file public key!")
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

                    # Hiển thị key trong hộp thoại thông báo
                    custom_showinfo("Thành công", f"File đã được mã hóa và tải lên thành công!\nKey: {key}")

                    # Lưu key vào clipboard
                    pyperclip.copy(key)

                    # Thông báo về việc đã sao chép key vào clipboard
                    custom_showinfo("Key đã được sao chép", "Key đã được sao chép vào clipboard!")
            else:
                custom_showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))
        
        # Xóa file đã mã hóa sau khi tải lên (nếu không cần lưu)
        os.remove(encrypted_file_path)

    except Exception as e:
        custom_showerror("Lỗi", f"Không thể tải lên file: {str(e)}")
        
def download_file():
    """Tải xuống file đã giải mã từ server."""
    file_key = custom_askstring("Nhập Key", "Vui lòng nhập key:")
    if not file_key:
        custom_showerror("Lỗi", "Bạn chưa nhập key!")
        return

    custom_showinfo("Chọn Private Key", "Vui lòng chọn file private key (PEM).")
    private_key_path = filedialog.askopenfilename(title="Chọn file private key (PEM)")
    if not private_key_path:
        custom_showerror("Lỗi", "Bạn chưa chọn file private key!")
        return

    try:
        with open(private_key_path, 'rb') as private_key_file:
            files = {'private_key': private_key_file}
            data = {'key': file_key}
            response = requests.post(DOWNLOAD_URL, data=data, files=files)

            if response.status_code == 200:
                content_disposition = response.headers.get('Content-Disposition', '')
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    filename = "downloaded_file.decrypted"

                if filename.endswith('.decrypted'):
                    filename = filename.rsplit('.decrypted', 1)[0]

                save_path = filedialog.asksaveasfilename(
                    title="Lưu file dưới tên...",
                    initialfile=filename,
                    defaultextension="." + filename.split('.')[-1],
                    filetypes=[("All Files", "*.*")]
                )
                if not save_path:
                    custom_showinfo("Hủy", "Bạn đã hủy lưu file.")
                    return

                with open(save_path, 'wb') as f:
                    f.write(response.content)

                custom_showinfo("Thành công", f"Tải xuống file thành công!\nFile được lưu tại: {save_path}")
            else:
                custom_showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))
    except Exception as e:
        custom_showerror("Lỗi", f"Không thể tải xuống file: {str(e)}")
    
def generate_keys():
    """Tạo cặp khóa công khai và riêng."""
    try:
        private_key, public_key = generate_key_pair()
        
        # Lưu khóa vào file
        save_private_key(private_key, 'private_key.pem')
        save_public_key(public_key, 'public_key.pem')
        
        messagebox.showinfo("Thành công", "Cặp khóa đã được tạo và lưu vào file: private_key.pem và public_key.pem")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tạo cặp khóa: {str(e)}")

# Tạo GUI
def create_gui():
    ctk.set_appearance_mode("dark")

    # Tạo cửa sổ chính
    root = ctk.CTk()
    root.title("Ứng dụng Tải Lên và Tải Xuống File")
    root.geometry("400x300")

    # Tạo một frame trung tâm để chứa các nút
    frame = ctk.CTkFrame(root)
    frame.pack(pady=40, padx=40, fill="both", expand=True)

    button_font = ("Papyrus", 14, "bold")

    # Tạo nút "Tải lên file"
    upload_btn = ctk.CTkButton(
        frame,
        text="Tải lên file",
        command=upload_file,
        width=200,
        height=50,
        corner_radius=20,       # Bo tròn các góc
        fg_color="#4CAF50",     # Màu nền ban đầu (xanh lá)
        hover_color="#388E3C",  # Màu nền khi hover (tối hơn)
        border_width=2,         # Độ dày viền
        border_color="#FFC107", # Màu viền (vàng tương phản)
        font=button_font        # Font chữ và cỡ chữ
    )
    upload_btn.pack(pady=10)

    # Tạo nút "Tải xuống file"
    download_btn = ctk.CTkButton(
        frame,
        text="Tải xuống file",
        command=download_file,
        width=200,
        height=50,
        corner_radius=20,
        fg_color="#2196F3",     # Màu nền ban đầu (xanh dương)
        hover_color="#1976D2",  # Màu nền khi hover (tối hơn)
        border_width=2,
        border_color="#FF5722", # Màu viền (cam tương phản)
        font=button_font
    )
    download_btn.pack(pady=10)

    # Tạo nút "Tạo Cặp Khóa"
    generate_keys_btn = ctk.CTkButton(
        frame,
        text="Tạo Cặp Khóa",
        command=generate_keys,
        width=200,
        height=50,
        corner_radius=20,
        fg_color="#F44336",     # Màu nền ban đầu (đỏ)
        hover_color="#D32F2F",  # Màu nền khi hover (tối hơn)
        border_width=2,
        border_color="#4CAF50", # Màu viền (xanh lá tương phản)
        font=button_font
    )
    generate_keys_btn.pack(pady=10)

    root.mainloop()

# Chạy ứng dụng
if __name__ == "__main__":
    create_gui()
