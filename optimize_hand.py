# optimize_hand

import numpy as np
import heapq as hq
from copy import deepcopy
from itertools import product
from unittest import main, TestCase

from Hand import Hand


def get_grime_combinations(n_dice, n_opp):
    dice = [k for k in range(n_dice)]
    combinations = dice[:]
    for k in range(1, n_opp):
        to_remove = set()
        combinations = set(product(combinations, dice))
        for combi in combinations:
            if combi != tuple(sorted(combi)):
                to_remove.add(combi)
            elif len(set(combi)) < len(combi):
                to_remove.add(combi)
        combinations = combinations.difference(to_remove)
    return combinations
    

class Optimized_Hand(Hand):
    def __init__(self,
                 dice_num: int=5,
                 face_average: int=None,
                 num_faces: int=None,
                 starting_dice: list=None,
                 roll_nums: list=None,
                 rng=None, #random number generator
                 opponents: int=None):
        super().__init__()
        if rng is None:
            self.rng = np.random.default_rng()
        else:
            print("rng")
            self.rng = rng

        if starting_dice is not None:
            self.set_dice_set(starting_dice)
        else:
            if num_faces is None:
                num_faces = 6
            self.create_random_hand(dice_num, face_average, num_faces)

        if roll_nums is None:
            self._interested = [1, 2]
        else:
            self._interested = roll_nums
        self._rolls_num = max(self._interested)
        self._second_hand = Hand()


        combinations = [die for die in self._dice.keys()]
        if opponents is not None:
            numbers = get_grime_combinations(dice_num, opponents)
            combinations = [[combinations[num] for num in combi]
                            for combi in numbers]
        self._combinations = combinations
            

    def create_random_die(self, face_num, face_average):
        """ creating a radnom die """
        faces = []
        max_face = face_num*face_average
        for k in range(1, face_num):
            new_face = self.rng.integers(0, max_face)
            max_face -= new_face
            faces.append(new_face)
        faces.append(max_face)
        return faces

    def create_random_hand(self, dice_num, face_average, num_faces):
        """ creating a random starting hand """
        hand = []
        for k in range(dice_num):
            faces = self.create_random_die(num_faces, face_average)
            hand.append(faces)
        self.set_dice_set(hand)

    """ criterion to optimize probabilities for """
    def efron_criterion(self, hand):
        """
        this criterion is maximal when every die has a hard winning matchup
        and a hard losing matchup.
        depending on the number of dice and number of faces the maximum is
        typically between 1/5 and 1/3.
        """
        single_ratings = {k: [] for k in self._interested}
        for die in hand._dice:
            perf = hand.get_die_performance(die, 3)
            for k in self._interested:
                max_p, min_p = max(perf[k]), min(perf[k])
                rating = round((max_p - min_p)*(max_p > 0.5)*(min_p < 0.5), 5)
                single_ratings[k].append(rating)
        worst_ratings = {k: min(val) for k, val in single_ratings.items()} 
        efron_rating = sum(worst_ratings[k] for k in self._interested)
        return efron_rating

    def grime_criterion(self, hand):
        """
        this criterion is maximal, when for every specified combination of dice
        there exists a die that has a greater than 50% chance to beat both
        when we can also decide how many dice are rolled.
        """
        single_ratings = []
        frame = hand.frame_results(self._interested)
        for combi in self._combinations:
            single_ratings = max()
        grime_rating = sum(single_ratings)
        return grime_rating

    """ main part """
    def find_initial_temperature(self, iterations):
        """ getting the starting temperature by randomly performing changes """
        self.roll_the_dice(self._rolls_num)
        rating = self.criterion(self)
        temperatures = [rating]
        for k in range(iterations):
            # making random changes and calculating the new rating
            new_hand = self.change_dice(self.get_faces(), self)
            new_rating = self.criterion(new_hand)
            temperatures.append(abs(rating - new_rating))
            rating = new_rating

        # returning the largest energy difference as temperature
        temperature = max(temperatures)
        return temperature

    def change_dice(self, numbers, hand):
        die = self.rng.integers(0, len(numbers))
        i, j = self.rng.choice(range(len(numbers[die])), 2)
        if numbers[die][j] > 0:
            numbers[die][i] += 1
            numbers[die][j] -= 1
        else:
            numbers[die][j] += 2
            numbers[die][i] -= 2
        hand.set_dice_set(numbers)
        hand.roll_the_dice(self._rolls_num)
        return hand

    def metropolis(self, n_iter, temperature):
        current = self.get_faces()
        copy = deepcopy(current)
        self.roll_the_dice(self._rolls_num)
        rating = self.criterion(self)
        hand_heap = [(-rating, -1, copy)]
        for n in range(n_iter):
            # print(hand_heap)
            # making random changes and calculating the new rating
            new_hand = self.change_dice(current, self._second_hand)
            new_rating = self.criterion(new_hand)
            energy_diff = rating - new_rating

            # checking if we should approve this hand
            if (energy_diff < 0 or
                self.rng.random() < np.exp(-energy_diff/temperature)):
                # adding the approved hand to the heap
                self._second_hand = new_hand
                current = self._second_hand.get_faces()
                copy = deepcopy(current)
                rating = new_rating
                hq.heappush(hand_heap, (-rating, n, copy))

        """ retrieving the best hand """
        # print(hand_heap)
        candidate = hq.heappop(hand_heap)
        self.set_dice_set(candidate[-1])
        # print(candidate)

    def efron_optimize(self, n_iter=500, factor=0.98, min_temp=0.01, cycles=10):
        """ using the efron criterion to optimize hand """
        # setting parameters
        self.criterion = self.efron_criterion
        temperature = max(0.1, self.find_initial_temperature(100))
        # we take the max with 0.1 to avoid a starting temperature of 0
        print(f"starting temperature is {temperature}")

        # optimizing the hand
        # while temperature > min_temp:
        for k in range(cycles): # easier to debug
            # print(f"{k}:  temperature = {temperature}")
            # print(self._dice)
            self.metropolis(n_iter, temperature)
            temperature *= factor

        self.roll_the_dice()
        print(f"\nfinal Efron rating is {self.criterion(self)}")
        return self.get_faces()

    # def grime_optimize(self, n_opponents=2, n_iter=500, factor=0.98):
    #     """ using the grime criterion to optimize hand """
    #     # setting parameters
    #     self.criterion = self.grime_criterion
    #     self.die_num = die_sum
    #     self.num_opponents = n_opponents
    #     # optimizing the hand
    #     self.metropolis(n_iter)
    #     return self._dice

    
