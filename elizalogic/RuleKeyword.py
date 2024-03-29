from typing import List, Dict, Tuple

import elizalogic.constant
from elizalogic.RuleBase import RuleBase
from elizalogic import ElizaConstant
from elizalogic.transform import Transform
from elizalogic import match, join, reassemble


class RuleKeyword(RuleBase):
    def __init__(self, keyword: str, word_substitution: str, precedence: int,
                 tags: List[str], link_keyword: str):
        super().__init__(keyword, word_substitution, precedence)
        self.tags = tags
        self.link_keyword = link_keyword

    def dlist_tags(self) -> List[str]:
        return self.tags

    def has_transformation(self) -> bool:
        return bool(self.transformations) or bool(self.link_keyword)

    def apply_transformation(self, words: List[str], tags: ElizaConstant.TagMap, link_keyword: str) -> Tuple[str, List[str]]:
        self.trace_begin(words)
        constituents = []
        for rule in self.transformations:
            if match(tags, rule.decomposition, words, constituents):
                self.trace_decomp(rule.decomposition, constituents)

                reassembly_rule = rule.reassembly_rules[rule.next_reassembly_rule]
                self.trace_reassembly(reassembly_rule)

                # update the reassembly rule index so that they all get cycled through
                # rule->next_reassembly_rule++;
                # dif (rule->next_reassembly_rule == rule->reassembly_rules.size())
                # rule->next_reassembly_rule = 0
                rule.next_reassembly_rule = (rule.next_reassembly_rule + 1) % len(rule.reassembly_rules)

                if len(reassembly_rule) == 1 and reassembly_rule[0] == "NEWKEY":
                    return "newkey", words

                if len(reassembly_rule) == 2 and reassembly_rule[0] == '=':
                    self.link_keyword = reassembly_rule[1]
                    return "linkkey", words

                # is it the special-case reassembly rule (PRE (reassembly) (=reference))
                # (note: this is the only reassembly_rule that is still in a list)
                if reassembly_rule and reassembly_rule[0] == "(":
                    reassembly = reassembly_rule[3:-2]
                    _words = reassemble(reassembly, constituents)
                    self.link_keyword = reassembly_rule[-1]
                    return "linkkey", _words

                _words = reassemble(reassembly_rule, constituents)
                return "complete", _words

        if self.link_keyword:
            return "linkkey", words

        self.trace_nomatch()
        return "inapplicable", []

    def to_string(self) -> str:
        sexp = f"({'NONE' if self.keyword == ElizaConstant.SPECIAL_RULE_NONE else self.keyword}"

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
                    sexp += "\n        (" + ''.join(reassembly_rule) + ")"
            sexp += ")"

        if self.link_keyword:
            sexp += f"\n    (= {self.link_keyword})"

        sexp += ")\n"
        return sexp

    def trace_begin(self, words: List[str]) -> None:
        self.trace = ""
        self.trace += f"{elizalogic.ElizaConstant.TRACE_PREFIX}keyword: {self.keyword}\n"
        self.trace += f"{ElizaConstant.TRACE_PREFIX}input: {' '.join(words)}\n"

    def trace_nomatch(self) -> None:
        self.trace += f"{ElizaConstant.TRACE_PREFIX}ill-formed script? No decomposition rule matches\n"

    def trace_reference(self, ref: str) -> None:
        self.trace += f"{ElizaConstant.TRACE_PREFIX}reference to equivalence class: {ref}\n"

    def trace_decomp(self, d: List[str], constituents: List[str]) -> None:
        self.trace += f"{ElizaConstant.TRACE_PREFIX}matching decompose pattern: {' '.join(d)}\n"
        self.trace += f"{ElizaConstant.TRACE_PREFIX}decomposition parts: "
        for id_, c in enumerate(constituents, start=1):
            self.trace += f"{id_}:\"{c}\" "
        self.trace += "\n"

    def trace_reassembly(self, r: List[str]) -> None:
        self.trace += f"{ElizaConstant.TRACE_PREFIX}selected reassemble rule: {' '.join(r)}\n"
