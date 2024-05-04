import unittest

from elizaconstant import TagMap
from elizautil import words_in_list, to_int, slip_match
from elizascript import StringIOWithPeek
from elizalogic import reassemble_from_rule
from elizaencoding import hash, last_chunk_as_bcd
from elizaencoding import filter_bcd



class TestInList(unittest.TestCase):
    def setUp(self):
        self.tags = {
            "FAMILY": ["MOTHER", "FATHER", "SISTER", "BROTHER", "WIFE", "CHILDREN"],
            "NOUN": ["MOTHER", "FATHER", "FISH", "FOUL"]
        }

    def test_inlist(self):
        self.assertTrue(words_in_list("MOTHER", "(/FAMILY)", self.tags))
        self.assertTrue(words_in_list("FATHER", "(/FAMILY)", self.tags))
        self.assertTrue(words_in_list("SISTER", "(/FAMILY)", self.tags))
        self.assertTrue(words_in_list("BROTHER", "( / FAMILY )", self.tags))
        self.assertTrue(words_in_list("WIFE", "(/FAMILY)", self.tags))
        self.assertTrue(words_in_list("CHILDREN", "(/FAMILY)", self.tags))
        self.assertFalse(words_in_list("FISH", "(/FAMILY)", self.tags))
        self.assertFalse(words_in_list("FOUL", "(/FAMILY)", self.tags))

        self.assertTrue(words_in_list("MOTHER", "(/NOUN)", self.tags))
        self.assertTrue(words_in_list("FATHER", "(/NOUN)", self.tags))
        self.assertFalse(words_in_list("SISTER", "(/NOUN)", self.tags))
        self.assertFalse(words_in_list("BROTHER", "(/NOUN)", self.tags))
        self.assertFalse(words_in_list("WIFE", "(/NOUN)", self.tags))
        self.assertFalse(words_in_list("CHILDREN", "(/NOUN)", self.tags))
        self.assertTrue(words_in_list("FISH", "(/NOUN)", self.tags))
        self.assertTrue(words_in_list("FOUL", "(/NOUN)", self.tags))

        self.assertTrue(words_in_list("MOTHER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("FATHER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("SISTER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("BROTHER", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("WIFE", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("CHILDREN", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("FISH", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("FOUL", "(/ NOUN  FAMILY )", self.tags))

        self.assertFalse(words_in_list("MOTHER", "(/NONEXISTANTTAG)", self.tags))
        self.assertTrue(words_in_list("MOTHER", "(/NON FAMILY TAG)", self.tags))

        self.assertFalse(words_in_list("DEPRESSED", "(/NOUN FAMILY)", self.tags))
        self.assertTrue(words_in_list("SAD", "(*SAD HAPPY DEPRESSED)", self.tags))
        self.assertTrue(words_in_list("HAPPY", "(*SAD HAPPY DEPRESSED)", self.tags))
        self.assertTrue(words_in_list("DEPRESSED", "(*SAD HAPPY DEPRESSED)", self.tags))
        self.assertTrue(words_in_list("SAD", "( * SAD HAPPY DEPRESSED )", self.tags))
        self.assertTrue(words_in_list("HAPPY", "( * SAD HAPPY DEPRESSED )", self.tags))
        self.assertTrue(words_in_list("DEPRESSED", "( * SAD HAPPY DEPRESSED )", self.tags))
        self.assertFalse(words_in_list("DRUNK", "( * SAD HAPPY DEPRESSED )", self.tags))

        self.assertTrue(words_in_list("WONDER", "(*HAPPY ELATED EXCITED GOOD WONDERFUL)", self.tags))
        self.assertTrue(words_in_list("FUL", "(*HAPPY ELATED EXCITED GOOD WONDERFUL)", self.tags))
        self.assertTrue(words_in_list("D", "(*HAPPY ELATED EXCITED GOOD WONDERFUL)", self.tags))


class TestToInt(unittest.TestCase):
    def test_to_int(self):
        self.assertEqual(to_int("0"), 0)
        self.assertEqual(to_int("1"), 1)
        self.assertEqual(to_int("2023"), 2023)
        self.assertEqual(to_int("-42"), -1)
        self.assertEqual(to_int("int"), -1)


class TestMadMatchFunction(unittest.TestCase):

    def run_test_case(self, words, pattern, expected, equality=True, tags={}):
        success, matching_components = slip_match(tags, pattern, words)
        self.assertEqual(success, equality)
        self.assertEqual(matching_components, expected)

    def test_mad_match_function(self):
        test_cases = [
            # Test case 1
            (["HELLO", "WORLD"], ["0", "0", "WORLD"], ["", "HELLO", "WORLD"], True),
            # Test case 2
            (["HELLO", "WORLD"], ["0", "0", "1"], ["", "HELLO", "WORLD"], True),
            # Test case 3
            (["HELLO", "WORLD"], ["HELLO", "0", "0", "WORLD"], ["HELLO", "", "", "WORLD"], True),
            # Test case 4
            (["'ELLO", "'ELLO"], ["0", "'ELLO"], ["'ELLO", "'ELLO"], True),
            # Test case 5
            (["'ELLO", "'ELLO"], ["0", "'ELLO", "0"], ["", "'ELLO", "'ELLO"], True),
            # Test case 6
            (["YOU", "NEED", "NICE", "FOOD"], ["0", "YOU", "(*WANT NEED)", "0"], ["", "YOU", "NEED", "NICE FOOD"], True),
            # Test case 7
            (["YOU", "WANT", "NICE", "FOOD"], ["0", "0", "YOU", "(*WANT NEED)", "0"],
             ["", "", "YOU", "WANT", "NICE FOOD"], True),
            # Test case 8
            (["YOU", "WANT", "NICE", "FOOD"], ["1", "(*WANT NEED)", "0"], ["YOU", "WANT", "NICE FOOD"], True),
            # Test case 9
            (["YOU", "WANT", "NICE", "FOOD"], ["1", "(*WANT NEED)", "1"], [], False),
            # Test case 10
            (["YOU", "WANT", "NICE", "FOOD"], ["1", "(*WANT NEED)", "2"], ["YOU", "WANT", "NICE FOOD"], True),
            # Test case 11

            (["CONSIDER", "YOUR", "AGED", "MOTHER", "AND", "FATHER", "TOO"],
             ["0", "YOUR", "0", "(* FATHER MOTHER)", "0"],
             ["CONSIDER", "YOUR", "AGED", "MOTHER", "AND FATHER TOO"],
             True),

            # Test case 12
            (["MOTHER", "AND", "FATHER", "MOTHER"],
             ["0", "(* FATHER MOTHER)", "(* FATHER MOTHER)", "0"],
             ["MOTHER AND", "FATHER", "MOTHER", ""],
             True),

            # Test case 13
            (["FIRST", "AND", "LAST", "TWO", "WORDS"],
             ["2", "0", "2"],
             ["FIRST AND", "LAST", "TWO WORDS"],
             True),

            # Test case 14
            (["THE", "NAME", "IS", "BOND", "JAMES", "BOND", "OR", "007", "IF", "YOU", "PREFER"],
             ["0", "0", "7"],
             ["", "THE NAME IS BOND", "JAMES BOND OR 007 IF YOU PREFER"],
             True),

            # Test case 15
            (["ITS", "MARY", "ITS", "NOT", "MARY", "IT", "IS", "MARY", "TOO"],
             ["0", "ITS", "0", "MARY", "1"],
             ["", "ITS", "MARY ITS NOT MARY IT IS", "MARY", "TOO"],
             True),

            # Test case 16
            (["YOU", "KNOW", "THAT", "I", "KNOW", "YOU", "HATE", "I", "AND", "YOU", "LIKE", "I", "TOO"],
             ["0", "YOU", "0", "I", "0"],
             ["", "YOU", "KNOW THAT", "I", "KNOW YOU HATE I AND YOU LIKE I TOO"],
             True),

            # Test case 17
            (["MARY", "HAD", "A", "LITTLE", "LAMB", "ITS", "PROBABILITY", "WAS", "ZERO"],
             ["MARY", "2", "2", "ITS", "1", "0"],
             ["MARY", "HAD A", "LITTLE LAMB", "ITS", "PROBABILITY", "WAS ZERO"],
             True),

            # Test case 18
            (["MARY", "HAD", "A", "LITTLE", "LAMB", "ITS", "PROBABILITY", "WAS", "ZERO"],
             ["1", "0", "2", "ITS", "0"],
             ["MARY", "HAD A", "LITTLE LAMB", "ITS", "PROBABILITY WAS ZERO"],
             True),

            # Test case 19
            ([], [], [], True),

            # Test case 20
            ([], ["0"], [""], True),

            # Test case 21
            (["MARY", "HAD", "A", "LITTLE", "LAMB"], ["MARY", "HAD", "A", "LITTLE", "LAMB"],
             ["MARY", "HAD", "A", "LITTLE", "LAMB"], True),

            # Test case 22
            (["HAD", "MARY", "A", "LITTLE", "LAMB"], ["MARY", "HAD", "A", "LITTLE", "LAMB"], [], False),

            # Test case 23
            (["MARY", "HAD", "A", "LAMB"], ["MARY", "HAD", "A", "LITTLE", "LAMB"], [], False),

            # Test case 24
            (["MARY", "HAD", "A", "LITTLE", "LAMB", "CALLED", "WOOLY"], ["MARY", "HAD", "A", "LITTLE", "LAMB"], [],
             False),

            # Test case 25
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["WHEN", "WILL", "2", "MEET"],
             ["WHEN", "WILL", "WE THREE", "MEET"], True),

            # Test case 26
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["WHEN", "1", "2", "MEET"], ["WHEN", "WILL", "WE THREE", "MEET"],
             True),

            # Test case 27
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["1", "1", "2", "1"], ["WHEN", "WILL", "WE THREE", "MEET"], True),

            # Test case 28
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["3", "2"], ["WHEN WILL WE", "THREE MEET"], True),

            # Test case 29
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["3", "0"], ["WHEN WILL WE", "THREE MEET"], True),

            # Test case 30
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["5"], ["WHEN WILL WE THREE MEET"], True),

            # Test case 31
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "5"], ["", "WHEN WILL WE THREE MEET"], True),

            # Test case 32
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["5", "0"], ["WHEN WILL WE THREE MEET", ""], True),

            # Test case 33
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["1", "0"], ["WHEN", "WILL WE THREE MEET"], True),

            # Test case 34
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1"], ["WHEN WILL WE THREE", "MEET"], True),

            # Test case 35
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["1", "1", "0"], ["WHEN", "WILL", "WE THREE MEET"], True),

            # Test case 36
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0"], ["", "WHEN", "WILL WE THREE MEET"], True),

            # Test case 37
            (
            ["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1"], ["", "WHEN", "WILL WE THREE", "MEET"],
            True),

            # Test case 38
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0"],
             ["", "WHEN", "", "WILL", "WE THREE MEET"], True),

            # Test case 39
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0", "1"],
             ["", "WHEN", "", "WILL", "WE THREE", "MEET"], True),

            # Test case 40
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0", "1", "0"],
             ["", "WHEN", "", "WILL", "", "WE", "THREE MEET"], True),

            # Test case 41
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0", "1", "0", "1"],
             ["", "WHEN", "", "WILL", "", "WE", "THREE", "MEET"], True),

            # Test case 42
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0", "1", "0", "1", "0"],
             ["", "WHEN", "", "WILL", "", "WE", "", "THREE", "MEET"], True),

            # Test case 43
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0", "1", "0", "1", "0", "1"],
             ["", "WHEN", "", "WILL", "", "WE", "", "THREE", "", "MEET" ], True),

            # Test case 44
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0", "1", "0", "1", "0", "1", "0"],
             ["", "WHEN", "", "WILL", "", "WE", "", "THREE", "", "MEET", "" ], True),

            # Test case 45
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["0", "1", "0", "1", "0", "1", "0", "1", "0", "1", "0", "1"], [],
             False),

            # Test case 46
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["6"], [], False),



            # Test case 47
            (["WHEN", "WILL", "WE", "THREE", "MEET"], ["1", "WHEN", "0"], [], False),

            # Test case 48
            (["IT'S", "MY", "EASTEREGG", "YUM"], ["1", "1", "1", "0", "1"], ["IT'S", "MY", "EASTEREGG", "", "YUM"],
             True),

            # Test case 49
            (["IT'S", "MY", "EASTEREGG", "YUM"], ["IT'S", "1", "1", "0", "1"], ["IT'S", "MY", "EASTEREGG", "", "YUM"],
             True),

            # Test case 50
            (["IT'S", "MY", "EASTEREGG", "YUM"], ["1", "MY", "1", "0", "1"], ["IT'S", "MY", "EASTEREGG", "", "YUM"],
             True),

            # Test case 51
            (["IT'S", "MY", "EASTEREGG", "YUM"], ["1", "1", "EASTEREGG", "0", "1"],
             ["IT'S", "MY", "EASTEREGG", "", "YUM"], True),

            # Test case 52
            (["IT'S", "MY", "EASTEREGG", "YUM"], ["1", "MY", "EASTEREGG", "0", "1"],
             ["IT'S", "MY", "EASTEREGG", "", "YUM"], True),

            # Test case 53
            (["IT'S", "MY", "EASTEREGG", "YUM"], ["IT'S", "MY", "EASTEREGG", "0", "1"],
             ["IT'S", "MY", "EASTEREGG", "", "YUM"], True),

            # Test case 54
            (["IT'S", "MY", "EASTEREGG", "YUM"], ["IT'S", "MY", "EASTEREGG", "YUM"], ["IT'S", "MY", "EASTEREGG", "YUM"],
             True),

            # Test case 55
            (["X", "X", "A", "X", "X", "A"], ["0", "A", "0", "A"], ["X X", "A", "X X", "A"], True),

            # Test case 56
            (["X", "X", "A", "X", "X", "A", "X", "X", "A"], ["0", "A", "0", "A"], ["X X", "A", "X X A X X", "A"], True),

            # Test case 57
            (
            ["X", "X", "A", "X", "X", "A", "X", "X", "A"], ["0", "A", "0", "A", "0"], ["X X", "A", "X X", "A", "X X A"],
            True),

            # Test case 58
            (["MY", "FAIR", "LADY"], ["MY", "(*FAIR GOOD)", "LADY"], ["MY", "FAIR", "LADY"], True),

            # Test case 59
            (["MY", "GOOD", "LADY"], ["MY", "(*FAIR GOOD)", "LADY"], ["MY", "GOOD", "LADY"], True),

            # Test case 60
            (["MY", "LADY"], ["MY", "(*FAIR GOOD)", "LADY"], [], False),

            # Test case 61
            (["MY", "FAIR", "GOOD", "LADY"], ["MY", "(*FAIR GOOD)", "LADY"], [], False),


        ]

        for words, pattern, expected, equality in test_cases:
            with self.subTest(words=words, pattern=pattern, expected=expected, equality=equality):
                self.run_test_case(words, pattern, expected, equality)

        tag_map = dict({ "FAMILY" : ["MOTHER", "FATHER"],
        "NOUN" : ["MOTHER", "FATHER"],
        "BELIEF" : ["FEEL"]})
        extended_test_cases = [
            # Test case 62
            (["MY", "MOTHER", "LOVES", "ME"], ["0", "(/FAMILY)", "0"], ["MY", "MOTHER", "LOVES ME"], True),

            # Test case 63
            (["MY", "MOTHER", "LOVES", "ME"], ["0", "(/NOUN)", "0"], ["MY", "MOTHER", "LOVES ME"], True),

            # Test case 64
            (["MY", "MOTHER", "LOVES", "ME"], ["0", "(/BELIEF FAMILY)", "0"], ["MY", "MOTHER", "LOVES ME"], True),

            # Test case 65
            (["MY", "MOTHER", "LOVES", "ME"], ["0", "(/BELIEF)", "0"], [], False),
        ]

        for words, pattern, expected, equality in extended_test_cases:
            with self.subTest(words=words, pattern=pattern, expected=expected, equality=equality, tags=tag_map):
                self.run_test_case(words, pattern, expected, equality, tags=tag_map)



