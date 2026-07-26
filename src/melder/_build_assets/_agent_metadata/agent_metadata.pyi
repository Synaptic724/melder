from typing import Dict
from typing import FrozenSet
from typing import Tuple

MANIFEST_VERSION: str
BUILT_FOR_VERSION: str
SOURCE_SHA256: str
MARKED_COUNT: int
EXEMPT_COUNT: int
PENDING_COUNT: int
AGENT_METADATA: Dict[Tuple[str, str], Tuple[str, str]]
EXEMPT: FrozenSet[Tuple[str, str]]
PENDING: FrozenSet[Tuple[str, str]]
CLASS_BASES: Dict[Tuple[str, str], Tuple[str, ...]]
