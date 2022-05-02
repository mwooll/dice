# Dice

from termcolor import colored

class Dice:
    """colours"""
    colours = ["Blue", "Red", "Magenta", "Yellow", "Olive", "Cyan", "White", "Grey", "Black"]
    text_colour = ["blue", "red", "magenta", "yellow", "green", "cyan", "white", "grey", None]
    hex_colour = [[0x0, 0x0, 0xFF], [0xDD, 0x0, 0x0], [0x7F, 0x0, 0xFF], [0xFF, 0xCC, 0x00], [0x0, 0xAA, 0x0], 
                  [0x0, 0xDD, 0xDD], [0xC0, 0xC0, 0xC0], [0x60, 0x60, 0x60], [0x0, 0x0, 0x0]]

    def __init__(self,
                 numbers=[],
                 name="Blank",
                 colour=None,
                 word_colour=None,
                 index=None):
        if numbers == []:
            numbers = [0]
        numbers.sort()
        self.name = name
        self.colour = colour
        self.word_colour = word_colour
        self.list = numbers
        self.index = -1

        if index != None:
            try:
                self.name = Dice.colours[index]
                self.colour = Dice.text_colour[index]
                self.word_colour = Dice.word_colour[index]
                self.index = index
            except IndexError:
                "index is too high"
            except TypeError:
                "index needs to be an integer"

    def roll(self, rolls):
        self.reset()
        for n in self.list:
            if n not in self.dict[0]:
                self.dict[0][n] = 0
            if n in self.dict[0]:
                self.dict[0][n] += 1

        for r in range(rolls-1):
            self.dict.append({})
            for n in self.dict[r].keys():
                for k in self.dict[0]:
                    if n+k not in self.dict[r+1]:
                        self.dict[r+1][n+k] = 0
                    if n+k in self.dict[r+1]:
                        self.dict[r+1][n+k] += self.dict[r][n] * self.dict[0][k]

        for p in range(rolls):
            self.prob.append({})
            self.prob_r.append({})
            total_p = 0
            for n in self.dict[p]:
                total_p += self.dict[p][n]
            self.total.append(total_p)
            for n in self.dict[p]:
                self.prob[p][n] = self.dict[p][n]/self.total[p]
                self.prob_r[p][n] = "{}/{}".format(self.dict[p][n], self.total[p])

    def reset(self):
        self.dict    = [{}]
        self.prob    = []
        self.prob_r  = []
        self.total   = []
        self.battles = {"Colour": self.name}

    def print_die(self):
        print(colored(self.name, self.colour))
        print(self.name, self.colour, self.word_colour)
        for roll in range(len(self.dict)):
            print()
            print(self.dict[roll])
            print(self.prob_r[roll])
            print(self.prob[roll])

    def __repr__(self):
        return self.name
