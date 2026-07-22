from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    compile_no_overrides_codegen_creation_executor_from_plan,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers import (
    ManyOnlyCodegenCreationHelpers,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state import (
    ManyOnlyCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)


class ManyOnlyNoOverridesCodegenCreationStep(CodegenCreationFamilyStep):
    """
    Many-only family no-overrides executor build step.

    Purpose:
        Compile the spell-static no-overrides executor from the many-only lane
        plan and store the many-only transient specialization on both the family
        state and the final output object.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable no-overrides step id.
        """
        return "many_only_no_overrides_codegen_creation"

    def apply(
            self,
            state: ManyOnlyCodegenCreationState,
    ) -> None:
        """
        Populate no-overrides executor output from many-only lane truth.

        Contract:
            Requires a no_overrides lane plan (raises otherwise). Compiles the
            spell-static no-overrides executor (and its code object) from the
            plan, then publishes it onto state and the creation along with the
            code object, metadata, and the deterministic executor signature.

        Args:
            state:
                Family-local state carrying model, plan, and creation; mutated
                in place.

        Returns:
            None.

        Raises:
            RuntimeError: If the no_overrides lane plan is missing.
        """
        spell_codegen_plan = state.spell_codegen_plan
        spell_codegen_creation = state.spell_codegen_creation

        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        if no_overrides_plan is None:
            raise RuntimeError(
                "Many-only no-overrides codegen creation requires a no_overrides_plan."
            )

        compiled_executor, compiled_code_object = (
            compile_no_overrides_codegen_creation_executor_from_plan(
                plan=no_overrides_plan,
                return_compiled_code_object=True,
            )
        )
        executor_signature = self._build_executor_signature(
            no_overrides_plan=no_overrides_plan,
        )

        state.base_no_overrides_executor = compiled_executor
        spell_codegen_creation.no_overrides_executor = compiled_executor
        spell_codegen_creation.no_overrides_code_object = compiled_code_object
        spell_codegen_creation.metadata["no_overrides_lane_id"] = (
            no_overrides_plan.lane_id
        )
        spell_codegen_creation.metadata["no_overrides_root_spell_id"] = (
            no_overrides_plan.root_spell_id
        )
        spell_codegen_creation.metadata["no_overrides_step_count"] = (
            len(no_overrides_plan.steps)
        )
        spell_codegen_creation.metadata["no_overrides_plan_kind"] = (
            "many_only_no_overrides"
        )
        spell_codegen_creation.metadata["no_overrides_executor_signature"] = (
            executor_signature
        )
        spell_codegen_creation.metadata["_no_overrides_executor_signature"] = (
            executor_signature
        )

    @staticmethod
    def _build_executor_signature(
            *,
            no_overrides_plan: object,
    ) -> str:
        """
        Build the deterministic no-overrides executor signature.
        """
        step_signature_rows = tuple(
            ManyOnlyCodegenCreationHelpers.build_no_overrides_step_signature_row(
                step
            )
            for step in no_overrides_plan.steps
        )
        root_instance_key = ManyOnlyCodegenCreationHelpers.normalize_instance_key(
            no_overrides_plan.root_instance_key
        )
        return ManyOnlyCodegenCreationHelpers.hash_signature(
            no_overrides_plan.root_spell_id,
            root_instance_key,
            step_signature_rows,
            no_overrides_plan.step_call_modes,
            no_overrides_plan.root_step_index,
            no_overrides_plan.step_has_disposal_methods,
        )
