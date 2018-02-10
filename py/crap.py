from nose.tools import eq_
from copy import deepcopy

def merge_groups(first, second):
    """
    (['a'], ['b', 'c']) -> [['a'], ['b', 'c']]
    (['a', ['b', 'c']], ['d']) -> [['a', ['b', 'c']], ['d']]
    """
    return [first, second]


def groups_with_same_probabilities_present(lst):
    return len(set(l[0] for l in lst)) < len(lst)


def aggregate_probabilities(grouped_by_probability):
    """
    multiply the probabilities by number of letters
    {0.5: {'a'}, 0.25: {'b', 'c'}} -> [(0.5, ['a']), (0.5, ['b', 'c'])]
    """
    aggregated_list = []
    for p, letter_list in grouped_by_probability.items():
        aggregated_list.append((p * len(letter_list), letter_list))
    return aggregated_list


def group_by_probability(probabilities):
    """
    group letters by probabilities
    {'a': 0.5, 'b': 0.25, 'c': 0.25} -> {0.5: {'a'}, 0.25: {'b', 'c'}}
    """
    result_ = {}
    for key, p in probabilities.items():
        if p in result_:
            result_[p].add(key)
        else:
            result_[p] = {key, }
    return result_


def distribute_probabilities(probabilities):
    """
    distributes letters into buckets with same probabilities
    with probability multiplication:
    {'a': 0.5, 'b': 0.25, 'c': 0.25} -> {0.5: ['a'], 0.25: ['b', 'c']} -> 0.5: 'a' + -> {1: ['a', ['b', 'c']]}
    """
    grouped_by_probability = group_by_probability(probabilities)

    multiplied_list = aggregate_probabilities(grouped_by_probability)
    """
    group letter lists with the same probability, summing up their probabilities
    """
    results = {}
    while multiplied_list:
        p, group = multiplied_list.pop()
        if p not in results:
            results[p] = group
        else:
            current_p = p
            current_group = deepcopy(group)
            while True:
                existing_group = results.pop(current_p)
                merged_group = merge_groups(current_group, existing_group)
                current_p += current_p
                if current_p not in results:
                    results[current_p] = merged_group
                    break
                else:
                    current_group = merged_group

    results['sorted_probabilities'] = sorted(results.keys())
    return results


def distribute_probabilities_old(probabilities):
    """
    distributes keys into buckets with similar probabilities
    """
    results = {'sorted_probabilities': sorted(set(probabilities.values()))}
    for key, p in probabilities.items():
        if p in results:
            results[p].add(key)
        else:
            results[p] = set(key, )
    return results


def process_distribution(distribution):
    for k in distribution.keys():
        distribution[k] = distribute_probabilities(distribution[k])


# def get_final(probabilities):
#     """
#     {'x': {'sorted_probabilities': [0.1111, 0.1667, 0.2222], 0.1111: {'a', '_'}, 0.1667: {'e', 'i'},
#            0.2222: {'p', 't'}},
#      'z': {'sorted_probabilities': [0.1, 0.4, 0.5], 0.4: {'i', }, 0.5: {'e', }, 0.1: {'o', }}}
#     """
#     # get a random number _r_ between 0 and 1
#     r = random.uniform(0, 1)
#
#     sorted_probabilities = probabilities['sorted_probabilities']
#
#     # discard all that are less than R
#     sorted_greater_than_r = [p for p in sorted_probabilities if p > r]
#     # print r, sorted_greater_than_r
#
#     if sorted_greater_than_r:
#         # get the closest probability
#         smallest_probability_greater_than_r = sorted_greater_than_r[0]
#
#         keys_with_same_probability = probabilities[smallest_probability_greater_than_r]
#         # return a key from one of those
#         return random.choice(list(keys_with_same_probability))
#     else:
#         # just return one of those with the biggest probability (???)
#         biggest_probability = sorted_probabilities[-1]
#
#         keys_with_same_probability = probabilities[biggest_probability]
#         # print 'sorted_greater_than_r was empty, returning ' + key
#         return random.choice(list(keys_with_same_probability))


