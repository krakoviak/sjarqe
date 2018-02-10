from generator import *
from probability_counter_tests import assert_is_close_to


def test_get_letter():
    def check(probabilities):
        ITERATIONS = 10000
        ALLOWED_DEVIATION = 0.05

        for letter, p in probabilities.items():
            actual_count = 0
            for _ in range(ITERATIONS):
                if get_letter(probabilities) == letter:
                    actual_count += 1
            actual_frequency = 1.0 * actual_count / ITERATIONS
            msg = 'Calculated frequency %s over %s iterations for key "%s" is more than %s away from its probability %s' % (
                actual_frequency, ITERATIONS, letter, round(ALLOWED_DEVIATION * 100), p)

            assert_is_close_to(p, actual_frequency, ALLOWED_DEVIATION, msg)

    test_cases = [
        {'a': 1},
        {'a': 0.5, 'b': 0.5},
        {'a': 0.3333, 'b': 0.3333, 'c': 0.3333},
        {'a': 0.5, 'b': 0.25, 'c': 0.25},
    ]
    for probabilities in test_cases:
        yield check, probabilities
