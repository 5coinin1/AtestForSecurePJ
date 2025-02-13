import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
import pyperclip
import requests
import sys
import io
import os

import threading
from PIL import Image
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

def custom_showinfo(title, message, icon="info"):
    """Hiển thị hộp thoại thông báo với UI đẹp, hiệu ứng động."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")  # Màu nền tối hiện đại
    dialog.attributes("-alpha", 0)  # Bắt đầu với hiệu ứng fade-in

    # Biểu tượng cho thông báo
    icons = {
        "info": "🛈",   # Thông tin
        "success": "✔", # Thành công
        "error": "✖",   # Lỗi
        "warning": "⚠"  # Cảnh báo
    }
    icon_text = icons.get(icon, "🛈")

    # Hiển thị icon và tiêu đề
    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=10)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    icon_label = ctk.CTkLabel(frame, text=icon_text, font=("Arial", 36), text_color="#FFD700")
    icon_label.pack(pady=(10, 5))

    label = ctk.CTkLabel(frame, text=message, font=("Arial", 14), wraplength=400, justify="center")
    label.pack(pady=10, padx=20)

    # Nút OK với hiệu ứng hover
    def on_hover(event):
        button.configure(fg_color="#1E90FF")

    def on_leave(event):
        button.configure(fg_color="#5865F2")

    button = ctk.CTkButton(frame, text="OK", font=("Arial", 14, "bold"), corner_radius=20, 
                           fg_color="#5865F2", text_color="white", hover_color="#1E90FF",
                           command=dialog.destroy)
    button.pack(pady=15)
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    # Hiệu ứng fade-in
    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    dialog.grab_set()
    dialog.wait_window()

def custom_showerror(title, message):
    """Hiển thị hộp thoại lỗi (Error) với UI đẹp, hiệu ứng động."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")  # Màu nền tối
    dialog.attributes("-alpha", 0)  # Bắt đầu với hiệu ứng fade-in

    # Khung chứa nội dung
    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=10)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Biểu tượng lỗi (màu đỏ)
    icon_label = ctk.CTkLabel(frame, text="✖", font=("Arial", 36), text_color="red")
    icon_label.pack(pady=(10, 5))

    # Nội dung lỗi
    label = ctk.CTkLabel(frame, text=message, font=("Arial", 14), wraplength=400, justify="center", text_color="white")
    label.pack(pady=10, padx=20)

    # Nút OK với hiệu ứng hover
    def on_hover(event):
        button.configure(fg_color="#FF6347")  # Đổi sang màu cam đỏ

    def on_leave(event):
        button.configure(fg_color="#FF0000")  # Quay lại màu đỏ

    button = ctk.CTkButton(frame, text="OK", font=("Arial", 14, "bold"), corner_radius=20, 
                           fg_color="#FF0000", text_color="white", hover_color="#FF6347",
                           command=dialog.destroy)
    button.pack(pady=15)
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    # Hiệu ứng fade-in
    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    dialog.grab_set()
    dialog.wait_window()

