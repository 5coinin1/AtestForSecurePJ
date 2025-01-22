import tkinter as tk
from tkinter import messagebox
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Hàm giải mã AES
def aes_decrypt(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data)  # Giải mã Base64
    iv = encrypted_data[:AES.block_size]  # Tách IV
    encrypted_data = encrypted_data[AES.block_size:]  # Tách dữ liệu mã hóa
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Tạo cipher để giải mã
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()

# Hàm xử lý khi nhấn nút "Giải mã mật khẩu"
def on_decrypt_password():
    encrypted_password = encrypted_password_entry.get()
    key_hex = key_entry.get()

    if not encrypted_password:
        messagebox.showwarning("Thiếu mật khẩu", "Vui lòng nhập mật khẩu đã mã hóa!")
        return
    if not key_hex:
        messagebox.showwarning("Thiếu khóa AES", "Vui lòng nhập khóa AES!")
        return

    try:
        # Chuyển khóa từ hex sang bytes
        key = bytes.fromhex(key_hex)

        # Giải mã mật khẩu
        decrypted_password = aes_decrypt(encrypted_password, key)
        result_entry.delete(0, tk.END)  # Xóa nội dung cũ trong Entry kết quả
        result_entry.insert(0, decrypted_password)  # Hiển thị kết quả giải mã
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi giải mã: {e}")

# Giao diện người dùng (GUI)
root = tk.Tk()
root.title("Giải Mã Mật Khẩu RAR")

# Tạo các phần tử giao diện
instructions_label = tk.Label(root, text="Nhập mật khẩu đã mã hóa (Base64):")
instructions_label.pack(padx=10, pady=10)

encrypted_password_entry = tk.Entry(root, width=50)
encrypted_password_entry.pack(padx=10, pady=10)

key_label = tk.Label(root, text="Nhập khóa AES (dưới dạng Hex):")
key_label.pack(padx=10, pady=10)

key_entry = tk.Entry(root, width=50)
key_entry.pack(padx=10, pady=10)

decrypt_button = tk.Button(root, text="Giải mã mật khẩu", command=on_decrypt_password)
decrypt_button.pack(pady=20)

# Label để hiển thị kết quả giải mã
result_label = tk.Label(root, text="Mật khẩu đã giải mã sẽ hiển thị ở đây:")
result_label.pack(padx=10, pady=10)

# Entry để hiển thị kết quả giải mã (có thể sao chép)
result_entry = tk.Entry(root, width=50)
result_entry.pack(padx=10, pady=10)

# Chạy giao diện
root.mainloop()
