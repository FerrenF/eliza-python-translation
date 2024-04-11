from typing import Dict, Optional, List, Any, OrderedDict

RuleMap = OrderedDict[str, Optional[Any]]
TagMap = OrderedDict[str, List[str]]
# Define the special NONE rule
SPECIAL_RULE_NONE = "zNONE"

# Define the trace prefix
TRACE_PREFIX = " | "