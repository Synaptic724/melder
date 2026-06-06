from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CodegenPlanDiscovery:
    """
    Discovery result for one codegen-plan selection pass.

    Purpose:
        Hold the planner's current selected plan strategy id plus one compact
        reason describing why that strategy was chosen.
    """

    selected_strategy_id: str
    discovery_reason: str
