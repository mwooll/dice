# optimize_hand

import numpy as np
import heapq as hq
from copy import deepcopy
from unittest import main, TestCase

from Hand import Hand


class Optimized_Hand(Hand):
    def __init__(self,
                 dice_num: int=5,
                 face_average: int=None,
                 num_faces: int=None,
                 starting_dice: list=None,
                 roll_nums: list=None,
                 rng=None, #random number generator
                 opponents: int=1,
                 cut_off: float=0):
        super().__init__()
        if rng is None:
            self.rng = np.random.default_rng()
        else:
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

        self._num_opp = opponents
        self.get_combinations(dice_num, opponents)  

        self._cut_off = 0          

    def create_random_die(self, face_num, face_average):
        """ creating a radnom die """
        faces = []
        max_face = face_num*face_average
        for k in range(1, face_num):
            new_face = self.rng.integers(0, max_face)
            max_face -= new_face
            faces.append(new_face)
        faces.append(max_face)
        print(faces)
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

    def greedy_criterion(self, hand):
        """
        this criterion is maximal, when for every specified combination of dice
        there exists a die that has a large chance to beat all of them,
        when that die also can decide how many dice are rolled.
        """
        single_ratings = []
        raw = hand.raw_results(self._interested, self._cut_off)
        single_ratings = [max([sum(raw.loc[k, combi])
                               for k in range(len(raw))])
                          for combi in self._combinations[self._num_opp]]
        greedy_rating = sum(single_ratings)/len(self._combinations[self._num_opp])/self._num_opp
        return greedy_rating

    def grime_criterion(self, hand):
        """
        similar to the greedy criterion but punishes if one die is too strong.
        and hence is maximal when every die is needed to beat some combinations.
        """
        raw = hand.raw_results(self._interested)
        greedy_rating = self.greedy_criterion(self)

        variance = 0
        mean = 0.5 # mean chance of winning
        for col in self._dice:
            variance += sum((raw[col] - mean)**2)
        variance /= self.get_number_of_dice()
        grime_rating = greedy_rating - variance
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
        hand.set_dice_set(numbers)
        hand.roll_the_dice(self._rolls_num)
        return hand

    def metropolis(self, n_iter, temperature):
        current = self.get_faces()
        copy = deepcopy(current)
        self.roll_the_dice(self._rolls_num)
        rating = self.criterion(self)
        priority = (self.calculate_simplicity(), -1)
        hand_heap = [(-rating, priority, copy)]
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
                priority = (self._second_hand.calculate_simplicity(), n)
                hq.heappush(hand_heap, (-rating, priority, copy))

        """ retrieving the best hand """
        # print(hand_heap)
        first = hand_heap[0]
        promising = [candidate for candidate in hand_heap
                     if candidate[0] == first[0]]
        candidate = promising[self.rng.choice(len(promising))]
        self.set_dice_set(candidate[-1])
        print(candidate)

    def optimize_hand(self,
                      criterion: str="grime" or "efron" or "greedy",
                      n_iter: int=500,
                      factor: float=0.98,
                      cycles: int=10):
        """ uses the specified criterion to find a optimal set of dice """
        # determining the criterion
        lower = criterion.lower()
        if lower == "efron":
            self.criterion = self.efron_criterion
        elif lower == "greedy":
            self.criterion = self.greedy_criterion
            if self._num_opp < 2:
                raise Exception("the greedy criterion is not suited with 1 opponent.")
        elif lower == "grime":
            self.criterion = self.grime_criterion
            if self._num_opp < 2:
                raise Exception("the grime criterion is not suited with 1 opponent.")
        else:
            raise Exception(f"Criterion {lower} unknown. Valid " +
                            'criteria are "grime", "efron" and "greedy".')

        temperature = max(0.1, self.find_initial_temperature(100))
        print(f"starting temperature is {temperature}")

        # optimizing the hand
        for k in range(cycles): 
            print(f"{k}:  temperature = {temperature}")
            # print(self._dice)
            self.metropolis(n_iter, temperature)
            temperature *= factor

        self.roll_the_dice(self._rolls_num)
        print(f"\nfinal {lower} rating is {self.criterion(self)}")
        return self.get_faces()
    
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


