from typing import Any, Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SpellCodegenPlan(Cleanable):
    """
    Planner-owned codegen plan container for one spell.

    Purpose:
        Hold the 3 planner output lanes the planner will eventually define:
        `no_overrides`, `overrides`, and `mutation_overrides`.

    Contract:
        - Lives on `SpellCompilerArtifact` as generic codegen output.
        - Stores planner provenance plus 3 lane homes.
        - Does not pretend lane families or emitter choices are already solved
          before planner strategies exist.
    """

    __slots__ = Cleanable.__slots__ + [
        "processor_strategy_ids",
        "plan_strategy_ids",
        "no_overrides_plan",
        "overrides_plan",
        "mutation_overrides_plan",
        "metadata",
    ]

    def __init__(
            self,
            *,
            processor_strategy_ids: Tuple[str, ...],
            plan_strategy_ids: Tuple[str, ...],
            no_overrides_plan: Optional[Any],
            overrides_plan: Optional[Any],
            mutation_overrides_plan: Optional[Any],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one planner-owned codegen plan container.

        Contract:
            - Lane payloads may be `None` while planner strategies are still a
              scaffold.
            - `metadata` is the mutable diagnostics/provenance bag.
        """
        super().__init__()
        self.processor_strategy_ids: Tuple[str, ...] = processor_strategy_ids
        self.plan_strategy_ids: Tuple[str, ...] = plan_strategy_ids
        self.no_overrides_plan: Optional[Any] = no_overrides_plan
        self.overrides_plan: Optional[Any] = overrides_plan
        self.mutation_overrides_plan: Optional[Any] = mutation_overrides_plan
        self.metadata: Dict[str, Any] = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the codegen plan container.

        Contract:
            - Idempotent cleanup.
            - Clears mutable metadata.
            - Best-effort cleans non-None lane payloads when they expose
              `cleanup()`.
        """
        if self._cleaned:
            return

        self._cleaned = True
        if self.no_overrides_plan is not None:
            try:
                self.no_overrides_plan.cleanup()
            except Exception:
                pass
        if self.overrides_plan is not None:
            try:
                self.overrides_plan.cleanup()
            except Exception:
                pass
        if self.mutation_overrides_plan is not None:
            try:
                self.mutation_overrides_plan.cleanup()
            except Exception:
                pass
        self.metadata.clear()

        del self.processor_strategy_ids
        del self.plan_strategy_ids
        del self.no_overrides_plan
        del self.overrides_plan
        del self.mutation_overrides_plan
        del self.metadata
