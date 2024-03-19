from io import StringIO

import elizalogic.constant
from elizalogic.RuleKeyword import RuleKeyword
from elizalogic.RuleMemory import RuleMemory
from elizascript.token import Token
from elizascript.tokenizer import Tokenizer


class ElizaScriptReader:
    def __init__(self, script_file: StringIO):

        self.tokenizer = Tokenizer(script_file)
        self.script = None

        self.script.hello_message = self.rdlist()
        if self.tokenizer.peektok().symbol("START"):
            self.tokenizer.nexttok()  # skip over START, if present

        while self.read_rule():
            pass

        # Check if the script meets the minimum requirements
        if elizalogic.constant.SPECIAL_RULE_NONE not in self.script.rules:
            raise RuntimeError("Script error: no NONE rule specified; see Jan 1966 CACM page 41")
        if not self.script.mem_rule:
            raise RuntimeError("Script error: no MEMORY rule specified; see Jan 1966 CACM page 41")
        if self.script.mem_rule.keyword() not in self.script.rules:
            msg = f"Script error: MEMORY rule keyword '{self.script.mem_rule.keyword()}' "
            msg += "is not also a keyword in its own right; see Jan 1966 CACM page 41"
            raise RuntimeError(msg)

    def errormsg(self, msg):
        return f"Script error on line {self.tokenizer.line()}: {msg}"

    def rdlist(self, prior=True):
        s = []
        t = self.tokenizer.nexttok()
        if prior and not t.open():
            raise RuntimeError(self.errormsg("expected '('"))
        while not t.close():
            if t.symbol():
                s.append(t.value)
            elif t.number():
                s.append(t.value)
            elif t.open():
                sublist = []
                t = self.tokenizer.nexttok()
                while not t.close():
                    if not t.symbol():
                        raise RuntimeError(self.errormsg("expected symbol"))
                    if sublist:
                        sublist.append(' ')
                    sublist.append(t.value)
                    t = self.tokenizer.nexttok()
                s.append("(" + " ".join(sublist) + ")")
            else:
                raise RuntimeError(self.errormsg("expected ')'"))
            t = self.tokenizer.nexttok()
        return s

    def read_memory_rule(self):
        t = self.tokenizer.nexttok()
        if t.symbol("MEMORY"):
            t = self.tokenizer.nexttok()
            if not t.symbol():
                raise RuntimeError(self.errormsg("expected keyword to follow MEMORY"))
            if self.script.mem_rule:
                raise RuntimeError(self.errormsg("multiple MEMORY rules specified"))
            self.script.mem_rule = RuleMemory(t.value)

            for _ in range(RuleMemory.num_transformations):
                decomposition = []
                reassembly_rules = []

                if not self.tokenizer.nexttok().open():
                    raise RuntimeError(self.errormsg("expected '('"))
                for t in iter(self.tokenizer.nexttok, Token(Token.Typ.EOF)):
                    if t.symbol("="):
                        break
                    decomposition.append(t.value)
                if not decomposition:
                    raise RuntimeError(self.errormsg("expected 'decompose_terms = reassemble_terms'"))
                if not t.symbol("="):
                    raise RuntimeError(self.errormsg("expected '='"))

                reassembly = []
                for t in iter(self.tokenizer.nexttok, Token(Token.Typ.EOF)):
                    if t.close():
                        break
                    reassembly.append(t.value)
                if not reassembly:
                    raise RuntimeError(self.errormsg("expected 'decompose_terms = reassemble_terms'"))
                if not t.close():
                    raise RuntimeError(self.errormsg("expected ')'"))
                reassembly_rules.append(reassembly)

                self.script.mem_rule.add_transformation_rule(decomposition, reassembly_rules)

            if not self.tokenizer.nexttok().close():
                raise RuntimeError(self.errormsg("expected ')'"))
            return True
        return False

    def read_reassembly(self):
        if not self.tokenizer.nexttok().open():
            raise RuntimeError(self.errormsg("expected '('"))
        if not self.tokenizer.peektok().symbol("PRE"):
            return self.rdlist(False)

        # It's a PRE reassembly, e.g. (PRE (I ARE 3) (=YOU))
        self.tokenizer.nexttok()  # skip "PRE"
        pre = ["(", "PRE"]
        reconstruct = self.rdlist()
        reference = self.rdlist()
        if len(reference) != 2 or reference[0] != "=":
            raise RuntimeError(self.errormsg("expected '(=reference)' in PRE rule"))
        pre.extend(["(", *reconstruct, ")", "(", *reference, ")", ")", ])
        if not self.tokenizer.nexttok().close():
            raise RuntimeError(self.errormsg("expected ')'"))
        return pre

    def read_keyword_rule(self):
        keyword = ""
        keyword_substitution = ""
        precedence = 0
        tags = []
        transformation = []
        class_name = ""

        t = self.tokenizer.nexttok()
        if t.symbol():
            keyword = t.value
            if keyword == "NONE":
                keyword = elizalogic.constant.SPECIAL_RULE_NONE

            if keyword in self.script.rules:
                raise RuntimeError(f"keyword rule already specified for keyword '{keyword}'")

            if self.tokenizer.peektok().close():
                raise RuntimeError(f"keyword '{keyword}' has no associated body")

            for t in iter(self.tokenizer.nexttok, Token(Token.Typ.EOF)):
                if t.symbol("="):
                    t = self.tokenizer.nexttok()
                    if not t.symbol():
                        raise RuntimeError(self.errormsg("expected keyword"))
                    keyword_substitution = t.value
                elif t.number():
                    precedence = int(t.value)
                elif t.symbol("DLIST"):
                    tags = self.rdlist()
                elif t.open():
                    t = self.tokenizer.peektok()
                    if t.symbol("="):
                        self.tokenizer.nexttok()
                        t = self.tokenizer.nexttok()
                        if not t.symbol():
                            raise RuntimeError(self.errormsg("expected equivalence class name"))
                        class_name = t.value

                        if not self.tokenizer.nexttok().close():
                            raise RuntimeError(self.errormsg("expected ')'"))
                        if not self.tokenizer.peektok().close():
                            raise RuntimeError(self.errormsg("expected ')'"))
                    else:
                        trans = {"decomposition": self.rdlist()}
                        if not trans["decomposition"]:
                            raise RuntimeError(self.errormsg("decompose pattern cannot be empty"))
                        while self.tokenizer.peektok().open():
                            trans["reassembly"].append(self.read_reassembly())
                        transformation.append(trans)
                else:
                    raise RuntimeError(self.errormsg("malformed rule"))

            r = RuleKeyword(
                keyword, keyword_substitution, precedence, tags, class_name)
            for tr in transformation:
                r.add_transformation_rule(tr["decomposition"], tr["reassembly"])
            self.script.rules[keyword] = r

            return True
        return False

    def read_rule(self):
        t = self.tokenizer.nexttok()
        if t.eof():
            return False
        if not t.open():
            raise RuntimeError(self.errormsg("expected '('"))
        t = self.tokenizer.peektok()
        if t.close():
            self.tokenizer.nexttok()
            return True  # ignore empty rule list, if present
        if not t.symbol():
            raise RuntimeError(self.errormsg("expected keyword|MEMORY|NONE"))
        if t.value == "MEMORY":
            return self.read_memory_rule()
        return self.read_keyword_rule()
