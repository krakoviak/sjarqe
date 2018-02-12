import re

ALPHABET = '_abcdefghijklmnopqrstuvwxyz'
INITIAL = 'bigrams_with_this_initial'
INITIAL_AND_FINAL = 'bigrams_with_this_initial_and_this_final'
ROUND_TO = 4


def symbol_to_alphabet_letter(sym):
    sym_ = sym.lower()
    if sym_ in ALPHABET:
        return sym_
    else:
        return '_'


def clean_results(dict_):
    results = {}
    for first_, v in dict_.items():
        # v: {'bigrams_with_this_initial': 666, 'b': {'p': 0.1234, 'bigrams_with_this_initial_and_this_final': 58}}
        for k, vv in v.items():
            # k: ('bigrams_with_this_initial', 'b')
            # vv: (666, {'p': 0.1234, 'bigrams_with_this_initial_and_this_final': 58})
            if isinstance(vv, dict):
                # in this case k == next_
                if first_ not in results:
                    results[first_] = {k: vv['p']}
                else:
                    results[first_][k] = vv['p']
    return results


def recalculate(d, initial, final):
    """
    {}, 'a', 'a' -> {'a': {'bigrams_with_this_initial': 1, 'a': {'p': 0.5, 'bigrams_with_this_initial_and_this_final': 1}}}
    {'a': {'bigrams_with_this_initial': 1, 'a': {'p': 0.5, 'bigrams_with_this_initial_and_this_final': 1}}}, 'a', 'a' ->
     -> {'a': {'bigrams_with_this_initial': 2, 'a': {'p': 0.5, 'bigrams_with_this_initial_and_this_final': 2}}}
    {'a': {'bigrams_with_this_initial': 2, 'a': {'p': 0.5, 'bigrams_with_this_initial_and_this_final': 2}}}, 'a', 'b' ->
     -> {'a': {'bigrams_with_this_initial': 3, 'a': {'p': 0.6666, 'bigrams_with_this_initial_and_this_final': 2},
                                               'b': {'p': 0.3333, 'bigrams_with_this_initial_and_this_final': 1}}}
    changes in place!
    """
    if initial in d:
        total_occurrences = d[initial][INITIAL] + 1
        if final in d[initial]:
            occurrences = d[initial][final][INITIAL_AND_FINAL] + 1
        else:
            occurrences = 1

        p = round(1. * occurrences / total_occurrences, ROUND_TO)

        d[initial][INITIAL] = total_occurrences
        d[initial][final] = {'p': p,
                             INITIAL_AND_FINAL: occurrences}
    else:
        total_occurrences = 1
        occurrences = 1
        p = round(1. * occurrences / total_occurrences, ROUND_TO)
        d[initial] = {INITIAL: total_occurrences,
                      final: {'p': p,
                              INITIAL_AND_FINAL: occurrences}}
    # recalc the rest
    for f, value in d[initial].items():
        if f not in ALPHABET or f == final:
            continue
        value['p'] = round(1. * value['bigrams_with_this_initial_and_this_final'] / total_occurrences, ROUND_TO)


def count_bigrams(text, d):
    """
    d = {'a': {'bigrams_with_this_initial': 666, 'a': {'p': 0.1234, 'bigrams_with_this_initial_and_this_final': 58}}}
    """
    length = len(text)
    for i, ch in enumerate(text):
        initial = symbol_to_alphabet_letter(ch)
        next_index = i + 1
        if next_index == length:
            next_ = '_'
        else:
            next_ = symbol_to_alphabet_letter(text[next_index])
        recalculate(d, initial, next_)
    return clean_results(d)


def count_trigrams(text, d):
    text = cleanup_text(text)
    length = len(text)
    # for i, ch in enumerate(text):
    for i in range(len(text)):
        one = text[i]
        two_index = i + 1
        if two_index == length:
            # means there's not enough letters already
            break
        else:
            two = text[two_index]
        three_index = i + 2
        if three_index == length:
            three = '_'
        else:
            three = text[three_index]
        one, two, three = map(symbol_to_alphabet_letter, [one, two, three])

        recalculate(d, one + two, three)
    return clean_results(d)


def cleanup_text(text):
    raw_words = text.split()
    result = []
    for raw in raw_words:
        regex = re.compile('[^a-z]')
        cleaned = regex.sub('', raw.lower()).strip()
        if cleaned:
            result.append(cleaned)
        # else:
        #     print 'what was left was no longer a word'
    return ' '.join(result)


def calculate_trigrams():
    with open('/Users/kirill/code/input_eng.txt') as f:
        result_dict = {}
        for line in f.readlines():
            result = count_trigrams(line, result_dict)

        print result

from trigram_distribution import distribution

# print len(distribution.keys())

# trigram_initials = {}
# with open('/Users/kirill/code/input_eng.txt') as f:
#     result_dict = {}
#     for line in f.readlines():

# for k, v in distribution.items():
#     if k[1] == '_' and '_' in v.keys():
#         print k, [v_v for v_k, v_v in v.items() if v_k == '_']
# print '-------------------------'
# print len(distribution.keys())
# for k, v in distribution.items():
#     if k[1] == '_' and '_' in v.keys():
#         print k, [v_v for v_k, v_v in v.items() if v_k == '_']
