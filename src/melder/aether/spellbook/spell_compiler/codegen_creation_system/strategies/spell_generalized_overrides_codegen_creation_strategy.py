from typing import Any, Dict, Sequence, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.generalized_overrides_codegen_creation_compiler import (
    compile_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenLanePlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)


class SpellGeneralizedOverridesCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Generalized overrides codegen creation strategy.

    Purpose:
        Port the normal override packaging into the codegen-creation layer,
        using the generalized overrides lane plan as the spell-static source
        of truth.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable overrides creation strategy id.
        """
        return "generalized_overrides_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Populate the normal overrides creation payload.

        Contract:
            - Requires the planner to have already produced an overrides lane
              plan.
            - Builds the spell-static `OverrideRouteConfig` from the generalized
              lane plan instead of reading old exported IR.
            - Prebuilds the empty-shape baseline override executor for later
              runtime reuse.
            - Ports the Phase 10 bridge into a compiler-owned override
              targeting artifact instead of leaving the old patch-map object in
              the runtime path.
        """
        overrides_plan = spell_codegen_plan.overrides_plan
        if overrides_plan is None:
            raise RuntimeError(
                "Overrides codegen creation requires an overrides_plan."
            )
        override_targeting_shape = spell_codegen_model.override_targeting_shape
        if override_targeting_shape is None:
            raise RuntimeError(
                "Overrides codegen creation requires override_targeting_shape."
            )

        override_runtime_inputs = self._build_override_runtime_inputs(
            spell_codegen_model=spell_codegen_model,
            overrides_plan=overrides_plan,
        )
        spell_codegen_creation.metadata["_override_targeting"] = (
            SpellOverrideTargetingCodegenCreation.from_analysis(
                root_spell_id=overrides_plan.root_spell_id,
                targets_by_spec=override_targeting_shape.targets_by_spec,
                specificity_by_spec=override_targeting_shape.specificity_by_spec,
            )
        )
        spell_codegen_creation.metadata["_override_plan_signature"] = (
            override_runtime_inputs["plan_signature"]
        )
        spell_codegen_creation.metadata["_override_path_registry"] = (
            override_runtime_inputs["path_registry"]
        )
        spell_codegen_creation.metadata["_override_plan_rows"] = (
            override_runtime_inputs["plan_rows"]
        )
        spell_codegen_creation.metadata["_override_root_spell_id"] = (
            override_runtime_inputs["root_spell_id"]
        )
        spell_codegen_creation.metadata["_override_spell_lookup"] = (
            override_runtime_inputs["spell_lookup"]
        )
        spell_codegen_creation.metadata["_override_empty_shape_key"] = (
            override_runtime_inputs["empty_shape_key"]
        )
        spell_codegen_creation.metadata["_override_baseline_executor"] = (
            override_runtime_inputs["baseline_executor"]
        )
        spell_codegen_creation.metadata["override_lane_id"] = overrides_plan.lane_id
        spell_codegen_creation.metadata["override_root_spell_id"] = (
            overrides_plan.root_spell_id
        )
        spell_codegen_creation.metadata["override_step_count"] = (
            len(overrides_plan.steps)
        )
        spell_codegen_creation.metadata["override_steps_rows_signature"] = (
            override_runtime_inputs["plan_signature"][2]
        )

    def _build_override_runtime_inputs(
            self,
            *,
            spell_codegen_model: SpellCodegenModel,
            overrides_plan: SpellGeneralizedCodegenLanePlan,
    ) -> Dict[str, Any]:
        """
        Build the spell-static override runtime scratch inputs.

        Contract:
            - Uses the generalized overrides lane plan as the source of truth.
            - Derives deterministic plan rows compatible with the current
              override executor compiler.
            - Prebuilds the baseline empty-shape override executor.
        """
        steps_rows = self._build_steps_rows(overrides_plan.steps)
        steps_rows_signature = SharedCompilerExecutions.hash_codegen_signature(
            steps_rows
        )
        step_spell_ids = tuple(
            step.spell.spell_index.current
            for step in overrides_plan.steps
        )
        plan_signature = (
            "generalized_overrides_lane_plan",
            SharedCompilerExecutions.hash_codegen_signature(
                overrides_plan.lane_id,
                overrides_plan.root_spell_id,
                step_spell_ids,
                steps_rows_signature,
            ),
            steps_rows_signature,
        )
        spell_lookup = self._build_spell_lookup(overrides_plan)
        path_registry = None
        graph_shape = spell_codegen_model.graph_shape
        if graph_shape is not None:
            path_registry = graph_shape.path_registry

        baseline_executor = compile_overrides_codegen_creation_executor(
            execution_plan=None,
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=path_registry,
            plan_rows=steps_rows,
            root_spell_id=overrides_plan.root_spell_id,
            spell_lookup=spell_lookup,
        )
        return {
            "plan_signature": plan_signature,
            "path_registry": path_registry,
            "plan_rows": steps_rows,
            "root_spell_id": overrides_plan.root_spell_id,
            "spell_lookup": spell_lookup,
            "empty_shape_key": (
                plan_signature,
                (),
                -1,
            ),
            "baseline_executor": baseline_executor,
        }

    @staticmethod
    def _build_spell_lookup(
            overrides_plan: SpellGeneralizedCodegenLanePlan,
    ) -> Dict[str, Any]:
        """
        Build the spell-id lookup required by override lane hydration.

        Contract:
            - Uses the lane-plan step order as the source of truth.
            - Keeps only the first encountered runtime object per spell id.
        """
        spell_lookup: Dict[str, Any] = {}
        for step in overrides_plan.steps:
            spell_id = step.spell.spell_index.current
            if spell_id in spell_lookup:
                continue
            spell_lookup[spell_id] = step.spell
        return spell_lookup

    @staticmethod
    def _build_steps_rows(
            steps: Sequence[Any],
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Build override-compatible schema rows from generalized lane steps.

        Contract:
            - Uses the same row-builder semantics the old phase11 IR export
              used for override-aware variants.
            - Returns deterministic tuple-backed row order.
        """
        return tuple(
            SharedCompilerExecutions.build_phase11_step_ir_row(
                step,
                include_override_metadata=True,
            )
            for step in steps
        )
