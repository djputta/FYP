import socket
import pickle
from Bet import Bet


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65437        # Port to listen on (non-privileged ports are > 1023)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
num_of_players = int(input("Please enter the number of players:"))
dice_per_player = int(input("Please enter the number od dice per player:"))
players = {}

i = 0
bet = Bet(2, 2)
data = pickle.dumps([1, 2])
while len(players) < num_of_players:
    conn, addr = sock.accept()
    print('Connected by', addr)
    players[i] = (conn, addr)
    i += 1
print("All Players Connected")

for addr in players.values():
    with addr[0]:
        addr[0].sendall(b"Ready")
        addr[0].sendall(data)
print("Ready to play")


#players[0][0].sendall(data)

sock.close()
