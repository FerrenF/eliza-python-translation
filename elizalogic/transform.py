from typing import List

class Transform:
    def __init__(self, decomposition: List[str], reassembly_rules: List[List[str]]):
        self.decomposition = decomposition
        self.reassembly_rules = reassembly_rules
        self.next_reassembly_rule = 0

    def __str__(self):
        return f"Transform: Decomposition={self.decomposition}, Reassembly Rules={self.reassembly_rules},\
         Next Reassembly Rule={self.next_reassembly_rule}"
