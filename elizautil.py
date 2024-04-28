from collections import OrderedDict
from typing import Dict, List, Tuple

import ctypes
from typing import List, Dict

from elizaconstant import TagMap, RuleMap
import re

# CONTAINS ALL UTILITY FUNCTIONS
def split_user_input(s, punctuation):
    result = []
    word = ''
    for ch in s:
        if ch == ' ' or ch in punctuation:
            if word:
                result.append(word)
                word = ''
            if ch != ' ':
                result.append(ch)
        else:
            word += ch
    if word:
        result.append(word)
    return result


def elz_join(s):
    result = ""
    for word in s:
        if word:
            if result:
                result += ' '
            result += word
    return result

def elz_split(s: str) -> List[str]:
    return s.split(' ')

def to_int(s: str) -> int:
    result = 0
    for c in s:
        if c.isdigit():
            result = 10 * result + ord(c) - ord('0')
        else:
            return -1
    return result

def char2uint(c: str) -> ctypes.c_char_p:
    b_string1 = c.encode('utf-8')
    return ctypes.c_char_p(b_string1)

def unsigned(i: int) -> ctypes.c_uint:
    return ctypes.c_uint(i)

def reassemble(reassembly_rule: List[str], components: List[str]) -> List[str]:
    result: List[str] = []
    for r in reassembly_rule:
        n = to_int(r)
        if n < 0:
            result.append(r)
        elif n == 0 or n > len(components):
            result.append("THINGY")
        else:
            j = elz_split(components[n - 1])
            result.extend(j)
    return result

def inlist(word: str, wordlist: str, tags: Dict[str, List[str]]) -> bool:
    assert word, "Word should not be empty"
    cp = wordlist.strip(" ()")

    if cp.startswith('*'):
        cp = cp[1:]
        s = cp.split()
        for w in s:
            if word in w:
                return True
        return False
    elif cp.startswith('/'):
        cp = cp[1:].strip()
        s = cp.split()
        for w in s:
            if w in tags:
                tagList = tags.get(w) or []
                if word in tagList:
                    return True


        return False
    return False



# Define types
tagmap = Dict[str, List[str]]
vecstr = List[str]
stringlist = List[str]

def xmatch(tags: tagmap,
           pat_array: vecstr,
           word_array: vecstr,
           p_begin: int,  # index into pat_array where match pattern begins
           pat_end: int,  # index into pat_array just after match pattern ends
           word_ind_begin: int,  # index into word_array where pattern must begin matching
           fixed_len: int,  # total number of words required to match non-0-wildcard part

           w_end: int, #<- IN. : index into word_array just after pattern matching ended
           # Python does not pass non-immutable objects as references, so we must return what we need.
           result: vecstr  # <- TO out: matches will be written to result at [p_begin..p_end)
           ) -> (bool, int): # w_end OUT. is the second spot in this tuple

    w_end_result = w_end
    """Match pattern segment to words segment."""
    if len(word_array) - word_ind_begin < fixed_len:
        return False, w_end_result  # Insufficient words to match pattern

    wildcard_len = 0
    wildcard_end = 0
    has_wildcard = to_int(pat_array[p_begin]) == 0

    if has_wildcard:
        if pat_end == len(pat_array):
            # Last segment of the whole pattern: must match up to last word
            wildcard_len = len(word_array) - word_ind_begin - fixed_len
            wildcard_end = wildcard_len
        else:
            # Not the last segment: consume the smallest number of words possible
            wildcard_len = 0
            wildcard_end = len(word_array) - word_ind_begin - fixed_len

    # Loop until a match is found or all possible wildcard_len values tried
    while True:
        p = p_begin + has_wildcard
        w = word_ind_begin + wildcard_len

        # Loop to match pattern at p to words at w
        # Exit if p == p_end (success) or if all wildcard_len values tried
        while p < pat_end:
            n = to_int(pat_array[p])
            assert n != 0
            if n > 0:  # wildcard of specific length
                assert w + n <= len(word_array)
                part = []
                for i in range(n):
                    part.append(word_array[w])
                    w += 1
                result[p] = elz_join(part)
            else:  # pat_array[p] is a literal or list
                assert w < len(word_array)
                if pat_array[p][0] == '(':  # it's a list, e.g., "(*SAD HAPPY)"
                    if inlist(word_array[w], pat_array[p], tags):
                        result[p] = word_array[w]
                        w += 1
                    else:
                        break
                elif pat_array[p] == word_array[w]:  # it's a literal, e.g., "ARE"
                    result[p] = word_array[w]
                    w += 1
                else:
                    break
            p += 1

        if p == pat_end:
            w_end_result = w
            if has_wildcard:
                part = []
                for i in range(wildcard_len):
                    part.append(word_array[word_ind_begin + i])
                result[p_begin] = elz_join(part)
            return True, w_end_result
        if wildcard_len == wildcard_end:
            break

        # end of loop increment
        wildcard_len += 1

    return False, w_end_result


