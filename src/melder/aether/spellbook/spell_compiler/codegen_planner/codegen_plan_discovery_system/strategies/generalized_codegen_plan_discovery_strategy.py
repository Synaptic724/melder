from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery import (
    CodegenPlanDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy import (
    CodegenPlanDiscoveryStrategy,
)
class GeneralizedCodegenPlanDiscoveryStrategy(CodegenPlanDiscoveryStrategy):
    """
    Default generalized phase-10 discovery strategy.

    Purpose:
        Preserve the current planner discovery behavior while moving that
        behavior behind an explicit discovery-strategy contract.

    Contract:
        - Claims every model for now.
        - Emits the generalized planner strategy plus the generalized planning
          family that phase 11 will later consume.
        - Provides the current candidate codegen style list for that family.
        - Does not choose the final codegen style; it only bounds what phase
          11 is allowed to pick from.

    Registration:
        MELDER KERNEL. A built-in
        discovery strategy; not bound as a spell.

    Subsystem Context:
        The fallback claimant of the `codegen_plan_discovery_system/strategies` family;
        registered last so it runs only when no narrower strategy claimed the model.

    System Context:
        Phase 10 (codegen planning) discovery of the conjure pipeline.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Default catch-all phase-10 discovery strategy: always claims, "
        "selecting the generalized_codegen_plan strategy / generalized family / generalized_default "
        "style. Registered last; runs only when no narrower strategy claimed the model."
    )
    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable discovery strategy id.
        """
        return "generalized_codegen_plan_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
    ) -> CodegenPlanDiscovery:
        """
        Claim the model and return the generalized planner-family selection.

        Contract:
            The default catch-all: never declines (the return type is
            non-optional), ignores model specifics, and always selects the
            "generalized_codegen_plan" strategy / "generalized" family with the
            "generalized_default" candidate style. Registered last so it runs
            only when no narrower strategy claimed the model.

        Args:
            spell_codegen_model:
                Processor-owned model (unused; this strategy always claims).

        Returns:
            CodegenPlanDiscovery:
                The generalized planner-family selection (never None).
        """
        _ = spell_codegen_model
        return CodegenPlanDiscovery(
            selected_strategy_id="generalized_codegen_plan",
            discovery_reason="default_generalized_model_native_strategy",
            plan_family_id="generalized",
            candidate_codegen_style_ids=("generalized_default",),
        )
