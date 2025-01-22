import tkinter as tk
from tkinter import filedialog, messagebox
import rarfile
import os
import shutil
import py7zr
import hashlib
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# Tạo khóa AES (32 bytes cho AES-256)
AES_KEY = os.urandom(32)  # Tạo ngẫu nhiên
print(f"Key: {AES_KEY.hex()}")  # Hiển thị khóa ra terminal

# Hàm mã hóa AES
def aes_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC)  # Sử dụng AES-CBC
    iv = cipher.iv  # Lấy IV ngẫu nhiên
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))  # Mã hóa dữ liệu
    # Ghép IV và dữ liệu mã hóa lại để lưu trữ
    return base64.b64encode(iv + encrypted_data).decode()

# Hàm giải mã AES
def aes_decrypt(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data)  # Giải mã Base64
    iv = encrypted_data[:AES.block_size]  # Tách IV
    encrypted_data = encrypted_data[AES.block_size:]  # Tách dữ liệu mã hóa
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Tạo cipher để giải mã
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()

# Hàm tạo mật khẩu mới dựa trên thời gian
def generate_new_password():
    # Sử dụng thời gian hiện tại để tạo mật khẩu mới
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"newPassword_{current_time}"

# Hàm giải nén tệp RAR với mật khẩu cũ
def extract_rar(rar_file, password, extract_to):
    try:
        with rarfile.RarFile(rar_file) as rf:
            rf.extractall(path=extract_to, pwd=password)
        return True
    except rarfile.BadRarFile:
        messagebox.showerror("Lỗi", "Tệp RAR không hợp lệ.")
        return False
    except rarfile.PasswordRequired:
        messagebox.showerror("Lỗi", "Mật khẩu không đúng.")
        return False
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        return False

# Hàm tạo tệp RAR mới với mật khẩu mới
def create_rar_from_folder(folder_path, new_rar_file, new_password):
    try:
        with py7zr.SevenZipFile(new_rar_file, mode='w', password=new_password) as archive:
            archive.writeall(folder_path, os.path.basename(folder_path))
        return True
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi tạo tệp nén mới: {e}")
        return False

# Hàm thay đổi mật khẩu tệp RAR
def change_rar_password(rar_file, old_password, extract_folder):
    # Tạo mật khẩu mới dựa trên thời gian
    new_password = generate_new_password()

    # Giải nén tệp RAR với mật khẩu cũ
    if not extract_rar(rar_file, old_password, extract_folder):
        return None
    
    # Tạo lại tệp RAR với mật khẩu mới
    if create_rar_from_folder(extract_folder, "new_" + os.path.basename(rar_file), new_password):
        # Mã hóa mật khẩu mới bằng AES
        encrypted_new_password = aes_encrypt(new_password, AES_KEY)
        
        # Hiển thị cửa sổ thông báo tùy chỉnh
        show_custom_message(encrypted_new_password)
        
        # Xóa thư mục tạm
        shutil.rmtree(extract_folder)
        return new_password
    else:
        return None

# Hàm chọn tệp RAR
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("RAR files", "*.rar")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# Hàm xử lý khi nhấn nút "Thay đổi mật khẩu"
def on_change_password():
    rar_file = file_entry.get()

    if not rar_file:
        messagebox.showwarning("Thiếu tệp", "Vui lòng chọn tệp RAR!")
        return

    old_password = "oldPassword123"  # Mật khẩu cũ (định sẵn)
    extract_folder = "extracted_files"

    # Thay đổi mật khẩu và lấy mật khẩu mới
    new_password = change_rar_password(rar_file, old_password, extract_folder)

    if new_password:
        # Cập nhật mật khẩu cũ thành mật khẩu mới để lần sau sử dụng
        global current_old_password
        current_old_password = new_password

## Hàm hiển thị thông báo với mật khẩu mã hóa và nút sao chép
def show_custom_message(encrypted_password):
    # Tạo cửa sổ thông báo mới
    custom_window = tk.Toplevel(root)
    custom_window.title("Mật khẩu đã mã hóa")

    # Tạo nhãn thông báo
    message_label = tk.Label(custom_window, text="Mật khẩu đã mã hóa (bạn có thể sao chép):")
    message_label.pack(padx=20, pady=10)

    # Tạo hộp văn bản để hiển thị mật khẩu đã mã hóa
    text_box = tk.Text(custom_window, height=4, width=50)
    text_box.insert(tk.END, encrypted_password)
    text_box.pack(padx=20, pady=10)

    # Vô hiệu hóa chỉnh sửa nội dung của hộp văn bản (chỉ đọc)
    text_box.config(state=tk.DISABLED)

    # Hàm sao chép mật khẩu mã hóa vào clipboard
    def copy_to_clipboard():
        root.clipboard_clear()  # Xóa clipboard hiện tại
        root.clipboard_append(encrypted_password)  # Thêm nội dung mới vào clipboard
        root.update()  # Cập nhật clipboard
        messagebox.showinfo("Sao chép thành công", "Mật khẩu đã mã hóa đã được sao chép vào clipboard!")

    # Thêm nút sao chép mật khẩu
    copy_button = tk.Button(custom_window, text="Sao chép", command=copy_to_clipboard)
    copy_button.pack(pady=5)

    # Thêm nút đóng cửa sổ
    close_button = tk.Button(custom_window, text="Đóng", command=custom_window.destroy)
    close_button.pack(pady=10)

# Giao diện người dùng (GUI)
root = tk.Tk()
root.title("Thay Đổi Mật Khẩu Tệp RAR")

# Mật khẩu cũ được lưu lại ở đây
current_old_password = "oldPassword123"

# Tạo các phần tử giao diện
file_label = tk.Label(root, text="Chọn tệp RAR:")
file_label.grid(row=0, column=0, padx=10, pady=10)

file_entry = tk.Entry(root, width=40)
file_entry.grid(row=0, column=1, padx=10, pady=10)

browse_button = tk.Button(root, text="Chọn tệp", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=10)

change_button = tk.Button(root, text="Thay đổi mật khẩu", command=on_change_password)
change_button.grid(row=1, column=0, columnspan=3, pady=20)

# Chạy giao diện
root.mainloop()
