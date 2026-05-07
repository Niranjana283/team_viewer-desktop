import customtkinter as ctk
from tkinter import simpledialog
import threading

from screen_share import send_screen, receive_screen
from control import send_control, receive_control

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("500x400")
app.title("Remote Desktop App")

title = ctk.CTkLabel(
    app,
    text="Remote Desktop App",
    font=("Arial", 24)
)
title.pack(pady=20)


# ================= CONNECT =================
def connect_to_pc():

    ip = simpledialog.askstring(
        "Connect",
        "Enter Receiver PC IP:"
    )

    if ip:

        # START SCREEN SHARE
        threading.Thread(
            target=send_screen,
            args=(ip,),
            daemon=True
        ).start()

        # START CONTROL
        threading.Thread(
            target=send_control,
            args=(ip,),
            daemon=True
        ).start()

        print("Connected to:", ip)


# ================= SHARE SCREEN =================
def share_screen():

    # RECEIVE SCREEN
    threading.Thread(
        target=receive_screen,
        daemon=True
    ).start()

    # RECEIVE CONTROL
    threading.Thread(
        target=receive_control,
        daemon=True
    ).start()

    print("Ready to share screen...")


# CONNECT BUTTON
connect_btn = ctk.CTkButton(
    app,
    text="Connect",
    command=connect_to_pc
)
connect_btn.pack(pady=10)


# SHARE SCREEN BUTTON
share_btn = ctk.CTkButton(
    app,
    text="Share Screen",
    command=share_screen
)
share_btn.pack(pady=10)

app.mainloop()