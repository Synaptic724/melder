from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    compile_no_overrides_codegen_creation_executor_from_plan,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers as SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.shared_strategy_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)


class GeneralizedNoOverridesCodegenCreationStep(CodegenCreationFamilyStep):
    """
    Generalized family no-overrides executor build step.

    Purpose:
        Compile the spell-static no-overrides executor from the generalized lane
        plan and store it on both the family state and the final output object.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable no-overrides step id.
        """
        return "generalized_no_overrides_codegen_creation"

    def apply(
            self,
            state: GeneralizedCodegenCreationState,
    ) -> None:
        """
        Populate no-overrides executor output from generalized lane truth.
        """
        spell_codegen_plan = state.spell_codegen_plan
        spell_codegen_creation = state.spell_codegen_creation

        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        if no_overrides_plan is None:
            raise RuntimeError(
                "Generalized no-overrides codegen creation requires a no_overrides_plan."
            )

        transient_schema = SharedCompilerExecutions.build_fast_transient_schema(
            no_overrides_plan.fast_transient_plan,
        )
        compiled_executor = compile_no_overrides_codegen_creation_executor_from_plan(
            plan=no_overrides_plan,
            transient_schema=transient_schema,
        )
        executor_signature = self._build_executor_signature(
            no_overrides_plan=no_overrides_plan,
            transient_schema=transient_schema,
        )

        state.base_no_overrides_executor = compiled_executor
        spell_codegen_creation.no_overrides_executor = compiled_executor
        spell_codegen_creation.metadata["no_overrides_lane_id"] = (
            no_overrides_plan.lane_id
        )
        spell_codegen_creation.metadata["no_overrides_root_spell_id"] = (
            no_overrides_plan.root_spell_id
        )
        spell_codegen_creation.metadata["no_overrides_step_count"] = (
            len(no_overrides_plan.steps)
        )
        spell_codegen_creation.metadata["no_overrides_fast_transient_available"] = (
            no_overrides_plan.fast_transient_plan is not None
        )
        spell_codegen_creation.metadata["no_overrides_executor_signature"] = (
            executor_signature
        )

    @staticmethod
    def _build_executor_signature(
            *,
            no_overrides_plan: object,
            transient_schema: object,
    ) -> str:
        """
        Build the deterministic no-overrides executor signature.
        """
        step_signature_rows = tuple(
            SharedCompilerExecutions.build_no_overrides_codegen_creation_step_signature_row(
                step
            )
            for step in no_overrides_plan.steps
        )
        transient_signature = (
            SharedCompilerExecutions.build_fast_transient_signature(
                transient_schema
            )
        )
        root_instance_key = SharedCompilerExecutions.normalize_instance_key(
            no_overrides_plan.root_instance_key
        )
        return SharedCompilerExecutions.hash_codegen_signature(
            no_overrides_plan.root_spell_id,
            root_instance_key,
            step_signature_rows,
            transient_signature,
        )
