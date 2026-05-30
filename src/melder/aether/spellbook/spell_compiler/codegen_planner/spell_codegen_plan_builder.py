from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_state import (
    SpellArtifactProcessorState,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy import (
    SpellCodegenPlanStrategy,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.existence.existence import Existence


class SpellCodegenPlanBuilder:
    """
    Build the compiler-owned Phase 12 codegen plan from assessed processor
    state.

    Purpose:
        Convert the artifact-processor result into the plan object that later
        backend-emitter work can consume.

    Contract:
        - Uses the assessed processor state as the sole source of truth.
        - Produces a meaningful baseline plan even when no concrete plan
          strategies exist yet.
        - Future `SpellCodegenPlanStrategy` implementations may refine the
          baseline plan without changing ownership or storage location.

    Ownership:
        - Owns no runtime/compiler artifacts.
        - Produces compiler-owned `SpellCodegenPlan` objects only.
    """

    __slots__ = ()

    @staticmethod
    def build(
            processor: SpellArtifactProcessor,
            *,
            strategies: Optional[Sequence[SpellCodegenPlanStrategy]] = None,
    ) -> SpellCodegenPlan:
        """
        Build one Phase 12 codegen plan from the processed state.

        Purpose:
            Convert processed Phase 12 state into the compiler-owned codegen
            plan and then apply any later plan-shaping strategies.

        Contract:
            - Forces processor execution before reading assessed state.
            - Produces a baseline plan even with zero plan strategies.
            - Applies plan strategies in the order supplied.
            - Returns the final plan object.

        Args:
            processor:
                Phase 12 artifact processor that has already assessed the
                current spell/artifact surface.
            strategies:
                Optional ordered plan strategies. `None` means the baseline
                plan is returned unchanged.

        Returns:
            SpellCodegenPlan:
                Compiler-owned Phase 12 output.
        """
        state = processor.process()
        plan = SpellCodegenPlanBuilder._build_baseline_plan(state)

        if strategies is None:
            return plan

        plan_strategy_ids: list[str] = []
        for strategy in strategies:
            plan = strategy.apply(state, plan)
            plan_strategy_ids.append(strategy.strategy_id)

        plan.plan_strategy_ids = tuple(plan_strategy_ids)
        return plan

    @staticmethod
    def _build_baseline_plan(
            state: SpellArtifactProcessorState,
    ) -> SpellCodegenPlan:
        """
        Build the first meaningful Phase 12 baseline plan.

        Purpose:
            Produce a stable, compiler-owned baseline plan from the current
            processed state before any concrete plan strategies exist.

        Contract:
            - Consumes the full state but derives only stable baseline facts in
              this scaffold slice.
            - Chooses a route key directly from spell existence.
            - Carries lane-support and hot-path hints that later strategies can
              refine.

        Args:
            state:
                Assessed Phase 12 processor state.

        Returns:
            SpellCodegenPlan:
                Baseline plan carrying the current best non-strategy-specific
                interpretation of the spell/runtime shape.
        """
        spell_facts = state.spell_facts
        planning_artifacts = state.compiler_planning_artifacts
        compiler_handoffs = state.compiler_handoff_artifacts
        compiler_metrics = state.compiler_metrics

        route_key = SpellCodegenPlanBuilder._resolve_route_key(
            spell_type=spell_facts["spell_type"],
            existence=spell_facts["existence"],
            is_existing_creation=spell_facts["is_existing_creation"],
        )
        supports_no_overrides_lane = (
            planning_artifacts["execution_plan_phase11_no_overrides"] is not None
            or compiler_handoffs["phase13_no_overrides_executor"] is not None
        )
        supports_overrides_lane = (
            planning_artifacts["execution_plan_phase11_overrides"] is not None
            or planning_artifacts["override_patch_map_phase10"] is not None
        )
        supports_mutation_lane = (
            planning_artifacts["execution_plan_phase11"] is not None
            or planning_artifacts["mutation_patch_map_phase10"] is not None
            or spell_facts["has_mutation_override"]
        )

        dispatch_route = spell_facts["execution_plan_dispatch_route"]
        no_overrides_family: Optional[str] = None
        if supports_no_overrides_lane:
            no_overrides_family = dispatch_route

        overrides_family: Optional[str] = None
        if supports_overrides_lane:
            overrides_family = "phase11_overrides_present"

        mutation_family: Optional[str] = None
        if supports_mutation_lane:
            mutation_family = "phase11_mutation_lane_present"

        fast_transient_no_overrides_enabled = bool(
            dispatch_route is not None
            and dispatch_route.startswith("FAST_TRANSIENT")
        )
        if not fast_transient_no_overrides_enabled:
            no_overrides_plan = planning_artifacts["execution_plan_phase11_no_overrides"]
            if no_overrides_plan is not None:
                fast_transient_no_overrides_enabled = (
                    no_overrides_plan.fast_transient_plan is not None
                )

        execution_shape_profile = state.shape_profiles["execution_shape_profile_phase11"]
        spell_lock_step_count = 0
        must_register_count = 0
        if execution_shape_profile is not None:
            spell_lock_step_count = execution_shape_profile.get(
                "spell_lock_step_count",
                0,
            )
            must_register_count = execution_shape_profile.get(
                "must_register_count",
                0,
            )

        if spell_lock_step_count > 0:
            lock_strategy_hint = "spell_lock_required"
        elif route_key == "shared":
            lock_strategy_hint = "shared_owner_lock_path"
        elif route_key in ("unique_per_conduit", "spellspace"):
            lock_strategy_hint = "scoped_creation_lock_path"
        elif route_key == "many":
            lock_strategy_hint = "transient_creation_path"
        else:
            lock_strategy_hint = "existing_creation_path"

        if must_register_count > 0:
            registration_strategy_hint = "registration_required"
        else:
            registration_strategy_hint = "no_registration_required"

        if compiler_metrics["execution_plan_has_calln_phase11"]:
            call_mode_hint = "calln_present"
        else:
            call_mode_hint = "fixed_arity_only"

        metadata: Dict[str, Any] = {
            "processor_section_names": state.section_names(),
            "phase11_no_overrides_plan_signature": (
                compiler_handoffs["phase11_no_overrides_plan_signature"]
            ),
            "phase13_no_overrides_executor_signature": (
                compiler_handoffs["phase13_no_overrides_executor_signature"]
            ),
            "phase8_11_codegen_ir_dirty": (
                compiler_handoffs["phase8_11_codegen_ir_dirty"]
            ),
        }

        return SpellCodegenPlan(
            processor_strategy_ids=state.snapshot_applied_strategy_ids(),
            plan_strategy_ids=(),
            no_overrides_family=no_overrides_family,
            overrides_family=overrides_family,
            mutation_family=mutation_family,
            route_key=route_key,
            supports_no_overrides_lane=supports_no_overrides_lane,
            supports_overrides_lane=supports_overrides_lane,
            supports_mutation_lane=supports_mutation_lane,
            requires_spellspace_request=spell_facts["requires_spellspace_request"],
            execution_plan_dispatch_route=dispatch_route,
            step_count=compiler_metrics["execution_plan_step_count_phase11"],
            unique_spell_count=compiler_metrics["execution_plan_unique_spell_count_phase11"],
            max_occurrence_depth=compiler_metrics["execution_plan_max_occurrence_depth_phase11"],
            max_dependency_count=compiler_metrics["execution_plan_max_dependency_count_phase11"],
            fast_transient_no_overrides_enabled=(
                fast_transient_no_overrides_enabled
            ),
            lock_strategy_hint=lock_strategy_hint,
            registration_strategy_hint=registration_strategy_hint,
            call_mode_hint=call_mode_hint,
            emitter_family_id="phase13_placeholder",
            fallback_reason=None,
            step_rows=(),
            metadata=metadata,
        )

    @staticmethod
    def _resolve_route_key(
            *,
            spell_type: SpellType,
            existence: Existence,
            is_existing_creation: bool,
    ) -> str:
        """
        Resolve the baseline Phase 12 route/storage family key.

        Args:
            spell_type:
                Current spell binding family.
            existence:
                Current spell existence mode.
            is_existing_creation:
                Existing-creation runtime flag from `Spell`.

        Returns:
            str:
                Stable baseline route/storage family key for Phase 12.

        Contract:
            - Existing-creation takes priority over existence-family routing.
            - Spell type is accepted so future strategies can refine the route
              policy without changing the call contract.
        """
        _ = spell_type
        if is_existing_creation:
            return "existing_creation"
        if existence is Existence.unique_per_spell_space:
            return "spellspace"
        if existence is Existence.unique_per_conduit:
            return "unique_per_conduit"
        if existence is Existence.many:
            return "many"
        return "shared"
