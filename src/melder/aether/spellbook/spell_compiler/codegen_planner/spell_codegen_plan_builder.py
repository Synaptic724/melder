from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy import (
    SpellCodegenPlanStrategy,
)


class SpellCodegenPlanBuilder:
    """
    Build compiler-owned codegen plans from an already-finished model.

    Purpose:
        Keep the builder's role literal: it owns the ordered plan-strategy
        registry and produces `SpellCodegenPlan` objects from finished
        `SpellCodegenModel` inputs.

    Contract:
        - Does not consume raw artifact bags directly.
        - Does not build the model itself.
        - Produces a meaningful baseline plan even when no concrete plan
          strategies exist yet.
        - Applies plan strategies in the stored order.
    """

    __slots__ = [
        "_strategies",
    ]

    def __init__(
            self,
            *,
            strategies: Optional[Sequence[SpellCodegenPlanStrategy]] = None,
    ) -> None:
        """
        Build one plan builder with an ordered strategy registry.
        """
        if strategies is None:
            self._strategies: Tuple[SpellCodegenPlanStrategy, ...] = ()
        else:
            self._strategies = tuple(strategies)

    def build(
            self,
            model: SpellCodegenModel,
    ) -> SpellCodegenPlan:
        """
        Build one Phase 12 codegen plan from the finished model.
        """
        plan = self._build_baseline_plan(model)

        plan_strategy_ids: list[str] = []
        for strategy in self._strategies:
            plan = strategy.apply(model, plan)
            plan_strategy_ids.append(strategy.strategy_id)

        plan.plan_strategy_ids = tuple(plan_strategy_ids)
        return plan

    @staticmethod
    def _build_baseline_plan(
            model: SpellCodegenModel,
    ) -> SpellCodegenPlan:
        """
        Build the first meaningful Phase 12 baseline plan from the model.
        """
        build_kind = model.build_kind
        route_key = model.route_family
        if build_kind == "existing_creation":
            no_overrides_family = None
            overrides_family = None
            mutation_family = None
            lock_strategy_hint = "existing_creation_path"
            registration_strategy_hint = "no_registration_required"
            emitter_family_id = "phase13_existing_creation_placeholder"
        else:
            if model.fast_transient_eligible:
                no_overrides_family = "transient_fast_plan"
            elif model.graph_family == "single":
                no_overrides_family = "single_plan"
            elif model.graph_family == "flat":
                no_overrides_family = "flat_plan"
            elif model.graph_family == "chain":
                no_overrides_family = "chain_plan"
            elif model.graph_family == "shared_dag":
                no_overrides_family = "shared_dag_plan"
            else:
                no_overrides_family = "generic_plan"

            if model.override_shape_family == "none":
                overrides_family = "default_override_plan"
            elif model.override_shape_family == "simple":
                overrides_family = "simple_override_plan"
            elif model.override_shape_family == "wide":
                overrides_family = "wide_override_plan"
            elif model.override_shape_family == "deep":
                overrides_family = "deep_override_plan"
            else:
                overrides_family = "complex_override_plan"

            mutation_family = "default_mutation_plan"
            if route_key == "shared":
                lock_strategy_hint = "shared_owner_lock_path"
            elif route_key in ("unique_per_conduit", "spellspace"):
                lock_strategy_hint = "scoped_creation_lock_path"
            elif route_key == "many":
                lock_strategy_hint = "transient_creation_path"
            else:
                lock_strategy_hint = "generic_creation_path"

            if build_kind == "construct" and route_key != "many":
                registration_strategy_hint = "registration_required"
            else:
                registration_strategy_hint = "no_registration_required"
            emitter_family_id = "phase13_placeholder"

        if model.has_calln:
            call_mode_hint = "calln_present"
        else:
            call_mode_hint = model.call_shape_family

        metadata: Dict[str, Any] = {
            "processor_section_names": model.section_names(),
            "graph_family": model.graph_family,
            "override_shape_family": model.override_shape_family,
        }

        return SpellCodegenPlan(
            processor_strategy_ids=model.snapshot_applied_strategy_ids(),
            plan_strategy_ids=(),
            no_overrides_family=no_overrides_family,
            overrides_family=overrides_family,
            mutation_family=mutation_family,
            route_key=route_key,
            supports_no_overrides_lane=build_kind == "construct",
            supports_overrides_lane=build_kind == "construct",
            supports_mutation_lane=build_kind == "construct",
            requires_spellspace_request=route_key == "spellspace",
            execution_plan_dispatch_route=None,
            step_count=model.node_count,
            unique_spell_count=model.node_count,
            max_occurrence_depth=model.max_depth,
            max_dependency_count=model.max_dependency_count,
            fast_transient_no_overrides_enabled=model.fast_transient_eligible,
            lock_strategy_hint=lock_strategy_hint,
            registration_strategy_hint=registration_strategy_hint,
            call_mode_hint=call_mode_hint,
            emitter_family_id=emitter_family_id,
            fallback_reason=None,
            step_rows=(),
            metadata=metadata,
        )
