from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state import (
    ManyOnlyCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)


class ManyOnlyCreationContextSetupStep(CodegenCreationFamilyStep):
    """
    Many-only family setup step.

    Purpose:
        Resolve many-only route/setup facts that the later many-only steps use
        while keeping those intermediate values off the final output artifact.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable setup step id.
        """
        return "many_only_creation_context_setup"

    def apply(
            self,
            state: ManyOnlyCodegenCreationState,
    ) -> None:
        """
        Populate many-only route/setup facts on family-local state.
        """
        spell_codegen_model = state.spell_codegen_model
        spell_codegen_plan = state.spell_codegen_plan

        _ = spell_codegen_model
        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        fast_transient_no_overrides_enabled = (
            no_overrides_plan is not None
            and no_overrides_plan.fast_transient_plan is not None
        )

        state.resolve_route_key = "many"
        state.fast_transient_no_overrides_enabled = (
            fast_transient_no_overrides_enabled
        )
