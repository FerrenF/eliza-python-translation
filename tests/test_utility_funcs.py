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
    extended_tests = True

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
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)

        words = ["YOU", "WANT", "NICE", "FOOD"]
        pattern = ["1", "(*WANT NEED)", "2"]
        expected = ["YOU", "WANT", "NICE FOOD"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(c, expected)

       #   // test (0 YOUR 0 (* FATHER MOTHER) 0) matches
       #  // (CONSIDER YOUR AGED MOTHER AND FATHER TOO)
       #  /* "The above input text would have been decomposed precisely as stated
       #  above by the decomposition rule: (0 YOUR 0 (*FATHER MOTHER) 0) which,
       #  by virtue of the presence of "*" in the sublist structure seen above,
       #  would have isolated either the word "FATHER" or "MOTHER" (in that
       #  order) in the input text, whichever occurred first after the first
       #  appearance of the word "YOUR". -- Weizenbaum 1966, page 42
       # What does "in that order" mean? */

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

        if self.extended_tests:
            self.extended_test_match_function()

    def extended_test_match_function(self):

        matching_components = [] # set up
        # Patterns don't require literals
        words = ["FIRST", "AND", "LAST", "TWO", "WORDS"]
        pattern = ["2", "0", "2"]
        expected = ["FIRST AND", "LAST", "TWO WORDS"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Pointless but not prohibited
        words =["THE", "NAME", "IS", "BOND", "JAMES", "BOND", "OR", "007", "IF", "YOU", "PREFER"]
        pattern =["0", "0", "7"]
        expected = ["", "THE NAME IS BOND", "JAMES BOND OR 007 IF YOU PREFER"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # How are ambiguous matches resolved?
        words =["ITS", "MARY", "ITS", "NOT", "MARY", "IT", "IS", "MARY", "TOO"]
        pattern =["0", "ITS", "0", "MARY", "1"]
        expected = ["", "ITS", "MARY ITS NOT MARY IT IS", "MARY", "TOO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # How are ambiguous matches resolved? ("I know that you know I hate you and I like you too")
        words =["YOU", "KNOW", "THAT", "I", "KNOW", "YOU", "HATE", "I", "AND", "YOU", "LIKE", "I", "TOO"]
        pattern =["0", "YOU", "0", "I", "0"]  # from the I rule in the DOCTOR script
        expected = ["", "YOU", "KNOW THAT", "I", "KNOW YOU HATE I AND YOU LIKE I TOO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # A test pattern from the YMATCH function description in the SLIP manual
        words =["MARY", "HAD", "A", "LITTLE", "LAMB", "ITS", "PROBABILITY", "WAS", "ZERO"]
        pattern =["MARY", "2", "2", "ITS", "1", "0"]
        expected = ["MARY", "HAD A", "LITTLE LAMB", "ITS", "PROBABILITY", "WAS ZERO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # A test pattern from the RULE function description in the SLIP manual
        words =["MARY", "HAD", "A", "LITTLE", "LAMB", "ITS", "PROBABILITY", "WAS", "ZERO"]
        pattern =["1", "0", "2", "ITS", "0"]
        expected = ["MARY", "HAD A", "LITTLE LAMB", "ITS", "PROBABILITY WAS ZERO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Empty inputs
        words = list()
        pattern = list()
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Empty pattern with non-empty words
        words = list()
        pattern =["0"]
        expected = [""]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Exact match
        words =["MARY", "HAD", "A", "LITTLE", "LAMB"]
        pattern =["MARY", "HAD", "A", "LITTLE", "LAMB"]
        expected = ["MARY", "HAD", "A", "LITTLE", "LAMB"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Words not in the correct order
        words =["HAD", "MARY", "A", "LITTLE", "LAMB"]
        pattern =["MARY", "HAD", "A", "LITTLE", "LAMB"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Words missing from the pattern
        words =["MARY", "HAD", "A", "LITTLE", "LAMB", "CALLED", "WOOLY"]
        pattern =["MARY", "HAD", "A", "LITTLE", "LAMB"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Variable number of words between literals
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["WHEN", "WILL", "2", "MEET"]
        expected = ["WHEN", "WILL", "WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Variable number of words between literals with different approach
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["WHEN", "1", "2", "MEET"]
        expected = ["WHEN", "WILL", "WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Variable number of words before literals
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["1", "1", "2", "1"]
        expected = ["WHEN", "WILL", "WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Splitting words based on a fixed number
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["3", "2"]
        expected = ["WHEN WILL WE", "THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining all words into one component
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["5"]
        expected = ["WHEN WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining all words into one component with a leading empty component
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["0", "5"]
        expected = ["", "WHEN WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining all words into one component with a trailing empty component
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["5", "0"]
        expected = ["WHEN WILL WE THREE MEET", ""]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words before a literal
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["1", "0"]
        expected = ["WHEN", "WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words after a literal
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["0", "1"]
        expected = ["WHEN WILL WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words between literals
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["1", "1", "0"]
        expected = ["WHEN", "WILL", "WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words before the first literal and between literals
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["0", "1", "0"]
        expected = ["", "WHEN", "WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["6"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern with a leading empty component
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["0", "6"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern with a trailing empty component
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["6", "0"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern with words before the first literal
        words =["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern =["1", "WHEN", "0"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Literal with multiple possible substitutions
        words =["MY", "FAIR", "LADY"]
        pattern =["MY", "(*FAIR GOOD)", "LADY"]
        expected = ["MY", "FAIR", "LADY"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Literal with one of multiple possible substitutions
        words =["MY", "GOOD", "LADY"]
        pattern =["MY", "(*FAIR GOOD)", "LADY"]
        expected = ["MY", "GOOD", "LADY"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Literal with no matching substitution
        words =["MY", "LADY"]
        pattern =["MY", "(*FAIR GOOD)", "LADY"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Literal with incomplete matching substitution
        words =["MY", "FAIR", "GOOD", "LADY"]
        pattern =["MY", "(*FAIR GOOD)", "LADY"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)
