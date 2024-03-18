from typing import Dict, Optional, List
from elizalogic.RuleBase import RuleBase

RuleMap = Dict[str, RuleBase]
TagMap = Dict[str, List[str]]
# Define the special NONE rule
SPECIAL_RULE_NONE = "zNONE"

# Define the trace prefix
TRACE_PREFIX = " | "