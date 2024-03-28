from typing import Dict, Optional, List, Any
from elizalogic import RuleBase


class ElizaConstant:

    RuleMap = Dict[str, Optional[Any]]
    TagMap = Dict[str, List[str]]
    # Define the special NONE rule
    SPECIAL_RULE_NONE = "zNONE"

    # Define the trace prefix
    TRACE_PREFIX = " | "