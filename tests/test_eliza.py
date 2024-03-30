import unittest

import elizascript
from eliza.eliza import Eliza
from elizalogic import collect_tags, ElizaConstant, join
from elizascript.eliza_script_reader import read_script
from elizascript.DOCTOR_1966_01_CACM import CACM_1966_01_DOCTOR_script
from elizascript.script import script_to_string
from tests.cacm_1966_01_DOCTOR_TEST import CACM_1966_01_DOCTOR_test_script
from tests.cacm_1966_conversation import cacm_1966_conversation


class TestEliza(unittest.TestCase):
    def test_eliza(self):
        r = CACM_1966_01_DOCTOR_script
        status, script = read_script(r)

        self.assertEqual(len(script.rules), 67)
        self.assertEqual(script_to_string(s), CACM_1966_01_DOCTOR_test_script)

        tags = ElizaConstant.TagMap(collect_tags(script.rules))
        self.assertEqual(len(tags), 3)
        self.assertEqual(join(tags["BELIEF"]), "BELIEVE FEEL THINK WISH")
        self.assertEqual(join(tags["FAMILY"]), "BROTHER CHILDREN DAD FATHER MOM MOTHER SISTER WIFE")
        self.assertEqual(join(tags["NOUN"]), "FATHER MOTHER")

        eliza = Eliza(script.rules, script.mem_rule)
        for exchg in cacm_1966_conversation:
            (prompt, response) = exchg
            self.assertEqual(eliza.response(prompt), response)

        imagined_continuation_2023 = [
            ("My boyfriend loves me, he's not a bully.", "WHY DO YOU SAY YOUR BOYFRIEND LOVES YOU"),
            ("He annoys me sometimes, but I know he cares about me.", "YOU SAY YOU KNOW HE CARES ABOUT YOU"),
            ("That's why he wanted me to come here, because he knows I'm unhappy.", "WHY DO YOU ASK"),
            ("I didn't.", "CAN YOU ELABORATE ON THAT"),
            ("He knows I'm not getting on with my family and thought it would help me if I talked to someone.", "DO YOU THINK ITS LIKELY THAT YOU TALKED TO SOMEONE"),
            ("That's why I'm talking to you.", "DOES THAT QUESTION INTEREST YOU"),
            ("What question?", "WHAT IS IT YOU REALLY WANT TO KNOW"),
            ("How to have a good relationship with my parents.", "DOES THAT SUGGEST ANYTHING ELSE WHICH BELONGS TO YOU"),
            ("A brighter future?", "I AM NOT SURE I UNDERSTAND YOU FULLY"),
            ("If I could get on better with my parents I'd be a lot happier.", "DO YOU WISH THAT YOU COULD GET ON BETTER WITH YOUR PARENTS I'D BE A LOT HAPPIER"),
            ("I do.", "DO YOU SAY YOU DO FOR SOME SPECIAL REASON"),
            ("Not really.", "DOES THAT HAVE ANYTHING TO DO WITH THE FACT THAT YOUR MOTHER"),
            ("I'll never be as good as my sister in my mom's eyes.", "TELL ME MORE ABOUT YOUR FAMILY"),
            ("My sister did better at school than me and she's always got on better with my parents.", "WHO ELSE IN YOUR FAMILY DID BETTER AT SCHOOL THAN YOU AND SHE'S ALWAYS GOT ON BETTER WITH YOUR PARENTS"),
            ("It's just me and my sister.", "YOUR SISTER"),
            ("That's right.", "BUT YOUR MOTHER TAKES CARE OF YOU"),
            ("She does, sure. She's not mean to me. It's just little things she does, probably without even knowing she's doing them, that make me feel stupid and not as loved as my sister.", "WHAT ELSE COMES TO MIND WHEN YOU THINK OF YOUR SISTER"),
            ("I don't think she likes me much either.", "DON'T YOU REALLY THINK SHE LIKES YOU MUCH EITHER"),
            ("She's older than me and I was always her silly little annoying sister.", "WERE YOU REALLY"),
            ("She thought so.", "BUT YOUR FATHER"),
            ("He dotes on her too.", "PLEASE GO ON")
        ]

        for exchg in imagined_continuation_2023:
            self.assertEqual(eliza.response(exchg[0]), exchg[1])

if __name__ == '__main__':
    unittest.main()
