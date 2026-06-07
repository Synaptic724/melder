from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_no_overrides_codegen_creation_compiler import (
    compile_solo_no_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)


class SoloNoOverridesCodegenCreationStep(CodegenCreationFamilyStep):
    """
    Solo family no-overrides executor build step.

    Purpose:
        Compile the root-only solo no-overrides executor and publish it onto
        family state plus the final `SpellCodegenCreation` output.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable solo no-overrides step id.
        """
        return "solo_no_overrides_codegen_creation"

    def apply(
            self,
            state: SoloCodegenCreationState,
    ) -> None:
        """
        Populate the solo no-overrides executor.
        """
        root_spell = state.root_spell
        solo_emit_key = state.solo_emit_key
        spell_codegen_creation = state.spell_codegen_creation
        spell_codegen_plan = state.spell_codegen_plan

        executor = compile_solo_no_overrides_codegen_creation_executor(
            spell=root_spell,
            solo_emit_key=solo_emit_key,
            fast_transient_no_overrides_enabled=(
                state.fast_transient_no_overrides_enabled
            ),
        )
        lane_id = spell_codegen_plan.no_overrides_plan.lane_id
        signature = (
            "solo",
            solo_emit_key,
            int(state.fast_transient_no_overrides_enabled),
            int(root_spell.has_disposal_methods),
            int(root_spell.is_existing_creation),
        )

        state.no_overrides_executor = executor
        spell_codegen_creation.no_overrides_executor = executor
        spell_codegen_creation.metadata["no_overrides_lane_id"] = lane_id
        spell_codegen_creation.metadata["no_overrides_root_spell_id"] = (
            state.root_spell_id
        )
        spell_codegen_creation.metadata["no_overrides_step_count"] = 1
        spell_codegen_creation.metadata["no_overrides_fast_transient_available"] = (
            state.fast_transient_no_overrides_enabled
        )
        spell_codegen_creation.metadata["no_overrides_executor_signature"] = (
            signature
        )
        spell_codegen_creation.metadata["_no_overrides_executor_signature"] = (
            signature
        )
