from Bet import Bet
from random import randint
import operator as op
from functools import reduce
from scipy.stats import skewnorm
import numpy as np


class Player:
    def __init__(self, num_dice=5):
        self.num_dice = num_dice
        self.out = False
        self.dice_list = []

    def roll_dice(self):
        self.dice_list = [randint(1, 6) for _ in range(self.num_dice)]

    def place_bet(self, bet):
        pass


class HumanPlayer(Player):
    def place_bet(self, total_num_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        print("Your dice are: " + ", ".join(str(die) for die in self.dice_list))
        current_bet = None
        while True:
            entered_value = input("Place your bet or call: ")
            print()
            if entered_value.lower() == "call":
                if last_bet is not None:
                    return "call"
                else:
                    print("Cannot call on first bet")
                    continue
            else:
                current_bet = [int(x) for x in entered_value.split()]
                if len(current_bet) != 2:
                    print("Bet is misformatted. Should be n d (n dice of value d)")
                    continue
                current_bet = Bet(current_bet[1], current_bet[0])
                if current_bet.verify_bet(total_num_of_dice, previous_bet=last_bet):
                    return current_bet


class RandomAI(Player):
    def place_bet(self, total_number_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        if not last_bet:
            return Bet(randint(2, 6), randint(1, total_number_of_dice))
        while True:
            bet = Bet(randint(2, 6), randint(last_bet.num_of_dice, total_number_of_dice))
            if bet.verify_bet(total_number_of_dice, last_bet, verbose=False):
                return np.random.choice([bet, 'call'], 1)[0]


class DumbAIPlayer(Player):
    def ncr(self, n, r):
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        return numer / denom

    def calc_prob(self, total_dice, dice_value, num_of_dice):
        return sum([self.ncr(total_dice, i) * (2**(total_dice - i) / 3**total_dice)
                    for i in range(num_of_dice, total_dice + 1)])

    def gen_bets(self, total_dice, bet_history, last_bet=None, num_bets=30):
        if last_bet:
            bets = set()
            i = 0
            probs = skewnorm.pdf(range(last_bet.num_of_dice, total_dice + 1), 5, .5, 4)
            probs = probs / sum(probs)
            dice_probs = [1/5 for _ in range(5)]
            for die in bet_history.keys():
                dice_probs[i - 2] += bet_history[die] / 100
            dice_probs = [x/sum(dice_probs) for x in dice_probs]
            while len(bets) != num_bets and i < 150:
                die_value = int(np.random.choice(np.arange(2, 7), 1, p=dice_probs)[0])
                die_amount = int(np.random.choice(np.arange(last_bet.num_of_dice, total_dice + 1), 1, p=probs)[0])
                bet = Bet(die_value, die_amount)
                if bet.verify_bet(total_dice, last_bet, verbose=False):
                    bets.add(bet)

                i += 1

            return list(bets)

        return [Bet(x, y) for x in range(2, 7) for y in range(1, 4)]

    def get_best(self, total_dice, prob, bluff, bet_history, last_bet):
        if not last_bet and len(self.dice_list) == 1:
            return Bet(self.dice_list[0], 1)
        else:
            bets = self.gen_bets(total_dice, bet_history, last_bet)
            probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice) for bet in bets]

            if not probs:
                return "call"

            sorted_bets = [(x, y) for x, y in sorted(list(zip(probs, bets)), key=lambda pair: -pair[0])]
            if sorted_bets[0][0] < prob:
                return "call"
            else:
                if randint(1, int(1/bluff)) == 1:
                    return sorted_bets[randint(0, int(len(bets) / 3))][1]

                return sorted_bets[0][1]

    def place_bet(self, total_number_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        bet = self.get_best(total_number_of_dice, prob, bluff, bet_history, last_bet)
        return bet


class SLDumbAIPlayer(DumbAIPlayer):
    def ncr(self, n, r):
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        return numer / denom

    def calc_prob(self, total_dice, dice_value, num_of_dice):
        end_index = total_dice - len(self.dice_list)
        our_dice = self.dice_list.count(dice_value) + self.dice_list.count(1)
        start_index = num_of_dice - our_dice
        return sum([self.ncr(end_index, i) * (2**(end_index - i)) / (3**end_index)
                    for i in range(start_index, end_index + 1)])

    def get_best(self, total_dice, prob, bluff, bet_history, last_bet):

        if not last_bet and len(self.dice_list) == 1:
            return Bet(self.dice_list[0], 1)
        else:
            bets = super().gen_bets(total_dice, bet_history, last_bet)
            probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice) for bet in bets]
            if not probs:
                return "call"
            sorted_bets = [(x, y) for x, y in sorted(list(zip(probs, bets)), key=lambda pair: -pair[0])]
            if sorted_bets[0][0] < prob:
                return "call"
            else:
                if randint(1, int(1/bluff)) == 1:
                    return sorted_bets[randint(0, int(len(bets) / 3))][1]

                return sorted_bets[0][1]

    def place_bet(self, total_number_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        bet = self.get_best(total_number_of_dice, prob, bluff, bet_history, last_bet)
        return bet


class LDumbAIPlayer(SLDumbAIPlayer):
    def ncr(self, n, r):
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        return numer / denom

    def calc_prob(self, total_dice, dice_value, num_of_dice, bet_history):
        end_index = total_dice - len(self.dice_list)
        our_dice = self.dice_list.count(dice_value) + self.dice_list.count(1)
        start_index = num_of_dice - our_dice
        prob = sum([self.ncr(end_index, i) * 2**(end_index - i) / 3**end_index
                    for i in range(start_index, end_index + 1)])
        prob += bet_history[dice_value] / 100
        return prob

    def get_best(self, total_dice, bet_history, prob, bluff, last_bet):
        if not last_bet and len(self.dice_list) == 1:
            return Bet(self.dice_list[0], 1)
        elif len(self.dice_list) == 1:
            return "call"
        else:
            bets = super().gen_bets(total_dice, bet_history, last_bet)
            probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice, bet_history) for bet in bets]
            if not probs:
                return "call"

            sorted_bets = [(x, y) for x, y in sorted(list(zip(probs, bets)), key=lambda pair: -pair[0])]
            if sorted_bets[0][0] < prob:
                return "call"
            else:
                if randint(1, int(1/bluff)) == 1:
                    return sorted_bets[randint(0, int(len(bets) / 3))][1]

                return sorted_bets[0][1]

    def place_bet(self, total_number_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        bet = self.get_best(total_number_of_dice, bet_history, prob, bluff, last_bet)
        return bet


class LMiniMax(LDumbAIPlayer):

    def minimax(self, alpha, beta, total_dice, bet_history, last_bet, max_turn=True, max_depth=5):

        bets = super().gen_bets(total_dice, bet_history, last_bet, 3)

        if max_depth == 0 or not bets:
            return (last_bet, super().calc_prob(total_dice, last_bet.dice_value, last_bet.num_of_dice, bet_history))

        # print(bets)

        best_value = float('-inf') if max_turn else float('inf')
        bet_to_make = ""

        for bet in bets:
            bet_to_place, value = self.minimax(alpha, beta, total_dice, bet_history, bet, not max_turn, max_depth - 1)

            if value > best_value and max_turn:
                best_value = value
                bet_to_make = bet
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break

            if value < best_value and not max_turn:
                best_value = value
                bet_to_make = bet
                beta = min(beta, best_value)
                if beta <= alpha:
                    break

        return (bet_to_make, best_value)

    def get_best(self, total_dice, bet_history, prob, bluff, last_bet):
        if not last_bet and len(self.dice_list) == 1:
            return Bet(self.dice_list[0], 1)
        elif len(self.dice_list) == 1:
            return "call"
        else:
            bet, _ = self.minimax(float('-inf'), float('inf'), total_dice, bet_history, last_bet)
            bet_prob = super().calc_prob(total_dice, bet.dice_value, bet.num_of_dice, bet_history)

            if bet_prob < prob:
                return 'call'
            elif randint(1, int(1/bluff)) == 1:
                bets = super().gen_bets(total_dice, bet_history, last_bet)
                probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice, bet_history) for bet in bets]
                if not probs:
                    return "call"

                sorted_bets = [(x, y) for x, y in sorted(list(zip(probs, bets)), key=lambda pair: -pair[0])]

                return sorted_bets[randint(0, int(len(sorted_bets) / 3))][1]

            return bet

    def place_bet(self, total_number_of_dice, bet_history, prob=0.1, bluff=0.1, last_bet=None):
        bet = self.get_best(total_number_of_dice, bet_history, prob, bluff, last_bet)
        return bet


