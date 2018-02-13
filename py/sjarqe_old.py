import random

# from generator import get_next
from sjarqe_base import *

MAX_CONSONANT_SEQUENCE = 4
MAX_VOWEL_COUNT = 3
MIN_VOWEL_COUNT = 2
CLOSED_SYLLABLE_FREQUENCY = 5
LONGER_WORDS_FREQUENCY = 5


class SjarqeLegacy(SjarqeGenerator):

    def __init__(self):
        super(SjarqeLegacy, self).__init__()
        self.generate_line_method = self.generate_line_old

    def get_vowel(self):
        return self.generator.get_next(self.line_end, self.VOWELS.keys())

    def get_consonant(self):
        return self.generator.get_next(self.line_end, self.CONSONANTS.keys())

    # old versions:
    # def get_vowel():
    #     while True:
    #         random_letter = random.choice(VOWELS.keys())
    #         if VOWELS[random_letter] > random.randrange(0, 10):
    #             return random_letter
    #
    #
    # def get_consonant():
    #     while True:
    #         random_letter = random.choice(CONSONANTS.keys())
    #         if CONSONANTS[random_letter] > random.randrange(0, 10):
    #             return random_letter

    def get_rhyme_letter(self, rhyme_, vowel_or_consonant, current_syllable_number_, syllable_count_):
        # """
        # c2 is the initial consonant of the 2nd syllable from the end
        # v2 is the vowel of the 2nd syllable from the end, following c2
        # c1 is the initial consonant of the 1st syllable from the end, following v2
        # v1 is the last vowel, folowing c1
        # c0 is an optional final consonant with a 0.5p of happening
        # so, the word is CVCV[..]c2v2c1v1c0?
        # """
        index = syllable_count_ - current_syllable_number_
        # FIXME: we rhyme only two last syllables -- can be tweaked!
        if index > 2:
            return None
        key = '%s%s' % (vowel_or_consonant[0], index)
        if key not in rhyme_:
            # the closing consonant of the last syllable
            if key == 'c0':
                rhyme_[key] = self.get_consonant() if random.randrange(0, 2) else self.SILENT_CONSONANT
            else:
                rhyme_[key] = {'c': self.get_consonant, 'v': self.get_vowel}[vowel_or_consonant[0]]()
        return rhyme_[key]

    # the 'old' version which takes into account the config parameters
    # that affect word length, consonant cluster probability etc etc
    def generate_line_old(self, rhyme, syllable_count):
        line = []
        current_syllable_number = 0
        # to avoid consonant clusters at word start
        word_start = True
        cons_sequence = 0
        vowels_in_current_word = 0
        while current_syllable_number < syllable_count:
            if (word_start and cons_sequence == 0) or (
                    cons_sequence < MAX_CONSONANT_SEQUENCE and not word_start):
                # time to start rhyming?
                if syllable_count - current_syllable_number < 3:
                    rhyming_consonant = self.get_rhyme_letter(rhyme, 'consonant', current_syllable_number,
                                                              syllable_count)
                    consonant = self.get_consonant_rhyming_variant(rhyming_consonant)
                else:
                    consonant = self.get_consonant()
                # print "before: %s" % consonant
                self.append_character_to_line(line, consonant)

            # time to start rhyming?
            if syllable_count - current_syllable_number <= 2:
                vowel = self.get_rhyme_letter(rhyme, 'vowel', current_syllable_number, syllable_count)
            else:
                vowel = self.get_vowel()

            current_syllable_number += 1
            vowels_in_current_word += 1

            self.append_character_to_line(line, vowel)

            cons_sequence = 0
            word_start = False

            # FIXME: why is it done before doing the closed syllable?
            # inserting a whitespace (i.e. finishing the word)
            # tune word length: the first part (before 'or') is for max syllable count,
            # the second part is for probability of inserting a whitespace
            # (the greater the value the shorter the words)
            # also here we make sure no words with no vowels appear (FIXME: why not?)
            current_word_has_more_than_enough_vowels = vowels_in_current_word >= MAX_VOWEL_COUNT
            lets_make_a_longer_word = random.randrange(0, 10) > LONGER_WORDS_FREQUENCY
            current_word_has_at_least_the_minimum_vowels = vowels_in_current_word >= MIN_VOWEL_COUNT
            this_is_not_the_last_syllable_in_line = current_syllable_number < syllable_count
            if (current_word_has_more_than_enough_vowels or (
                    lets_make_a_longer_word and current_word_has_at_least_the_minimum_vowels)) and this_is_not_the_last_syllable_in_line:
                self.append_character_to_line(line, ' ')
                vowels_in_current_word = 0
                cons_sequence = 0
                word_start = True

            # closed syllables are still needed, but not many
            lets_make_a_closed_syllable = random.randrange(0, 10) > CLOSED_SYLLABLE_FREQUENCY
            the_word_just_started_and_no_cluster_present = word_start and cons_sequence == 0
            in_the_middle_of_word_and_current_cluster_not_too_long = cons_sequence < MAX_CONSONANT_SEQUENCE and not word_start
            this_is_the_last_syllable = current_syllable_number == syllable_count
            rhyming_consonant = self.get_rhyme_letter(rhyme, 'consonant', current_syllable_number, syllable_count)
            the_rhyme_for_it_is_not_empty = rhyming_consonant is not None and rhyming_consonant != ''
            if (lets_make_a_closed_syllable and (
                    the_word_just_started_and_no_cluster_present or in_the_middle_of_word_and_current_cluster_not_too_long) or (
                    this_is_the_last_syllable and the_rhyme_for_it_is_not_empty)):
                if rhyming_consonant:
                    add = self.get_consonant_rhyming_variant(rhyming_consonant)
                # elif syllable_count - current_syllable_number == 0:
                #     # FIXME: why???
                #     add = SILENT_CONSONANT
                else:
                    add = self.get_consonant()

                self.append_character_to_line(line, add)
                cons_sequence += 1
        return line

# TEXT = {'verse': ['a9', 'b9', 'a9', 'b9'], 'verse2': ['a9', 'b8', 'a9', 'b8'], 'structure': ['verse', 'line', 'verse2']}
#
# sg_old = SjarqeLegacy()
# sg_old.generate(TEXT)