class TestOptimizer(TestCase):
    def test_efron_criterion_single(self):
        efron_dice = [[3], [2, 2, 6], [1, 5], [0, 4, 4]]
        efron = Optimized_Hand(starting_dice=efron_dice, roll_nums=[1])
        efron.roll_the_dice(rolls=1, accuracy=5)

        actual = efron.efron_criterion(efron)
        expected = 0.333339999 # some rounding quirk is going on
        self.assertAlmostEqual(actual, expected)

    def test_efron_criterion_double(self):
        own_dice = [[2], [1, 1, 4], [0, 3, 3]]
        own = Optimized_Hand(starting_dice=own_dice, roll_nums=[1,2])
        own.roll_the_dice(rolls=2, accuracy=8)

        actual = own.efron_criterion(own)
        expected = round(2/9 + 1/9, 5)
        self.assertAlmostEqual(actual, expected)

    def test_grime_criterion_one_opponent(self):
        rowett_dice = [[2, 5], [3, 3, 3, 3, 3, 6], [1, 4, 4, 4, 4, 4]]
        rowett = Optimized_Hand(starting_dice=rowett_dice, roll_nums=[1, 2])
        rowett.roll_the_dice(rolls=2, accuracy=5)

        actual = rowett.grime_criterion(rowett)
        expected = 1
        self.assertAlmostEqual(actual, expected)

    def test_grime_criterion_two_opponents(self):
        grime_dice = [[2, 7], [1, 6, 6], [0, 5, 5, 5, 5, 5],
                      [4, 4, 4, 4, 4, 9], [3, 3, 8]]
        grime = Optimized_Hand(starting_dice=grime_dice, roll_nums=[1, 2])
        grime.roll_the_dice(rolls=2, accuracy=5)

        actual = grime.grime_criterion(grime)
        expected = 1
        self.assertAlmostEqual(actual, expected)


def find_Efron_dice():
    dice_num = 3
    roll_nums = [1]
    face_average = 2
    hand = Optimized_Hand(dice_num=dice_num,
                          roll_nums=roll_nums,
                          face_average=face_average)
    print(hand._dice)
    hand.roll_the_dice(1)
    print(hand.efron_criterion(hand))

def optimize_Efron():
    dice_num = 3
    num_faces = 3
    roll_nums = [1, 2]
    face_average = 4
    rng = np.random.default_rng(2)
    hand = Optimized_Hand(dice_num=dice_num,
                          roll_nums=roll_nums,
                          face_average=face_average,
                           rng=rng,
                          num_faces=num_faces)
    print(hand._dice)

    n_iter = 200
    factor = 0.98
    min_temp = 0.1
    dice_set = hand.efron_optimize(n_iter, cycles=25)
    print(dice_set)
    return dice_set

def test_efron(dice=None):
    if dice is None:
        dice = [[2], [1, 1, 4], [0, 3, 3]]
        # dice = [[4, 4, 4], [1, 5, 6], [2, 3, 7]]
        # dice = [[2, 3, 3, 8], [3, 3, 5, 5], [0, 4, 6, 6], [1, 1, 7, 7]]
        # dice = [[0, 4, 4], [3], [2, 2, 6], [1, 5]]
        dice = [[2, 5, 5], [4, 4, 4], [3, 3, 6]]
    hand = Optimized_Hand(starting_dice=dice, roll_nums=[1, 2])
    hand.roll_the_dice(2, ".")
    print(hand.efron_criterion(hand))
    print(hand.frame_results([1, 2]))

def test_grime(dice=None):
    if dice is None:
        dice = [[2, 7], [1, 6, 6], [0, 5, 5, 5, 5, 5],
                [4, 4, 4, 4, 4, 9], [3, 3, 8]]
        dice = [[2, 2, 2, 7, 7], [1, 1, 6, 6, 6], [0, 5, 5, 5, 5],
                [4, 4, 4, 4, 4], [3, 3, 3, 3, 8]]
    hand = Optimized_Hand(starting_dice=dice, roll_nums=[1, 2], opponents=2)
    hand.roll_the_dice(2, ".")
    print(hand.grime_criterion(hand))
    # print(hand.frame_results([1, 2]))

if __name__ == "__main__":
    # main()
    # find_Efron_dice()
    # optimized = optimize_Efron()
    out = test_efron()
    # out = test_grime()
    # print(out)

