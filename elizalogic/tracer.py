# Base class for tracer
from abc import abstractmethod, ABC
from typing import List

from elizalogic import ElizaConstant
from elizalogic import join


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
    def subclause_complete(self, subclause: str, keystack: List[str], rules: ElizaConstant.RuleMap) -> None:
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

    def subclause_complete(self, subclause: str, keystack: List[str], rules: ElizaConstant.RuleMap) -> None:
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
        print(join(words), "   :", keyword)

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
        self.trace_ += "input: " + join(words) + '\n'

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

    def subclause_complete(self, subclause: str, keystack: List[str], rules: ElizaConstant.RuleMap) -> None:
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