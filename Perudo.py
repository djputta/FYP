from Player import HumanPlayer, SLDumbAIPlayer, LDumbAIPlayer
from random import choice


class Perudo():
    def __init__(self, dice_per_player=5, human_players=2, bot_player=0):
        self.player_list = [HumanPlayer(dice_per_player) for _ in range(human_players)] + \
            [LDumbAIPlayer(dice_per_player) for _ in range(bot_player)]
        self.bet_history = dict(zip(range(2, 7), [0] * 6))
        self.all_bets = []
        self.first_player = choice(self.player_list)
        self.round_number = 0
        self.total_dice = dice_per_player * (human_players + bot_player)

    def check_call(self, last_bet, current_player):
        actual_amount = 0
        for player in self.player_list:
            actual_amount += sum([x == last_bet.dice_value or x == 1 for x in player.dice_list])
        if last_bet.num_of_dice > actual_amount:
            print("Successful Call")
            self.player_list[(current_player - 1) % len(self.player_list)].num_dice -= 1
            if self.player_list[(current_player - 1) % len(self.player_list)].num_dice == 0:
                self.player_list[(current_player - 1) % len(self.player_list)].out = True
        else:
            print("Unsuccessful Call")
            self.player_list[current_player].num_dice -= 1
            if self.player_list[current_player].num_dice == 0:
                self.player_list[current_player].out = True

    def roll_dices(self):
        for player in self.player_list:
            player.roll_dice(player.num_dice)
        self.bet_history = dict(zip(range(2, 7), [0] * 6))
        self.all_bets = []

    def play_round(self):
        self.total_dice = sum([player.num_dice for player in self.player_list])
        self.roll_dices()
        player = 0
        while True:
            print(self.round_number)
            current_player = self.player_list[player]
            print("Player {}'s turn".format(player + 1))
            if self.round_number == 0:
                bet = current_player.place_bet(self.total_dice, self.bet_history)
                self.bet_history[bet.dice_value] = bet.num_of_dice
                self.all_bets.append(bet)
            else:
                bet = current_player.place_bet(self.total_dice, self.bet_history, self.all_bets[-1])
                if bet == 'call':
                    self.check_call(self.all_bets[-1], player)
                    self.round_number = 0
                    return
                self.all_bets.append(bet)
                self.bet_history[bet.dice_value] = bet.num_of_dice
            self.round_number += 1
            player = (player + 1) % len(self.player_list)
