from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)


class GeneralizedCreationContextSetupStep(CodegenCreationFamilyStep):
    """
    Generalized family setup step.

    Purpose:
        Resolve shared route/setup facts that the later generalized steps use
        while keeping those intermediate values off the final output artifact.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable setup step id.
        """
        return "generalized_creation_context_setup"

    def apply(
            self,
            state: GeneralizedCodegenCreationState,
    ) -> None:
        """
        Populate generalized route/setup facts on family-local state.
        """
        spell_codegen_model = state.spell_codegen_model
        spell_codegen_plan = state.spell_codegen_plan

        route_key = self._resolve_route_key(spell_codegen_model)
        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        fast_transient_no_overrides_enabled = False
        if no_overrides_plan is not None:
            fast_transient_no_overrides_enabled = (
                route_key == "many"
                and no_overrides_plan.fast_transient_plan is not None
            )

        state.resolve_route_key = route_key
        state.fast_transient_no_overrides_enabled = (
            fast_transient_no_overrides_enabled
        )

    @staticmethod
    def _resolve_route_key(
            spell_codegen_model: object,
    ) -> str:
        """
        Resolve the current creation-context route key from model truth.
        """
        build_kind = spell_codegen_model.build_kind
        if build_kind == "existing_creation":
            return "existing_creation"

        route_family = spell_codegen_model.route_family
        if route_family in (
                "spellspace",
                "unique_per_conduit",
                "many",
                "shared",
        ):
            return route_family

        raise RuntimeError(
            "SpellCodegenModel route_family is not ready for creation-context "
            f"setup: {route_family!r}."
        )
