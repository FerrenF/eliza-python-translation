import argparse
import ctypes
import sys
import time
from typing import Any
from typing import Dict, Optional
from typing import List, Tuple, Dict

import elizalogic.constant
from elizalogic.RuleMemory import RuleMemory
from elizalogic import RuleMap, TagMap
from elizalogic.tracer import NullTracer
from elizalogic.util import split
from hollerith.encoding import filter_bcd


# this should be moved into the 'eliza' module


class Eliza:

    nomatch_msgs_:List[str] = {
    "PLEASE CONTINUE",
    "HMMM",
    "GO ON , PLEASE",
    "I SEE"
}
    def __init__(self, rules: RuleMap, mem_rule: RuleMemory):
        self.rules = rules
        self.mem_rule = mem_rule
        self.tags = elizalogic.util.collect_tags(rules)
        self.limit = 1  # JW's "a certain counting mechanism," cycles through 1..4, then back to 1
        self.use_limit = True
        self.delimiters = [",", ".", "BUT"]
        self.punctuation = ""


        #  In the 1966 CACM ELIZA paper on page 41 Weizenbaum says
        #
        # "A serious problem which remains to be discussed is the reaction of
        # the system in case no keywords remain to serve as transformation
        # triggers. This can arise either in case the keystack is empty when
        # NEWKEY is invoked or when the input text contained no keywords
        # initially.
        # "The simplest mechanism supplied is in the form of the special
        # reserved keyword "NONE" which must be part of any script."
        #
        # However, the McGuire, Lorch, Quarton study conversations show that
        # if the keystack is empty when NEWKEY is invoked the response is a
        # nomatch message, not a NONE message.
        self.on_newkey_fail_use_none = True


        # true use built-in error msgs (default); false use NONE messages instead
        # (Weizenbaum's ELIZA used built-in error messages. The option to use
        # NONE messages instead is provided for attempts to reproduce conversations
        # with some non-Weizenbaum ELIZAs.)
        self.use_nomatch_msgs = True


        self.null_tracer = NullTracer()
        self.trace = self.null_tracer

     # true use built-in error msgs (default); false use NONE messages instead
     # (Weizenbaum's ELIZA used built-in error messages. The option to use
     # NONE messages instead is provided for attempts to reproduce conversations
     # with some non-Weizenbaum ELIZAs.)
    def set_use_nomatch_msgs(self, flag: bool):
        self.use_nomatch_msgs = flag

    def set_on_newkey_fail_use_none(self, flag: bool):
        self.on_newkey_fail_use_none = flag

    def set_delimiters(self, delims: List[str]):
        self.delimiters = delims
        bcd_punctuation = "='+.)-$*/,("
        self.punctuation = "".join(d[0] for d in delims if len(d) == 1 and d[0] in bcd_punctuation)

    # provide the user with a window into ELIZA's thought processes(!)
    def set_tracer(self, tracer):
        self.trace = tracer if tracer else self.null_tracer

    def response(self, input_str: str) -> str:

        # for simplicity, convert the given input string to a list of uppercase words
        # e.g. "Hello, world!" -> ("HELLO" "," "WORLD" ".")

        words = self._preprocess_input(input_str)
        self.trace.begin_response(words)

        # J W's "a certain counting mechanism" is updated for each response
        self.limit = self.limit % 4 + 1
        self.trace.limit(self.limit, self._get_nomatch_msg())


        keystack: List[str] = []
        top_rank = 0

        for idx, word in enumerate(words):
            if self._is_delimiter(word):
                if len(keystack) == 0:
                    self.trace.discard_subclause(word)
                    self._handle_empty_keystack(words, idx)
                    continue
                else:
                    words = words.remove(word)
                    break

            rule = self.rules.get(word)
            if rule:

                if rule.has_transformation():
                    if rule.precedence > top_rank:
                        keystack.insert(0, word)
                        top_rank = rule.precedence
                    else:
                        keystack.append(word)

            substitute = rule.word_substitute(word)
            self.trace.word_substitution(word, substitute)
            words[idx] = substitute

        self.trace.subclause_complete(' '.join(words), keystack, self.rules)
        self.mem_rule.clear_trace()
        self.trace.memory_stack(self.mem_rule.trace_memory_stack())

        if not keystack:
                # a text without keywords; can we recall a MEMORY ? [page 41 (f)]
                # JW's 1966 CACM paper refers to this decision as "a certain counting
                # mechanism is in a particular state." The ELIZA code shows that the
                # memory is recalled only when LIMIT has the value 4

            if not self.use_limit or self.limit == 4:
                if self.mem_rule.memory_exists():
                    self.trace.using_memory(self.mem_rule.to_string())
                    return self.mem_rule.recall_memory()

            # the keystack contains all keywords that occur in the given 'input';
            # apply transformation associated with the top keyword [page 39 (d)]
        while keystack:
            top_keyword = keystack.pop(0)
            self.trace.pre_transform(top_keyword, words)
            rule = self.rules.get(top_keyword)
            if not rule:
                if self.use_nomatch_msgs:
                    self.trace.unknown_key(top_keyword, True)
                    return self._get_nomatch_msg()

                #e.g. could happen if a rule links to a non-existent keyword
                self.trace.unknown_key(top_keyword, False)
                break

            # try to lay down a memory for future use
            self.mem_rule.create_memory(top_keyword, words, self.tags)
            self.trace.create_memory(self.mem_rule.trace())

            link_keyword = ""
            action = rule.apply_transformation(words, self.tags, link_keyword)
            self.trace.transform(rule.trace(), rule.to_string())

            if action == "complete":
                return ' '.join(words)

            if action == "inapplicable":
                if self.use_nomatch_msgs:
                    self.trace.decomp_failed(True)
                    return self._get_nomatch_msg()
                else:
                    self.trace.decomp_failed(False)
                    break

            assert action == "linkkey" or action == "newkey"

            if action == "linkkey":
                keystack.insert(0, link_keyword)

            elif not keystack:
                 # newkey means try next highest keyword, but keystack is empty.
                 # The 1966 CACM ELIZA paper, page 41, implies in this situation
                 # a NONE message is used. The conversations in the Quarton pilot
                 # study suggests that a built-in message is used.

                if self.on_newkey_fail_use_none and self.use_nomatch_msgs:
                    self.trace.newkey_failed("built-in nomatch")
                    return self._get_nomatch_msg()
                else:
                    self.trace.newkey_failed("NONE")
                    break

        none_rule = self.rules.get(elizalogic.SPECIAL_RULE_NONE)
        discard = ""
        none_rule.apply_transformation(words, self.tags, discard)
        self.trace.using_none(none_rule.to_string())
        return ' '.join(words)

    def _preprocess_input(self, input_str: str) -> List[str]:
        input_str = filter_bcd(input_str)
        return split(input_str, self.punctuation)

    def _is_delimiter(self, word: str) -> bool:
        return word in self.delimiters

    def _handle_empty_keystack(self, words: List[str], idx: int) -> None:
        if self.mem_rule.memory_exists() and (not self.use_limit or self.limit == 4):
            self.trace.using_memory(self.mem_rule.to_string())
        else:
            self.trace.discard_subclause(' '.join(words[:idx]))

    def _get_nomatch_msg(self) -> str:
        return Eliza.nomatch_msgs_[self.limit - 1]

