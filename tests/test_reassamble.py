import unittest

from elizalogic import reassemble


class TestReassamble(unittest.TestCase):

    def test_reassemble(self):
        matching_components = [
            "MARY", "HAD A", "LITTLE LAMB", "ITS", "PROBABILITY", "WAS ZERO"
        ]

        # Test pattern from the ASSMBL function description in the SLIP manual
        reassembly_rule = ["DID", "1", "HAVE", "A", "3"]
        expected = ["DID", "MARY", "HAVE", "A", "LITTLE", "LAMB"]
        result = reassemble(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "1", "1"]
        expected = ["MARY", "MARY", "MARY"]
        result = reassemble(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "-1", "1"]
        expected = ["MARY", "-1", "MARY"]
        result = reassemble(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "0", "1"]
        expected = ["MARY", "THINGY", "MARY"]
        result = reassemble(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "6", "1"]
        expected = ["MARY", "WAS", "ZERO", "MARY"]
        result = reassemble(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "7", "1"]
        expected = ["MARY", "THINGY", "MARY"]
        result = reassemble(reassembly_rule, matching_components)
        assert result == expected
