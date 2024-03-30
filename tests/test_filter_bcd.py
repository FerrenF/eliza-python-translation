import unittest

from hollerith.encoding import filter_bcd


class bcdTest(unittest.TestCase):
    def test_filter_bcd(self):
        result = filter_bcd("")
        assert result == "", f"Expected: '', Actual: {result}"

        result = filter_bcd("HELLO")
        assert result == "HELLO", f"Expected: 'HELLO', Actual: {result}"

        result = filter_bcd("Hello! How are you?")
        assert result == "HELLO. HOW ARE YOU.", f"Expected: 'HELLO. HOW ARE YOU.', Actual: {result}"

        result = filter_bcd("Æmilia, Æsop & Phœbë")
        assert result == "-MILIA, -SOP - PH-B-", f"Expected: '-MILIA, -SOP - PH-B-', Actual: {result}"

        # 'LEFT SINGLE QUOTATION MARK' (U+2018)
        result = filter_bcd("I‘m depressed")
        assert result == "I'M DEPRESSED", f"Expected: 'I'M DEPRESSED', Actual: {result}"

        # 'RIGHT SINGLE QUOTATION MARK' (U+2019)
        result = filter_bcd("I’m depressed")
        assert result == "I'M DEPRESSED", f"Expected: 'I'M DEPRESSED', Actual: {result}"

        # 'QUOTATION MARK' (U+0022)
        result = filter_bcd("I'm \"depressed\"")
        assert result == "I'M 'DEPRESSED'", f"Expected: 'I'M 'DEPRESSED'', Actual: {result}"

        # 'GRAVE ACCENT' (U+0060) [backtick]
        result = filter_bcd("I'm `depressed`")
        assert result == "I'M 'DEPRESSED'", f"Expected: 'I'M 'DEPRESSED'', Actual: {result}"

        # 'LEFT-POINTING DOUBLE ANGLE QUOTATION MARK' (U+00AB)
        # 'RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK' (U+00BB)
        result = filter_bcd("I'm «depressed»")
        assert result == "I'M 'DEPRESSED'", f"Expected: 'I'M 'DEPRESSED'', Actual: {result}"

        # 'SINGLE LOW-9 QUOTATION MARK' (U+201A)
        # 'SINGLE HIGH-REVERSED-9 QUOTATION MARK' (U+201B)
        result = filter_bcd("I'm ‚depressed‛")
        assert result == "I'M 'DEPRESSED'", f"Expected: 'I'M 'DEPRESSED'', Actual: {result}"

        # 'LEFT DOUBLE QUOTATION MARK' (U+201C)
        # 'RIGHT DOUBLE QUOTATION MARK' (U+201D)
        result = filter_bcd("I'm “depressed”")
        assert result == "I'M 'DEPRESSED'", f"Expected: 'I'M 'DEPRESSED'', Actual: {result}"

        # 'DOUBLE LOW-9 QUOTATION MARK' (U+201E)
        # 'DOUBLE HIGH-REVERSED-9 QUOTATION MARK' (U+201F)
        result = filter_bcd("I'm „depressed‟")
        assert result == "I'M 'DEPRESSED'", f"Expected: 'I'M 'DEPRESSED'', Actual: {result}"

        # 'SINGLE LEFT-POINTING ANGLE QUOTATION MARK' (U+2039)
        # 'SINGLE RIGHT-POINTING ANGLE QUOTATION MARK' (U+203A)
        result = filter_bcd("I'm ‹depressed›")
        assert result == "I'M 'DEPRESSED'", f"Expected: 'I'M 'DEPRESSED'', Actual: {result}"

        all_valid_bcd = "0123456789=\'+ABCDEFGHI.)-JKLMNOPQR$* /STUVWXYZ,("
        result = filter_bcd(all_valid_bcd)
        assert result == all_valid_bcd, f"Expected: '{all_valid_bcd}', Actual: {result}"
