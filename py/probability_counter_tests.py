import random

from nose.tools import eq_

from count_letter_collocation_probabilities import *


def test_symbol_to_alphabet_letter():
    def check(exp, case):
        eq_(exp, symbol_to_alphabet_letter(case))

    for test_case, expected in [('A', 'a'),
                                ('%', '_'),
                                ('_', '_'),
                                (' ', '_')]:
        yield check, expected, test_case


def test_clean_results():
    def check(exp, case):
        eq_(exp, clean_results(case))

    cases = [({'a': {INITIAL: 666, 'b': {'p': 0.1234, INITIAL_AND_FINAL: 58}}}, {'a': {'b': 0.1234}}),
             ({
                  'a': {INITIAL: 666, 'b': {'p': 0.1234, INITIAL_AND_FINAL: 58},
                        'd': {'p': 0.6666, INITIAL_AND_FINAL: 58}},
                  'b': {INITIAL: 666, '_': {'p': 0.7777, INITIAL_AND_FINAL: 58}}},
              {'a': {'b': 0.1234, 'd': 0.6666},
               'b': {'_': 0.7777}})]

    for c, exp in cases:
        yield check, exp, c


def test_count_bigrams():
    def check(exp, case):
        eq_(exp, count_bigrams(case, {}))

    cases = [('a', {'a': {'_': 1}}),
             ('aa', {'a': {'a': 0.5, '_': 0.5}}),
             ('aba', {'a': {'b': 0.5, '_': 0.5}, 'b': {'a': 1}}),
             ('abab', {'a': {'b': 1}, 'b': {'a': 0.5, '_': 0.5}}),
             ('abaca', {'a': {'b': 0.3333, 'c': 0.3333, '_': 0.3333}, 'b': {'a': 1}, 'c': {'a': 1.0}}),
             ('aba ca', {'a': {'b': 0.3333, '_': 0.6667}, 'b': {'a': 1}, 'c': {'a': 1}, '_': {'c': 1}})
             ]
    for text, expected in cases:
        yield check, expected, text


def test_recalculate():
    def check(exp, case):
        d, initial, final = case
        recalculate(d, initial, final)
        eq_(exp, d)

    cases = [
        (({}, 'a', 'a'),
         {'a': {'bigrams_with_this_initial': 1, 'a': {'p': 1, 'bigrams_with_this_initial_and_this_final': 1}}}),
        (({'a': {'bigrams_with_this_initial': 1, 'a': {'p': 1, 'bigrams_with_this_initial_and_this_final': 1}}},
          'a', 'a'),
         {'a': {'bigrams_with_this_initial': 2, 'a': {'p': 1, 'bigrams_with_this_initial_and_this_final': 2}}}),
        (({'a': {'bigrams_with_this_initial': 2, 'a': {'p': 1, 'bigrams_with_this_initial_and_this_final': 2}}},
          'a', 'b'),
         {'a': {'bigrams_with_this_initial': 3, 'a': {'p': 0.6667, 'bigrams_with_this_initial_and_this_final': 2},
                'b': {'p': 0.3333, 'bigrams_with_this_initial_and_this_final': 1}}})
    ]

    for case, exp in cases:
        yield check, exp, case


def assert_is_close_to(expected, actual, allowed_deviation=0, msg_override=''):
    msg = msg_override or 'Actual value %s is more than allowed deviation %s away from expected value %s' % (
        actual, allowed_deviation, expected)
    assert expected - allowed_deviation <= actual <= expected + allowed_deviation, msg


def test_random_distribution():
    def check(multiplier, allowed_deviation):
        s = 'a' * 2 * multiplier + 'b' * 3 * multiplier + 'c' * 5 * multiplier
        s_list = list(s)
        random.shuffle(s_list)
        s_shuffled = ''.join(s_list)
        bigrams = count_bigrams(s_shuffled, {})
        for initial, values in bigrams.items():
            assert_is_close_to(0.2, values['a'], allowed_deviation)
            assert_is_close_to(0.3, values['b'], allowed_deviation)
            assert_is_close_to(0.5, values['c'], allowed_deviation)

    cases = [(1000, 0.1),
             (10000, 0.05)]
    for c in cases:
        m, d = c
        yield check, m, d
