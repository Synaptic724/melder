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
        if root_spell is None:
            raise RuntimeError(
                "Solo overrides codegen creation requires root_spell."
            )
        resolve_route_key = state.resolve_route_key
        if resolve_route_key is None:
            raise RuntimeError(
                "Solo overrides codegen creation requires resolve_route_key."
            )
        spell_codegen_creation = state.spell_codegen_creation
        spell_codegen_plan = state.spell_codegen_plan

        executor = compile_solo_overrides_codegen_creation_executor(
            spell=root_spell,
            resolve_route_key=resolve_route_key,
        )
        lane_id = "solo_overrides"
        if spell_codegen_plan.overrides_plan is not None:
            lane_id = spell_codegen_plan.overrides_plan.lane_id

        state.overrides_executor = executor
        spell_codegen_creation.overrides_executor = executor
        spell_codegen_creation.metadata["override_lane_id"] = lane_id
        spell_codegen_creation.metadata["override_root_spell_id"] = (
            state.root_spell_id
        )
        spell_codegen_creation.metadata["override_step_count"] = 1