def custom_askstring(title, prompt):
    """Hiển thị hộp thoại nhập chuỗi với giao diện đẹp và hiệu ứng động."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")  # Màu nền tối
    dialog.attributes("-alpha", 0)  # Bắt đầu với hiệu ứng fade-in

    # Khung chứa nội dung
    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=10)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Tiêu đề
    label = ctk.CTkLabel(frame, text=prompt, font=("Arial", 14), text_color="white", wraplength=400, justify="center")
    label.pack(pady=15, padx=20)

    # Ô nhập liệu với placeholder
    entry = ctk.CTkEntry(frame, font=("Arial", 14), width=350, corner_radius=8, placeholder_text="Nhập vào đây...")
    entry.pack(pady=5, padx=20)

    result = {"value": None}

    # Xử lý khi nhấn OK
    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()

    # Xử lý khi nhấn Cancel
    def on_cancel():
        result["value"] = None
        dialog.destroy()

    # Nút OK & Cancel với hiệu ứng hover
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(pady=15)

    ok_button = ctk.CTkButton(button_frame, text="OK", font=("Arial", 14, "bold"), corner_radius=20,
                              fg_color="#008CBA", hover_color="#0073A8", text_color="white", command=on_ok)
    ok_button.pack(side="left", padx=10)

    cancel_button = ctk.CTkButton(button_frame, text="Cancel", font=("Arial", 14), corner_radius=20,
                                  fg_color="#FF4C4C", hover_color="#D43F3F", text_color="white", command=on_cancel)
    cancel_button.pack(side="right", padx=10)

    # Nhấn Enter để xác nhận
    entry.bind("<Return>", lambda event: on_ok())

    # Hiệu ứng fade-in
    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    entry.focus()  # Tự động focus vào ô nhập liệu
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
    
def generate_keys_ui():
    """Hiển thị giao diện tạo khóa với UI đẹp, hiệu ứng động."""
    dialog = ctk.CTkToplevel()
    dialog.title("Tạo Cặp Khóa")
    dialog.geometry("500x340")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")  # Màu nền tối
    dialog.attributes("-alpha", 0)  # Hiệu ứng fade-in ban đầu

    # Frame chứa nội dung
    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=12)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Icon khóa 🔑
    icon_label = ctk.CTkLabel(frame, text="🔑", font=("Arial", 50), text_color="#FFD700")
    icon_label.pack(pady=(10, 5))

    # Tiêu đề
    title_label = ctk.CTkLabel(frame, text="Tạo Cặp Khóa RSA", font=("Arial", 16, "bold"), text_color="white")
    title_label.pack()

    # Khu vực hiển thị kết quả
    result_label = ctk.CTkLabel(frame, text="", font=("Arial", 13), text_color="lightgreen", wraplength=460)
    result_label.pack(pady=5)

    path_label = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#1E90FF", wraplength=460, justify="center")
    path_label.pack(pady=5)

    # Hàm xử lý khi nhấn "Tạo Khóa"
    def handle_generate_keys():
        try:
            private_key, public_key = generate_key_pair()
            private_path = os.path.abspath('private_key.pem')
            public_path = os.path.abspath('public_key.pem')

            save_private_key(private_key, private_path)
            save_public_key(public_key, public_path)

            result_label.configure(text="✔ Cặp khóa đã tạo thành công!", text_color="lightgreen")
            path_label.configure(
                text=f"📂 Khóa riêng: {private_path}\n📂 Khóa công khai: {public_path}"
            )
        except Exception as e:
            result_label.configure(text=f"❌ Lỗi: {str(e)}", text_color="red")
            path_label.configure(text="")

    # Nút "Tạo Khóa"
    generate_button = ctk.CTkButton(
        frame, text="Tạo Khóa", font=("Arial", 14, "bold"), corner_radius=20,
        fg_color="#5865F2", text_color="white", hover_color="#1E90FF",
        command=handle_generate_keys
    )
    generate_button.pack(pady=10)

    # Nút "Đóng"
    close_button = ctk.CTkButton(
        frame, text="Đóng", font=("Arial", 14), corner_radius=20,
        fg_color="#FF5555", text_color="white", hover_color="#D32F2F",
        command=dialog.destroy
    )
    close_button.pack(pady=5)

    # Hiệu ứng fade-in
    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    dialog.grab_set()
    dialog.wait_window()

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

    # Load icon cho từng nút
    upload_icon = ctk.CTkImage(light_image=Image.open(r"C:\Users\lenovo\Desktop\new project\PythonPJ\AtestForSecurePJ\icons\upload.png"), size=(25, 25))
    download_icon = ctk.CTkImage(light_image=Image.open(r"C:\Users\lenovo\Desktop\new project\PythonPJ\AtestForSecurePJ\icons\download.png"), size=(25, 25))
    key_icon = ctk.CTkImage(light_image=Image.open(r"C:\Users\lenovo\Desktop\new project\PythonPJ\AtestForSecurePJ\icons\key.png"), size=(25, 25))

    # Tạo nút "Tải lên file"
    upload_btn = ctk.CTkButton(
        frame,
        text="Tải lên file",
        command=upload_file,
        width=200,
        height=50,
        corner_radius=20,
        fg_color="#4CAF50",
        hover_color="#388E3C",
        border_width=2,
        border_color="#FFC107",
        font=button_font,
        image=upload_icon,  # Gán icon
        compound="left"  # Icon bên trái chữ
    )
    upload_btn.pack(pady=10, padx=10)  # Thêm padding ở đây

    # Tạo nút "Tải xuống file"
    download_btn = ctk.CTkButton(
        frame,
        text="Tải xuống file",
        command=download_file,
        width=200,
        height=50,
        corner_radius=20,
        fg_color="#2196F3",
        hover_color="#1976D2",
        border_width=2,
        border_color="#FF5722",
        font=button_font,
        image=download_icon,  
        compound="left"
    )
    download_btn.pack(pady=10, padx=10)

    # Tạo nút "Tạo Cặp Khóa"
    generate_keys_btn = ctk.CTkButton(
        frame,
        text="Tạo Cặp Khóa",
        command=generate_keys_ui,  # Gọi hàm giao diện thay vì generate_keys
        width=200,
        height=50,
        corner_radius=20,
        fg_color="#F44336",
        hover_color="#D32F2F",
        border_width=2,
        border_color="#4CAF50",
        font=button_font,
        image=key_icon,  
        compound="left"
    )
    generate_keys_btn.pack(pady=10, padx=10)
    root.mainloop()

# Chạy ứng dụng
if __name__ == "__main__":
    create_gui()
