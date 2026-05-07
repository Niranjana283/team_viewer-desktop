import socket
import json

HOST = "0.0.0.0"
PORT = 5000

devices = {}
requests = {}
responses = {}

server = socket.socket()
server.bind((HOST, PORT))
server.listen(5)

print("Server running...")

while True:
    conn, addr = server.accept()
    data = conn.recv(4096).decode()

    request = json.loads(data)

    # REGISTER
    if request["type"] == "register":
        devices[request["id"]] = request["name"]
        conn.send(json.dumps({"status": "registered"}).encode())

    # LIST DEVICES
    elif request["type"] == "list":
        conn.send(json.dumps(devices).encode())

    # SEND REQUEST
    elif request["type"] == "connect":
        target = request["target"]
        requests[target] = request
        print("Stored request for:", target)
        conn.send(b"request_sent")

    # CHECK REQUEST
    elif request["type"] == "check":
        my_id = request["id"]

        if my_id in requests:
            conn.send(json.dumps(requests[my_id]).encode())
        else:
            conn.send(b"none")

    # SEND RESPONSE (ACCEPT / REJECT)
    elif request["type"] == "response":
        sender = request["to"]
        responses[sender] = request
        conn.send(b"response_sent")

    # CHECK RESPONSE
    elif request["type"] == "check_response":
        my_id = request["id"]

        if my_id in responses:
            conn.send(json.dumps(responses[my_id]).encode())
            del responses[my_id]
        else:
            conn.send(b"none")

    conn.close()