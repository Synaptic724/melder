from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, slots=True)
class CodegenCreationDiscovery:
    """
    Discovery result for one codegen-creation selection pass.

    Purpose:
        Hold the ordered codegen-creation strategy chain plus one compact
        reason describing why that chain was chosen.
    """

    selected_strategy_ids: Tuple[str, ...]
    discovery_reason: str
