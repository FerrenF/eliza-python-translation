import unittest
from io import StringIO

import elizascript
from elizalogic import ElizaConstant
from elizalogic import collect_tags
from elizascript import StringIOWithPeek
from elizascript.eliza_script_reader import ElizaScriptReader
from unittest.mock import patch

from elizascript.script import script_to_string


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
        self.assertEqual(script_to_string(s), self.recreated_script_text)

        # Ensure tags are collected correctly
        tags: ElizaConstant.TagMap = collect_tags(s.rules)
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags["TAG1"],
                         ["K01", "K12", "K14", "K16", "K17", "K22", "K24", "K26", "K27", "K32", "K34", "K36", "K37",
                          "K38"])
        self.assertEqual(tags["TAG2"],
                         ["K01", "K12", "K14", "K16", "K17", "K22", "K24", "K27", "K32", "K34", "K36", "K37", "K38"])
        self.assertEqual(tags["TAG3"], ["K32"])


        tests = [
                ("","Script error on line 1: expected '('"),
                ("(","Script error on line 1: expected ')'"),
                ("()","Script error: no NONE rule specified; see Jan 1966 CACM page 41"),
                ("()\n(","Script error on line 2: expected keyword|MEMORY|NONE"),
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

if __name__ == '__main__':
    unittest.main()
