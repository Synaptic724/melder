from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    compile_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers as SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)


class GeneralizedOverridesCodegenCreationStep(CodegenCreationFamilyStep):
    """
    Generalized family overrides packaging step.

    Purpose:
        Build the spell-static override-targeting and override-runtime input
        artifacts that the generalized finalizer consumes.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable overrides step id.
        """
        return "generalized_overrides_codegen_creation"

    def apply(
            self,
            state: GeneralizedCodegenCreationState,
    ) -> None:
        """
        Populate generalized override scratch on family-local state.
        """
        spell_codegen_model = state.spell_codegen_model
        spell_codegen_plan = state.spell_codegen_plan
        spell_codegen_creation = state.spell_codegen_creation

        overrides_plan = spell_codegen_plan.overrides_plan
        if overrides_plan is None:
            raise RuntimeError(
                "Generalized overrides codegen creation requires an overrides_plan."
            )
        override_targeting_shape = spell_codegen_model.override_targeting_shape
        if override_targeting_shape is None:
            raise RuntimeError(
                "Generalized overrides codegen creation requires override_targeting_shape."
            )

        override_runtime_inputs = self._build_override_runtime_inputs(
            spell_codegen_model=spell_codegen_model,
            overrides_plan=overrides_plan,
        )
        state.override_targeting = (
            SpellOverrideTargetingCodegenCreation.from_analysis(
                root_spell_id=overrides_plan.root_spell_id,
                targets_by_spec=override_targeting_shape.targets_by_spec,
                specificity_by_spec=override_targeting_shape.specificity_by_spec,
            )
        )
        state.override_plan_signature = override_runtime_inputs["plan_signature"]
        state.override_path_registry = override_runtime_inputs["path_registry"]
        state.override_plan_rows = override_runtime_inputs["plan_rows"]
        state.override_root_spell_id = override_runtime_inputs["root_spell_id"]
        state.override_spell_lookup = override_runtime_inputs["spell_lookup"]
        state.override_empty_shape_key = override_runtime_inputs["empty_shape_key"]
        state.override_baseline_executor = override_runtime_inputs[
            "baseline_executor"
        ]

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
            spell_codegen_model: object,
            overrides_plan: object,
    ) -> dict[str, object]:
        """
        Build the spell-static override runtime scratch inputs.
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
            overrides_plan: object,
    ) -> dict[str, object]:
        """
        Build the spell-id lookup required by override lane hydration.
        """
        spell_lookup: dict[str, object] = {}
        for step in overrides_plan.steps:
            spell_id = step.spell.spell_index.current
            if spell_id in spell_lookup:
                continue
            spell_lookup[spell_id] = step.spell
        return spell_lookup

    @staticmethod
    def _build_steps_rows(
            steps: object,
    ) -> tuple[dict[str, object], ...]:
        """
        Build override-compatible schema rows from generalized lane steps.
        """
        return tuple(
            SharedCompilerExecutions.build_phase11_step_ir_row(
                step,
                include_override_metadata=True,
            )
            for step in steps
        )
