from io import StringIO
from typing import List, Any, Tuple

import elizalogic.constant
from elizalogic.RuleKeyword import RuleKeyword
from elizalogic.RuleMemory import RuleMemory
from elizalogic.transform import Transform
from elizascript import StringIOWithPeek
from elizascript.script import Script
from elizascript.token import Token
from elizascript.tokenizer import Tokenizer



class ElizaScriptReader:

    @staticmethod
    def read_script(stream: Any) -> Tuple[str, Script]:
        if isinstance(stream, str):
            return ElizaScriptReader.read_script(StringIOWithPeek(stream))

        elif isinstance(stream, StringIOWithPeek):
            try:
                reader: ElizaScriptReader = ElizaScriptReader(stream)
                return "success", reader.script
            except RuntimeError as e:
                raise e

        else:
            raise TypeError("Invalid script type. NEED: str or IOStream")


    def __init__(self, script_file: StringIOWithPeek):

        self.tokenizer = Tokenizer(script_file)
        self.script: Script = Script()
        self.script.hello_message = self.rdlist()
        if self.tokenizer.peektok().is_symbol("START"):
            self.tokenizer.nexttok()  # skip over START, if present

        # Begin reading rules until we can't.
        while self.read_rule():

            pass

        # Check if the script meets the minimum requirements
        if elizalogic.ElizaConstant.SPECIAL_RULE_NONE not in self.script.rules:
            raise RuntimeError("Script error: no NONE rule specified; see Jan 1966 CACM page 41")
        if not self.script.mem_rule.is_valid():
            raise RuntimeError("Script error: no MEMORY rule specified; see Jan 1966 CACM page 41")
        if self.script.mem_rule.keyword not in self.script.rules:
            msg = f"Script error: MEMORY rule keyword '{self.script.mem_rule.keyword}' "
            msg += " `'` is not also a keyword in its own right; see Jan 1966 CACM page 41"
            raise RuntimeError(msg)


    def errormsg(self, msg):
        return f"Script error on line {self.tokenizer.line()}: {msg}"


    # // in the following comments, @ = position in symbol stream on function entry
    # // return words between opening and closing brackets
    # // if prior is true nexttok() should be the opening bracket, e.g. @(WORD WORD 0 WORD)
    # // if prior is false nexttok() should be the first symbol following the
    # // opening bracket, e.g. (@WORD WORD 0 WORD)
    def rdlist(self, prior=True) -> List[str]:
        s: List[str] = []
        t: Token = self.tokenizer.nexttok()
        if prior:
            if not t.is_open():
                raise RuntimeError(self.errormsg("expected '('"))
            t = self.tokenizer.nexttok()
        while not t.is_close():
            if t.is_symbol():
                s.append(t.value)
            elif t.is_number():
                s.append(t.value)
            elif t.is_open():
                sublist = str()
                t = self.tokenizer.nexttok()
                while not t.is_close():
                    if not t.is_symbol():
                        raise RuntimeError(self.errormsg("expected symbol"))
                    if len(sublist) > 0:
                        sublist += ' '
                    sublist += t.value
                    t = self.tokenizer.nexttok()

                s.append("(" + sublist + ")")
            else:
                raise RuntimeError(self.errormsg("expected ')'"))
            t = self.tokenizer.nexttok()
        return s


    # /* e.g.
    #     (@MEMORY MY
    #         (0 YOUR 0 = LETS DISCUSS FURTHER WHY YOUR 3)
    #         (0 YOUR 0 = EARLIER YOU SAID YOUR 3)
    #         (0 YOUR 0 = BUT YOUR 3)
    #         (0 YOUR 0 = DOES THAT HAVE ANYTHING TO DO WITH THE FACT THAT YOUR 3))
    # */
    def read_memory_rule(self):
        t: Token = self.tokenizer.nexttok()
        if t.is_symbol("MEMORY"):
            t = self.tokenizer.nexttok()
            if not t.is_symbol():
                raise RuntimeError(self.errormsg("expected keyword to follow MEMORY"))
            if self.script.mem_rule.is_valid():
                raise RuntimeError(self.errormsg("multiple MEMORY rules specified"))
            self.script.mem_rule = RuleMemory(t.value)

            for _ in range(RuleMemory.num_transformations):
                decomposition: List[str] = []
                reassembly_rules: List[List[str]] = []

                if not self.tokenizer.nexttok().is_open():
                    raise RuntimeError(self.errormsg("expected '('"))
                for t in iter(self.tokenizer.nexttok, Token(Token.Typ.EOF)):
                    if t.is_symbol("="):
                        break
                    decomposition.append(t.value)
                if not decomposition:
                    raise RuntimeError(self.errormsg("expected 'decompose_terms = reassemble_terms'"))
                if not t.is_symbol("="):
                    raise RuntimeError(self.errormsg("expected '='"))

                reassembly: List[str] = []
                for t in iter(self.tokenizer.nexttok, Token(Token.Typ.EOF)):
                    if t.is_close():
                        break
                    reassembly.append(t.value)
                if not reassembly:
                    raise RuntimeError(self.errormsg("expected 'decompose_terms = reassemble_terms'"))
                if not t.is_close():
                    raise RuntimeError(self.errormsg("expected ')'"))
                reassembly_rules.append(reassembly)

                self.script.mem_rule.add_transformation_rule(decomposition, reassembly_rules)

            if not self.tokenizer.nexttok().is_close():
                raise RuntimeError(self.errormsg("expected ')'"))
            return True

        return False


    def read_reassembly(self) -> List[List[str]]:

        if not self.tokenizer.nexttok().is_open():
            raise RuntimeError(self.errormsg("expected '('"))
        if not self.tokenizer.peektok().is_symbol("PRE"):
            return [self.rdlist(False)]

        # It's a PRE reassembly, e.g. (PRE (I ARE 3) (=YOU))
        self.tokenizer.nexttok()  # skip "PRE"
        pre: List[str] = ["(", "PRE"]
        reconstruct = self.rdlist()
        reference = self.rdlist()
        if len(reference) != 2 or reference[0] != "=":
            raise RuntimeError(self.errormsg("expected '(=reference)' in PRE rule"))
        pre.extend(["(", *reconstruct, ")", "(", *reference, ")", ")", ])
        if not self.tokenizer.nexttok().is_close():
            raise RuntimeError(self.errormsg("expected ')'"))
        return [pre]

    def read_keyword_rule(self):
        keyword = ""
        keyword_substitution = ""
        precedence = 0
        tags: List[str] = []

        transformation = (List[str], List[List[str]])
        transform: List[transformation] = []
        class_name = ""

        t: Token = self.tokenizer.nexttok()
        if t.is_symbol():
            keyword = t.value
            if keyword == "NONE":
                keyword = elizalogic.ElizaConstant.SPECIAL_RULE_NONE

            if keyword in self.script.rules:
                raise RuntimeError(f"keyword rule already specified for keyword '{keyword}'")

            t = self.tokenizer.peektok()
            if t.is_close():
                raise RuntimeError(f"keyword '{keyword}' has no associated body")

            t = self.tokenizer.nexttok()
            while not t.is_close():
                if t.is_symbol("="):
                    t = self.tokenizer.nexttok()
                    if not t.is_symbol():
                        raise RuntimeError(self.errormsg("expected keyword"))
                    keyword_substitution = t.value
                elif t.is_number():
                    precedence = int(t.value)
                elif t.is_symbol("DLIST"):
                    tags = self.rdlist()
                elif t.is_open():
                    # // a transformation rule
                    t = self.tokenizer.peektok()
                    if t.is_symbol("="):
                        # // a reference
                        t = self.tokenizer.nexttok()
                        t = self.tokenizer.nexttok()
                        if not t.is_symbol():
                            raise RuntimeError(self.errormsg("expected equivalence class name"))
                        class_name = t.value

                        pk = self.tokenizer.nexttok()
                        if not pk.is_close():
                            raise RuntimeError(self.errormsg("expected ')'"))
                        # redundant
                        pk = self.tokenizer.peektok()
                        if not pk.is_close():
                            raise RuntimeError(self.errormsg("expected ')'"))
                    else:
                        # // a decompose/reassemble transformation

                        decomp_list = self.rdlist()

                        if not decomp_list:
                            raise RuntimeError(self.errormsg("decompose pattern cannot be empty"))

                        assembly_list: List[List[str]] = self.read_reassembly()
                        while self.tokenizer.peektok().is_open():
                            assembly_list.append(self.read_reassembly()[0])

                        pk = self.tokenizer.nexttok()
                        if not pk.is_close():
                            raise RuntimeError(self.errormsg("expected ')'"))

                        transform.append((decomp_list, assembly_list))
                else:
                    raise RuntimeError(self.errormsg("malformed rule"))

                t = self.tokenizer.nexttok()

            r = RuleKeyword(
                keyword, keyword_substitution, precedence, tags, class_name)

            for tr in transform:
                r.add_transformation_rule(tr[0], tr[1])

            self.script.rules[keyword] = r
            return True
        return False

    # // read one rule of any type; return false => end of file reached
    def read_rule(self) -> bool:
        t: Token = self.tokenizer.nexttok()
        if t.is_eof():
            return False
        if not t.is_open():
            raise RuntimeError(self.errormsg("expected '('"))

        t = self.tokenizer.peektok()
        if t.is_close():
            self.tokenizer.nexttok()
            return True  # ignore empty rule list, if present

        if not t.is_symbol():
            raise RuntimeError(self.errormsg("expected keyword|MEMORY|NONE"))

        if t.value == "MEMORY":
            return self.read_memory_rule()

        return self.read_keyword_rule()