def optimize_Efron():
    dice_num = 3
    num_faces = 6
    roll_nums = [1]
    face_average = 21/6
    rng = np.random.default_rng(5)
    hand = Optimized_Hand(dice_num=dice_num,
                          roll_nums=roll_nums,
                          face_average=face_average,
                          rng=rng,
                          num_faces=num_faces)
    print(hand._dice)

    n_iter = 2000
    dice_set = hand.optimize_hand("efron", n_iter, cycles=25)
    print(dice_set)
    return dice_set

def test_efron(dice=None):
    if dice is None:
        dice = [[2], [1, 1, 4], [0, 3, 3]]
        dice = [[2, 5, 5], [4, 4, 4], [3, 3, 6]]
        dice = [[1, 1, 5, 5], [1, 2, 3, 6], [1, 3, 4, 4]]
    hand = Optimized_Hand(starting_dice=dice, roll_nums=[1])
    hand.roll_the_dice(1, ".")
    print(hand.efron_criterion(hand))
    print(hand.frame_results([1]))
    return hand

def optimize_greedy():
    dice_num = 5
    num_faces = 5
    roll_nums = [1, 2]
    face_average = 4
    rng = np.random.default_rng(2)
    hand = Optimized_Hand(dice_num=dice_num,
                          roll_nums=roll_nums,
                          face_average=face_average,
                          rng=rng,
                          num_faces=num_faces,
                          opponents=2,
                          cut_off=0.50)
    print(hand._dice)

    n_iter = 100
    dice_set = hand.optimize_hand("greedy", n_iter, cycles=10)
    print(dice_set)
    return dice_set

def test_greedy(dice=None):
    opponents = 2
    rolls = 2
    if dice is None:
        dice = [[0, 2, 10], [3, 4, 5], [1, 2, 9]]
    hand = Optimized_Hand(starting_dice=dice,
                          roll_nums=[k for k in range(1, rolls+1)],
                          opponents=opponents)
    hand.roll_the_dice(rolls, ".")
    hand.get_combinations(len(dice), opponents)
    print(hand.greedy_criterion(hand,))
    print(hand.frame_results([1, 2]))
    return hand

def optimize_Grime():
    dice_num = 5
    num_faces = 5
    roll_nums = [1, 2]
    face_average = 4
    rng = np.random.default_rng(3)
    hand = Optimized_Hand(dice_num=dice_num,
                          roll_nums=roll_nums,
                          face_average=face_average,
                          rng=rng,
                          num_faces=num_faces,
                          opponents=2)
    print(hand._dice)

    n_iter = 100
    dice_set = hand.optimize_hand("grime", n_iter, cycles=10)
    print(dice_set)
    return dice_set

def test_grime(dice=None):
    opponents = 2
    rolls = 2
    if dice is None:
        # dice = [[1, 2, 9], [2, 2, 8], [3, 4, 5]]
        dice = [[0, 1, 2, 3, 14], [2, 2, 3, 3, 10], [1, 2, 2, 3, 12],
                [1, 2, 2, 2, 13], [3, 4, 4, 4, 5]]
    hand = Optimized_Hand(starting_dice=dice,
                          roll_nums=[k for k in range(1, rolls+1)],
                          opponents=opponents)
    hand.roll_the_dice(rolls, ".")
    hand.get_combinations(len(dice), opponents)
    print(hand.grime_criterion(hand))
    print(hand.frame_results([1, 2]))
    return hand

if __name__ == "__main__":
    main()

    # efron = optimize_Efron()
    # out = test_efron()

    # greedy = optimize_greedy()
    # out = test_greedy()

    # grime = optimize_Grime()
    # out = test_grime()