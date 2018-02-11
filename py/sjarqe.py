from generator import *

VOWELS = {
    # # empty vowel
    # '': 5,
    # SHORT_VOWELS
    'a': 6, 'ya': 3, 'e': 5, 'ye': 2, 'u': 6, 'i': 3, 'o': 7, 'yo': 2,
    # LONG_VOWELS
    'aa': 0, 'ee': 0, 'uu': 0, 'ii': 0, 'oo': 0,
    # DIPHTONGS
    'ai': 3, 'ei': 3, 'yei': 1, 'oi': 2, 'ou': 2, 'au': 2
}

CONSONANTS = {
    '': 0, 'y': 4, 'q': 4, 'kh': 4, 'w': 3, 'r': 7, 'R': 5, 't': 7, 'p': 6, 's': 8, 'd': 8, 'f': 3, 'g': 4,
    'x': 4, 'k': 6, 'l': 6, 'z': 7, 'v': 6, 'b': 3, 'n': 5, 'm': 5, 'sj': 4, 'dj': 4, 'ch': 4, 'th': 6,
    'dh': 6, 'j': 2, 'ts': 5, 'dz': 5
}

TEXT = {'verse': ['a4', 'b4', 'a4', 'b4'], 'structure': ['verse']}

MAX_CONSONANT_SEQUENCE = 4
MAX_VOWEL_COUNT = 3
MIN_VOWEL_COUNT = 2
CLOSED_SYLLABLE_FREQUENCY = 5
LONGER_WORDS_FREQUENCY = 5


def load(file_path):
    result = {}
    with open('./' + file_path) as f:
        for line in f.readlines():
            if line.strip() and line.strip()[0] != '#' and '=>' in line:
                rule = line.split('=>')
                result[rule[0].strip()] = rule[1].strip()
    return result


# maps consonants to their possible variations that may be used when rhyming
consonant_rhyme_map = load('../lib/consonant_rhyme')

assimilations = load('../lib/assimilation_rules')
palatalizations = load('../lib/palatalizations')
palatalizers = load('../lib/palatalizers')


def get_vowel():
    while True:
        random_letter = random.choice(VOWELS.keys())
        if VOWELS[random_letter] > random.randrange(0, 10):
            return random_letter


def get_consonant():
    while True:
        random_letter = random.choice(CONSONANTS.keys())
        if CONSONANTS[random_letter] > random.randrange(0, 10):
            return random_letter


# def get_vowel(last):
#     while True:
#         l = get_next(last)
#         if l in VOWELS.keys():
#             return l
#
#
# def get_consonant(last):
#     while True:
#         l = get_next(last)
#         if l in VOWELS.keys():
#             return l


def remove_empty_chars(line):
    return [ch for ch in line if ch != '']


def apply_assimilations(line):
    for _ in range(2):
        line = remove_empty_chars(line)

        for i in range(len(line)):
            try:
                next_letter = line[i + 1] or ''
            except IndexError:
                next_letter = ''

            key = "%s|%s" % (line[i], next_letter)
            # to avoid infinite rule loops
            tries_count = 0
            while key in assimilations and tries_count < 4:
                # print assimilations[key]
                rule = assimilations[key].split('|')
                line[i] = rule[0]
                if next_letter:
                    line[i + 1] = rule[1]
                    key = '%s|%s' % (line[i], line[i + 1])
                else:
                    key = ''
                tries_count += 1
            try:
                line[i] = palatalizations[line[i]]
                line[i + 1] = palatalizers[line[i + 1]]
            except IndexError:
                # do nothing, the line is finished
                pass
            except KeyError:
                # do nothing, no rule to palatalize
                pass

        line = remove_empty_chars(line)


def get_rhyme_letter(rhyme_, vowel_or_consonant, current_syllable_number_, syllable_count_):
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
        if key == 'c0':
            rhyme_[key] = get_consonant() if random.randrange(0, 2) else ''
        else:
            rhyme_[key] = {'c': get_consonant, 'v': get_vowel}[vowel_or_consonant[0]]()
    return rhyme_[key]


def generate(structure):
    """
    {'verse': ['a4', 'b4', 'a4', 'b4'], 'structure': ['verse']}
    text_block: 'verse', 'chorus', 'line' etc.
    line_type: 'a4, 'b4' etc.
    syllable_count is the '4' from the list in 'verse'
    rhyme_key is the 'a', 'b' etc. from the list in 'verse', i.e. the specific rhyme 
    
    rhymes: {'a': {'c2': C, 'v2': V, 'c1': C, 'v1': V, 'c0': C}, 'b': {..}}
    """
    for text_block in structure['structure']:
        if text_block == 'line':
            print
        else:
            # maps the line type (e.g. 'a', 'b' etc. in 'a4', 'b7' etc.)
            # to the last rhyme-forming vowels and consonants in the line
            rhymes = {}
            for line_type in structure[text_block]:
                rhyme_key = ''.join([ch for ch in line_type if not ch.isdigit()])
                if rhyme_key not in rhymes:
                    # initialize with an empty dict to be filled later
                    rhymes[rhyme_key] = {}

                syllable_count = int(''.join([ch for ch in line_type if ch.isdigit()]))
                rhyme = rhymes[rhyme_key]
                line = generate_line(rhyme, syllable_count)
                apply_assimilations(line)

                print ''.join(line)


def generate_line(rhyme, syllable_count):
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
                rhyming_consonant = get_rhyme_letter(rhyme, 'consonant', current_syllable_number, syllable_count)
                consonant = random.choice(
                    consonant_rhyme_map[rhyming_consonant].split())
            else:
                consonant = get_consonant()
            # print "before: %s" % consonant
            line.append(consonant)

        # time to start rhyming?
        if syllable_count - current_syllable_number <= 2:
            vowel = get_rhyme_letter(rhyme, 'vowel', current_syllable_number, syllable_count)
        else:
            vowel = get_vowel()

        current_syllable_number += 1
        vowels_in_current_word += 1

        line.append(vowel)

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
            line.append(' ')
            vowels_in_current_word = 0
            cons_sequence = 0
            word_start = True

        # closed syllables are still needed, but not many
        lets_make_a_closed_syllable = random.randrange(0, 10) > CLOSED_SYLLABLE_FREQUENCY
        the_word_just_started_and_no_cluster_present = word_start and cons_sequence == 0
        in_the_middle_of_word_and_current_cluster_not_too_long = cons_sequence < MAX_CONSONANT_SEQUENCE and not word_start
        this_is_the_last_syllable = current_syllable_number == syllable_count
        rhyming_consonant = get_rhyme_letter(rhyme, 'consonant', current_syllable_number, syllable_count)
        the_rhyme_for_it_is_not_empty = rhyming_consonant is not None and rhyming_consonant != ''
        if (lets_make_a_closed_syllable and (
                the_word_just_started_and_no_cluster_present or in_the_middle_of_word_and_current_cluster_not_too_long) or (
                this_is_the_last_syllable and the_rhyme_for_it_is_not_empty)):
            if rhyming_consonant:
                add = random.choice(
                    consonant_rhyme_map[rhyming_consonant].split())
            elif syllable_count - current_syllable_number == 0:
                add = ''
            else:
                add = get_consonant()
            line.append(add)
            cons_sequence += 1
    return line


generate(TEXT)
