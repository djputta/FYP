from Bet import Bet
from random import randint, choices
import operator as op
from functools import reduce
from scipy.stats import skewnorm


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
    def place_bet(self, total_num_of_dice, bet_history, last_bet=None):
        print("Your dice are: " + ", ".join(str(die) for die in self.dice_list))
        current_bet = None
        while True:
            entered_value = input("Place your bet or call: ")
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
                # print(current_bet)
                if current_bet.verify_bet(total_num_of_dice, previous_bet=last_bet):
                    print(repr(current_bet))
                    return current_bet


class DumbAIPlayer(Player):
    def ncr(self, n, r):
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        # print(numer / denom)
        return numer / denom

    def calc_prob(self, total_dice, dice_value, num_of_dice):
        return sum([self.ncr(total_dice, i) * (2**(total_dice - i) / 3**total_dice)
                    for i in range(num_of_dice, total_dice + 1)])

    def gen_bets(self, total_dice, last_bet=None, num_bets=15):
        bets = set()

        # print("Dice left: " + str(total_dice))
        # print(repr(last_bet))

        i = 0
        while len(bets) != num_bets and i < 40:
            if last_bet:
                probs = skewnorm.pdf(range(last_bet.num_of_dice, total_dice + 1), 5, .5, 4)
                probs = probs / sum(probs)
                bet = Bet(randint(2, 6), choices(range(last_bet.num_of_dice, total_dice + 1), probs)[0])
                if bet.verify_bet(total_dice, last_bet, verbose=False):
                    bets.add(bet)
            else:
                bet = Bet(randint(2, 6), randint(1, 3))
                bets.add(bet)
            i += 1

        return list(bets)

    def get_best(self, total_dice, prob, bluff, last_bet):
        bets = self.gen_bets(total_dice, last_bet)
        probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice) for bet in bets]
        if probs == [] and last_bet is not None:
            return "call"
        elif probs == [] and last_bet is None:
            return Bet(randint(2, 6), randint(1, total_dice))
        else:
            index, value = max(enumerate(probs), key=op.itemgetter(1))
            if value <= prob:
                return "call"
            else:
                if randint(0, int(1/bluff)) == 0:
                    return bets[randint(0, len(bets) - 1)]

                return bets[index]

    def place_bet(self, total_number_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        # print("Your dice are: " + ", ".join(str(die) for die in self.dice_list))
        bet = self.get_best(total_number_of_dice, prob, bluff, last_bet)
        # print(repr(bet))
        return bet


class SLDumbAIPlayer(DumbAIPlayer):
    def ncr(self, n, r):
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        return numer / denom

    def calc_prob(self, total_dice, dice_value, num_of_dice):
        end_index = total_dice - len(self.dice_list)
        our_dice = self.dice_list.count(dice_value)
        start_index = num_of_dice - our_dice
        return sum([self.ncr(end_index, i) * 2**(end_index - i) / 3**end_index
                    for i in range(start_index, end_index + 1)])

    def get_best(self, total_dice, prob, bluff, last_bet):

        if not last_bet and len(self.dice_list) == 1:
            return Bet(self.dice_list[0], 1)
        elif len(self.dice_list) == 1:
            return "call"
        else:
            bets = super().gen_bets(total_dice, last_bet)
            probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice) for bet in bets]
            index, value = max(enumerate(probs), key=op.itemgetter(1))
            # print(bets)
            # print(probs)
            if value <= prob:
                return "call"
            else:
                if randint(0, int(1/bluff)) == 0:
                    return bets[randint(0, len(bets) - 1)]

                return bets[index]

    def place_bet(self, total_number_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        # print("Your dice are: " + ", ".join(str(die) for die in self.dice_list))
        bet = self.get_best(total_number_of_dice, prob, bluff, last_bet)
        # print(repr(bet))
        return bet


class LDumbAIPlayer(SLDumbAIPlayer):
    def ncr(self, n, r):
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        return numer / denom

    def calc_prob(self, total_dice, dice_value, num_of_dice, bet_history, last_bet=None):
        if not last_bet:
            last_bet = Bet(0, 0)
        end_index = total_dice - len(self.dice_list) - sum(bet_history.values()) + last_bet.num_of_dice
        our_dice = self.dice_list.count(dice_value) + self.dice_list.count(1)
        start_index = num_of_dice - our_dice
        return sum([self.ncr(end_index, i) * 2**(end_index - i) / 3**end_index
                    for i in range(start_index, end_index + 1)])

    def get_best(self, total_dice, bet_history, prob, bluff, last_bet):
        if not last_bet and len(self.dice_list) == 1:
            return Bet(self.dice_list[0], 1)
        elif len(self.dice_list) == 1:
            return "call"
        else:
            bets = super().gen_bets(total_dice, last_bet)
            probs = [self.calc_prob(total_dice, bet.dice_value, bet.num_of_dice, bet_history, last_bet) for bet in bets]
            index, value = max(enumerate(probs), key=op.itemgetter(1))
            # print(probs)
            if value <= prob:
                return "call"
            else:
                if randint(0, int(1/bluff)) == 0:
                    return bets[randint(0, len(bets) - 1)]

                return bets[index]

    def place_bet(self, total_number_of_dice, bet_history, prob=.1, bluff=.1, last_bet=None):
        # print("Your dice are: " + ", ".join(str(die) for die in self.dice_list))
        bet = self.get_best(total_number_of_dice, bet_history, prob, bluff, last_bet)
        # print(repr(bet))
        return bet


class MiniMax(SLDumbAIPlayer):
    pruned = 0

    def minimax(self, alpha, beta, total_dice, last_bet, max_turn=True, max_depth=4):
        print(max_depth)
        if max_depth == 0:
            print("Finished on {}'s turn".format("Max" if max_turn else "Min"))
            return (last_bet, super().calc_prob(total_dice, last_bet.dice_value, last_bet.num_of_dice) * (1 if not max_turn else -1))

        bets = super().gen_bets(total_dice, last_bet, 10)
        print(bets)

        best_value = float('-inf') if max_turn else float('inf')
        bet_to_make = ""

        for bet in bets:
            bet_to_place, value = self.minimax(alpha, beta, total_dice, bet, not max_turn, max_depth - 1)
            print("It is {}'s turn".format("Max" if max_turn else "Min"))
            print("{} has probability {}".format(repr(bet_to_place), value))

            if value > best_value and max_turn:
                best_value = value
                bet_to_make = bet
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    self.pruned += 1
                    break

            if value < best_value and not max_turn:
                best_value = value
                bet_to_make = bet
                beta = min(beta, best_value)
                if beta <= alpha:
                    self.pruned += 1
                    break

        print("{}: On {}'s turn the best bet was {} with a prob of {}".format(max_depth, "Max" if max_turn else "Min", repr(bet_to_make), best_value))
        return (bet_to_make, best_value)

    def place_bet(self, total_number_of_dice, bet_history, prob=0.1, bluff=0.1, last_bet=None):
        bet, value = self.minimax(float('-inf'), float('inf'), total_number_of_dice, last_bet)
        print(self.pruned)
        return (bet, value)
