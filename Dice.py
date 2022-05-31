# Dice

from unittest import main, TestCase

"""colours"""
colours = ["blue", "red", "magenta", "yellow", "olive",
           "cyan", "white", "grey", "black"]

def decompose_string(string):
    pieces = {}
    for letter in string:
        if letter not in pieces:
            pieces[letter] = 1
        else:
            pieces[letter] += 1

    sorted_letters = sorted(pieces.keys())
    decomposed = ""
    for letter in sorted_letters:
        onset = f"{pieces[letter]}*" if pieces[letter]>1 else ""
        decomposed += onset + f"{letter} + " 
    decomposed = decomposed[:-3]
    return decomposed


class Dice:
    def __init__(self,
                 numbers=[],
                 name="Blank"):
        if numbers == []:
            numbers = [0]
        numbers.sort()
        self.name = name
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

    def simplify_letter_die(self, rolls):
        if not isinstance(self._list[0], str):
            raise ValueError("The die faces are not strings.")

        roll_num = min(rolls, max(self._prob.keys()))
        simplified = {}
        for roll in range(1, roll_num+1):
            simplified[roll] = {}
            for key, value in self._prob[roll].items():
                value = round(value, 5)
                decomp = decompose_string(key)
                if decomp not in simplified[roll]:
                    simplified[roll][decomp] = value
                else:
                    simplified[roll][decomp] += value
        return simplified

    def reset(self):
        self._dict = {1: {}}
        self._prob = {}
        self._prob_r = {}
        self._total = {}
        self.battles = {"Colour": self.name}

    def get_probabilities(self, rolls):
        roll_num = min(rolls, max(self._prob.keys()))
        return {key: value
                for key, value in self._prob.items() 
                if key <= roll_num}

    def get_fractions(self, rolls):
        roll_num = min(rolls, max(self._prob_r.keys()))
        return {key: value
                for key, value in self._prob_r.items() 
                if key <= roll_num}

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self._list)


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
        die = Dice([0, 1], "yellow")
        die.roll(1)
        actual = die.get_probabilities(1)
        self.assertEqual(expected, actual)

    def test_get_probabilities_2_rolls(self):
        expected = {1: {0: 0.5, 1: 0.5},
                    2: {0: 0.25, 1: 0.5, 2: 0.25}}
        die = Dice([0, 1], "magenta")
        die.roll(2)
        actual = die.get_probabilities(2)
        self.assertEqual(expected, actual)

    def test_simplify_letter_die(self):
        expected = {1: {"a": round(1/3, 5), "b": round(2/3, 5)},
                    2: {"2*a": round(1/9, 5), "a + b": round(4/9, 5),
                        "2*b": round(4/9, 5)}}
        die = Dice(["a", "b", "b"], "letters")
        die.roll(2)
        actual = die.simplify_letter_die(2)
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    main()

    dice = Dice([1, 2], "dice")
    dice.roll(4)
    print(dice.get_fractions(3))
