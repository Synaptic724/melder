from typing import FrozenSet
from typing import Tuple

MANIFEST_VERSION: str
BUILT_FOR_VERSION: str
SOURCE_SHA256: str
MANIFEST_ENTRY_COUNT: int
INTERNAL_MANIFEST: FrozenSet[Tuple[str, str]]
