import random

from count_letter_collocation_probabilities import ALPHABET

from trigram_distribution import *

from generator import Generator


class SjarqeGenerator(object):
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
        # SILENT_CONSONANT: 0,
        'y': 4, 'q': 4, 'kh': 4, 'w': 3, 'r': 7, 'R': 5, 't': 7, 'p': 6, 's': 8, 'd': 8, 'f': 3,
        'g': 4,
        'x': 4, 'k': 6, 'l': 6, 'z': 7, 'v': 6, 'b': 3, 'n': 5, 'm': 5, 'sj': 4, 'dj': 4, 'ch': 4, 'th': 6,
        'dh': 6, 'j': 2, 'ts': 5, 'dz': 5
    }

    SILENT_CONSONANT = ''

    def load(self, file_path):
        result = {}
        with open('./' + file_path) as f:
            for line in f.readlines():
                if line.strip() and line.strip()[0] != '#' and '=>' in line:
                    rule = line.split('=>')
                    result[rule[0].strip()] = rule[1].strip()
        return result

    def __init__(self):
        # maps consonants to their possible variations that may be used when rhyming
        self.consonant_rhyme_map = self.load('../lib/consonant_rhyme')

        self.assimilations = self.load('../lib/assimilation_rules')
        self.palatalizations = self.load('../lib/palatalizations')
        self.palatalizers = self.load('../lib/palatalizers')

        self.distribution = basque
        self.generator = Generator(self.distribution)

        # whatever the line is currently ending, whether we are using bi- or trigrams
        self.line_end = random.choice([k for k in self.distribution.keys() if k[1] == '_'])
        # line_end = '_'

        # self.generate_line_method = None

    def generate_line_method(self, rhyme, syllable_count):
        return ""

    def get_consonant_rhyming_variant(self, consonant_, filter_existing_only=True):
        variants = self.consonant_rhyme_map[consonant_].split()
        if filter_existing_only:
            variants = [v for v in variants if v in list(ALPHABET)]
        return random.choice(variants)

    def append_character_to_line(self, line, character):
        # sometimes we get None, e.g. if distribution doesn't provide a consonant after a 'q'
        if character:
            line.append(character)
            # line_end = character
            self.line_end = (self.line_end + character)[-2:]
            # print(line_end)

    def remove_empty_chars(self, line):
        return [ch for ch in line if ch != '']

    def apply_assimilations(self, line):
        line = self.remove_empty_chars(line)
        for _ in range(2):
            for i in range(len(line)):
                try:
                    next_letter = line[i + 1] or ''
                except IndexError:
                    next_letter = ''

                key = "%s|%s" % (line[i], next_letter)
                # to avoid infinite rule loops
                tries_count = 0
                while key in self.assimilations and tries_count < 4:
                    # print(assimilations[key])
                    rule = self.assimilations[key].split('|')
                    line[i] = rule[0]
                    if next_letter:
                        line[i + 1] = rule[1]
                        key = '%s|%s' % (line[i], line[i + 1])
                    else:
                        key = ''
                    tries_count += 1
            line = self.remove_empty_chars(line)
        return line

    def apply_palatalizations(self, line):
        line = self.remove_empty_chars(line)
        for _ in range(2):
            for i in range(len(line)):
                palatalization = self.palatalizations.get(line[i])
                palatalizer = i + 1 < len(line) and self.palatalizers.get(line[i + 1])
                if palatalization and palatalizer:
                    # randomize a bit
                    if random.choice([True, False]):
                        line[i] = palatalization
                        line[i + 1] = palatalizer

            line = self.remove_empty_chars(line)
        return line

    def generate(self, structure):
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
                print()
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
                    line = self.generate_line_method(rhyme, syllable_count)
                    line = self.apply_assimilations(line)
                    # line = apply_palatalizations(line)

                    # print ''.join(line)
                    print(''.join(line))  # , line
