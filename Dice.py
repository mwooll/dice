# Dice

from unittest import main, TestCase

"""colours"""
colours = ["blue", "red", "magenta", "yellow", "olive",
           "cyan", "white", "grey", "black"]

class Dice:
    def __init__(self,
                 numbers=[],
                 name="Blank"):
        if numbers == []:
            numbers = [0]
        numbers.sort()
        self._name = name
        self._list = numbers

    def get_numbers(self):
        return self._list

    def roll(self, rolls):
        self.reset()
        for n in self._list:
            if n not in self._dict[1]:
                self._dict[1][n] = 0
            if n in self._dict[1]:
                self._dict[1][n] += 1

        for r in range(1, rolls):
            self._dict[r+1] = {}
            for n in self._dict[r].keys():
                for k in self._dict[1]:
                    if n+k not in self._dict[r+1]:
                        self._dict[r+1][n+k] = 0
                    if n+k in self._dict[r+1]:
                        self._dict[r+1][n+k] += self._dict[r][n] * self._dict[1][k]

        for p in range(1, rolls+1):
            self._prob[p] = {}
            self._prob_r[p] = {}
            self._total[p] = sum(val for val in self._dict[p].values())
            for n in self._dict[p]:
                self._prob[p][n] = self._dict[p][n]/self._total[p]
                self._prob_r[p][n] = "{}/{}".format(self._dict[p][n], self._total[p])

    def reset(self):
        self._dict = {1: {}}
        self._prob = {}
        self._prob_r = {}
        self._total = {}
        self.battles = {"Colour": self._name}

    def get_probabilities(self):
        return self._prob

    def _str_(self):
        return self._name

    def _repr_(self):
        return self._name


class DiceTest(TestCase):
    def test_get_numbers(self):
        expected = [1, 2, 3]
        actual = Dice([1, 2, 3], "blue").get_numbers()
        self.assertAlmostEqual(expected, actual)

    def test_empty_numbers(self):
        expected = [0]
        actual = Dice([], "green").get_numbers()
        self.assertEqual(expected, actual)

    def test_duplicates(self):
        expected = [17, 17]
        actual = Dice([17, 17], "red").get_numbers()
        self.assertEqual(expected, actual)

    def test_get_probabilities_1_roll(self):
        expected = {1: {0: 0.5, 1: 0.5}}
        dice = Dice([0, 1], "yellow")
        dice.roll(1)
        actual = dice.get_probabilities()
        self.assertEqual(expected, actual)

    def test_get_probabilities_2_rolls(self):
        expected = {1: {0: 0.5, 1: 0.5},
                    2: {0: 0.25, 1: 0.5, 2: 0.25}}
        dice = Dice([0, 1], "magenty")
        dice.roll(2)
        actual = dice.get_probabilities()
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    main()
    # dice = Dice([0, 1], "dice")
    # dice.roll(2)
    # print(dice.get_probabilities())