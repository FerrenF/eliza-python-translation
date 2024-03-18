# Constants
hollerith_undefined = 0xFF  # Must be > 63

# "The 7090 BCD character codes are given in the accompanying table.
#       Six bits are used for each character. [...] The code is generally
#       termed binary-coded-decimal or BCD. For compactness, the codes are
#       generally expressed as 2-digit octal numbers, as in the table. The
#       term Hollerith is used synonomously with BCD." [1]
#
#       The following array is derived from the above mentioned table, with
#       one exception: BCD code 14 (octal) is a single quote (prime), not a
#       double quote. See [2].
#
#       The Hollerith code is the table offset. 0 means unused code.
#
#       [1] Philip M. Sherman
#           Programming and Coding the IBM 709-7090-7094 Computers
#           John Wiley and Sons, 1963
#           Page 62
#       [2] University of Michigan Executive System for the IBM 7090 Computer
#           September 1964
#           In section THE UNIVERSITY OF MICHIGAN MONITOR
#           APPENDIX 2, page 30, TABLE OF BCD--OCTAL EQUIVALENTS
#           (Available online from Google Books. Search for PRIME.)

hollerith_encoding = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', None, '=', '\'', None, None, None,
    '+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', None, '.', ')', None, None, None,
    '-', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', None, '$', '*', None, None, None,
    ' ', '/', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', None, ',', '(', None, None, None
]

# Conversion table from ASCII to BCD
to_bcd = [hollerith_undefined] * 256
for c in range(64):
    if hollerith_encoding[c]:
        to_bcd[ord(hollerith_encoding[c])] = c


def hollerith_defined(c):
    return to_bcd[ord(c)] != hollerith_undefined


def utf8_to_utf32(utf8_string):
    s = []
    i = 0
    while i < len(utf8_string):
        c32 = 0
        trailing = 0
        c = utf8_string[i]
        i += 1

        if (ord(c) & 0x80) == 0x00:
            c32 = ord(c)
        elif (ord(c) & 0xE0) == 0xC0:
            c32 = ord(c) - 0xC0
            trailing = 1
        elif (ord(c) & 0xF0) == 0xE0:
            c32 = ord(c) - 0xE0
            trailing = 2
        elif (ord(c) & 0xF8) == 0xF0:
            c32 = ord(c) - 0xF0
            trailing = 3
        elif (ord(c) & 0xFC) == 0xF8:
            c32 = ord(c) - 0xF8
            trailing = 4
        elif (ord(c) & 0xFE) == 0xFC:
            c32 = ord(c) - 0xFC
            trailing = 5
        else:
            raise RuntimeError("utf8_to_utf32: invalid lead byte")

        if trailing > len(utf8_string) - i:
            raise RuntimeError("utf8_to_utf32: missing trail byte")

        while trailing > 0:
            c = utf8_string[i]
            i += 1
            if (ord(c) & 0xC0) != 0x80:
                raise RuntimeError("utf8_to_utf32: invalid trail byte")
            c32 <<= 6
            c32 |= ord(c) & 0x3F
            trailing -= 1

        s.append(chr(c32))

    return ''.join(s)


# Function to filter non-Hollerith characters
def filter_bcd(utf8_string):
    non_bcd_replacement_char = '-'
    result = []
    utf32 = utf8_to_utf32(utf8_string)
    for ch in utf32:
        c32 = ord(ch)

        # case 0x2018:        // 'LEFT SINGLE QUOTATION MARK' (U+2018)
        # case 0x2019:        // 'RIGHT SINGLE QUOTATION MARK' (U+2019)
        # case 0x0022:        // 'QUOTATION MARK' (U+0022)
        # case 0x0060:        // 'GRAVE ACCENT' (U+0060) [backtick]
        # case 0x00AB:        // 'LEFT-POINTING DOUBLE ANGLE QUOTATION MARK' (U+00AB)
        # case 0x00BB:        // 'RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK' (U+00BB)
        # case 0x201A:        // 'SINGLE LOW-9 QUOTATION MARK' (U+201A)
        # case 0x201B:        // 'SINGLE HIGH-REVERSED-9 QUOTATION MARK' (U+201B)
        # case 0x201C:        // 'LEFT DOUBLE QUOTATION MARK' (U+201C)
        # case 0x201D:        // 'RIGHT DOUBLE QUOTATION MARK' (U+201D)
        # case 0x201E:        // 'DOUBLE LOW-9 QUOTATION MARK' (U+201E)
        # case 0x201F:        // 'DOUBLE HIGH-REVERSED-9 QUOTATION MARK' (U+201F)
        # case 0x2039:        // 'SINGLE LEFT-POINTING ANGLE QUOTATION MARK' (U+2039)
        # case 0x203A:        // 'SINGLE RIGHT-POINTING ANGLE QUOTATION MARK' (U+203A)

        if c32 in [0x2018, 0x2019, 0x0022, 0x0060, 0x00AB, 0x00BB, 0x201A, 0x201B,
                   0x201C, 0x201D, 0x201E, 0x201F, 0x2039, 0x203A]:
            result.append('\'')
            continue
        if c32 > 127:
            # The code point is not ASCII, which implies it's not Hollerith
            # either as ASCII is a superset of Hollerith. Since we're
            # just about to uppercase it with std::toupper, which
            # has undefined behaviour for characters that can't be
            # encoded in an unsigned char, we'll just replace it with dash.

            result.append(non_bcd_replacement_char)
            continue
        c = chr(c32).upper()
        if c == '?' or c == '!':
            result.append('.')
        elif ord(c) < len(hollerith_encoding) and hollerith_encoding[ord(c)] is not None:
            result.append(c)
        else:
            result.append(non_bcd_replacement_char)
    return ''.join(result)
