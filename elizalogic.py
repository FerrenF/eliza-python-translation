from abc import abstractmethod, ABC
from typing import Tuple, Dict, List

from elizaconstant import TRACE_PREFIX, TagMap, SPECIAL_RULE_NONE, RuleMap
from elizaencoding import last_chunk_as_bcd, hash
from elizautil import reassemble_from_rule, eliza_specific_join, slip_match


def match_func(tags, pattern, words) -> Tuple[bool, List[str]]:
    """
    This method facilitates easy swapping out of different match methods. Anthony tried a few over the course of his research and as such, did I.
    :param tags:
    :param pattern:
    :param words:
    :return:
    """
    return slip_match(tags, pattern, words)
    
class RuleBase:
    def __init__(self, keyword: str, word_substitution: str, precedence: int):
        self.keyword = keyword
        self.word_substitution = word_substitution
        self.precedence = precedence
        self.transformations: List[Transform] = []

    def add_transformation_rule(self, decomposition: List[str], reassembly_rules: List[List[str]]):
        """Add a transformation rule associated with this rule."""
        self.transformations.append(Transform(decomposition, reassembly_rules))

    def word_substitute(self, word: str) -> str:
        """Apply word substitution if applicable."""
        if word == self.keyword and self.word_substitution:
            return self.word_substitution
        return word

    def apply_transformation(self, words: List[str], tags: TagMap, link_keyword: str) -> (str, List[str]):
        """Apply transformation rules to input words."""
        for decomposition, reassembly_rules in self.transformations:
            # Implementation of decomposition and reassembly
            pass
        return " ".join(words)  # Placeholder for the transformed sentence

    def has_transformation(self):
        return False

    def dlist_tags(self) -> List[str]:
        """Get DLIST tags associated with this rule."""
        return []  # Placeholder for DLIST tags

    def to_string(self) -> str:
        """Convert the rule to a string representation."""
        return f"Rule: Keyword={self.keyword}, Substitution={self.word_substitution}, Precedence={self.precedence}"

    def trace(self)-> str:
        return ""


