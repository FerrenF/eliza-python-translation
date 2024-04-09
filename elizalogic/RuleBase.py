from .constant import ElizaConstant
from .transform import Transform
from typing import List

class RuleBase:
    def __init__(self, keyword: str, word_substitution: str, precedence: int):
        self.keyword = keyword
        self.word_substitution = word_substitution
        self.precedence = precedence
        self.transformations: List[Transform] = []

    def add_transformation_rule(self, decomposition: List[str], reassembly_rules: List[List[str]]):
        """Add a transformation rule associated with this rule."""
        self.transformations.append(Transform(decomposition, reassembly_rules))

    def word_substitute(self, word: str) -> str:
        """Apply word substitution if applicable."""
        if word == self.keyword and self.word_substitution:
            return self.word_substitution
        return word

    def apply_transformation(self, words: List[str], tags: ElizaConstant.TagMap, link_keyword: str) -> (str, List[str]):
        """Apply transformation rules to input words."""
        for decomposition, reassembly_rules in self.transformations:
            # Implementation of decomposition and reassembly
            pass
        return " ".join(words)  # Placeholder for the transformed sentence

    def has_transformation(self):
        return False

    def dlist_tags(self) -> List[str]:
        """Get DLIST tags associated with this rule."""
        return []  # Placeholder for DLIST tags

    def to_string(self) -> str:
        """Convert the rule to a string representation."""
        return f"Rule: Keyword={self.keyword}, Substitution={self.word_substitution}, Precedence={self.precedence}"

    def trace(self)-> str:
        return ""
