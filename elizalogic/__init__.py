from typing import Dict, List

import ctypes
from typing import List, Dict
from elizalogic.RuleBase import RuleBase
from elizalogic.constant import ElizaConstant
def join(s: List[str]) -> str:
    return ' '.join(s)

def split(s: str, punctuation: str="") -> List[str]:
    return s.split(punctuation)

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
            expanded = split(components[n - 1])
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
        cp = cp[1:]
        taglist = cp.split()
        for tag in taglist:
            if tag in tags:
                s = tags[tag]
                if word in s:
                    return True
        return False
    return False

def match(tags: Dict[str, List[str]], pattern: List[str], words: List[str], matching_components: List[str]) -> bool:
    matching_components.clear()

    if not pattern:
        return not words

    patword = pattern.pop(0)
    n = int(patword)

    if n < 0:
        if not words:
            return False

        current_word = words.pop(0)

        if patword[0] == '(':
            if current_word not in tags.get(patword, []):
                return False
        elif patword != current_word:
            return False

        mc = []
        if match(tags, pattern, words, mc):
            matching_components.append(current_word)
            matching_components.extend(mc)
            return True

    elif n == 0:
        component = []
        mc = []
        while True:
            if match(tags, pattern, words, mc):
                matching_components.append(join(component))
                matching_components.extend(mc)
                return True

            if not words:
                return False

            component.append(words.pop(0))

    else:
        if len(words) < n:
            return False

        component = [words.pop(0) for _ in range(n)]
        mc = []
        if match(tags, pattern, words, mc):
            matching_components.append(join(component))
            matching_components.extend(mc)
            return True
    return False

def collect_tags(rules: ElizaConstant.RuleMap) -> ElizaConstant.TagMap:
    tags = ElizaConstant.TagMap()
    for tag, rule in rules.items():
        keyword_tags = rule.dlist_tags()
        for tag2 in keyword_tags:
            if tag2 == "/":
                continue
            if len(tag2) > 1 and tag2[0] == '/':
                keyword_tags = keyword_tags[1:]
            tags[tag2].append(rule.keyword)
    return tags

def get_rule(rules: ElizaConstant.RuleMap, keyword: str) -> RuleBase:
    rule = rules.get(keyword, None)
    if not rule:
        raise RuntimeError()

    if not issubclass(rule.__class__, RuleBase):
        raise RuntimeError()

    return rule

def delimiter_character(c: str) -> bool:
    return len(c) == 1 and c in ",."

class RuleBase:
    def dlist_tags(self) -> List[str]:
        pass

    def to_string(self) -> str:
        pass

