# Dice

from termcolor import colored

"""colours"""
colours = ["Blue", "Red", "Magenta", "Yellow", "Olive",
           "Cyan", "White", "Grey", "Black"]

class Dice:
    def __init__(self,
                 numbers=[],
                 name="Blank"):
        if numbers == []:
            numbers = [0]
        numbers.sort()
        self.name = name
        self.list = numbers

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
        print(self.name)
        for roll in range(len(self.dict)):
            print(self.dict[roll])
            print(self.prob_r[roll])
            print(self.prob[roll])

    def __repr__(self):
        return self.name


if __name__ == "__main__":
    blue = Dice([1, 2, 3], "blue")
    blue.roll(1)
    blue.print_die()

    red = Dice([2, 3], "red")
    red.roll(2)
    red.print_die()