class TestScriptReader(unittest.TestCase):
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



class TestReassamble(unittest.TestCase):

    def test_reassemble(self):
        matching_components = [
            "MARY", "HAD A", "LITTLE LAMB", "ITS", "PROBABILITY", "WAS ZERO"
        ]

        # Test pattern from the ASSMBL function description in the SLIP manual
        reassembly_rule = ["DID", "1", "HAVE", "A", "3"]
        expected = ["DID", "MARY", "HAVE", "A", "LITTLE", "LAMB"]
        result = reassemble_from_rule(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "1", "1"]
        expected = ["MARY", "MARY", "MARY"]
        result = reassemble_from_rule(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "-1", "1"]
        expected = ["MARY", "-1", "MARY"]
        result = reassemble_from_rule(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "0", "1"]
        expected = ["MARY", "THINGY", "MARY"]
        result = reassemble_from_rule(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "6", "1"]
        expected = ["MARY", "WAS", "ZERO", "MARY"]
        result = reassemble_from_rule(reassembly_rule, matching_components)
        assert result == expected

        reassembly_rule = ["1", "7", "1"]
        expected = ["MARY", "THINGY", "MARY"]
        result = reassemble_from_rule(reassembly_rule, matching_components)
        assert result == expected



class TestHashFunc(unittest.TestCase):

    def test_last_chunk_as_bcd(self):
        # Test cases with expected results
        self.assertEqual(last_chunk_as_bcd(""), int(0o606060606060))  # _ _ _ _ _ _)
        self.assertEqual(last_chunk_as_bcd("X"), int(0o676060606060))  # X _ _ _ _ _
        self.assertEqual(last_chunk_as_bcd("HERE"), int(0o302551256060))  # H E R E _ _
        self.assertEqual(last_chunk_as_bcd("ALWAYS"), int(0o214366217062))  # A L W A Y S
        self.assertEqual(last_chunk_as_bcd("INVENTED"), int(0o252460606060))# E D _ _ _ _ # why doesnt this one pass
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



class TestBCDFilter(unittest.TestCase):
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
from elizautil import collect_tags, eliza_specific_join
from elizascript import ElizaScriptReader
from DOCTOR_1966_01_CACM import CACM_1966_01_DOCTOR_script
import elizascript
from eliza_test_conversations import CACM_1966_01_DOCTOR_test_script
from eliza_test_conversations import cacm_1966_conversation


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
        self.assertEqual(eliza_specific_join(tags["BELIEF"]), "FEEL THINK BELIEVE WISH")
        self.assertEqual(eliza_specific_join(tags["FAMILY"]), "MOTHER MOM DAD FATHER SISTER BROTHER WIFE CHILDREN")
        self.assertEqual(eliza_specific_join(tags["NOUN"]), "MOTHER FATHER")

        eliza = Eliza(script)
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

            (response, real) = (eliza.response(exchg[0]), exchg[1])
            self.assertEqual(response, real)


if __name__ == '__main__':
    unittest.main()
