import customtkinter as ctk
from PIL import Image
from file_services import upload_file, download_file, generate_keys_ui

def create_gui():
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title("Ứng dụng Mã Hóa Và Lưu Trữ FILE")
    root.geometry("400x300")

    frame = ctk.CTkFrame(root)
    frame.pack(pady=40, padx=40, fill="both", expand=True)

    button_font = ("Papyrus", 14, "bold")

    # Load icon (đường dẫn đến file icon, chỉnh lại cho phù hợp)
    upload_icon = ctk.CTkImage(
        light_image=Image.open(r"icons\upload.png"),
        size=(25, 25)
    )
    download_icon = ctk.CTkImage(
        light_image=Image.open(r"icons\download.png"),
        size=(25, 25)
    )
    key_icon = ctk.CTkImage(
        light_image=Image.open(r"icons\key.png"),
        size=(25, 25)
    )

    upload_btn = ctk.CTkButton(
        frame,
        text="Tải lên file",
        command=upload_file,  # gọi hàm xử lý upload
        width=200,
        height=50,
        corner_radius=20,
        fg_color="#4CAF50",
        hover_color="#388E3C",
        border_width=2,
        border_color="#FFC107",
        font=button_font,
        image=upload_icon,
        compound="left"
    )
    upload_btn.pack(pady=10, padx=10)

    download_btn = ctk.CTkButton(
        frame,
        text="Tải xuống file",
        command=download_file,  # gọi hàm xử lý download
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

    generate_keys_btn = ctk.CTkButton(
        frame,
        text="Tạo Cặp Khóa",
        command=generate_keys_ui,  # gọi hàm tạo khóa
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
