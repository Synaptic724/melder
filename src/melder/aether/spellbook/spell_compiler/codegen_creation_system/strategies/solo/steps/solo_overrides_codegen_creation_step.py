from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_overrides_codegen_creation_compiler import (
    compile_solo_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)


class SoloOverridesCodegenCreationStep(CodegenCreationFamilyStep):
    """
    Solo family overrides executor build step.

    Purpose:
        Compile the root-only solo overrides executor and publish it onto family
        state plus the final `SpellCodegenCreation` output.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable solo overrides step id.
        """
        return "solo_overrides_codegen_creation"

    def apply(
            self,
            state: SoloCodegenCreationState,
    ) -> None:
        """
        Populate the solo overrides executor.
        """
        root_spell = state.root_spell
        solo_emit_key = state.solo_emit_key
        spell_codegen_creation = state.spell_codegen_creation
        spell_codegen_plan = state.spell_codegen_plan

        executor, code_object = compile_solo_overrides_codegen_creation_executor(
            spell=root_spell,
            solo_emit_key=solo_emit_key,
            return_compiled_code_object=True,
        )
        lane_id = spell_codegen_plan.overrides_plan.lane_id

        state.overrides_executor = executor
        spell_codegen_creation.overrides_executor = executor
        spell_codegen_creation.overrides_code_object = code_object
        spell_codegen_creation.metadata["override_lane_id"] = lane_id
        spell_codegen_creation.metadata["override_root_spell_id"] = (
            state.root_spell_id
        )
        spell_codegen_creation.metadata["override_step_count"] = 1
        spell_codegen_creation.metadata["override_executor_signature"] = (
            "solo",
            solo_emit_key,
            int(root_spell.has_disposal_methods),
            int(root_spell.is_existing_creation),
        )