class SLMiniMax(SLDumbAIPlayer):

    def minimax(self, alpha, beta, total_dice, bet_history, last_bet, max_turn=True, max_depth=5):
        bets = super().gen_bets(total_dice, bet_history, last_bet, 3)

        if max_depth == 0 or not bets:
            return (last_bet, super().calc_prob(total_dice, last_bet.dice_value, last_bet.num_of_dice))

        best_value = float('-inf') if max_turn else float('inf')
        bet_to_make = ""

        for bet in bets:
            bet_to_place, value = self.minimax(alpha, beta, total_dice, bet_history, bet, not max_turn, max_depth - 1)

            if value > best_value and max_turn:
                best_value = value
                bet_to_make = bet
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break

            if value < best_value and not max_turn:
                best_value = value
                bet_to_make = bet
                beta = min(beta, best_value)
                if beta <= alpha:
                    break

        return (bet_to_make, best_value)

    def get_best(self, total_dice, bet_history, prob, bluff, last_bet):
        if not last_bet and len(self.dice_list) == 1:
            return Bet(self.dice_list[0], 1)
        elif len(self.dice_list) == 1:
            return "call"
        else:
            bet, _ = self.minimax(float('-inf'), float('inf'), total_dice, bet_history, last_bet)
            bet_prob = super().calc_prob(total_dice, bet.dice_value, bet.num_of_dice)

            if bet_prob < prob:
                return 'call'
            elif randint(1, int(1/bluff)) == 1:
                bets = super().gen_bets(total_dice, bet_history, last_bet)
                probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice) for bet in bets]
                if not probs:
                    return "call"

                sorted_bets = [(x, y) for x, y in sorted(list(zip(probs, bets)), key=lambda pair: -pair[0])]

                return sorted_bets[randint(0, int(len(sorted_bets) / 3))][1]

            return bet

    def place_bet(self, total_number_of_dice, bet_history, prob=0.1, bluff=0.1, last_bet=None):
        bet = self.get_best(total_number_of_dice, bet_history, prob, bluff, last_bet)
        return bet
