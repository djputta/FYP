# from Player import Player
import socket
import pickle


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65437        # The port used by the server

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

while True:
    data = sock.recv(4096)
    print(data)
    if data == b"Ready":
        break

data = sock.recv(4096)

print("OK")
print(data)
print(type(data))
sock.close()
