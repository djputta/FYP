class Bet:
    def __init__(self, dice_value, num_of_dice):
        self.dice_value = dice_value
        self.num_of_dice = num_of_dice

    def __repr__(self):
        return ("There are {} {}'s" if self.num_of_dice != 1 else "There is {} {}").format(self.num_of_dice, self.dice_value)

    def __str__(self):
        return "{} {}".format(self.num_of_dice, self.dice_value)

    def __eq__(self, value):
        if self.dice_value == value.dice_value and self.num_of_dice == value.num_of_dice:
            return True
        return False

    def __hash__(self):
        return hash(self.num_of_dice * 10 + self.dice_value)

    def verify_bet(self, total_dice, previous_bet=None, verbose=True):
        if self.dice_value not in range(2, 7):
            if verbose:
                print('dice_value should be between 2 and 6.')
            return False
        if self.num_of_dice not in range(1, total_dice + 1):
            if verbose:
                print('You bet more dice than were in the game')
            return False
        if previous_bet:
            if int(str(self.num_of_dice) + str(self.dice_value)) <= int(str(previous_bet.num_of_dice) +
                                                                        str(previous_bet.dice_value)):
                if verbose:
                    print('Rules have been broken.')
                return False
        return True
