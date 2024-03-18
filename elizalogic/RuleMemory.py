from typing import List, Dict
from elizalogic.constant import SPECIAL_RULE_NONE, TRACE_PREFIX
from elizalogic.transform import Transform
from elizalogic.RuleBase import RuleBase
from elizalogic.util import reassemble, match


class RuleMemory(RuleBase):
    def __init__(self, keyword: str):
        super().__init__(keyword, "", 0)
        self.memories: List[str] = []
        self.trace = ""

    def create_memory(self, keyword: str, words: List[str], tags: Dict[str, List[str]]):
        if keyword != self.keyword:
            return

        assert len(self.transformations) == self.num_transformations

        transformation = self.transformations[hash(words[-1], 2)]
        constituents = []
        if not match(tags, transformation.decomposition, words, constituents):
            return

        new_memory = str.join(reassemble(transformation.reassembly_rules[0], constituents))
        self.trace += f"{TRACE_PREFIX}new memory: {new_memory}\n"
        self.memories.append(new_memory)

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