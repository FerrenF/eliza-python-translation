from collections import OrderedDict
from typing import Dict, List

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
    return ' '.join(s)

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
            j = components[n - 1]
            expanded = elz_split(j)
            result.extend(expanded)
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

def match(tags: Dict[str, List[str]], pattern: List[str], words: List[str], matching_components: List[str]) -> (bool, List[str]):

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
        m, c = match(tags, pattern[:], words[:], mc)
        if m:
            matching_components.append(current_word)
            matching_components.extend(c)
            return True, matching_components

    elif n == 0: # 0 matches zero or more of any words
        component = []
        mc = []
        while True:
            m, c = match(tags, pattern[:], words[:], mc)
            mc = c
            if m:
                j = elz_join(component)
                matching_components.append(j)
                matching_components.extend(mc)
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
        m, c = match(tags, pattern[:], words[:], mc)
        if m:
            matching_components.append(elz_join(component))
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


