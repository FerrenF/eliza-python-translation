from typing import List, Dict

import hollerith
from elizalogic.constant import SPECIAL_RULE_NONE, TRACE_PREFIX
from elizalogic.transform import Transform
from elizalogic.RuleBase import RuleBase
from elizalogic.util import reassemble, match, join


class RuleMemory(RuleBase):

    def __init__(self, keyword: str = ""):
        super().__init__(keyword, "", 0)
        self.memories: List[str] = []
        self.trace = ""
        self._activity = False

    # We just want to know if the rule has been used?
    def __eq__(self, other):
        self._activity = True

    def create_memory(self, keyword: str, words: List[str], tags: Dict[str, List[str]]):
        if keyword != self.keyword:
            return

        # // JW says rules are selected at random [page 41 (f)]
        # // But the ELIZA code shows that rules are actually selected via a HASH
        # // function on the last word of the user's input text.
        assert len(self.transformations) == self.num_transformations

        transformation = self.transformations[hollerith.hash(hollerith.last_chunk_as_bcd(words[-1]), 2)]
        constituents:List[str] = []
        if not match(tags, transformation.decomposition, words, constituents):
            return

        new_memory = join(reassemble(transformation.reassembly_rules[0], constituents))
        self.trace += f"{TRACE_PREFIX}new memory: {new_memory}\n"
        self.memories.append(new_memory)

    def is_valid(self) -> bool:
        return self._activity and self.memory_exists()

    def memory_exists(self) -> bool:
        return len(self.memories) > 0

    def recall_memory(self) -> str:
        return self.memories.pop(0) if self.memory_exists else ""

    def to_string(self) -> str:
        sexp = f"(MEMORY {self.keyword}"
        for transform in self.transformations:
            sexp += f"\n    ({' '.join(transform.decomposition)} = {' '.join(transform.reassembly_rules[0])})"
        sexp += ")\n"
        return sexp

    def clear_trace(self):
        self.trace = ""

    def trace_memory_stack(self) -> str:
        if not self.memories:
            return f"{TRACE_PREFIX}memory queue: <empty>\n"
        else:
            return f"{TRACE_PREFIX}memory queue:\n" + "\n".join(f"{TRACE_PREFIX}  {m}" for m in self.memories)

    # the MEMORY rule must have this number of transformations
    num_transformations = 4