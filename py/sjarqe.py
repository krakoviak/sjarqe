#!/usr/local/bin/python3

import random
from collections import OrderedDict

from sjarqe_base import SjarqeGenerator
from sjarqe_old import SjarqeLegacy


# TEXT = {'verse': ['a4', 'b4', 'a4', 'b4'], 'structure': ['verse']}


# the 'new' version which (almost?) purely uses the trigram distributions

class SjarqeNew(SjarqeGenerator):
    def __init__(self):
        super(SjarqeNew, self).__init__()
        self.generate_line_method = self.generate_line

    def generate_line(self, rhyme, syllable_count):
        line = []

        # init line end
        self.line_end = random.choice([k for k in self.distribution.keys() if k[1] == '_'])

        current_syllable_number = 0
        rhymes_for_this_line = OrderedDict()
        for rh in ['c2', 'v2', 'c1', 'v1']:
            rhymes_for_this_line[rh] = None

        panic_ticker = 0

        while current_syllable_number < syllable_count:
            index = syllable_count - current_syllable_number
            # FIXME: we rhyme only two last syllables -- can be tweaked!
            if index > 2:
                # just get something
                next_char = self.generator.get_next(self.line_end)
            else:
                # time to rhyme!
                # first determine what we want -- c or v
                next_unfilled_rhyme_position = next(k_ for k_, v in rhymes_for_this_line.items() if not v)
                vowel_or_consonant = next_unfilled_rhyme_position[0]
                # key = '%s%s' % (vowel_or_consonant, index)
                if next_unfilled_rhyme_position in rhyme:
                    if vowel_or_consonant == 'v':
                        next_char = rhyme[next_unfilled_rhyme_position]
                    else:
                        next_char = self.generator.get_next(self.line_end,
                                                            filter_=self.get_consonant_rhyming_variant(
                                                                rhyme[next_unfilled_rhyme_position]))
                else:
                    filter_ = {'v': self.VOWELS.keys(), 'c': self.CONSONANTS.keys()}[vowel_or_consonant]
                    next_char = self.generator.get_next(self.line_end, filter_)
                    rhyme[next_unfilled_rhyme_position] = next_char

                rhymes_for_this_line[next_unfilled_rhyme_position] = next_char

            if next_char in self.VOWELS:
                current_syllable_number += 1

            self.append_character_to_line(line, next_char)
            panic_ticker += 0
            if panic_ticker > 100:
                raise RuntimeError('PANIC!')
        return line


# l = ['d', 'o', 't', 'd', 'e', 'm']
# l = apply_assimilations(l)
# print l
sg_new = SjarqeNew()
# sg_new = SjarqeLegacy()

TEXT = {
    'verse': ['a9', 'b9', 'a9', 'b9'],
    'verse2': ['a9', 'b8', 'a9', 'b8'],
    'structure': ['verse', 'line', 'verse2']}
sg_new.generate(TEXT)
