from Player import Player, HumanPlayer, DumbAIPlayer, SLDumbAIPlayer, LDumbAIPlayer
import socket
import pickle
from Bet import Bet
from time import sleep


class PlayerClient(Player):

    players = {0: HumanPlayer, 1: DumbAIPlayer, 2: SLDumbAIPlayer, 3: LDumbAIPlayer}

    def __init__(self, type=0, port=65443):
        self.out = False
        self.HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))
        self.all_bets = []
        self.bet_history = dict(zip(range(1, 7), [0 for _ in range(5)]))
        self.bot = self.players[type]()
        self.out = False
        self.game_over = False
        self.num_dice = 0

    def receive_info(self):
        x = pickle.loads(self.sock.recv(131072))
        sleep(.01)
        # print(x)
        old_dice = self.num_dice
        self.num_dice = pickle.loads(self.sock.recv(131072))
        if old_dice != self.num_dice and old_dice != 0:
            # print("You have lost a dice")
            pass
        sleep(.01)
        # print("There are " + str(self.num_dice) + " dice left in the game.")
        self.dice_list = pickle.loads(self.sock.recv(131072))
        # print("Dice is:", self.dice_list)
        self.bot.dice_list = self.dice_list
        sleep(.01)

    def place_bet(self):
        last_bet = None if len(self.all_bets) == 0 else self.all_bets[-1]
        # print(last_bet)
        bet = self.bot.place_bet(self.num_dice, self.bet_history, last_bet=last_bet)
        print(bet)
        if bet == 'call':
            self.sock.sendall(pickle.dumps(str(bet)))
            # print("You have called")
            return True
        self.all_bets.append(bet)
        self.bet_history[bet.dice_value] = bet.num_of_dice
        self.sock.sendall(pickle.dumps(str(bet)))
        return False

    def play_round(self):
        if not self.out:
            self.receive_info()
            # print(self.dice_list)
            # print("OK")
            while True:
                response = pickle.loads(self.sock.recv(24))
                # print(response)
                if response == 'S':
                    # print("Place a bet:")
                    called = self.place_bet()
                    if called:
                        self.all_bets = []
                        self.bet_history = dict(zip(range(1, 7), [0 for _ in range(5)]))
                        return
                elif response == 'call':
                    # print("Somebody has called")
                    self.all_bets = []
                    self.bet_history = dict(zip(range(1, 7), [0 for _ in range(5)]))
                    return
                else:
                    # print("The previous bet is:")
                    response = response.split()
                    bet = Bet(int(response[1]), int(response[0]))
                    # print(repr(bet))
                    self.all_bets.append(bet)
                    # print(self.all_bets)
                    self.bet_history[bet.dice_value] = bet.num_of_dice
        else:
            print("You are out")

    def check_out(self):
        check = pickle.loads(self.sock.recv(16384))
        # print("Check is:")
        # print(check)
        self.out = check

    def check_game_over(self):
        self.game_over = pickle.loads(self.sock.recv(16384))

    def check_won(self):
        return pickle.loads(self.sock.recv(16384))

    def reset(self):
        self.all_bets = []
        self.bet_history = dict(zip(range(1, 7), [0 for _ in range(5)]))
        self.out = False
        self.game_over = False

    def num_games(self):
        return pickle.loads(self.sock.recv(1024))
