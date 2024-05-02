from typing import Optional, List, Any, OrderedDict

# Type definitins.
RuleMap = OrderedDict[str, Optional[Any]]
TagMap = OrderedDict[str, List[str]]


# Constants
SPECIAL_RULE_NONE = "zNONE"
TRACE_PREFIX = " | "