# # checks that after a significant number of iterations
# # the values returned by get_final are close to probabilities
# def test_get_final():
#     def check(probabilities):
#         ITERATIONS = 1000
#         ALLOWED_DEVIATION = 0.05
#         letters = []
#         for p, letters_set in probabilities.items():
#             if type(letters_set) == set:
#                 letters += [(l, p) for l in letters_set]
#
#         # print letters
#         for l, p in letters:
#             actual_count = 0
#             for _ in range(ITERATIONS):
#                 if get_final(probabilities) == l:
#                     actual_count += 1
#             actual_frequency = 1.0 * actual_count / ITERATIONS
#             msg = 'Calculated frequency %s over %s iterations for key "%s" is more than %s away from its probability %s' % (
#                 actual_frequency, ITERATIONS, l, round(ALLOWED_DEVIATION * 100), p)
#
#             assert_is_close_to(p, actual_frequency, ALLOWED_DEVIATION, msg)
#
#     test_cases = [{'sorted_probabilities': [1], 1: {'b'}},
#                   {'sorted_probabilities': [0.5], 0.5: {'a', 'b'}},
#                   {'sorted_probabilities': [0.3333, 0.6667], 0.3333: {'a'}, 0.6667: {'c'}},
#                   {'sorted_probabilities': [0.25, 0.5], 0.25: {'a', 'b'}, 0.5: {'c'}}]
#     for t in test_cases:
#         yield check, t


def test_distribute_probabilities():
    def check(expected, probabilities):
        eq_(expected, distribute_probabilities(probabilities))

    test_cases = [({'b': 1}, {'sorted_probabilities': [1], 1: set('b')}),
                  ({'a': 0.3333, 'b': 0.3333, 'c': 0.6667},
                   {'sorted_probabilities': [0.6666, 0.6667], 0.6666: {'a', 'b'}, 0.6667: set('c')}),
                  ({'a': 0.25, 'b': 0.25, 'c': 0.5, 'd': 0.6},
                   {'sorted_probabilities': [0.6, 1.0], 1.0: [{'a', 'b'}, {'c'}], 0.6: {'d', }})]
    for probabilities, expected in test_cases:
        yield check, expected, probabilities


# def test_process_distribution():
#     distribution = {'x': {'a': 0.1111, 'e': 0.1667, 'i': 0.1667, 'p': 0.2222, 't': 0.2222, '_': 0.1111},
#                     'z': {'i': 0.2, 'e': 0.5, 'o': 0.1, 'x': 0.1}}
#     expected = {'x': {'sorted_probabilities': [0.1111, 0.1667, 0.2222], 0.1111: {'a', '_'}, 0.1667: {'e', 'i'},
#                       0.2222: {'p', 't'}},
#                 'z': {'sorted_probabilities': [0.4, 0.5], 0.4: [{'i'}, {'o', 'x'}], 0.5: {'e'}}}
#     process_distribution(distribution)
#     eq_(expected, distribution)


def test_merge_groups():
    def check(groups, expected):
        eq_(expected, merge_groups(*groups))

    test_cases = [
        ((['a'], ['b', 'c']), [['a'], ['b', 'c']]),
        ((['a', ['b', 'c']], ['d']), [['a', ['b', 'c']], ['d']])
    ]
    for groups, expected in test_cases:
        yield check, groups, expected


def test_aggregate_probabilities():
    def check(case, expected):
        eq_(expected, aggregate_probabilities(case))

    test_cases = [({0.5: ['a'], 0.25: ['b', 'c']}, [(0.5, ['a']), (0.5, ['b', 'c'])]),
                  ({0.5: ['a', 'b', 'c']}, [(1.5, ['a', 'b', 'c'])])]
    for case, expected in test_cases:
        yield check, case, expected


def test_group_by_probability():
    def check(case, expected):
        eq_(expected, group_by_probability(case))

    test_cases = [({'a': 0.5, 'b': 0.25, 'c': 0.25}, {0.5: {'a', }, 0.25: {'b', 'c'}})]
    for case, expected in test_cases:
        yield check, case, expected
