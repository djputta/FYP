from Perudo import Perudo
import socket
from collections import OrderedDict
import pickle
from Player import Player
from Bet import Bet
from time import sleep


class PerudoServer(Perudo):
    def __init__(self, dice_per_player=5, num_players=1, num_games=1, port=65443):
        self.HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.HOST, self.PORT))
        self.sock.listen()
        self.player_list = OrderedDict()
        self.num_games = num_games
        self.total_dice = dice_per_player * num_players
        self.dice_pp = dice_per_player
        self.all_bets = []
        self.game_over = False
        self.turn = 0

    def add_players(self):
        while len(self.player_list) < self.total_dice / self.dice_pp:
            conn, addr = self.sock.accept()
            print('Connected by', addr)
            self.player_list[(conn, addr)] = Player(self.dice_pp)
        print("All Players Connected")

    def check_call(self, last_bet, current_player):
        actual_amount = 0
        for player in self.player_list.values():
            actual_amount += sum([x == last_bet.dice_value or x == 1 for x in player.dice_list])

        if last_bet.num_of_dice > actual_amount:
            # print("Successful Call")
            previous_player = list(self.player_list.keys())[(current_player - 1) % len(self.player_list)]
            self.turn = (current_player - 1) % len(self.player_list)
            if not self.player_list[previous_player].out:
                self.player_list[previous_player].num_dice -= 1
                if self.player_list[previous_player].num_dice == 0:
                    self.player_list[previous_player].out = True
                return True
            else:
                while True:
                    current_player -= 1
                    previous_player = list(self.player_list.keys())[(current_player - 1) % len(self.player_list)]
                    if not self.player_list[previous_player].out:
                        self.player_list[previous_player].num_dice -= 1
                        if self.player_list[previous_player].num_dice == 0:
                            self.player_list[previous_player].out = True
                        return False

        else:
            # print("Unsuccessful Call")
            self.turn = current_player
            self.player_list[list(self.player_list.keys())[current_player]].num_dice -= 1
            if self.player_list[list(self.player_list.keys())[current_player]].num_dice == 0:
                self.player_list[list(self.player_list.keys())[current_player]].out = True
            return False

    def send_dice(self):
        # print("Sending info...")
        for player in list(self.player_list.keys()):
            self.player_list[player].roll_dice()

        for player in list(self.player_list.keys()):
            if not self.player_list[player].out:
                player[0].sendall(pickle.dumps(self.total_dice))
                player[0].recv(131072)
                dice_list = self.player_list[player].dice_list
                player[0].sendall(pickle.dumps(dice_list))
                player[0].recv(131072)

    def play_round(self):
        self.total_dice = sum([player.num_dice for player in self.player_list.values()])
        self.send_dice()
        while True:
            # current_player = self.player_list[self.player_list.keys()[turn]]
            if not list(self.player_list.values())[self.turn].out:
                # print("Player {}'s turn".format(self.turn + 1))
                # dice = self.player_list[list(self.player_list.keys())[self.turn]].num_dice
                # print("They have {} dice left in the game".format(dice))
                bet = self.get_bet(self.turn)

                for i, player in enumerate(self.player_list.keys()):
                    if i != self.turn and not self.player_list[player].out:
                        player[0].sendall(pickle.dumps(str(bet)))
                        player[0].recv(131072)

                if isinstance(bet, str):
                    return (self.turn, self.check_call(self.all_bets[-1], self.turn))

                self.all_bets.append(bet)
            self.turn = (self.turn + 1) % len(self.player_list)

    def get_bet(self, turn):
        player = list(self.player_list.keys())[self.turn][0]
        player.sendall(pickle.dumps("S"))
        player.recv(131072)
        bet = pickle.loads(player.recv(131072))
        if bet == 'call':
            return 'call'
        bet = bet.split()
        # print(bet[2], bet[0])
        return Bet(int(bet[1]), int(bet[0]))

    def send_out(self):
        for player in list(self.player_list.keys()):
            if self.player_list[player].out:
                player[0].sendall(pickle.dumps(True))
                player[0].recv(131072)
            else:
                player[0].sendall(pickle.dumps(False))
                player[0].recv(131072)

    def send_game_over(self):
        for player in list(self.player_list.keys()):
            if sum([x.out for x in self.player_list.values()]) == len(self.player_list) - 1:
                self.game_over = True
                print("Game Over")
                player[0].sendall(pickle.dumps(True))
                player[0].recv(131072)
            else:
                player[0].sendall(pickle.dumps(False))
                player[0].recv(131072)

    def broadcast_win(self):
        for player in list(self.player_list.keys()):
            if self.player_list[player].out:
                player[0].sendall(pickle.dumps(False))
                player[0].recv(131072)
            else:
                player[0].sendall(pickle.dumps(True))
                player[0].recv(131072)

    def reset(self):
        for player in list(self.player_list.keys()):
            self.player_list[player].num_dice = self.dice_pp
            self.player_list[player].out = False
        self.all_bets = []
        self.game_over = False
        self.total_dice = self.dice_pp * len(self.player_list)

    def send_num_games(self):
        for player in list(self.player_list.keys()):
            player[0].sendall(pickle.dumps(self.num_games))
            player[0].recv(131072)
