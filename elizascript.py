import io
from typing import Dict
from typing import List, Any, Tuple

from constant import SPECIAL_RULE_NONE
from elizalogic import RuleKeyword, RuleMemory
from util import join


def _is_whitespace(ch):
    return ch <= 0x20 or ch == 0x7F or chr(ch).isspace()


def _is_newline(ch):
    return ch in (0x0A, 0x0B, 0x0C, 0x0D, '\n')


def _is_digit(ch):
    return chr(ch).isdigit()


def _check_if_not_symbol(ch):
    return ch in (ord('('), ord(')'), ord(';')) or _is_whitespace(ch)

class StringIOWithPeek(io.StringIO):
    def peek(self, size=1):
        current_position = self.tell()
        data = self.read(size)
        self.seek(current_position)
        return data


## SCRIPT: This class holds a parsed eliza profile, including a map of rules and a conversation memory.

class Script:

    def __init__(self):
        # ELIZA's opening remarks e.g. "HOW DO YOU DO.  PLEASE TELL ME YOUR PROBLEM"
        self.hello_message: List[str] = []
        # maps keywords -> transformation rules
        self.rules: Dict[str, RuleKeyword] = {}
        # the one and only special case MEMORY rule.
        self.mem_rule: RuleMemory = RuleMemory()

def script_to_string(s: Script):
    result = str()
    result += "(" + join(s.hello_message) + ")\n"
    for (k, v) in s.rules.items():
        result += v.to_string()
    result += s.mem_rule.to_string()
    return result


class Token:
    class Typ:
        EOF = 'eof'
        SYMBOL = 'symbol'
        NUMBER = 'number'
        OPEN_BRACKET = 'open_bracket'
        CLOSE_BRACKET = 'close_bracket'

    def __init__(self, t: str = Typ.EOF, value: str = ''):
        self.t = t
        self.value = value

    def is_symbol(self, v=None):
        if v:
            return self.t == self.Typ.SYMBOL and self.value == v
        return self.t == self.Typ.SYMBOL

    def is_number(self):
        return self.t == self.Typ.NUMBER

    def is_open(self):
        return self.t == self.Typ.OPEN_BRACKET

    def is_close(self):
        return self.t == self.Typ.CLOSE_BRACKET

    def is_eof(self):
        return self.t == self.Typ.EOF

    def __eq__(self, other):
        return isinstance(other, Token) and self.t == other.t and self.value == other.value





class Tokenizer:
    def __init__(self, script_stream: StringIOWithPeek):
        self.stream: StringIOWithPeek = script_stream
        self.line_number: int = 1

    def peektok(self) -> Token:
        pos = self.stream.tell()
        mline = self.line_number
        ch = self.stream.peek(1)
        if not ch:
            return Token(Token.Typ.EOF)

        tok = self._readtok()
        pos2 = self.stream.tell()
        ch2 = self.stream.peek(1)

        ret = pos2 - (pos2 - pos)
        self.stream.seek(ret, io.SEEK_SET)
        self.line_number = mline
        ch2 = self.stream.peek(1)
        return tok

    def nexttok(self) -> Token:
        ch = self.stream.peek(1)
        if not ch:
            return Token(Token.Typ.EOF)
        return self._readtok()

    def line(self):
        return self.line_number

    def _consume_newline(self, ch):
        while ch.isspace() or ch == '\n':
            if ch == '\n':
                self.line_number += 1
            ch = self.stream.read(1)
        return ch
    def _readtok(self) -> Token:
        ch = self.stream.read(1)
        ch = self._consume_newline(ch)

        while(True):

            if ch == '' or ch is None:
                return Token(Token.Typ.EOF)

            if ch == ';':
                while not _is_newline(ch):
                    ch = self.stream.read(1)
                    if ch is None:
                        return Token(Token.Typ.EOF)
                ch = self._consume_newline(ch)
            else:
                break

        if ch == '(':
            return Token(Token.Typ.OPEN_BRACKET)
        if ch == ')':
            return Token(Token.Typ.CLOSE_BRACKET)
        if ch == '=':
            return Token(Token.Typ.SYMBOL, "=")
        if ch.isdigit():
            value = str(ch)
            while True:
                peek_ch = self.stream.peek(1)
                if peek_ch and peek_ch.isdigit():
                    value += peek_ch
                    self.stream.read(1)
                else:
                    break
            return Token(Token.Typ.NUMBER, value)
        value = ch

        while self.stream.peek(1) and not _check_if_not_symbol(ord(self.stream.peek(1))) and self.stream.peek(1) != '=':
            value += self.stream.read(1)
        return Token(Token.Typ.SYMBOL, value)





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
        if SPECIAL_RULE_NONE not in self.script.rules:
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
                keyword = SPECIAL_RULE_NONE

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

