from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery import (
    CodegenCreationDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy import (
    CodegenCreationDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class FallbackNoOverridesCodegenCreationDiscoveryStrategy(
    CodegenCreationDiscoveryStrategy
):
    """
    Fallback phase-11 discovery strategy.

    Purpose:
        Preserve the current fallback no-overrides discovery result when no
        earlier phase-11 discovery strategy claims the model/plan pair.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable discovery strategy id.
        """
        return "fallback_no_overrides_codegen_creation_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> CodegenCreationDiscovery:
        """
        Unconditionally claim the pair for the no-overrides fallback family.

        Contract:
            The terminal discovery strategy: it NEVER declines (the return type
            is non-optional). Registered last, so it runs only when no earlier
            strategy claimed the pair, and always routes to the
            "generalized_no_overrides_codegen_creation" family. Neither the
            model nor the plan is inspected.

        Args:
            spell_codegen_model:
                Analyzed spell model (unused).
            spell_codegen_plan:
                Phase-10 plan (unused).

        Returns:
            CodegenCreationDiscovery:
                The fallback no-overrides discovery result (never None).
        """
        _ = spell_codegen_model
        _ = spell_codegen_plan
        return CodegenCreationDiscovery(
            selected_strategy_ids=(
                "generalized_no_overrides_codegen_creation",
            ),
            discovery_reason="fallback_no_overrides_creation_strategy",
        )
