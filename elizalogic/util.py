import ctypes
from typing import List, Dict

from elizalogic.RuleBase import RuleBase
from elizalogic.constant import TagMap, RuleMap


#hash, join, match, reassemble, pop_front



def join(s: List[str]) -> str:
    return ' '.join(s)
def split(s: str, punctuation: str="") -> List[str]:
    return s.split(punctuation)


# return numeric value of given s or -1
# e.g. to_int("2") -> 2, to_int("two") -> -1
def to_int(s: str)->int:
    result = 0
    for c in s:
        if c.isdigit():
            result = 10 * result + ord(c) - ord('0')
        else:
            return -1
    return result


def char2uint(c: str) -> ctypes.c_char_p:
    # create byte objects from the string
    b_string1 = c.encode('utf-8')
    return ctypes.c_char_p(b_string1)


def unsigned(i: int)-> ctypes.c_uint:
    return ctypes.c_uint(i)


# return words constructed from given reassembly_rule and components
# e.g. reassemble([ARE, YOU, 1], [MAD, ABOUT YOU]) -> [ARE, YOU, MAD]
def reassemble(reassembly_rule: List[str], components: List[str]) -> List[str]:
    result: List[str] = []
    for r in reassembly_rule:
        n = to_int(r)
        if n < 0:
            result.append(r)
        elif n == 0 or n > len(components):
            result.append("THINGY") # script error: index out of range (in the style of HMMM)
        else:
            expanded = split(components[n - 1])
            result.extend(expanded)
    return result


def inlist(word: str, wordlist: str, tags: Dict[str, List[str]]) -> bool:
    assert word, "Word should not be empty"

    cp = wordlist.strip(" ()")

    if cp.startswith('*'):  # (*SAD HAPPY DEPRESSED)
        cp = cp[1:]
        s = cp.split()
        for w in s:
            if word in w:
                return True
        return False
    elif cp.startswith('/'):  # (/NOUN FAMILY)
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

    if n < 0: #patword is e.g. "ARE" or "(*SAD HAPPY DEPRESSED)"
        if not words:
            return False # patword cannot match nothing

        current_word = words.pop(0)

        if patword[0] == '(':
            # patword is a group, is current_word in that group?
            if current_word not in tags.get(patword, []):
                return False
        elif patword != current_word:
            return False
        # so far so good; can we match remainder of pattern with remainder of words?
        mc = []
        if match(tags, pattern, words, mc):
            matching_components.append(current_word)
            matching_components.extend(mc)
            return True

    elif n == 0: # 0 matches zero or more of any words
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

#
# // collect all tags from any of the given rules that have them into a tagmap
# tagmap collect_tags(const rulemap & rules)
# {
#     tagmap tags;
#     for (const auto & tag : rules) {
#         stringlist keyword_tags(tag.second->dlist_tags());
#         for (auto t : keyword_tags) {
#             if (t == "/")
#                 continue;
#             if (t.size() > 1 && t.front() == '/')
#                 pop_front(t);
#             tags[t].push_back(tag.second->keyword());
#         }
#     }
#     return tags;
# }

def collect_tags(rules: RuleMap) -> TagMap:
    tags = TagMap()
    for tag, rule in rules.items():
        keyword_tags = rule.dlist_tags()
        for tag2 in keyword_tags:
            if tag2 == "/":
                continue
            if len(tag2)>1 and tag2[0] == '/':
                keyword_tags = keyword_tags[1:]
            tags[tag2].append(rule.keyword)
    return tags


# template<typename T>
# auto get_rule(rulemap & rules, const std::string & keyword)
# {
#     auto rule = rules.find(keyword);
#     if (rule == rules.end()) {
#         std::string msg("script error: missing keyword ");
#         msg += keyword;
#         throw std::runtime_error(msg);
#     }
#     auto castrule = std::dynamic_pointer_cast<T>(rule->second);
#     if (!castrule) {
#         std::string msg("internal error for keyword ");
#         msg += keyword;
#         throw std::runtime_error(msg);
#     }
#     return castrule;
# }

def get_rule(rules: RuleMap, keyword: str) -> RuleBase:
    rule = rules.get(keyword, None)
    if not rule:
        raise RuntimeError()

    if not issubclass(rule.__class__, RuleBase):
        raise RuntimeError()

    return rule

#
# // return true iff given c is delimiter (see delimiter())
# bool delimiter_character(char c)
# {
#     return c == ',' || c == '.';
# };

def delimiter_character(c: str)->bool:
    return (len(str)==1) and c in ",."