class RuleKeyword(RuleBase):
    def __init__(self, keyword: str, word_substitution: str, precedence: int,
                 tags: List[str], link_keyword: str):
        super().__init__(keyword, word_substitution, precedence)
        self.tags = tags
        self.link_keyword = link_keyword

    def dlist_tags(self) -> List[str]:
        return self.tags

    def has_transformation(self) -> bool:
        return (len(self.transformations) > 0) or (len(self.link_keyword) > 0)

    def apply_transformation(self, words: List[str], tags: TagMap, link_keyword: str) -> Tuple[str, List[str], str]:
        self.trace_begin(words)

        constituents = []
        rule = None

        _words = words.copy()
        for idx, item in enumerate(self.transformations):
            status, constituents = match_func(tags, item.decomposition, _words)
            if status:
                rule = item
                rule_index = idx
                break

        if rule is None:
            if not self.link_keyword:
                self.trace_nomatch()
                return "inapplicable", words, link_keyword  # [page 39 (f)] should not happen?
            self.trace_reference(link_keyword)
            link_keyword = self.link_keyword
            return "linkkey", words, link_keyword
        self.trace_decomp(rule.decomposition, constituents)

        reassembly_rule = rule.reassembly_rules[rule.next_reassembly_rule]
        self.trace_reassembly(reassembly_rule)

        rule.next_reassembly_rule = (rule.next_reassembly_rule + 1)
        if rule.next_reassembly_rule == len(rule.reassembly_rules):
            rule.next_reassembly_rule = 0

        if len(reassembly_rule) == 1 and reassembly_rule[0] == "NEWKEY":
            return "newkey", words, link_keyword

        if len(reassembly_rule) == 2 and reassembly_rule[0] == '=':
            link_keyword = reassembly_rule[1]
            return "linkkey", words, link_keyword

        # is it the special-case reassembly rule (PRE (reassembly) (=reference))
        # (note: this is the only reassembly_rule that is still in a list)
        if (len(reassembly_rule) > 0) and reassembly_rule[0] == "(":
            link_keyword = reassembly_rule[-3]
            reassembly = reassembly_rule[3:reassembly_rule.index(')')]

            _words = reassemble_from_rule(reassembly, constituents)
            return "linkkey", _words, link_keyword

        _words = reassemble_from_rule(reassembly_rule, constituents)
        return "complete", _words, link_keyword

    def to_string(self) -> str:
        sexp = f"({'NONE' if self.keyword == SPECIAL_RULE_NONE else self.keyword}"

        if self.word_substitution:
            sexp += f" = {self.word_substitution}"

        if self.tags:
            sexp += f" DLIST({' '.join(self.tags)})"

        if self.precedence > 0:
            sexp += f" {self.precedence}"

        for rule in self.transformations:
            sexp += "\n    ((" + ' '.join(rule.decomposition) + ")"
            for reassembly_rule in rule.reassembly_rules:
                if not reassembly_rule:
                    sexp += "\n        ()"
                elif reassembly_rule[0] == "(":
                    sexp += "\n        " + ' '.join(reassembly_rule)  # it's a PRE rule
                elif reassembly_rule[0] == "=":
                    sexp += f"\n        (={' '.join(reassembly_rule[1:])})"  # it's a reference =XXX
                else:
                    sexp += "\n        (" + ' '.join(reassembly_rule) + ")"

            sexp += ")"

        if self.link_keyword:
            sexp += f"\n    (={self.link_keyword})"

        sexp += ")\n"
        return sexp

    def trace_begin(self, words: List[str]) -> None:
        w = ' '.join(words or [])
        self.trace = ""
        self.trace += f"{TRACE_PREFIX}keyword: {self.keyword}\n"
        self.trace += f"{TRACE_PREFIX}input: {w}\n"

    def trace_nomatch(self) -> None:
        self.trace += f"{TRACE_PREFIX}ill-formed script? No decomposition rule matches\n"

    def trace_reference(self, ref: str) -> None:
        self.trace += f"{TRACE_PREFIX}reference to equivalence class: {ref}\n"

    def trace_decomp(self, d: List[str], constituents: List[str]) -> None:
        self.trace += f"{TRACE_PREFIX}matching decompose pattern: {' '.join(d)}\n"
        self.trace += f"{TRACE_PREFIX}decomposition parts: "
        for id_, c in enumerate(constituents, start=1):
            self.trace += f"{id_}:\"{c}\" "
        self.trace += "\n"

    def trace_reassembly(self, r: List[str]) -> None:
        self.trace += f"{TRACE_PREFIX}selected reassemble rule: {' '.join(r)}\n"


class RuleMemory(RuleBase):

    def __init__(self, keyword: str = ""):
        super().__init__(keyword, "", 0)
        self.memories: List[str] = []
        self.trace = ""
        self._activity = False

    def create_memory(self, keyword: str, words: List[str], tags: Dict[str, List[str]]):
        if keyword != self.keyword:
            return

        # // JW says rules are selected at random [page 41 (f)]
        # // But the ELIZA code shows that rules are actually selected via a HASH
        # // function on the last word of the user's input text.
        assert len(self.transformations) == self.num_transformations

        lc = last_chunk_as_bcd(words[-1])
        hsh = hash(lc, 2)
        transformation = self.transformations[hsh]
        (found, mat) = match_func(tags, transformation.decomposition, words)
        if not found:
            return
        reassembly_rule = transformation.reassembly_rules[0]
        assmbl = reassemble_from_rule(reassembly_rule, mat)
        new_memory = eliza_specific_join(assmbl)
        self.trace += f"{TRACE_PREFIX}new memory: {new_memory}\n"
        self.memories.append(new_memory)

    def is_valid(self) -> bool:
        return len(self.keyword) or self.memory_exists()

    def memory_exists(self) -> bool:
        return len(self.memories) > 0

    def recall_memory(self) -> str:
        return self.memories.pop(0) if self.memory_exists else ""

    def to_string(self) -> str:
        sexp = f"(MEMORY {self.keyword}"
        for transform in self.transformations:
            sexp += f"\n    ({' '.join(transform.decomposition)} = {' '.join(transform.reassembly_rules[0])})"
        sexp += ")\n"
        return sexp

    def clear_trace(self):
        self.trace = ""

    def trace_memory_stack(self) -> str:
        if not self.memories:
            return f"{TRACE_PREFIX}memory queue: <empty>\n"
        else:
            return f"{TRACE_PREFIX}memory queue:\n" + "\n".join(f"{TRACE_PREFIX}  {m}" for m in self.memories)

    # the MEMORY rule must have this number of transformations
    num_transformations = 4


