import socket
import json
import uuid
import time
import threading

SERVER_IP = "127.0.0.1"
PORT = 5000

device_id = input("Enter your device ID (or press Enter for new): ")

if device_id == "":
    device_id = str(uuid.uuid4())
    print("Your new device ID:", device_id)

name = input("Enter your name: ")

# REGISTER
client = socket.socket()
client.connect((SERVER_IP, PORT))
client.send(json.dumps({
    "type": "register",
    "id": device_id,
    "name": name
}).encode())
print(client.recv(1024).decode())
client.close()


# 🔥 LISTEN FOR REQUESTS (RECEIVER SIDE)
def listen_requests():
    while True:
        client = socket.socket()
        client.connect((SERVER_IP, PORT))

        client.send(json.dumps({
            "type": "check",
            "id": device_id
        }).encode())

        response = client.recv(4096).decode()
        client.close()

        if response != "none":
            req = json.loads(response)
            print(f"\n🔥 Connection request from {req['name']}")

            choice = input("Accept? (y/n): ")

            client = socket.socket()
            client.connect((SERVER_IP, PORT))

            if choice == "y":
                client.send(json.dumps({
                    "type": "response",
                    "to": req["from"],
                    "status": "accepted"
                }).encode())
                print("✅ Accepted")

                # START RECEIVER FIRST
                from screen_share import receive_screen
                threading.Thread(target=receive_screen, daemon=True).start()

            else:
                client.send(json.dumps({
                    "type": "response",
                    "to": req["from"],
                    "status": "rejected"
                }).encode())
                print("❌ Rejected")

            client.close()

        time.sleep(2)


# 🔥 LISTEN FOR RESPONSE (SENDER SIDE)
def listen_response():
    while True:
        client = socket.socket()
        client.connect((SERVER_IP, PORT))

        client.send(json.dumps({
            "type": "check_response",
            "id": device_id
        }).encode())

        res = client.recv(4096).decode()
        client.close()

        if res != "none":
            response = json.loads(res)

            if response["status"] == "accepted":
                print("\n🎉 Connection ACCEPTED")

                # START SENDER AFTER ACCEPT
                from screen_share import send_screen
                time.sleep(2)
                send_screen("172.29.16.1")
                from control import send_control

                send_control("172.29.16.1")

            else:
                print("\n❌ Connection REJECTED")

            break

        time.sleep(2)


# START BACKGROUND LISTENER
threading.Thread(target=listen_requests, daemon=True).start()
from control import receive_control, send_control

threading.Thread(target=receive_control, daemon=True).start()


# GET DEVICE LIST
client = socket.socket()
client.connect((SERVER_IP, PORT))
client.send(json.dumps({"type": "list"}).encode())
devices = json.loads(client.recv(4096).decode())
client.close()

print("\nAvailable devices:")
for k, v in devices.items():
    print(k, ":", v)


# SELECT TARGET
target_id = input("\nEnter device ID to connect: ")

if target_id not in devices:
    print("❌ Invalid ID")
    exit()


# SEND REQUEST
client = socket.socket()
client.connect((SERVER_IP, PORT))
client.send(json.dumps({
    "type": "connect",
    "from": device_id,
    "name": name,
    "target": target_id
}).encode())
print(client.recv(1024).decode())
client.close()

print("Waiting for response...")

# WAIT RESPONSE
listen_response()