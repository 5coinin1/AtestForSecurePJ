import tkinter as tk
from tkinter import filedialog, messagebox
import requests

# Địa chỉ server (thay bằng URL Render của bạn)
SERVER_URL = "https://atestforsecurepj.onrender.com"

# Upload file lên server
def upload_file():
    file_path = filedialog.askopenfilename(title="Select File to Upload")
    if not file_path:
        return
    
    try:
        url = f"{SERVER_URL}/upload"
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        if response.status_code == 200:
            messagebox.showinfo("Success", f"File uploaded successfully: {response.json()}")
        else:
            messagebox.showerror("Error", f"Failed to upload file: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Download file từ server
def download_file():
    file_name = file_name_entry.get().strip()
    if not file_name:
        messagebox.showwarning("Input Error", "Please enter the file name to download!")
        return
    
    save_path = filedialog.asksaveasfilename(title="Save File As")
    if not save_path:
        return
    
    try:
        url = f"{SERVER_URL}/download/{file_name}"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            messagebox.showinfo("Success", f"File downloaded successfully: {save_path}")
        else:
            messagebox.showerror("Error", f"Failed to download file: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Lấy mật khẩu từ server
def get_password():
    try:
        url = f"{SERVER_URL}/get_password"
        response = requests.get(url)
        if response.status_code == 200:
            password = response.json().get('password')
            messagebox.showinfo("Password", f"Retrieved password: {password}")
        else:
            messagebox.showerror("Error", f"Failed to retrieve password: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Tạo GUI chính
root = tk.Tk()
root.title("File Manager")
root.geometry("400x300")

# Label
title_label = tk.Label(root, text="File Manager", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Upload button
upload_button = tk.Button(root, text="Upload File", command=upload_file, width=20, bg="lightblue")
upload_button.pack(pady=10)

# Download section
download_label = tk.Label(root, text="Download File")
download_label.pack()

file_name_entry = tk.Entry(root, width=30)
file_name_entry.pack(pady=5)

download_button = tk.Button(root, text="Download File", command=download_file, width=20, bg="lightgreen")
download_button.pack(pady=10)

# Get password button
password_button = tk.Button(root, text="Get Password", command=get_password, width=20, bg="lightcoral")
password_button.pack(pady=10)

# Run the application
root.mainloop()
