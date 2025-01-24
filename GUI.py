import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import sys
import io

# Thay đổi mã hóa đầu ra của stdout thành utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# URL của server Flask (phải thay đổi nếu sử dụng server khác)
UPLOAD_URL = "https://atestforsecurepj.onrender.com/client"
import requests

def upload_file():
    """ Hàm tải file lên server """
    file_path = filedialog.askopenfilename()  # Chọn file
    if not file_path:
        return
    
    files = {'file': open(file_path, 'rb')}
    response = requests.post(UPLOAD_URL, files=files)
    files['file'].close()
    
    if response.status_code == 200:
        key = response.json().get('key')
        messagebox.showinfo("Tải lên thành công", f"File đã được tải lên thành công. Key: {key}")
    else:
        messagebox.showerror("Lỗi", "Có lỗi xảy ra khi tải lên file.")

def download_file():
    """ Hàm tải file từ server theo key """
    key = download_key_entry.get()  # Lấy key từ ô nhập liệu
    if not key:
        messagebox.showwarning("Thiếu key", "Bạn phải nhập key để tải xuống file.")
        return

    # Thay thế 'YOUR_KEY_HERE' bằng key người dùng nhập
    download_url_with_key = f"https://atestforsecurepj.onrender.com/download?key={key}"
    
    response = requests.get(download_url_with_key)
    
    if response.status_code == 200:
        # Lưu file đã tải về
        save_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            messagebox.showinfo("Tải xuống thành công", "File đã được tải xuống thành công.")
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy file với key đã nhập.")

# Tạo giao diện Tkinter
app = tk.Tk()
app.title("Ứng dụng Tải lên và Tải xuống File")
app.geometry("400x200")

# Nút tải lên file
upload_button = tk.Button(app, text="Tải lên File", command=upload_file)
upload_button.pack(pady=10)

# Nhập key và nút tải xuống file
download_key_label = tk.Label(app, text="Nhập key để tải xuống file:")
download_key_label.pack(pady=5)

download_key_entry = tk.Entry(app)
download_key_entry.pack(pady=5)

download_button = tk.Button(app, text="Tải xuống File", command=download_file)
download_button.pack(pady=10)

# Chạy ứng dụng
app.mainloop()
