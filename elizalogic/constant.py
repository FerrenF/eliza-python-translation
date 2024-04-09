from typing import Optional, List, Any, OrderedDict
class ElizaConstant:

    RuleMap = OrderedDict[str, Optional[Any]]
    TagMap = OrderedDict[str, List[str]]
    # Define the special NONE rule
    SPECIAL_RULE_NONE = "zNONE"

    # Define the trace prefix
    TRACE_PREFIX = " | "