import customtkinter as ctk

def custom_showinfo(title, message, icon="info"):
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")
    dialog.attributes("-alpha", 0)

    icons = {
        "info": "🛈",
        "success": "✔",
        "error": "✖",
        "warning": "⚠"
    }
    icon_text = icons.get(icon, "🛈")

    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=10)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    icon_label = ctk.CTkLabel(frame, text=icon_text, font=("Arial", 36), text_color="#FFD700")
    icon_label.pack(pady=(10, 5))

    label = ctk.CTkLabel(frame, text=message, font=("Arial", 14), wraplength=400, justify="center")
    label.pack(pady=10, padx=20)

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

    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    dialog.grab_set()
    dialog.wait_window()

def custom_showerror(title, message):
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")
    dialog.attributes("-alpha", 0)

    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=10)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    icon_label = ctk.CTkLabel(frame, text="✖", font=("Arial", 36), text_color="red")
    icon_label.pack(pady=(10, 5))

    label = ctk.CTkLabel(frame, text=message, font=("Arial", 14), wraplength=400, justify="center", text_color="white")
    label.pack(pady=10, padx=20)

    def on_hover(event):
        button.configure(fg_color="#FF6347")
    def on_leave(event):
        button.configure(fg_color="#FF0000")
    button = ctk.CTkButton(frame, text="OK", font=("Arial", 14, "bold"), corner_radius=20, 
                           fg_color="#FF0000", text_color="white", hover_color="#FF6347",
                           command=dialog.destroy)
    button.pack(pady=15)
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    dialog.grab_set()
    dialog.wait_window()

def custom_askstring(title, prompt):
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.configure(fg_color="#2C2F33")
    dialog.attributes("-alpha", 0)

    frame = ctk.CTkFrame(dialog, fg_color="#23272A", corner_radius=10)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    label = ctk.CTkLabel(frame, text=prompt, font=("Arial", 14), text_color="white", wraplength=400, justify="center")
    label.pack(pady=15, padx=20)

    entry = ctk.CTkEntry(frame, font=("Arial", 14), width=350, corner_radius=8, placeholder_text="Nhập vào đây...")
    entry.pack(pady=5, padx=20)

    result = {"value": None}
    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()
    def on_cancel():
        result["value"] = None
        dialog.destroy()
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(pady=15)
    ok_button = ctk.CTkButton(button_frame, text="OK", font=("Arial", 14, "bold"), corner_radius=20,
                              fg_color="#008CBA", hover_color="#0073A8", text_color="white", command=on_ok)
    ok_button.pack(side="left", padx=10)
    cancel_button = ctk.CTkButton(button_frame, text="Cancel", font=("Arial", 14), corner_radius=20,
                                  fg_color="#FF4C4C", hover_color="#D43F3F", text_color="white", command=on_cancel)
    cancel_button.pack(side="right", padx=10)

    entry.bind("<Return>", lambda event: on_ok())

    for i in range(0, 11):
        dialog.attributes("-alpha", i / 10)
        dialog.update_idletasks()
        dialog.after(30)

    entry.focus()
    dialog.grab_set()
    dialog.wait_window()
    return result["value"]
