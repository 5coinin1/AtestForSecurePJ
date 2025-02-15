import os
import requests
import pyperclip
from tkinter import filedialog
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

from encryption_utils import encrypt_file, generate_key_pair, save_private_key, save_public_key
from dialogs import custom_showinfo, custom_showerror, custom_askstring

load_dotenv()
UPLOAD_URL = os.environ.get("UPLOAD_URL")
DOWNLOAD_URL = os.environ.get("DOWNLOAD_URL")

def load_public_key(public_key_pem: bytes):
    return serialization.load_pem_public_key(public_key_pem)

def upload_file():
    """Mã hóa file và tải lên server."""
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
        with open(public_key_path, 'rb') as pub_key_file:
            public_key_pem = pub_key_file.read()
            public_key = load_public_key(public_key_pem)

        encrypted_file_path = file_path + '.enc'
        encrypt_file(file_path=file_path, public_key=public_key, output_path=encrypted_file_path)

        with open(encrypted_file_path, 'rb') as encrypted_file:
            files = {'file': encrypted_file}
            response = requests.post(UPLOAD_URL, files=files)

            if response.status_code == 200:
                key = response.json().get('key')
                if key:
                    with open("key.txt", "w") as key_file:
                        key_file.write(key)
                    custom_showinfo("Thành công", f"File đã được mã hóa và tải lên thành công!\nKey: {key}")
                    pyperclip.copy(key)
                    custom_showinfo("Key đã được sao chép", "Key đã được sao chép vào clipboard!")
            else:
                custom_showerror("Lỗi", response.json().get('error', 'Không rõ lỗi'))
        
        os.remove(encrypted_file_path)

    except Exception as e:
        custom_showerror("Lỗi", f"Không thể tải lên file: {str(e)}")

def download_file():
    """Download file từ server và giải mã."""
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
    """Hiển thị giao diện tạo cặp khóa."""
    import customtkinter as ctk
    dialog = ctk.CTkToplevel()
    dialog.title("Tạo Cặp Khóa")
    dialog.geometry("500x340")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")
    dialog.attributes("-alpha", 0)

    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=12)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    icon_label = ctk.CTkLabel(frame, text="🔑", font=("Arial", 50), text_color="#FFD700")
    icon_label.pack(pady=(10, 5))

    title_label = ctk.CTkLabel(frame, text="Tạo Cặp Khóa RSA", font=("Arial", 16, "bold"), text_color="white")
    title_label.pack()

    result_label = ctk.CTkLabel(frame, text="", font=("Arial", 13), text_color="lightgreen", wraplength=460)
    result_label.pack(pady=5)

    path_label = ctk.CTkLabel(frame, text="", font=("Arial", 12), text_color="#1E90FF", wraplength=460, justify="center")
    path_label.pack(pady=5)

    def handle_generate_keys():
        try:
            private_key, public_key = generate_key_pair()
            private_path = os.path.abspath('private_key.pem')
            public_path = os.path.abspath('public_key.pem')

            save_private_key(private_key, private_path)
            save_public_key(public_key, public_path)

            result_label.configure(text="✔ Cặp khóa đã tạo thành công!", text_color="lightgreen")
            path_label.configure(text=f"📂 Khóa riêng: {private_path}\n📂 Khóa công khai: {public_path}")
        except Exception as e:
            result_label.configure(text=f"❌ Lỗi: {str(e)}", text_color="red")
            path_label.configure(text="")

    generate_button = ctk.CTkButton(
        frame, text="Tạo Khóa", font=("Arial", 14, "bold"), corner_radius=20,
        fg_color="#5865F2", text_color="white", hover_color="#1E90FF",
        command=handle_generate_keys
    )
    generate_button.pack(pady=10)

    close_button = ctk.CTkButton(
        frame, text="Đóng", font=("Arial", 14), corner_radius=20,
        fg_color="#FF5555", text_color="white", hover_color="#D32F2F",
        command=dialog.destroy
    )
    close_button.pack(pady=5)

    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    dialog.grab_set()
    dialog.wait_window()
