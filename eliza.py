from typing import List

from elizaconstant import SPECIAL_RULE_NONE
from elizalogic import eliza_specific_join, NullTracer
from elizaencoding import filter_bcd
from elizautil import collect_tags, get_rule, split_input


class Eliza:
    nomatch_msgs_: List[str] = [
        "PLEASE CONTINUE",
        "HMMM",
        "GO ON , PLEASE",
        "I SEE"
    ]

    def __init__(self, script):

        self.greetings = script.hello_message
        self.rules = script.rules
        self.mem_rule = script.mem_rule
        self.tags = collect_tags(self.rules)
        self.limit = 1  # JW's "a certain counting mechanism," cycles through 1..4, then back to 1
        self.use_limit = True
        self.punctuation = ""
        self.set_delimiters([",", ".", "BUT"])
        self.on_newkey_fail_use_none = True
        self.use_nomatch_msgs = True

        self.null_tracer = NullTracer()
        self.trace = self.null_tracer

    def set_use_nomatch_msgs(self, flag: bool):
        self.use_nomatch_msgs = flag

    def set_on_newkey_fail_use_none(self, flag: bool):
        self.on_newkey_fail_use_none = flag

    def set_delimiters(self, delims: List[str]):
        self.delimiters = delims
        self.punctuation = ""
        bcd_punctuation = "='+.)-$*/,("

        for d in delims:
            if len(d) == 1 and d in bcd_punctuation:
                self.punctuation += d

    # provide the user with a window into ELIZA's thought processes(!)
    def set_tracer(self, tracer):
        self.trace = tracer if tracer else self.null_tracer

    def get_tracer_text(self) -> str:
        """
        Returns tracer text if there is any, otherwise returns an error string.
        :return: str
        """
        if not hasattr(self.trace, "text") or self.trace is NullTracer:
            return "Null Trace"
        return self.trace.text()

    def response_list(self, input_str) -> List[str]:

        input_str = filter_bcd(input_str)
        # for simplicity, convert the given input string to a list of uppercase words
        # e.g. "Hello, world!" -> ("HELLO" "," "WORLD" ".")

        words = split_input(input_str, self.punctuation)
        self.trace.begin_response(words)

        # J W's "a certain counting mechanism" is updated for each response
        self.limit = (self.limit % 4) + 1
        self.trace.limit(self.limit, self._get_nomatch_msg())

        keystack: List[str] = []
        top_rank = 0

        idx = 0
        while idx < len(words) and words[idx]:
            word = words[idx]
            if self._is_delimiter(word):
                if len(keystack) == 0:
                    self.trace.discard_subclause(word)
                    if self.mem_rule.memory_exists() and (not self.use_limit or self.limit == 4):
                        self.trace.using_memory(self.mem_rule.to_string())
                    else:
                        self.trace.discard_subclause(' '.join(words[:idx]))
                    # discard to the left
                    words = words[idx + 1:]
                    idx = 0
                    continue
                else:
                    # discard to the right
                    words = words[:idx]
                    break

            rule = get_rule(self.rules, word, throw=False)

            if rule and len(rule.keyword):
                if rule.has_transformation():
                    if rule.precedence > top_rank:
                        # // *word is a keyword with precedence higher than the highest
                        # // keyword found previously: it goes top of the keystack [page 39 (d)]
                        keystack.insert(0, word)
                        top_rank = rule.precedence
                    else:
                        # // *word is a keyword with precedence lower than the highest
                        # // keyword found previously: it goes bottom of the keystack
                        keystack.append(word)

                substitute = rule.word_substitute(word)
                self.trace.word_substitution(word, substitute)
                words[idx] = substitute

            idx += 1

        w = ' '.join(words or [])
        self.trace.subclause_complete(w, keystack, self.rules)
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
                    return [self.mem_rule.recall_memory()]

            # the keystack contains all keywords that occur in the given 'input';
            # apply transformation associated with the top keyword [page 39 (d)]
        while len(keystack):
            top_keyword = keystack.pop(0)
            self.trace.pre_transform(top_keyword, words)

            rule = self.rules.get(top_keyword, None)
            if not rule:  # if (r == rules_.end())
                if self.use_nomatch_msgs:
                    self.trace.unknown_key(top_keyword, True)
                    return [self._get_nomatch_msg()]

                # e.g. could happen if a rule links to a non-existent keyword
                self.trace.unknown_key(top_keyword, False)
                break

            # try to lay down a memory for future use
            self.mem_rule.create_memory(top_keyword, words, self.tags)
            self.trace.create_memory(self.mem_rule.trace)

            action, words, link_keyword = rule.apply_transformation(words, self.tags, [])
            self.trace.transform(rule.trace, rule.to_string())

            if action == "complete":
                return words

            if action == "inapplicable":
                # no decomposition rule matched the input words; script error
                self.trace.decomp_failed(self.use_nomatch_msgs)
                if self.use_nomatch_msgs:
                    self.trace.decomp_failed(self.use_nomatch_msgs)
                    return [self._get_nomatch_msg()]
                break

            assert action == "linkkey" or action == "newkey"

            if action == "linkkey":
                # rule links to another; loop
                keystack.insert(0, link_keyword)

            elif not keystack or not len(keystack):
                # newkey means try next highest keyword, but keystack is empty.
                # The 1966 CACM ELIZA paper, page 41, implies in this situation
                # a NONE message is used. The conversations in the Quarton pilot
                # study suggests that a built-in message is used.

                if self.on_newkey_fail_use_none and self.use_nomatch_msgs:
                    self.trace.newkey_failed("built-in nomatch")
                    return [self._get_nomatch_msg()]
                else:
                    self.trace.newkey_failed("NONE")
                    break

        none_rule = self.rules.get(SPECIAL_RULE_NONE)
        discard = ""
        none_status, none_rule, none_keyword = none_rule.apply_transformation(words, self.tags, discard)
        self.trace.using_none(eliza_specific_join(none_rule))
        return none_rule

    def response(self, input_str: str) -> str:
        return eliza_specific_join(self.response_list(input_str))

    def _is_delimiter(self, word: str) -> bool:
        return word in self.delimiters

    def _handle_empty_keystack(self, words: List[str], idx: int) -> None:
        if self.mem_rule.memory_exists() and (not self.use_limit or self.limit == 4):
            self.trace.using_memory(self.mem_rule.to_string())
        else:
            self.trace.discard_subclause(' '.join(words[:idx]))

    def get_greeting(self) -> str:
        return eliza_specific_join(self.greetings) or "Hello."

    def _get_nomatch_msg(self) -> str:
        ind = self.limit - 1 % len(self.nomatch_msgs_)
        return Eliza.nomatch_msgs_[ind]

