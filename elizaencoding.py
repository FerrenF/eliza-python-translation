from typing import List, Dict
hollerith_undefined = 0xFF
# "The 7090 BCD character codes are given in the accompanying table.
#    Six bits are used for each character. [...] The code is generally
#    termed binary-coded-decimal or BCD. For compactness, the codes are
#    generally expressed as 2-digit octal numbers, as in the table. The
#    term Hollerith is used synonomously with BCD." [1]
#
#    The following array is derived from the above mentioned table, with
#    one exception: BCD code 14 (octal) is a single quote (prime), not a
#    double quote. See [2].
#
#    The Hollerith code is the table offset. 0 means unused code.
#
#    [1] Philip M. Sherman
#        Programming and Coding the IBM 709-7090-7094 Computers
#        John Wiley and Sons, 1963
#        Page 62
#    [2] University of Michigan Executive System for the IBM 7090 Computer
#        September 1964
#        In section THE UNIVERSITY OF MICHIGAN MONITOR
#        APPENDIX 2, page 30, TABLE OF BCD--OCTAL EQUIVALENTS
#        (Available online from Google Books. Search for PRIME.)

# from bitstring import Bits, BitArray, Bitstream, pack


# You can find the table here: https://en.wikipedia.org/wiki/BCD_(character_encoding)
bcd_table: List[int] = [
    # N is the zero-based position of the column on each row, in hexidecimal [0..9 - A..F]
    # character 1 in the first row has a hexidecimal value of 01, or a binary value of 0001.
    # Similarly, 5, or 31 would have a value of 11 0001
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 0, '=', '\'', 0, 0, 0,  # 0x[xN] = hex __
    '+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 0, '.', ')',  0, 0, 0,  # 1x[xN]
    '-', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 0, '$', '*',  0, 0, 0,  # 2x[xN]
    ' ', '/', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 0, ',', '(',  0, 0, 0   # 3x[xN]
]

def to_unsigned(c: str):
    return ord(c) % 256
def to_unsigned_int(c: int):
    return c % 256

# 16 bit integer values for our bcd_characters
to_bcd: Dict[str, int] = {}
def get_hex(char: str):
    value = hex(hollerith_undefined)
    if char in bcd_table:
        value = hex(bcd_table.index(char))
    return value

for n in range(256):
    v = get_hex(chr(n))
    to_bcd.update({chr(n): int(v, 16)})

def hollerith_defined(c: str) -> bool:
    """
    Check if a character is defined in the Hollerith encoding.

    :param c: Character to check
    :return: True if character is defined, False otherwise
    """
    return to_bcd.get(c) != hollerith_undefined


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

    for ch in utf8_string:
        c32 = ord(ch)

        if c32 in [0x2018, 0x2019, 0x0022, 0x0060, 0x00AB, 0x00BB, 0x201A, 0x201B,
                   0x201C, 0x201D, 0x201E, 0x201F, 0x2039, 0x203A]:
            result.append('\'')
            continue

        if c32 > 127:
            # Replace non-ASCII characters with non_bcd_replacement_char
            result.append(non_bcd_replacement_char)
            continue

        c = ch.upper()
        if c == '?' or c == '!':
            result.append('.')
        elif hollerith_defined(c):
            result.append(c)
        else:
            result.append(non_bcd_replacement_char)

    return ''.join(result) if len(result) else ''

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

# hehe, look at this hacky stuff
def six_bit_list_to_64_bit_representation(six_bit_list):
    # Initialize the result as 0
    result = 0

    # Iterate over the six-bit integers in the list
    for i, six_bit_integer in enumerate(six_bit_list):
        # Shift the six-bit integer to its appropriate position
        shifted_value = six_bit_integer << (6 * (len(six_bit_list) - 1 - i))

        # Combine the shifted value with the result using bitwise OR
        result |= shifted_value

    return result

def last_chunk_as_bcd(s):
    result = []
    def append(c: str):
        assert hollerith_defined(c)
        nonlocal result

        val = int(get_hex(c),16) % 64
        result.append(val)

    count = 0
    if s:
        while len(s) > 6:
            s = s[6:]
                #append(ch)
                #count += 1

        #cut = s[-((len(s) - 1) // 6) * 6:]
        for ch in s:
            append(ch)
            count += 1

    while count < 6:
        append(' ')
        count += 1
    r = six_bit_list_to_64_bit_representation(result)
    return r

