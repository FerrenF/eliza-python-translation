from typing import List, Union

from elizalogic.RuleMemory import RuleMemory
from elizalogic.constant import RuleMap


class Script:
    def __init__(self):
        # ELIZA's opening remarks e.g. "HOW DO YOU DO.  PLEASE TELL ME YOUR PROBLEM"
        self.hello_message: List[str] = []
        # maps keywords -> transformation rules
        self.rules: RuleMap = {}

        self.mem_rule: RuleMemory