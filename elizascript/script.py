from typing import List

from elizalogic.RuleMemory import RuleMemory
from elizalogic import ElizaConstant

## SCRIPT: This class holds a parsed eliza profile, including a map of rules and a conversation memory.


class Script:

    def __init__(self):
        # ELIZA's opening remarks e.g. "HOW DO YOU DO.  PLEASE TELL ME YOUR PROBLEM"
        self.hello_message: List[str] = []
        # maps keywords -> transformation rules
        self.rules: ElizaConstant.RuleMap = {}
        # the one and only special case MEMORY rule.
        self.mem_rule: RuleMemory = RuleMemory()
