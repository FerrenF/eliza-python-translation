# Constants
import string

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

# Hollerith encoding table
hollerith_encoding = {
    c: i for i, c in enumerate(string.ascii_uppercase + string.digits + ' $%*+-./')
}


# Conversion table from ASCII to BCD
to_bcd = [hollerith_undefined] * 256
for c in range(64):
    if hollerith_encoding[c]:
        to_bcd[ord(hollerith_encoding[c])] = c


def hollerith_defined(c: str) -> bool:
    """
    Check if a character is defined in the Hollerith encoding.

    :param c: Character to check
    :return: True if character is defined, False otherwise
    """
    return c in hollerith_encoding


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



def hash(d: int, n: int) -> int:
    """
    This function implements the SLIP HASH algorithm from the FAP
    code shown above.

    The function returns the middle n bits of d squared.
    This kind of hash is known as mid-square.

    The IBM 7094 uses sign-magnitude representation of integers:
    in a 36-bit integer, the most-significant bit is assumed to
    be the sign of the integer, and the least-significant 35-bits
    are assumed to be the magnitude of the integer. Therefore,
    in the SLIP HASH implementation only the least-significant
    35-bits of D are squared. When the datum holds six 6-bit
    characters the top bit of the first character in the given D
    will be assumed to be a sign bit and will not be part of
    the 35-bit multiplication (except as a sign).

    On the IBM 7094 multiplying two 35-bit numbers produces a
    70-bit result. In this code that 70-bit result will be
    truncated to 64-bits. (In C++, unsigned arithmetic overflow is
    not undefined behaviour, as it is for signed arithmetic.) If
    n is 15, the middle 15 bits of a 70-bit number are bits 42-28
    (bit 0 least significant), which is well within our 64-bit
    calculation.

    :param d: Input integer value
    :param n: Number of middle bits to extract
    :return: Hashed value
    """
    assert 0 <= n <= 15

    d &= 0x7FFFFFFFF  # clear the "sign" bit
    d *= d  # square it
    d >>= 35 - n // 2  # move middle n bits to least sig. bits
    return d & ((1 << n) - 1)  # mask off all but n least sig. bits



#
# /*  last_chunk_as_bcd() -- What the heck?
#
#     Very quick overview:
#
#     ELIZA was written in SLIP for an IBM 7094. The character encoding used
#     on the 7094 is called Hollerith (or BCD - see the hollerith_encoding
#     table above). The Hollerith encoding uses 6 bits per character.
#     The IBM 7094 machine word size is 36-bits.
#
#     SLIP stores strings in SLIP cells. A SLIP cell consists of two
#     adjacent machine words. The first word contains some type bits
#     and two addresses, one pointing to the previous SLIP cell and
#     the other pointing to the next SLIP cell. (The IBM 7094 had a
#     32,768 word core store, so only 15 bits are required for an
#     address. So two addresses fit into one 36-bit word with 6 bits
#     spare.) The second word may carry the "datum." This is where
#     the characters are stored.
#
#     Each SLIP cell can store up to 6 6-bit Hollerith characters.
#
#     If a string has fewer than 6 characters, the string is stored left-
#     justified and space padded to the right.
#
#     So for example, the string "HERE" would be stored in one SLIP cell,
#     which would have the octal value 30 25 51 25 60 60.
#
#     If a string has more than 6 characters, it is stored in successive
#     SLIP cells. Each cell except the last has the sign bit set in the
#     first word to indicated the string is continued in the next cell.
#
#     So the word "INVENTED" would be stored in two SLIP cells, "INVENT"
#     in the first and "ED    " in the second.
#
#     In ELIZA, the user's input text is read into a SLIP list, each word
#     in the sentence is in it's own cell, unless a word needs to be
#     continued in the next cell because it's more than 6 characters long.
#
#     When ELIZA chooses a MEMORY rule it hashes the last cell in the
#     input sentence. That will be the last word in the sentence, or
#     the last chunk of the last word, if the last word is more than
#     6 characters long.
#
#     This code doesn't use SLIP cells. A std::deque of std::string
#     provided enough functionality to manage without SLIP. In this
#     code, every word is contained in one std::string, no matter
#     how long.
#
#     Given the last word in a sentence, the last_chunk_as_bcd function
#     will return the 36-bit Hollerith encoding of the word, appropriately
#     space padded, or the last chunk of the word if over 6 characters long.
# */


def last_chunk_as_bcd(s: str) -> int:
    """
    Given the last word in a sentence, the last_chunk_as_bcd function
    will return the 36-bit Hollerith encoding of the word, appropriately
    space padded, or the last chunk of the word if over 6 characters long.

    :param s: Input string
    :return: Hollerith encoding of the last chunk of the word
    """
    result = 0

    def append(c: str) -> None:
        nonlocal result
        assert hollerith_defined(c)
        result <<= 6
        result |= hollerith_encoding[c]

    count = 0
    if s:
        for c in s[-((len(s) - 1) // 6) * 6:]:
            append(c)
            count += 1
    while count < 6:
        append(' ')
        count += 1

    return result
