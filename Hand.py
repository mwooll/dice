# Hand
import pandas as pd
# from itertools import product, reduce

from Dice import Dice


def get_grime_combinations(n_dice, n_opp):
    if n_opp >= n_dice:
        raise ValueError("No combinations can be found when rolling against " +
                         f"{n_opp} opponents with only {n_dice} dice.")

    dice = [[k] for k in range(n_dice)]
    combinations = {1: dice}
    for k in range(2, n_opp+1):
        combi_k = [combi + die for die in dice
                   for combi in combinations[k-1] if die[0] > combi[-1]]
        combinations[k] = [item for item in combi_k]
    return combinations
    

class Hand:
    def __init__(self):
        self._dice  = {}
        self._rolls = {}
        self._rolls_num = 1

    def add_die(self,
                numbers: list,
                name: str=None):
        new_dice = Dice(numbers, name)
        self._dice[name] = new_dice

    def set_dice_set(self, numbers, names=None):
        self.empty_hand()
        if names == None:
            names = [f"dice_{k}" for k in range(len(numbers))]
        for k, num_list in enumerate(numbers):
            self.add_die(num_list, names[k])

    def get_number_of_dice(self):
        return len(self._dice)

    def empty_hand(self):
        self._dice = {}

    def initiate_dice(self, rolls):
        for name, die in self._dice.items():
            die.roll(rolls)
        self._rolls_num = rolls

    def get_combinations(self, dice_num, opponents):
        combinations = [die for die in self._dice.keys()]
        if opponents > 1:
            dice_num = len(combinations)
            plain_combinations = get_grime_combinations(dice_num, opponents)
            combinations = {k: [[combinations[index] for index in numbers]
                                for numbers in plain_combinations[k]]
                            for k in range(1, opponents+1)}
        else:
            combinations = {1: combinations}
        self._combinations = combinations
        self._num_combi = len(combinations)
        # combinations["count"] = [len(combinations[k]) for k in combinations]
        return combinations

    def __str__(self):
        output = ""
        for name, dice in self._dice.items():
            output += f"{name}: {dice._list}, "
        output = output[:-2]
        return output

    def __repr__(self):
        name = ""
        for key, values in self._dice.items():
            name += f"{key}__"
            for value in values._list:
                name += f"{value}_"
            name += "_"
        return name

    def copy(self):
        return self._dice

    def get_faces(self):
        return [[face for face in die._list] for die in self._dice.values()]

    def calculate_simplicity(self):
        return sum(len(die._prob[1]) for die in self._dice.values())

    def fight(self, initiator: Dice, defender: Dice, lap: int, precision: int=5):
        """initiates a fight between two dice"""
        place = initiator.battles[lap][defender.name]
        for power in initiator._prob[lap].keys():
            for health in defender._prob[lap].keys():
                stat = round(initiator._prob[lap][power] * defender._prob[lap][health],
                             precision)
                if power > health:
                    place["{}>{}".format(power, health)] = ["won", stat]
                if power < health:
                    place["{}<{}".format(power, health)] = ["lost", stat]
                if power == health:
                    place["{}={}".format(power, health)] = ["tie", stat]

    def evaluate(self, message: str="\t", precision: int=5):
        """evaluates the tournament"""
        for die in self._dice.values():
            for series in list(die.battles.keys())[1:]:
                for opponent in self._dice.values():
                    winner_p = 0
                    ties_p   = 0
                    place = die.battles[series][opponent.name]
                    for pairing in place:
                        if place[pairing][0] == "won":
                            winner_p += place[pairing][1]
                        if place[pairing][0] == "lost":
                            winner_p -= place[pairing][1]
                        if place[pairing][0] == "tie":
                            ties_p += place[pairing][1]

                    difference = 0
                    if ties_p != 1:
                        difference = round(winner_p/(1-ties_p), precision)
                    winning = round(0.5 + difference/2, precision)
                    win_rate = f"{round(winning*100, 2)}%"

                    if difference > 0:
                        place["result"] = [die.name, abs(difference),
                                           win_rate, winning]
                    if difference < 0:
                        place["result"] = [opponent.name, abs(difference),
                                           win_rate, winning]
                    if difference == 0:
                        place["result"] = ["tie", 0, message, winning]

    def roll_the_dice(self,
                      rolls: int=2,
                      message: str="\t",
                      accuracy: int=5,
                      oppponents: int=1):
        """rolls the dice and saves the results"""
        self.initiate_dice(rolls)
        for attacker in self._dice.values():
            for roll in range(1, rolls+1):
                attacker.battles[roll] = {}
            
                for defender in self._dice.values():
                    attacker.battles[roll][defender.name] = {}
                    self.fight(attacker, defender, roll, accuracy)

        self.evaluate(message, accuracy)

    def show_results(self):
        for die in self._dice.values():
            print("\n", die.battles)

    def frame_results(self, rolls=None):
        if rolls == None:
            rolls = range(self._rolls_num)
        rolls = sorted(rolls)
        first = "1 die" if rolls[0] == 1 else f"{rolls[0]} dice"
        df = pd.DataFrame(columns=[first] + list(self._dice.keys()))

        rows = []
        for roll in rolls:
            rows.extend(list(self._dice.keys())+["", f"{roll+1} dice"])
        df[first] = rows

        for defender in self._dice.values():
            column = []
            for roll in rolls:
                for attacker in self._dice.values():
                    column.append(attacker.battles[roll][defender.name]["result"][2])
                column.extend(["", defender.name])
            df[defender.name] = column

        df = df[0: -2]
        return df

    def raw_results(self, rolls=None, cut_off=0):
        if rolls == None:
            rolls = range(self._rolls_num)
        rolls = sorted(rolls)
        df = pd.DataFrame(columns=list(self._dice.keys()))

        for defender in self._dice.values():
            column = []
            for roll in rolls:
                for attacker in self._dice.values():
                    chance = attacker.battles[roll][defender.name]["result"][3]
                    biased = chance*(chance > cut_off)
                    column.append(biased)
            df[defender.name] = column
        return df

    def get_die_performance(self, dice, index=3):
        performance = {k: [self._dice[dice].battles[k][opponent]["result"][index] 
                        for opponent in self._dice.keys()]
                       for k in range(1, self._rolls_num+1)}
        return performance


def roll_3_dice(n):
    h = Hand()
    h.add_die([2], "blue")
    h.add_die([1, 1, 4], "red")
    h.add_die([0, 3, 3], "green")
    h.roll_the_dice(n, ".")

    print(h.frame_results([k+1 for k in range(n)]))
    return h

def roll_Grime_dice(n):
    h = Hand()
    h.add_die([2, 2, 2, 7, 7, 7], "blue")
    h.add_die([1, 1, 6, 6, 6, 6], "magenta")
    h.add_die([0, 5, 5, 5, 5, 5], "olive")
    h.add_die([4, 4, 4, 4, 4, 9], "red")
    h.add_die([3, 3, 3, 3, 8, 8], "yellow")
    h.roll_the_dice(n, ".")

    print(h.frame_results([k+1 for k in range(n)]))
    return h

def roll_Efron_dice(n):
    dice = [[3], [2, 2, 6], [1, 5], [0, 4, 4]]
    names = ["blue", "red", "green", "yellow"]

    h = Hand()
    h.set_dice_set(dice, names)
    h.roll_the_dice(n, ".")

    print(h.frame_results([k+1 for k in range(n)]))
    return h


if __name__ == "__main__":
    dice_to_roll = 2
    # hand = roll_3_dice(dice_to_roll)
    grime = roll_Grime_dice(dice_to_roll)
    # effron = roll_Efron_dice(dice_to_roll)