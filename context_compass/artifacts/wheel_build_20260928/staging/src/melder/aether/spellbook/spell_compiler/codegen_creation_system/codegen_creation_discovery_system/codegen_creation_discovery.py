from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, slots=True)
class CodegenCreationDiscovery:
    """
    Discovery result for one codegen-creation selection pass.

    Purpose:
        Hold the ordered codegen-creation strategy chain plus the concrete
        codegen style phase 11 selected for the current plan family.

    Contract:
        - `selected_strategy_ids` is the ordered creation strategy chain to
          execute.
        - `selected_codegen_style_id` is the concrete codegen style chosen for
          this creation pass.
        - `discovery_reason` is compact provenance for the selection.
        - Phase 11 owns the final concrete codegen-style choice for the already
          selected phase-10 plan family.
        - This discovery result does not widen the runtime contract; it only
          selects how the final two executors will be built.
    """

    selected_strategy_ids: Tuple[str, ...]
    discovery_reason: str
    selected_codegen_style_id: str = "unknown"
