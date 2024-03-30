import unittest

from elizalogic import inlist, match, to_int


class TestInList(unittest.TestCase):
    def setUp(self):
        self.tags = {
            "FAMILY": ["MOTHER", "FATHER", "SISTER", "BROTHER", "WIFE", "CHILDREN"],
            "NOUN": ["MOTHER", "FATHER", "FISH", "FOUL"]
        }

    def test_inlist(self):
        self.assertTrue(inlist("MOTHER", "(/FAMILY)", self.tags))
        self.assertTrue(inlist("FATHER", "(/FAMILY)", self.tags))
        self.assertTrue(inlist("SISTER", "(/FAMILY)", self.tags))
        self.assertTrue(inlist("BROTHER", "( / FAMILY )", self.tags))
        self.assertTrue(inlist("WIFE", "(/FAMILY)", self.tags))
        self.assertTrue(inlist("CHILDREN", "(/FAMILY)", self.tags))
        self.assertFalse(inlist("FISH", "(/FAMILY)", self.tags))
        self.assertFalse(inlist("FOUL", "(/FAMILY)", self.tags))

        self.assertTrue(inlist("MOTHER", "(/NOUN)", self.tags))
        self.assertTrue(inlist("FATHER", "(/NOUN)", self.tags))
        self.assertFalse(inlist("SISTER", "(/NOUN)", self.tags))
        self.assertFalse(inlist("BROTHER", "(/NOUN)", self.tags))
        self.assertFalse(inlist("WIFE", "(/NOUN)", self.tags))
        self.assertFalse(inlist("CHILDREN", "(/NOUN)", self.tags))
        self.assertTrue(inlist("FISH", "(/NOUN)", self.tags))
        self.assertTrue(inlist("FOUL", "(/NOUN)", self.tags))

        self.assertTrue(inlist("MOTHER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("FATHER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("SISTER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("BROTHER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("WIFE", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("CHILDREN", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("FISH", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("FOUL", "(/ NOUN  FAMILY )", self.tags))

        self.assertFalse(inlist("MOTHER", "(/NONEXISTANTTAG)", self.tags))
        self.assertTrue(inlist("MOTHER", "(/NON FAMILY TAG)", self.tags))

        self.assertFalse(inlist("DEPRESSED", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(inlist("SAD", "(*SAD HAPPY DEPRESSED)", self.tags))
        self.assertTrue(inlist("HAPPY", "(*SAD HAPPY DEPRESSED)", self.tags))
        self.assertTrue(inlist("DEPRESSED", "(*SAD HAPPY DEPRESSED)", self.tags))
        self.assertTrue(inlist("SAD", "( * SAD HAPPY DEPRESSED )", self.tags))
        self.assertTrue(inlist("HAPPY", "( * SAD HAPPY DEPRESSED )", self.tags))
        self.assertTrue(inlist("DEPRESSED", "( * SAD HAPPY DEPRESSED )", self.tags))
        self.assertFalse(inlist("DRUNK", "( * SAD HAPPY DEPRESSED )", self.tags))

        self.assertTrue(inlist("WONDER", "(*HAPPY ELATED EXCITED GOOD WONDERFUL)", self.tags))
        self.assertTrue(inlist("FUL", "(*HAPPY ELATED EXCITED GOOD WONDERFUL)", self.tags))
        self.assertTrue(inlist("D", "(*HAPPY ELATED EXCITED GOOD WONDERFUL)", self.tags))


class TestToInt(unittest.TestCase):
    def test_to_int(self):
        self.assertEqual(to_int("0"), 0)
        self.assertEqual(to_int("1"), 1)
        self.assertEqual(to_int("2023"), 2023)
        self.assertEqual(to_int("-42"), -1)
        self.assertEqual(to_int("int"), -1)



class TestMatch(unittest.TestCase):
    def setUp(self):
        self.tags = {
            "FAMILY": ["MOTHER", "FATHER"],
            "NOUN": ["MOTHER", "FATHER"],
            "BELIEF": ["FEEL"]
        }

    def test_match(self):
        words = ["YOU", "NEED", "NICE", "FOOD"]
        pattern = ["0", "YOU", "(*WANT NEED)", "0"]
        expected = ["", "YOU", "NEED", "NICE FOOD"]
        matching_components = []

        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(c, expected)

        words = ["YOU", "WANT", "NICE", "FOOD"]
        pattern = ["0", "0", "YOU", "(*WANT NEED)", "0"]
        expected = ["", "", "YOU", "WANT", "NICE FOOD"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(c, expected)

        words = ["YOU", "WANT", "NICE", "FOOD"]
        pattern = ["1", "(*WANT NEED)", "0"]
        expected = ["YOU", "WANT", "NICE FOOD"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(c, expected)

        words = ["YOU", "WANT", "NICE", "FOOD"]
        pattern = ["1", "(*WANT NEED)", "1"]
        matching_components = []
        m,c = match({}, pattern, words, matching_components)
        self.assertFalse(m)

        words = ["YOU", "WANT", "NICE", "FOOD"]
        pattern = ["1", "(*WANT NEED)", "2"]
        expected = ["YOU", "WANT", "NICE FOOD"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(c, expected)

        words = ["CONSIDER", "YOUR", "AGED", "MOTHER", "AND", "FATHER", "TOO"]
        pattern = ["0", "YOUR", "0", "(* FATHER MOTHER)", "0"]
        expected = ["CONSIDER", "YOUR", "AGED", "MOTHER", "AND FATHER TOO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(c, expected)

        words = ["MOTHER", "AND", "FATHER", "MOTHER"]
        pattern = ["0", "(* FATHER MOTHER)", "(* FATHER MOTHER)", "0"]
        expected = ["MOTHER AND", "FATHER", "MOTHER", ""]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(c, expected)

        # Add more test cases here for other patterns and words