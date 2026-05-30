from typing import Any, Dict, Optional, Sequence, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SpellCodegenPlan(Cleanable):
    """
    Compiler-owned Phase 12 output for one spell.

    Purpose:
        Hold the codegen-ready plan that later backend-emitter work can consume
        without re-examining the full spell/artifact surface.

    Contract:
        - Lives on `SpellCompilerArtifact` as the Phase 12 output.
        - Stores the selected lane families and compile hints for one spell.
        - Remains intentionally strategy-light in this first scaffold slice:
          the initial plan is a meaningful baseline plan, not yet a deeply
          specialized family product.
        - Later Phase 12 strategies may replace or enrich this plan.

    Ownership:
        - Compiler-owned and stored on `SpellCompilerArtifact`.
        - Intended to be consumed later by backend-emitter and runtime-binding
          layers.

    Lifecycle:
        - Built during Phase 12.
        - Cleared when the owning compiler artifact clears later-phase state.
    """

    __slots__ = Cleanable.__slots__ + [
        "processor_strategy_ids",
        "plan_strategy_ids",
        "no_overrides_family",
        "overrides_family",
        "mutation_family",
        "route_key",
        "supports_no_overrides_lane",
        "supports_overrides_lane",
        "supports_mutation_lane",
        "requires_spellspace_request",
        "execution_plan_dispatch_route",
        "step_count",
        "unique_spell_count",
        "max_occurrence_depth",
        "max_dependency_count",
        "fast_transient_no_overrides_enabled",
        "lock_strategy_hint",
        "registration_strategy_hint",
        "call_mode_hint",
        "emitter_family_id",
        "fallback_reason",
        "step_rows",
        "metadata",
    ]

    def __init__(
            self,
            *,
            processor_strategy_ids: Tuple[str, ...],
            plan_strategy_ids: Tuple[str, ...],
            no_overrides_family: Optional[str],
            overrides_family: Optional[str],
            mutation_family: Optional[str],
            route_key: str,
            supports_no_overrides_lane: bool,
            supports_overrides_lane: bool,
            supports_mutation_lane: bool,
            requires_spellspace_request: bool,
            execution_plan_dispatch_route: Optional[str],
            step_count: Optional[int],
            unique_spell_count: Optional[int],
            max_occurrence_depth: Optional[int],
            max_dependency_count: Optional[int],
            fast_transient_no_overrides_enabled: bool,
            lock_strategy_hint: Optional[str],
            registration_strategy_hint: Optional[str],
            call_mode_hint: Optional[str],
            emitter_family_id: Optional[str],
            fallback_reason: Optional[str],
            step_rows: Sequence[Any],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one compiler-owned Phase 12 codegen plan.

        Purpose:
            Materialize the current best compiler-owned runtime/codegen plan
            for one spell from the assessed Phase 12 processor state.

        Contract:
            - Stores lane-family, route-family, and hint data only.
            - Stores `step_rows` as an immutable tuple snapshot.
            - Stores `metadata` as a mutable diagnostics/provenance map.

        Returns:
            None.
        """
        super().__init__()
        self.processor_strategy_ids: Tuple[str, ...] = processor_strategy_ids
        self.plan_strategy_ids: Tuple[str, ...] = plan_strategy_ids
        self.no_overrides_family: Optional[str] = no_overrides_family
        self.overrides_family: Optional[str] = overrides_family
        self.mutation_family: Optional[str] = mutation_family
        self.route_key: str = route_key
        self.supports_no_overrides_lane: bool = supports_no_overrides_lane
        self.supports_overrides_lane: bool = supports_overrides_lane
        self.supports_mutation_lane: bool = supports_mutation_lane
        self.requires_spellspace_request: bool = requires_spellspace_request
        self.execution_plan_dispatch_route: Optional[str] = (
            execution_plan_dispatch_route
        )
        self.step_count: Optional[int] = step_count
        self.unique_spell_count: Optional[int] = unique_spell_count
        self.max_occurrence_depth: Optional[int] = max_occurrence_depth
        self.max_dependency_count: Optional[int] = max_dependency_count
        self.fast_transient_no_overrides_enabled: bool = (
            fast_transient_no_overrides_enabled
        )
        self.lock_strategy_hint: Optional[str] = lock_strategy_hint
        self.registration_strategy_hint: Optional[str] = (
            registration_strategy_hint
        )
        self.call_mode_hint: Optional[str] = call_mode_hint
        self.emitter_family_id: Optional[str] = emitter_family_id
        self.fallback_reason: Optional[str] = fallback_reason
        self.step_rows: Tuple[Any, ...] = tuple(step_rows)
        self.metadata: Dict[str, Any] = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the Phase 12 codegen plan.

        Contract:
            - Idempotent cleanup.
            - Clears mutable metadata.
            - Drops all remaining references so stale plans cannot be reused
              after artifact invalidation.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self.metadata.clear()

        del self.processor_strategy_ids
        del self.plan_strategy_ids
        del self.no_overrides_family
        del self.overrides_family
        del self.mutation_family
        del self.route_key
        del self.supports_no_overrides_lane
        del self.supports_overrides_lane
        del self.supports_mutation_lane
        del self.requires_spellspace_request
        del self.execution_plan_dispatch_route
        del self.step_count
        del self.unique_spell_count
        del self.max_occurrence_depth
        del self.max_dependency_count
        del self.fast_transient_no_overrides_enabled
        del self.lock_strategy_hint
        del self.registration_strategy_hint
        del self.call_mode_hint
        del self.emitter_family_id
        del self.fallback_reason
        del self.step_rows
        del self.metadata
