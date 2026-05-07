# control.py

import socket
import json
import threading
import tkinter as tk
import pyautogui


# ================= RECEIVE CONTROL =================
def receive_control():
    host = "0.0.0.0"
    port = 9998

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((host, port))
    server.listen(1)

    print("🎮 Waiting for mouse control...")

    conn, addr = server.accept()
    print("🎮 Control connected:", addr)

    screen_width, screen_height = pyautogui.size()

    try:
        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            event = json.loads(data)

            # MOVE MOUSE
            if event["type"] == "move":

                x = int(event["x"] * screen_width)
                y = int(event["y"] * screen_height)

                pyautogui.moveTo(x, y)

            # LEFT CLICK
            elif event["type"] == "click":
                pyautogui.click()

            # RIGHT CLICK
            elif event["type"] == "right_click":
                pyautogui.rightClick()

    except Exception as e:
        print("Control Error:", e)

    finally:
        conn.close()
        server.close()


# ================= SEND CONTROL =================
def send_control(ip):
    port = 9998

    client = socket.socket()
    client.connect((ip, port))

    root = tk.Tk()
    root.title("Remote Mouse Control")

    # small controller window
    root.geometry("800x500")

    label = tk.Label(
        root,
        text="Move mouse inside this window",
        font=("Arial", 14)
    )
    label.pack()

    width = 800
    height = 500

    # SEND MOUSE MOVE
    def mouse_move(event):

        normalized_x = event.x / width
        normalized_y = event.y / height

        data = {
            "type": "move",
            "x": normalized_x,
            "y": normalized_y
        }

        client.send(json.dumps(data).encode())

    # LEFT CLICK
    def left_click(event):

        data = {
            "type": "click"
        }

        client.send(json.dumps(data).encode())

    # RIGHT CLICK
    def right_click(event):

        data = {
            "type": "right_click"
        }

        client.send(json.dumps(data).encode())

    root.bind("<Motion>", mouse_move)
    root.bind("<Button-1>", left_click)
    root.bind("<Button-3>", right_click)

    root.mainloop()

    client.close()