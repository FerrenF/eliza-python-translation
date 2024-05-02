from collections import OrderedDict
from typing import Tuple

import ctypes
from typing import List, Dict

from elizaconstant import TagMap, RuleMap


# CONTAINS ALL UTILITY FUNCTIONS
def split_input(input_string, punctuation_marks):
    """
    Splits a user input string into a list of words and punctuation marks.

    :param input_string: The input string to be split.
    :type input_string: str
    :param punctuation_marks: A string containing characters to be treated as punctuation marks.
    :type punctuation_marks: str
    :return: A list containing the words and punctuation marks from the input string.
    :rtype: list[str]
    """

    result_list = []
    word_accumulator = ''
    for character in input_string:
        if character == ' ' or character in punctuation_marks:
            if word_accumulator:
                result_list.append(word_accumulator)
                word_accumulator = ''
            if character != ' ':
                result_list.append(character)
        else:
            word_accumulator += character
    if word_accumulator:
        result_list.append(word_accumulator)
    return result_list


def eliza_specific_join(s):
    result = ""
    for word in s:
        if word:
            if result:
                result += ' '
            result += word
    return result

def eliza_specific_split(s: str) -> List[str]:
    """
    Where it could have been complex, it only needed to be simple. I thought there might be a possibility that the split
    functionality on 1966 CPU architecture might output differently. Nope. Just need to split it normally.
    :param s:
    :return:
    """
    return s.split(' ')

def to_int(symbols: str) -> int:
    """
        Converts a string containing digits into an integer.

        :param symbols: The string containing digits to be converted into an integer.
        :type symbols: str
        :return: The integer representation of the input string, or -1 if the input contains non-digit characters.
        :rtype: int
        """
    integer_value = 0
    for character in symbols:
        if character.isdigit():
            integer_value = 10 * integer_value + ord(character) - ord('0')
        else:
            return -1
    return integer_value

def char2uint(c: str) -> ctypes.c_char_p:
    b_string1 = c.encode('utf-8')
    return ctypes.c_char_p(b_string1)

def unsigned(i: int) -> ctypes.c_uint:
    return ctypes.c_uint(i)

def reassemble_from_rule(reassembly_rule: List[str], components: List[str]) -> List[str]:
    """
      Reassembles a list of components according to a reassembly rule.

      :param reassembly_rule: The list of reassembly rules containing wildcard symbols or component indices.
      :type reassembly_rule: List[str]
      :param components: The list of components to be reassembled.
      :type components: List[str]
      :return: The reassembled list of components.
      :rtype: List[str]
      """
    reassembled_components: List[str] = []
    for rule in reassembly_rule:
        index = to_int(rule)
        if index < 0:
            reassembled_components.append(rule)
        elif index == 0 or index > len(components):
            reassembled_components.append("THINGY")
        else:
            split_components = eliza_specific_split(components[index - 1])
            reassembled_components.extend(split_components)
    return reassembled_components


def words_in_list(word: str, wordlist: str, tags: Dict[str, List[str]]) -> bool:
    """
       Checks if a word is present in a word list or within tags in a dictionary.

       :param word: The word to search for.
       :type word: str
       :param wordlist: The string representing a word list or tags in a dictionary.
       :type wordlist: str
       :param tags: The dictionary containing tags and associated word lists.
       :type tags: Dict[str, List[str]]
       :return: True if the word is found, False otherwise.
       :rtype: bool
       """
    assert word, "Word should not be empty"
    cleaned_wordlist = wordlist.strip(" ()")

    if cleaned_wordlist.startswith('*'):
        cleaned_wordlist = cleaned_wordlist[1:]
        words = cleaned_wordlist.split()
        for word_group in words:
            if word in word_group:
                return True
        return False
    elif cleaned_wordlist.startswith('/'):
        cleaned_wordlist = cleaned_wordlist[1:].strip()
        tags_list = cleaned_wordlist.split()
        for tag in tags_list:
            if tag in tags:
                tag_list = tags.get(tag) or []
                if word in tag_list:
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
                result[p] = eliza_specific_join(part)
            else:  # pat_array[p] is a literal or list
                assert w < len(word_array)
                if pat_array[p][0] == '(':  # it's a list, e.g., "(*SAD HAPPY)"
                    if words_in_list(word_array[w], pat_array[p], tags):
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
                result[p_begin] = eliza_specific_join(part)
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
            if not words_in_list(current_word, patword, tags):
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
    """
        Collects tags from a dictionary of rules and returns a dictionary mapping tags to their associated keywords.

        :param rules: The dictionary of rules where tags are extracted from.
        :type rules: RuleMap
        :return: A dictionary mapping tags to their associated keywords.
        :rtype: TagMap
        """
    tags: TagMap = OrderedDict()
    for tag, rule in rules.items():
        keyword_tags = rule.dlist_tags()
        for index, tag_item in enumerate(keyword_tags):
            if tag_item == "/":
                continue
            if len(tag_item) > 1 and tag_item[0] == '/':
                tag_item = tag_item[1:]

            keyword = rule.keyword
            tag_name = tag_item
            keywords_for_tag = []
            if tag_name in tags.keys() and len(tags[tag_name]):
                keywords_for_tag = tags[tag_name]
            keywords_for_tag.append(keyword)
            tags[tag_name] = keywords_for_tag
    return tags


class RuleBase:
    """
        Stub.
    """
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


