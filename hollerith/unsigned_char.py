import hollerith.encoding
from hollerith import to_unsigned_int, to_unsigned


class UnsignedChar:
    def __init__(self, char, max_val=256):
        char = self._validate_init(char)
        self._value = self._constrain_int(char, max_val)

    def _constrain_int(self, n, max=256):
        if n < 0 or n >= max:
            return abs(n) % max
        return n

    def _validate_init(self, input):
        if isinstance(input, str):
            char = ord(input)
        elif isinstance(input, UnsignedChar):
            char = input.value
        elif isinstance(input, int):
            char = input
        else:
            raise TypeError("UnsignedChar must be initialized with an ASCII character, Unsigned Char, or integer.")
        return char

    @property
    def value(self):
        return self._value

    @property
    def char(self):
        return chr(self._value)

    def shift_left(self, n):
        return UnsignedChar(self.value << n)

    def binary_or(self, other):
        return UnsignedChar(self.value | UnsignedChar(other).value)

    def binary_and(self, other):
        return UnsignedChar(self.value & UnsignedChar(other).value)

    def __repr__(self):
        return f"UnsignedChar({self._value})"

    def __str__(self):
        return to_unsigned(self.char)

    def __int__(self):
        return to_unsigned_int(self._value)

    def __add__(self, other):
        if isinstance(other, str):
            return UnsignedChar((self._value + to_unsigned(other)))
        if isinstance(other, UnsignedChar):
            return UnsignedChar((self._value + other._value))
        elif isinstance(other, int):
            return UnsignedChar((self._value + other))
        else:
            raise TypeError("Unsupported operand type for +: UnsignedChar and " + type(other).__name__)

    def __sub__(self, other):
        if isinstance(other, str):
            return UnsignedChar((self._value - to_unsigned(other)))
        if isinstance(other, UnsignedChar):
            return UnsignedChar((self._value - other._value))
        elif isinstance(other, int):
            return UnsignedChar((self._value - other))
        else:
            raise TypeError("Unsupported operand type for -: UnsignedChar and " + type(other).__name__)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == to_unsigned(other)
        if isinstance(other, UnsignedChar):
            return self._value == other._value
        elif isinstance(other, int):
            return self._value == other
        else:
            return False


class HollerithChar(UnsignedChar):
    def __init__(self, char):
        if char is None:
            char = 0xff
        super().__init__(char, 64)
