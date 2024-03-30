from typing import List, Dict

from elizalogic.RuleKeyword import RuleKeyword
from elizalogic.RuleMemory import RuleMemory
from elizalogic import ElizaConstant, join


## SCRIPT: This class holds a parsed eliza profile, including a map of rules and a conversation memory.


class Script:

    def __init__(self):
        # ELIZA's opening remarks e.g. "HOW DO YOU DO.  PLEASE TELL ME YOUR PROBLEM"
        self.hello_message: List[str] = []
        # maps keywords -> transformation rules
        self.rules: Dict[str, RuleKeyword] = {}
        # the one and only special case MEMORY rule.
        self.mem_rule: RuleMemory = RuleMemory()


def script_to_string(s: Script):
    result = str()
    result += "(" + join(s.hello_message) + ")\n"
    for (k, v) in s.rules.items():
        result += v.to_string()
    result += s.mem_rule.to_string()
    return result
