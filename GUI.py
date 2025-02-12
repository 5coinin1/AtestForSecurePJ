import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
import pyperclip
import requests
import sys
import io
import os
import customtkinter as ctk
from main import upload_file,download_file,generate_keys


def custom_showinfo(title, message):
    """Hiển thị hộp thoại thông báo với CTkLabel, tự động xuống dòng với wraplength."""
    dialog = ctk.CTkToplevel()
    dialog.title(title)
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
    """Hiển thị hộp thoại lỗi (Error) theo giao diện CustomTkinter."""
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