def slip_match(
        tags: tagmap,
        pattern: stringlist,
        words: stringlist
) -> Tuple[bool, stringlist]:
    """
    A closer simulation to the MAD-SLIP YMATCH code. From Anthony:
     These things must be true
      - the pattern segment may contain at most one 0-wildcard
      - if the segment contains a 0-wildcard it must be the first element
      - the segment must either be the last in the whole pattern or
        be followed by another segment that begins with a 0-wildcard

    :param tags:
    :param pattern:
    :param words:
    :return: A tuple containing a True/False value indicating a match, and t list of the matching components.
    """
    pat_array = pattern.copy()
    word_array = words.copy()
    matches = [''] * len(pat_array)

    word_index = 0
    p_seg_end = 0

    while p_seg_end < len(pat_array):
        fixed_len = 0
        p = p_seg_end

        # Locate right boundary of next anchor segment
        while p_seg_end < len(pat_array):
            n = to_int(pat_array[p_seg_end])
            if n == 0:  # 0-wildcard
                if p_seg_end > p:
                    break  # Not the first element
            elif n > 0:
                fixed_len += n  # Fixed length wildcard, e.g., 3
            else:
                fixed_len += 1  # Literal or (*...) or (/...)
            p_seg_end += 1

        """from source: The current pattern segment is the half-open interval [p, p_seg_end).
            The segment always contains fixed size elements, unless there are
            no fixed size elements before the next 0-wildcard or the end of the
            pattern. If it contains a 0-wildcard that will be the first element.
            Following the wildcard (if present) will be only fixed sized elements
            (if any). I.e. the segment will have one of these three forms
                 (0)
                 (0 1 2 LITERAL (*LITERAL LITERAL) (/TAG TAG)), for example
                 (  1 2 LITERAL (*LITERAL LITERAL) (/TAG TAG)), for example
            Following this segment will either be a 0-wildcard or the end of the
            pattern. This segment must match the words at w. If the segment begins
            with a wildcard, then
              - if what follows this segment is a 0-wildcard, this segment must
                consume the smallest number of words possible
              - if what follows this segment is the pattern end, this segment must
                consume all the remaining words
            If the segment does not begin with a 0-wildcard it must consume the
            exact number of words described by the pattern elements. """
        # word_index juggling
        (m, word_index) = xmatch(tags, pat_array, word_array, p, p_seg_end, word_index, fixed_len, word_index, matches)
        if not m:
            return False, []  # Segment didn't match words

    if word_index < len(word_array):
        return False, []  # Pattern did not consume all words

    return True, matches

def recursive_match(tags: Dict[str, List[str]], pattern: List[str], words: List[str], matching_components: List[str]) -> (bool, List[str]):
    """
    BROKEN
    """
    matching_components.clear()

    if not pattern:
        return not words, []

    patword = pattern.pop(0)
    n = to_int(patword)

    if n < 0: #  patword is e.g. "ARE" or "(*SAD HAPPY DEPRESSED)"
        if not words:
            return False, [] # patword cannot match nothing

        current_word = words.pop(0)
        if patword[0] == '(':
            # patword is a group, is current_word in that group?
            if not inlist(current_word, patword, tags):
                return False, []

        elif patword != current_word:
            return False, [] # patword is a single word and it doesn't match

        # so far so good; can we match remainder of pattern with remainder of words?
        mc = []
        m, c = recursive_match(tags, pattern[:], words[:], mc)
        if m:
            matching_components.append(current_word)
            matching_components.extend(c)
            return True, matching_components

    elif n == 0: # 0 matches zero or more of any words
        component = []
        mc = []
        while True:

            m, c = recursive_match(tags, pattern[:], words[:], mc)
            if m:

                matching_components.extend(component)
                matching_components.extend(c)
                return True, matching_components

            if not words:
                return False, []

            w = words.pop(0)
            component.append(w)

    else:

        if len(words) < n:
            return False, []

        component = [words.pop(0) for _ in range(n)]
        mc = []
        m, c = recursive_match(tags, pattern[:], words[:], mc)
        if m:
            matching_components.extend(component)
            matching_components.extend(c)
            return True, matching_components
    return False, []

def collect_tags(rules: RuleMap) -> TagMap:
    tags: TagMap = OrderedDict()
    for tag, rule in rules.items():
        keyword_tags = rule.dlist_tags()
        for index, item in enumerate(keyword_tags):
            if item == "/":
                continue
            if len(item) > 1 and item[0] == '/':
                keyword_tags[index] = item[1:]

            ky = rule.keyword
            tg = keyword_tags[index]
            v = []
            if tg in tags.keys() and len(tags[tg]):
                v = tags[tg]
            v.append(ky)
            tags[tg] = v
    return tags

class RuleBase:
    def dlist_tags(self) -> List[str]:
        pass

    def to_string(self) -> str:
        pass

def get_rule(rules: RuleMap, keyword: str, **kwargs) -> RuleBase:
    rule = rules.get(keyword, None)
    if not rule and kwargs.get('throw', True):
        #Didn't find it.
        raise RuntimeError()
    return rule


def delimiter_character(c: str) -> bool:
    return c in [',', '.']