class Transform:

    stringList = List[str]
    def __init__(self, decomposition: List[str], reassembly_rules: List[stringList]):
        self.decomposition: List[str] = decomposition
        self.reassembly_rules: List[Transform.stringList] = reassembly_rules
        self.next_reassembly_rule = 0

    def __str__(self):
        return f"Transform: Decomposition={self.decomposition}, Reassembly Rules={self.reassembly_rules},\
         Next Reassembly Rule={self.next_reassembly_rule}"



class Tracer(ABC):
    @abstractmethod
    def begin_response(self, words: List[str]) -> None:
        pass

    @abstractmethod
    def limit(self, limit: int, built_in_msg: str) -> None:
        pass

    @abstractmethod
    def discard_subclause(self, text: str) -> None:
        pass

    @abstractmethod
    def word_substitution(self, word: str, substitute: str) -> None:
        pass

    @abstractmethod
    def create_memory(self, text: str) -> None:
        pass

    @abstractmethod
    def using_memory(self, script: str) -> None:
        pass

    @abstractmethod
    def subclause_complete(self, subclause: str, keystack: List[str], rules: RuleMap) -> None:
        pass

    @abstractmethod
    def unknown_key(self, keyword: str, use_nomatch_msg: bool) -> None:
        pass

    @abstractmethod
    def decomp_failed(self, use_nomatch_msg: bool) -> None:
        pass

    @abstractmethod
    def newkey_failed(self, response_source: str) -> None:
        pass

    @abstractmethod
    def transform(self, text: str, script: str) -> None:
        pass

    @abstractmethod
    def memory_stack(self, text: str) -> None:
        pass

    @abstractmethod
    def using_none(self, script: str) -> None:
        pass

    @abstractmethod
    def pre_transform(self, keyword: str, words: List[str]) -> None:
        pass

# Null tracer class
class NullTracer(Tracer):
    def begin_response(self, words: List[str]) -> None:
        pass

    def limit(self, limit: int, built_in_msg: str) -> None:
        pass

    def discard_subclause(self, text: str) -> None:
        pass

    def word_substitution(self, word: str, substitute: str) -> None:
        pass

    def create_memory(self, text: str) -> None:
        pass

    def using_memory(self, script: str) -> None:
        pass

    def subclause_complete(self, subclause: str, keystack: List[str], rules: RuleMap) -> None:
        pass

    def unknown_key(self, keyword: str, use_nomatch_msg: bool) -> None:
        pass

    def decomp_failed(self, use_nomatch_msg: bool) -> None:
        pass

    def newkey_failed(self, response_source: str) -> None:
        pass

    def transform(self, text: str, script: str) -> None:
        pass

    def memory_stack(self, text: str) -> None:
        pass

    def pre_transform(self, keyword:str, words:List[str]) -> None:
        pass

    def using_none(self, script: str) -> None:
        pass


# Pre tracer class
class PreTracer(NullTracer):
    def pre_transform(self, keyword: str, words: List[str]) -> None:
        print(eliza_specific_join(words), "   :", keyword)


