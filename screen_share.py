import socket
import mss
import pickle
import time
import cv2
import numpy as np

# ================= SEND SCREEN =================
def send_screen(ip):
    port = 9999

    s = socket.socket()
    s.connect((ip, port))

    with mss.mss() as sct:
        while True:
            img = sct.grab(sct.monitors[1])
            data = pickle.dumps((img.size, img.rgb))

            s.sendall(len(data).to_bytes(4, 'big') + data)

            time.sleep(0.03)   # smooth FPS


# ================= RECEIVE SCREEN =================
def receive_screen():
    port = 9999

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(1)

    print("🖥️ Waiting for screen...")
    conn, addr = server.accept()
    print("Connected to:", addr)

    data = b""
    payload_size = 4

    try:
        while True:
            while len(data) < payload_size:
                packet = conn.recv(4096)
                if not packet:
                    return
                data += packet

            packed_size = data[:payload_size]
            data = data[payload_size:]
            size = int.from_bytes(packed_size, 'big')

            while len(data) < size:
                packet = conn.recv(4096)
                if not packet:
                    return
                data += packet

            frame_data = data[:size]
            data = data[size:]

            screen_size, pixels = pickle.loads(frame_data)

            frame = np.frombuffer(pixels, dtype=np.uint8)
            frame = frame.reshape((screen_size[1], screen_size[0], 3))

            frame = cv2.resize(frame, (800, 500))

            cv2.imshow("Remote Screen", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()
        server.close()
        cv2.destroyAllWindows()