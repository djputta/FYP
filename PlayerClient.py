from Player import HumanPlayer, DumbAIPlayer, SLDumbAIPlayer, LDumbAIPlayer, LMiniMax, SLMiniMax, RandomAI
import socket
import pickle
from Bet import Bet


class PlayerClient():

    players = {0: HumanPlayer, 1: DumbAIPlayer, 2: SLDumbAIPlayer,
               3: LDumbAIPlayer, 4: LMiniMax, 5: SLMiniMax, 6: RandomAI}

    def __init__(self, type=0, host='127.0.0.1', port=65445):
        self.HOST = host  # Standard loopback interface address (localhost)
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))
        self.all_bets = []
        self.bet_history = dict(zip(range(2, 7), [0 for _ in range(5)]))
        self.bot = self.players[type]()
        self.out = False
        self.game_over = False
        self.num_dice = 0
        self.dice_list = []
        self.called = False
        self.opp_called = False
        self.went_previously = False

    def receive_info(self):
        '''
        Receives the number of dice and your dice for the round.
        '''
        self.num_dice = pickle.loads(self.sock.recv(131072))
        self.sock.sendall(pickle.dumps("OK"))
        print("There are " + str(self.num_dice) + " dice left in the game.")
        print()

        old_dice = self.dice_list
        self.dice_list = pickle.loads(self.sock.recv(131072))
        self.sock.sendall(pickle.dumps("OK"))

        if self.called and len(old_dice) > len(self.dice_list):
            print("You have called unsuccessfully")
            print()
            pass
        elif self.called and len(old_dice) == len(self.dice_list):
            print("You have called successfully")
            print()
        elif self.opp_called and len(old_dice) > len(self.dice_list):
            print("Somebody has called successfully against you")
            print()
        elif self.opp_called and len(old_dice) == len(self.dice_list) and self.went_previously:
            print("Somebody has called unsuccessfully against you")
            print()

        # print("Dice is:", self.dice_list)
        self.bot.dice_list = self.dice_list

    def place_bet(self, prob, bluff):
        '''
        Tell's whatever bet you are using to place a bet and to send it.
        '''
        last_bet = None if len(self.all_bets) == 0 else self.all_bets[-1]
        bet = self.bot.place_bet(self.num_dice, self.bet_history, prob, bluff, last_bet)
        if isinstance(bet, str):  # If you have called
            self.sock.sendall(pickle.dumps(str(bet)))
            return True
        self.all_bets.append(bet)
        self.bet_history[bet.dice_value] = bet.num_of_dice
        self.sock.sendall(pickle.dumps(str(bet)))
        return False

    def play_round(self, prob=.1, bluff=.1):
        '''
        prob: cutoff probability for deciding to place or call a bet
        bluff: probability to place a random bet

        Play a round of Perudo
        '''
        if not self.out:
            self.receive_info()
            while True:
                response = pickle.loads(self.sock.recv(24))
                self.sock.sendall(pickle.dumps("OK"))
                if response == 'S':
                    self.called = self.place_bet(prob, bluff)
                    self.went_previously = True
                    if self.called:
                        self.all_bets = []
                        self.bet_history = dict(zip(range(2, 7), [0 for _ in range(5)]))
                        return
                elif response == 'call':
                    print("Someone has called")
                    self.opp_called = True
                    self.all_bets = []
                    self.bet_history = dict(zip(range(2, 7), [0 for _ in range(5)]))
                    return
                else:
                    self.opp_called = False
                    self.went_previously = False
                    print("The previous bet is: ", end='')
                    response = response.split()
                    bet = Bet(int(response[1]), int(response[0]))
                    print(repr(bet))
                    print()
                    self.all_bets.append(bet)
                    self.bet_history[bet.dice_value] = bet.num_of_dice
        else:
            print("You are out")
            pass

    def check_out(self):
        check = pickle.loads(self.sock.recv(16384))
        self.sock.sendall(pickle.dumps("OK"))
        self.out = check

    def check_game_over(self):
        self.game_over = pickle.loads(self.sock.recv(16384))
        self.sock.sendall(pickle.dumps("OK"))

    def check_won(self):
        won = pickle.loads(self.sock.recv(16384))
        self.sock.sendall(pickle.dumps("OK"))
        return won

    def reset(self):
        self.all_bets = []
        self.bet_history = dict(zip(range(2, 7), [0 for _ in range(5)]))
        self.out = False
        self.game_over = False
        self.opp_called = False
        self.called = False

    def num_games(self):
        _num_games = pickle.loads(self.sock.recv(1024))
        self.sock.sendall(pickle.dumps("OK"))
        return _num_games
