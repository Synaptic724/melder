from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)


class SoloFinalizeCreationContextStep(CodegenCreationFamilyStep):
    """
    Solo family final output step.

    Purpose:
        Finish the narrow `SpellCodegenCreation` output for the solo family
        after the solo-owned runtime executors are built.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable solo finalization step id.
        """
        return "solo_finalize_creation_context"

    def apply(
            self,
            state: SoloCodegenCreationState,
    ) -> None:
        """
        Publish the solo route metadata onto the final output artifact.
        """
        resolve_route_key = state.resolve_route_key
        if resolve_route_key is None:
            raise RuntimeError(
                "Solo finalize creation-context step requires resolve_route_key."
            )
        spell_codegen_creation = state.spell_codegen_creation
        spell_codegen_creation.metadata["resolve_route_key"] = resolve_route_key
        spell_codegen_creation.metadata["fast_transient_no_overrides_enabled"] = (
            state.fast_transient_no_overrides_enabled
        )
        spell_codegen_creation.metadata["creation_context_strategy"] = (
            "solo_codegen_creation"
        )
