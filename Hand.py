# Hand
import pandas as pd

from Dice import Dice

class Hand:
    def __init__(self, base):
        self._dice  = {}
        self._rolls = {}

        # self._initiated = False
        # self._rolled    = False
        self._rolls_num = base

    def add_die(self,
                numbers: list,
                name: str=None):
        new_dice = Dice(numbers, name)
        self._dice[new_dice.name] = new_dice

    def get_number_of_dice(self):
        return len(self._dice)

    def empty_hand(self):
        self._dice    = {}

    def initiate_dice(self, rolls) -> None:
        for name, die in self._dice.items():
            die.roll(rolls)

    def __str__(self) -> str:
        output = ""
        for name, dice in self._dice.items():
            output += f"{name}: {dice.list}, "
        output = output[:-2]
        return output

    def __repr__(self) -> str:
        name = ""
        for key, values in self._dice.items():
            name += f"{key}__"
            for value in values.list:
                name += f"{value}_"
            name += "_"
        return name

    def fight(self, initiator: Dice, defender: Dice, lap: int, precision: int=5) -> None:
        """initiates a fight between two dice"""
        place = initiator.battles[lap][str(defender)]
        for power in initiator.prob[lap].keys():
            for health in defender.prob[lap].keys():
                stat = round(initiator.prob[lap][power] * defender.prob[lap][health], precision)
                if power > health:
                    place["{}>{}".format(power, health)] = ["won", stat]
                if power < health:
                    place["{}<{}".format(power, health)] = ["lost", stat]
                if power == health:
                    place["{}={}".format(power, health)] = ["tie", stat]

    def evaluate(self, message: str="\t", precision: int=5) -> None:
        """evaluates the tournament"""
        for die in self._dice.values():
            for series in list(die.battles.keys())[1:]:
                for opponent in self._dice.values():
                    winner_p = 0
                    ties_p   = 0
                    place = die.battles[series][str(opponent)]
                    for pairing in place:
                        if place[pairing][0] == "won":
                            winner_p += place[pairing][1]
                        if place[pairing][0] == "lost":
                            winner_p -= place[pairing][1]
                        if place[pairing][0] == "tie":
                            ties_p   += place[pairing][1]

                    difference = 0
                    if ties_p != 1:
                        difference = round(winner_p/(1-ties_p), precision)
                    win_rate   = f"{round(50 + difference*50, 1)}%"

                    if difference > 0:
                        place["result"] = [die.name, abs(difference), win_rate]
                    if difference < 0:
                        place["result"] = [opponent, abs(difference), win_rate]
                    if difference == 0:
                        place["result"] = ["tie", 0, message]

    def roll_the_dice(self, rolls: int, message: str="\t", accuracy: int=5) -> None:
        """rolls the dice and saves the results"""
        self.rolls_num = rolls
        self.initiate_dice(rolls)
        for attacker in self._dice.values():
            for roll in range(rolls):
                attacker.battles[roll] = {}
            
                for defender in self._dice.values():
                    attacker.battles[roll][str(defender)] = {}
                    self.fight(attacker, defender, roll, accuracy)

        self.evaluate(message, accuracy)

    def show_results(self) -> None:
        for die in self._dice.values():
            print("\n", die.battles)

    def frame_results(self, mode: str="") -> str:
        df = pd.DataFrame(columns=["1 die"] + list(self._dice.keys()))

        if mode == "split":
            rows = []
            for roll in range(self.rolls_num):
                rows.extend(list(self._dice.keys())+["", f"{roll+2} dice"])
            df["1 die"] = rows
        else:
            df["1 die"] = list(self._dice.keys())*self.rolls_num

        for defender in self._dice.values():
            column = []
            for roll in range(self.rolls_num):
                for attacker in self._dice.values():
                    column.append(attacker.battles[roll][str(defender)]["result"][2])
                if mode == "split":
                    column.extend(["", defender.name])
            df[str(defender)] = column

        if mode == "split":
            df = df[0: -2]
        return df


if __name__ == "__main__":
    h = Hand(1)