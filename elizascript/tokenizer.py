import io

from elizascript import StringIOWithPeek
from elizascript.token import Token


def _is_whitespace(ch):
    return ch <= 0x20 or ch == 0x7F or chr(ch).isspace()


def _is_newline(ch):
    return ch in (0x0A, 0x0B, 0x0C, 0x0D, '\n')


def _is_digit(ch):
    return chr(ch).isdigit()


def _check_if_not_symbol(ch):
    return ch in (ord('('), ord(')'), ord(';')) or _is_whitespace(ch)



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
            value = ch
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

# class Tokenizer:
#
#     #this is just good enough to divide the ELIZA script file format
#     #into tokens useful to eliza_script_reader
#
#
#     # Changes:
#     # 1. This class needs a StringIO object. How it gets one is up to the external application.
#     def __init__(self, script_stream: io.StringIO):
#         self.stream: io.StringIO = script_stream
#         self.token = None
#         self.got_token = False
#         self.buf_len = 512
#         self.buf = bytearray(self.buf_len)
#         self.buf_data = 0
#         self.buf_ptr = 0
#         self.line_number = 1
#
#     def peektok(self)->Token:
#         if self.got_token:
#             return self.token
#         self.got_token = True
#         return self._readtok()
#
#
#     def nexttok(self)-> Token:
#         if self.got_token:
#             self.got_token = False
#             if self.token:
#                 return self.token
#         return self._readtok()
#
#
#     def line(self):
#         return self.line_number
#
#
#     def _readtok(self) -> Token:
#         while _is_whitespace(self.buf[self.buf_ptr]):
#             self._nextch()
#             ch = self.buf[self.buf_ptr]
#             if _is_newline(ch):
#                 self._consume_newline(ch)
#
#
#         ch = self.buf[self.buf_ptr]
#         if not ch:
#             return Token(Token.Typ.EOF)
#
#         elif ch == ord('('):
#             return Token(Token.Typ.OPEN_BRACKET)
#
#         elif ch == ord(')'):
#             return Token(Token.Typ.CLOSE_BRACKET)
#
#         elif ch == ord('='):
#             return Token(Token.Typ.SYMBOL, "=")
#
#         elif ch == ord(';'):
#             while True:
#                 ch = self._nextch()
#                 if not ch or _is_newline(ch):
#                     break
#
#         value = chr(ch)
#         if _is_digit(ch):
#             while True:
#                 peek_ch = self._peekch()
#                 if (peek_ch is not None) and _is_digit(peek_ch):
#                     value += chr(peek_ch)
#                     self._nextch()
#                 else:
#                     break
#             return Token(Token.Typ.NUMBER, value)
#         else:
#             # anything else is a symbol
#             while True:
#                 peek_ch = self._peekch()
#                 if (peek_ch is not None) and (not _check_if_symbol(peek_ch)) and (peek_ch != ord('=')):
#                     value += chr(peek_ch)
#                     ch = self._nextch()
#                 else:
#                     break
#         return Token(Token.Typ.SYMBOL, value)
#
#
#     def _nextch(self):
#         """
#         Increments the position in the stack.
#         :return: the character that is 'bumped' from the stack.
#         """
#         if self._peekch() is not None:
#             self.buf_ptr += 1
#             return True
#         return False
#
#
#     def _peekch(self):
#         if self.buf_ptr == self.buf_data:
#             self._refilbuf()
#             if self.buf_ptr == self.buf_data:
#                 return None
#         return self.buf[self.buf_ptr]
#
#
#     def _refilbuf(self):
#         self.buf_ptr = self.buf_data = 0
#         if not self.stream.closed:
#             data = self.stream.read(self.buf_len)
#             b: bytearray = bytearray()
#             b.extend(map(ord, data))
#             self.buf[:len(data)] = b
#             self.buf_data = len(data)
#
#
#
#
#     def _consume_newline(self, ch):
#         if ch == 0x0D and self._peekch() == 0x0A:
#             self._nextch()
#         self.line_number += 1
#
#
#
