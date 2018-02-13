import random
from copy import deepcopy
from bigram_distribution import *
from count_letter_collocation_probabilities import ALPHABET
from trigram_distribution import basque  # distribution, finnish, basque


class Generator(object):
    def __init__(self, distribution_):
        self.distribution = distribution_

    def get_letter(self, probabilities):
        """
        {'a': 0.3333, 'b': 0.3333, 'c': 0.3333} should reliably return a, b, c with equal probability
        """
        while True:
            random_letter = random.choice(probabilities.keys())
            if probabilities[random_letter] > random.uniform(0, 1):
                return random_letter

    def get_next(self, last, filter_=None):
        """
        gets the next possible character based on distribution
        :param last: last character (or characters if using trigram distributions) in line
        :param filter_: None or list of acceptable characters
        :return:
        """
        last = last.replace(' ', '_')
        distribution_ = deepcopy(self.distribution[last])
        if filter_:
            distribution_ = {k: v for k, v in distribution_.items() if k in filter_}
        # e.g. if after 'q' a consonant is asked, we cannot do that
        if not distribution_:
            return
        return self.get_letter(distribution_).replace('_', ' ')

# print '15k:'
# s = random.choice(ALPHABET)
# for _ in range(100):
#     last_letter = s[-1]
#     s += get_letter(distribution_15k[last_letter])
#
# print s
# print
#
# print '300k:'
# s = random.choice(ALPHABET)
# for _ in range(100):
#     last_letter = s[-1]
#     s += get_letter(distribution_300k[last_letter])
#
# print s

# s = '_%s' % random.choice(ALPHABET)
# for _ in range(100):
#     last_bigram = ''.join(s[-2:])
#     distribution_for_last_bigram = distribution.get(last_bigram)
#     if distribution_for_last_bigram:
#         s += get_letter(distribution_for_last_bigram)
#     else:
#         print 'oops'
# print s
