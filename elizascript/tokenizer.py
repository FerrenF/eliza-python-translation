import io

from elizascript.token import Token


class Tokenizer:


    #this is just good enough to divide the ELIZA script file format
    #into tokens useful to eliza_script_reader
    def __init__(self, script_stream: io.StringIO):
        #script_file, stream_type:str='textfile'):
        self.stream: io.StringIO = script_stream
        self.token = None
        self.got_token = False
        self.buf_len = 512
        self.buf = bytearray(self.buf_len)
        self.buf_data = 0
        self.buf_ptr = 0
        self.line_number = 1

    def peektok(self):
        if self.got_token:
            return self.token
        self.got_token = True
        return self._readtok()


    def nexttok(self):
        if self.got_token:
            self.got_token = False
            return self.token
        return self._readtok()


    def line(self):
        return self.line_number


    def _readtok(self):
        while True:
            ch = self._nextch()
            while ch and self._is_whitespace(ch):
                if self._is_newline(ch):
                    self._consume_newline(ch)
                ch = self._nextch()

            if not ch:
                return Token(Token.Typ.EOF)

            if ch == ord('('):
                return Token(Token.Typ.OPEN_BRACKET)

            if ch == ord(')'):
                return Token(Token.Typ.CLOSE_BRACKET)

            if ch == ord('='):
                return Token(Token.Typ.SYMBOL, "=")

            if self._is_digit(ch):
                value = chr(ch)
                while True:
                    peek_ch = self._peekch()
                    if peek_ch and self._is_digit(peek_ch):
                        value += chr(peek_ch)
                        self._nextch()
                    else:
                        break
                return Token(Token.Typ.NUMBER, value)

            # anything else is a symbol
            value = chr(ch)
            while True:
                peek_ch = self._peekch()
                if peek_ch and not self._non_symbol(peek_ch) and peek_ch != ord('='):
                    value += chr(peek_ch)
                    self._nextch()
                else:
                    break
            return Token(Token.Typ.SYMBOL, value)

    def _nextch(self):
        if self._peekch():
            self.buf_ptr += 1
            return self.buf[self.buf_ptr - 1]
        return None

    def _peekch(self):
        if self.buf_ptr == self.buf_data:
            self._refilbuf()
            if self.buf_ptr == self.buf_data:
                return None
        return self.buf[self.buf_ptr]

    def _refilbuf(self):
        self.buf_ptr = self.buf_data = 0
        if not self.stream.closed:
            data = self.stream.read(self.buf_len)
            self.buf[:len(data)] = data
            self.buf_data = len(data)

    def _is_whitespace(self, ch):
        return ch <= 0x20 or ch == 0x7F

    def _is_newline(self, ch):
        return ch in (0x0A, 0x0B, 0x0C, 0x0D)

    def _consume_newline(self, ch):
        if ch == 0x0D and self._peekch() == 0x0A:
            self._nextch()
        self.line_number += 1

    def _non_symbol(self, ch):
        return ch in (ord('('), ord(')'), ord(';')) or self._is_whitespace(ch)

    def _is_digit(self, ch):
        return 48 <= ch <= 57