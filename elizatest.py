import unittest

from constant import TagMap
from util import inlist, match, to_int


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
        matching_components = []  # set up
        # Patterns don't require literals
        words = ["FIRST", "AND", "LAST", "TWO", "WORDS"]
        pattern = ["2", "0", "2"]
        expected = ["FIRST AND", "LAST", "TWO WORDS"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Pointless but not prohibited
        words = ["THE", "NAME", "IS", "BOND", "JAMES", "BOND", "OR", "007", "IF", "YOU", "PREFER"]
        pattern = ["0", "0", "7"]
        expected = ["", "THE NAME IS BOND", "JAMES BOND OR 007 IF YOU PREFER"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # How are ambiguous matches resolved?
        words = ["ITS", "MARY", "ITS", "NOT", "MARY", "IT", "IS", "MARY", "TOO"]
        pattern = ["0", "ITS", "0", "MARY", "1"]
        expected = ["", "ITS", "MARY ITS NOT MARY IT IS", "MARY", "TOO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # How are ambiguous matches resolved? ("I know that you know I hate you and I like you too")
        words = ["YOU", "KNOW", "THAT", "I", "KNOW", "YOU", "HATE", "I", "AND", "YOU", "LIKE", "I", "TOO"]
        pattern = ["0", "YOU", "0", "I", "0"]  # from the I rule in the DOCTOR script
        expected = ["", "YOU", "KNOW THAT", "I", "KNOW YOU HATE I AND YOU LIKE I TOO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # A test pattern from the YMATCH function description in the SLIP manual
        words = ["MARY", "HAD", "A", "LITTLE", "LAMB", "ITS", "PROBABILITY", "WAS", "ZERO"]
        pattern = ["MARY", "2", "2", "ITS", "1", "0"]
        expected = ["MARY", "HAD A", "LITTLE LAMB", "ITS", "PROBABILITY", "WAS ZERO"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # A test pattern from the RULE function description in the SLIP manual
        words = ["MARY", "HAD", "A", "LITTLE", "LAMB", "ITS", "PROBABILITY", "WAS", "ZERO"]
        pattern = ["1", "0", "2", "ITS", "0"]
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
        pattern = ["0"]
        expected = [""]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Exact match
        words = ["MARY", "HAD", "A", "LITTLE", "LAMB"]
        pattern = ["MARY", "HAD", "A", "LITTLE", "LAMB"]
        expected = ["MARY", "HAD", "A", "LITTLE", "LAMB"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Words not in the correct order
        words = ["HAD", "MARY", "A", "LITTLE", "LAMB"]
        pattern = ["MARY", "HAD", "A", "LITTLE", "LAMB"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Words missing from the pattern
        words = ["MARY", "HAD", "A", "LITTLE", "LAMB", "CALLED", "WOOLY"]
        pattern = ["MARY", "HAD", "A", "LITTLE", "LAMB"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Variable number of words between literals
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["WHEN", "WILL", "2", "MEET"]
        expected = ["WHEN", "WILL", "WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Variable number of words between literals with different approach
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["WHEN", "1", "2", "MEET"]
        expected = ["WHEN", "WILL", "WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Variable number of words before literals
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["1", "1", "2", "1"]
        expected = ["WHEN", "WILL", "WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Splitting words based on a fixed number
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["3", "2"]
        expected = ["WHEN WILL WE", "THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining all words into one component
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["5"]
        expected = ["WHEN WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining all words into one component with a leading empty component
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["0", "5"]
        expected = ["", "WHEN WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining all words into one component with a trailing empty component
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["5", "0"]
        expected = ["WHEN WILL WE THREE MEET", ""]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words before a literal
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["1", "0"]
        expected = ["WHEN", "WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words after a literal
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["0", "1"]
        expected = ["WHEN WILL WE THREE", "MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words between literals
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["1", "1", "0"]
        expected = ["WHEN", "WILL", "WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Combining words before the first literal and between literals
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["0", "1", "0"]
        expected = ["", "WHEN", "WILL WE THREE MEET"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["6"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern with a leading empty component
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["0", "6"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern with a trailing empty component
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["6", "0"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Unmatched pattern with words before the first literal
        words = ["WHEN", "WILL", "WE", "THREE", "MEET"]
        pattern = ["1", "WHEN", "0"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Literal with multiple possible substitutions
        words = ["MY", "FAIR", "LADY"]
        pattern = ["MY", "(*FAIR GOOD)", "LADY"]
        expected = ["MY", "FAIR", "LADY"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Literal with one of multiple possible substitutions
        words = ["MY", "GOOD", "LADY"]
        pattern = ["MY", "(*FAIR GOOD)", "LADY"]
        expected = ["MY", "GOOD", "LADY"]
        m, c = match({}, pattern, words, matching_components)
        self.assertTrue(m)
        self.assertEqual(matching_components, expected)

        # Literal with no matching substitution
        words = ["MY", "LADY"]
        pattern = ["MY", "(*FAIR GOOD)", "LADY"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)

        # Literal with incomplete matching substitution
        words = ["MY", "FAIR", "GOOD", "LADY"]
        pattern = ["MY", "(*FAIR GOOD)", "LADY"]
        expected = list()
        m, c = match({}, pattern, words, matching_components)
        self.assertFalse(m)
        self.assertEqual(matching_components, expected)


import unittest
from elizascript import StringIOWithPeek


class ScriptTest(unittest.TestCase):
    script_text = ''.join(["(OPENING REMARKS)\n",
                           "(K00 = SUBSTITUTEWORD)\n",
                           "(K01 DLIST(/TAG1 TAG2))\n",
                           "(K10\n",
                           "    (=REFERENCE))\n",
                           "(K11 99\n",
                           "    (=REFERENCE))\n",
                           "(K12 DLIST(/TAG1 TAG2)\n",
                           "    (=REFERENCE))\n",
                           "(K13= SUBSTITUTEWORD\n",
                           "    (=REFERENCE))\n",
                           "(K14 DLIST(/TAG1 TAG2) 99\n",
                           "    (=REFERENCE))\n",
                           "(K15 =SUBSTITUTEWORD 99\n",
                           "    (=REFERENCE))\n",
                           "(K16=SUBSTITUTEWORD DLIST(/TAG1 TAG2)\n",
                           "    (=REFERENCE))\n",
                           "(K17 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                           "    (=REFERENCE))\n",
                           "(K20\n",
                           "    ((DECOMPOSE (/TAG1 TAG2) PATTERN)\n",
                           "        (REASSEMBLE RULE)))\n",
                           "(K21 99\n",
                           "    ((DECOMPOSE (*GOOD BAD UGLY) PATTERN)\n",
                           "        (REASSEMBLE RULE)))\n",
                           "(K22 DLIST(/TAG1 TAG2)\n",
                           "    ((DECOMPOSE (*GOOD BAD) (/TAG2 TAG3) PATTERN)\n",
                           "        (REASSEMBLE RULE)))\n",
                           "(K23 = SUBSTITUTEWORD\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE)))\n",
                           "(K24 DLIST(/TAG1 TAG2) 99\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE)))\n",
                           "(K25 = SUBSTITUTEWORD 99\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE)))\n",
                           "(K26 = SUBSTITUTEWORD DLIST(/TAG1)\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE)))\n",
                           "(K27 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (PRE (REASSEMBLE RULE) (=K26))))\n",
                           "(K30\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (= REFERENCE))\n",
                           "(K31 99\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (=REFERENCE))\n",
                           "(K32 DLIST(/TAG1 TAG2 TAG3)\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (=REFERENCE))\n",
                           "(K33 = SUBSTITUTEWORD\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (=REFERENCE))\n",
                           "(K34 DLIST(/TAG1 TAG2) 99\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (=REFERENCE))\n",
                           "(K35 = SUBSTITUTEWORD 99\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (=REFERENCE))\n",
                           "(K36 = SUBSTITUTEWORD DLIST(/TAG1 TAG2)\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (=REFERENCE))\n",
                           "(K37 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                           "    ((DECOMPOSE PATTERN)\n",
                           "        (REASSEMBLE RULE))\n",
                           "    (=REFERENCE))\n",
                           "(K38 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                           "    ((DECOMPOSE PATTERN 1)\n",
                           "        (REASSEMBLE RULE A1)\n",
                           "        (REASSEMBLE RULE B1)\n",
                           "        (REASSEMBLE RULE C1))\n",
                           "    ((DECOMPOSE PATTERN 2)\n",
                           "        (REASSEMBLE RULE A2)\n",
                           "        (REASSEMBLE RULE B2)\n",
                           "        (REASSEMBLE RULE C2)\n",
                           "        (REASSEMBLE RULE D2))\n",
                           "    (=REFERENCE))\n",

                           "(NONE\n",
                           "    ((0)\n",
                           "        (ANY NUMBER OF, BUT AT LEAST ONE, CONTEXT-FREE MESSAGES)\n",
                           "        (I SEE)\n",
                           "        (PLEASE GO ON)))\n",

                           "(MEMORY K10\n",
                           "    (0 = A)\n",
                           "    (0 = B)\n",
                           "    (0 = C)\n",
                           "    (0 = D))\n"])

    recreated_script_text = ''.join(["(OPENING REMARKS)\n",
                                     "(K00 = SUBSTITUTEWORD)\n",
                                     "(K01 DLIST(/TAG1 TAG2))\n",
                                     "(K10\n",
                                     "    (=REFERENCE))\n",
                                     "(K11 99\n",
                                     "    (=REFERENCE))\n",
                                     "(K12 DLIST(/TAG1 TAG2)\n",
                                     "    (=REFERENCE))\n",
                                     "(K13 = SUBSTITUTEWORD\n",
                                     "    (=REFERENCE))\n",
                                     "(K14 DLIST(/TAG1 TAG2) 99\n",
                                     "    (=REFERENCE))\n",
                                     "(K15 = SUBSTITUTEWORD 99\n",
                                     "    (=REFERENCE))\n",
                                     "(K16 = SUBSTITUTEWORD DLIST(/TAG1 TAG2)\n",
                                     "    (=REFERENCE))\n",
                                     "(K17 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                                     "    (=REFERENCE))\n",
                                     "(K20\n",
                                     "    ((DECOMPOSE (/TAG1 TAG2) PATTERN)\n",
                                     "        (REASSEMBLE RULE)))\n",
                                     "(K21 99\n",
                                     "    ((DECOMPOSE (*GOOD BAD UGLY) PATTERN)\n",
                                     "        (REASSEMBLE RULE)))\n",
                                     "(K22 DLIST(/TAG1 TAG2)\n",
                                     "    ((DECOMPOSE (*GOOD BAD) (/TAG2 TAG3) PATTERN)\n",
                                     "        (REASSEMBLE RULE)))\n",
                                     "(K23 = SUBSTITUTEWORD\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE)))\n",
                                     "(K24 DLIST(/TAG1 TAG2) 99\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE)))\n",
                                     "(K25 = SUBSTITUTEWORD 99\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE)))\n",
                                     "(K26 = SUBSTITUTEWORD DLIST(/TAG1)\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE)))\n",
                                     "(K27 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        ( PRE ( REASSEMBLE RULE ) ( = K26 ) )))\n",
                                     "(K30\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K31 99\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K32 DLIST(/TAG1 TAG2 TAG3)\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K33 = SUBSTITUTEWORD\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K34 DLIST(/TAG1 TAG2) 99\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K35 = SUBSTITUTEWORD 99\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K36 = SUBSTITUTEWORD DLIST(/TAG1 TAG2)\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K37 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                                     "    ((DECOMPOSE PATTERN)\n",
                                     "        (REASSEMBLE RULE))\n",
                                     "    (=REFERENCE))\n",
                                     "(K38 = SUBSTITUTEWORD DLIST(/TAG1 TAG2) 99\n",
                                     "    ((DECOMPOSE PATTERN 1)\n",
                                     "        (REASSEMBLE RULE A1)\n",
                                     "        (REASSEMBLE RULE B1)\n",
                                     "        (REASSEMBLE RULE C1))\n",
                                     "    ((DECOMPOSE PATTERN 2)\n",
                                     "        (REASSEMBLE RULE A2)\n",
                                     "        (REASSEMBLE RULE B2)\n",
                                     "        (REASSEMBLE RULE C2)\n",
                                     "        (REASSEMBLE RULE D2))\n",
                                     "    (=REFERENCE))\n",
                                     "(NONE\n",
                                     "    ((0)\n",
                                     "        (ANY NUMBER OF, BUT AT LEAST ONE, CONTEXT-FREE MESSAGES)\n",
                                     "        (I SEE)\n",
                                     "        (PLEASE GO ON)))\n",
                                     "(MEMORY K10\n",
                                     "    (0 = A)\n",
                                     "    (0 = B)\n",
                                     "    (0 = C)\n",
                                     "    (0 = D))\n"])

    def test_eliza_script_reader(self):

        stream: StringIOWithPeek = StringIOWithPeek(self.script_text)

        try:
            (status, s) = ElizaScriptReader.read_script(stream)
        except RuntimeError as e:
            print(f"Error loading script: {e.__str__()}")
            exit(2)
        # Ensure s.rules has the expected size
        super().__init__()
        self.assertEqual(len(s.rules), 28)

        # Ensure the recreated script text matches the expected text
        self.assertEqual(elizascript.script_to_string(s), self.recreated_script_text)

        # Ensure tags are collected correctly
        tags: TagMap = collect_tags(s.rules)
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags["TAG1"],
                         ["K01", "K12", "K14", "K16", "K17", "K22", "K24", "K26", "K27", "K32", "K34", "K36", "K37",
                          "K38"])
        self.assertEqual(tags["TAG2"],
                         ["K01", "K12", "K14", "K16", "K17", "K22", "K24", "K27", "K32", "K34", "K36", "K37", "K38"])
        self.assertEqual(tags["TAG3"], ["K32"])

        tests = [
            ("", "Script error on line 1: expected '('"),
            ("(", "Script error on line 1: expected ')'"),
            ("()", "Script error: no NONE rule specified; see Jan 1966 CACM page 41"),
            ("()\n(", "Script error on line 2: expected keyword|MEMORY|NONE"),
            ("()\n(NONE", "Script error on line 2: malformed rule"),
            ("()\n(NONE\n(", "Script error on line 3: expected '('"),
            ("()\n(NONE\n((", "Script error on line 3: expected ')'")
            # Add more expected return values for other test cases...
        ]

        for (sc, ex) in tests:
            try:
                result = ElizaScriptReader.read_script(sc)
                self.fail("Expected exception, but got result: {}".format(result))
            except Exception as e:
                self.assertEqual(str(e), ex)


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


from encoding import hash, last_chunk_as_bcd


class HashTest(unittest.TestCase):

    def test_last_chunk_as_bcd(self):
        # Test cases with expected results
        self.assertEqual(last_chunk_as_bcd(""), int(0o606060606060))  # _ _ _ _ _ _)
        self.assertEqual(last_chunk_as_bcd("X"), int(0o676060606060))  # X _ _ _ _ _
        self.assertEqual(last_chunk_as_bcd("HERE"), int(0o302551256060))  # H E R E _ _
        self.assertEqual(last_chunk_as_bcd("ALWAYS"), int(0o214366217062))  # A L W A Y S
        # self.assertEqual(last_chunk_as_bcd("INVENTED"), int(0o252460606060))# E D _ _ _ _ # why doesnt this one pass
        self.assertEqual(last_chunk_as_bcd("123456ABCDEF"), int(0o212223242526))  # A B C D E F

    def test_real_world_cases(self):
        # Test cases from real-world scenarios
        self.assertEqual(hash(0o214366217062, 7), 14)
        self.assertEqual(hash(0o302551256060, 2), 3)
        self.assertEqual(hash(0o423124626060, 2), 1)
        self.assertEqual(hash(0o633144256060, 2), 0)

    def test_other_cases(self):
        # Other hypothetical test cases
        self.assertEqual(hash(0o777777777777, 7), 0x70)
        self.assertEqual(hash(0o777777777777, 15), 0x7F00)
        self.assertEqual(hash(0x555555555, 15), 0x46E3)
        self.assertEqual(hash(0xF0F0F0F0F, 15), 0x7788)
        self.assertEqual(hash(0o214366217062, 15), 0x70EE)
        self.assertEqual(hash(0o633144256060, 15), 0x252E)
        self.assertEqual(hash(0, 7), 0)


from encoding import filter_bcd


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


from eliza import Eliza
from util import collect_tags, join
from elizascript import ElizaScriptReader
from DOCTOR_1966_01_CACM import CACM_1966_01_DOCTOR_script
import elizascript
from cacm_1966_01_DOCTOR_TEST import CACM_1966_01_DOCTOR_test_script
from cacm_1966_conversation import cacm_1966_conversation


class TestEliza(unittest.TestCase):
    def test_eliza(self):

        # ready for spam? here it is
        self.maxDiff = None

        r = CACM_1966_01_DOCTOR_script
        try:
            status, script = ElizaScriptReader.read_script(r)
        except RuntimeError as e:
            print(f"Error loading script: {e.__str__()}")
            exit(2)

        s1 = elizascript.script_to_string(script)
        s2 = CACM_1966_01_DOCTOR_test_script
        self.assertEqual(len(script.rules), 67)
        # self.assertListEqual(s1, s2)

        tags: TagMap = collect_tags(script.rules)
        self.assertEqual(len(tags), 3)
        self.assertEqual(join(tags["BELIEF"]), "FEEL THINK BELIEVE WISH")
        self.assertEqual(join(tags["FAMILY"]), "MOTHER MOM DAD FATHER SISTER BROTHER WIFE CHILDREN")
        self.assertEqual(join(tags["NOUN"]), "MOTHER FATHER")

        eliza = Eliza(script.rules, script.mem_rule)
        for exchg in cacm_1966_conversation:
            (prompt, response) = exchg
            actualResponse = eliza.response(prompt)
            self.assertEqual(actualResponse, response)

        imagined_continuation_2023 = [
            ("My boyfriend loves me, he's not a bully.", "WHY DO YOU SAY YOUR BOYFRIEND LOVES YOU"),
            ("He annoys me sometimes, but I know he cares about me.", "YOU SAY YOU KNOW HE CARES ABOUT YOU"),
            ("That's why he wanted me to come here, because he knows I'm unhappy.", "WHY DO YOU ASK"),
            ("I didn't.", "CAN YOU ELABORATE ON THAT"),
            ("He knows I'm not getting on with my family and thought it would help me if I talked to someone.",
             "DO YOU THINK ITS LIKELY THAT YOU TALKED TO SOMEONE"),
            ("That's why I'm talking to you.", "DOES THAT QUESTION INTEREST YOU"),
            ("What question?", "WHAT IS IT YOU REALLY WANT TO KNOW"),
            (
                "How to have a good relationship with my parents.",
                "DOES THAT SUGGEST ANYTHING ELSE WHICH BELONGS TO YOU"),
            ("A brighter future?", "I AM NOT SURE I UNDERSTAND YOU FULLY"),
            ("If I could get on better with my parents I'd be a lot happier.",
             "DO YOU WISH THAT YOU COULD GET ON BETTER WITH YOUR PARENTS I'D BE A LOT HAPPIER"),
            ("I do.", "DO YOU SAY YOU DO FOR SOME SPECIAL REASON"),
            ("Not really.", "DOES THAT HAVE ANYTHING TO DO WITH THE FACT THAT YOUR MOTHER"),
            ("I'll never be as good as my sister in my mom's eyes.", "TELL ME MORE ABOUT YOUR FAMILY"),
            ("My sister did better at school than me and she's always got on better with my parents.",
             "WHO ELSE IN YOUR FAMILY DID BETTER AT SCHOOL THAN YOU AND SHE'S ALWAYS GOT ON BETTER WITH YOUR PARENTS"),
            ("It's just me and my sister.", "YOUR SISTER"),
            ("That's right.", "BUT YOUR MOTHER TAKES CARE OF YOU"),
            (
                "She does, sure. She's not mean to me. It's just little things she does, probably without even knowing she's doing them, that make me feel stupid and not as loved as my sister.",
                "WHAT ELSE COMES TO MIND WHEN YOU THINK OF YOUR SISTER"),
            ("I don't think she likes me much either.", "DON'T YOU REALLY THINK SHE LIKES YOU MUCH EITHER"),
            ("She's older than me and I was always her silly little annoying sister.", "WERE YOU REALLY"),
            ("She thought so.", "BUT YOUR FATHER"),
            ("He dotes on her too.", "PLEASE GO ON")
        ]

        for exchg in imagined_continuation_2023:
            self.assertEqual(eliza.response(exchg[0]), exchg[1])


if __name__ == '__main__':
    unittest.main()
