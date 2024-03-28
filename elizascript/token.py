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