# String tracer class
class StringTracer(NullTracer):
    def __init__(self):
        self.trace_ = ""
        self.script_ = ""
        self.word_substitutions_ = ""

    def begin_response(self, words: List[str]) -> None:
        self.trace_ = ""
        self.script_ = ""
        self.word_substitutions_ = ""
        self.trace_ += "input: " + eliza_specific_join(words) + '\n'

    def limit(self, limit: int, built_in_msg: str) -> None:
        self.trace_ += "LIMIT: " + str(limit) + " (" + built_in_msg + ")\n"

    def discard_subclause(self, s: str) -> None:
        self.trace_ += "word substitutions made: " + ("<none>" if not self.word_substitutions_ else self.word_substitutions_) + '\n'
        self.trace_ += "no keywords found in subclause: " + s + '\n'
        self.word_substitutions_ = ""

    def word_substitution(self, word: str, substitute: str) -> None:
        if substitute != word:
            if self.word_substitutions_:
                self.word_substitutions_ += ", "
            self.word_substitutions_ += word + '/' + substitute

    def create_memory(self, s: str) -> None:
        self.trace_ += s

    def using_memory(self, s: str) -> None:
        self.trace_ += "LIMIT=4, so the response is the oldest unused memory\n"
        self.script_ += s

    def subclause_complete(self, subclause: str, keystack: List[str], rules: RuleMap) -> None:
        self.trace_ += "word substitutions made: " + ("<none>" if not self.word_substitutions_ else self.word_substitutions_) + '\n'
        if not keystack:
            if subclause:
                self.trace_ += "no keywords found in subclause: " + subclause + '\n'
        else:
            self.trace_ += "keyword found in subclause: " + subclause + '\n'
            self.trace_ += "keyword stack(precedence):"
            comma = False
            for keyword in keystack:
                self.trace_ += (", " if comma else " ") + keyword + "("
                rule = rules.get(keyword)
                if rule:
                    if rule.has_transformation():
                        self.trace_ += str(rule.precedence)
                    else:
                        self.trace_ += "<internal error: no transform associated with this keyword>"
                else:
                    self.trace_ += "<internal error: unknown keyword>"
                self.trace_ += ')'
                comma = True
            self.trace_ += '\n'

    def unknown_key(self, keyword: str, use_nomatch_msg: bool) -> None:
        self.trace_ += "ill-formed script: \"" + keyword + "\" is not a keyword\n"
        if use_nomatch_msg:
            self.trace_ += "response is the built-in NOMATCH[LIMIT] message\n"

    def decomp_failed(self, use_nomatch_msg: bool) -> None:
        self.trace_ += "ill-formed script? No decomposition rule matched input\n"
        if use_nomatch_msg:
            self.trace_ += "response is the built-in NOMATCH[LIMIT] message\n"

    def newkey_failed(self, response_source: str) -> None:
        self.trace_ += "keyword stack is empty; response is a " + response_source + " message\n"

    def transform(self, t: str, s: str) -> None:
        self.trace_ += t
        self.script_ += s

    def memory_stack(self, t: str) -> None:
        self.trace_ += t

    def using_none(self, s: str) -> None:
        self.trace_ += "response is the next remark from the NONE rule\n"
        self.script_ += s

    def text(self) -> str:
        return self.trace_

    def script(self) -> str:
        return self.script_

    def clear(self) -> None:
        self.trace_ = ""
        self.script_ = ""


class Script:
    """
        The script class is a structure for containing the rules and memory of an eliza instance.
    """
    def __init__(self):
        # ELIZA's opening remarks e.g. "HOW DO YOU DO.  PLEASE TELL ME YOUR PROBLEM"
        self.hello_message: List[str] = []
        # maps keywords -> transformation rules
        self.rules: Dict[str, RuleKeyword] = {}
        # the one and only special case MEMORY rule.
        self.mem_rule: RuleMemory = RuleMemory()
