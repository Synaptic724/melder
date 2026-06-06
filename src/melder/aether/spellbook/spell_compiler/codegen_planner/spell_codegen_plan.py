from typing import Any, Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SpellCodegenPlan(Cleanable):
    """
    Planner-owned codegen plan container for one spell.

    Purpose:
        Hold the planner output lanes for one spell:
        `no_overrides` and `overrides`.

    Contract:
        - Lives on `SpellCompilerArtifact` as generic codegen output.
        - Stores planner provenance plus 2 lane homes.
        - `plan_family_id` is the higher-level planning family chosen by phase
          10 discovery.
        - `candidate_codegen_style_ids` is the bounded set of codegen styles
          phase 11 may consider for this plan.
        - Does not store final emitted executors.
    """

    __slots__ = Cleanable.__slots__ + [
        "processor_strategy_ids",
        "plan_strategy_ids",
        "plan_family_id",
        "candidate_codegen_style_ids",
        "no_overrides_plan",
        "overrides_plan",
        "metadata",
    ]

    def __init__(
            self,
            *,
            processor_strategy_ids: Tuple[str, ...],
            plan_strategy_ids: Tuple[str, ...],
            plan_family_id: Optional[str] = None,
            candidate_codegen_style_ids: Tuple[str, ...] = (),
            no_overrides_plan: Optional[Any] = None,
            overrides_plan: Optional[Any] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Build one planner-owned codegen plan container.

        Contract:
            - Lane payloads may be `None` while planner strategies are still a
              scaffold.
            - `plan_family_id` may be `None` until discovery has executed.
            - `metadata` is the mutable diagnostics/provenance bag.
        """
        super().__init__()
        self.processor_strategy_ids: Tuple[str, ...] = processor_strategy_ids
        self.plan_strategy_ids: Tuple[str, ...] = plan_strategy_ids
        self.plan_family_id: Optional[str] = plan_family_id
        self.candidate_codegen_style_ids: Tuple[str, ...] = (
            candidate_codegen_style_ids
        )
        self.no_overrides_plan: Optional[Any] = no_overrides_plan
        self.overrides_plan: Optional[Any] = overrides_plan
        self.metadata: Dict[str, Any] = {} if metadata is None else metadata

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
        self.metadata.clear()

        del self.processor_strategy_ids
        del self.plan_strategy_ids
        del self.plan_family_id
        del self.candidate_codegen_style_ids
        del self.no_overrides_plan
        del self.overrides_plan
        del self.metadata
