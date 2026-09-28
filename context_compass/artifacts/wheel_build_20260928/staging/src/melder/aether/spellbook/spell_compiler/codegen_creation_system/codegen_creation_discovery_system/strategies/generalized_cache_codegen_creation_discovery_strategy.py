from typing import Optional

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


class GeneralizedCacheCodegenCreationDiscoveryStrategy(
    CodegenCreationDiscoveryStrategy
):
    """
    Phase-11 discovery strategy for the generalized_cache family.

    Purpose:
        Route generalized planner output to the manifest-first creation
        family. Registered ahead of the legacy generalized discovery
        strategy, so every generalized plan now resolves to the
        generalized_cache family concretely - no stamp, no config gate.

    Contract:
        - Claims exactly the plans `generalized_codegen_creation_discovery`
          used to claim (`selected_strategy_id == "generalized_codegen_plan"`).
        - Declines every other plan family so solo/many_only routing is
          untouched.
        - The legacy generalized discovery strategy stays registered behind
          this one as the rollback seam: removing this strategy from the
          discovery registry restores the previous selection behavior.
        - Chooses the concrete codegen style exactly like the generalized
          discovery strategy.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable generalized_cache discovery id.
        """
        return "generalized_cache_codegen_creation_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> Optional[CodegenCreationDiscovery]:
        """
        Claim generalized planner output for the manifest-first family.

        Contract:
            Declines (returns None) unless the plan's
            metadata["selected_strategy_id"] is "generalized_codegen_plan" -
            exactly what the legacy generalized discovery claimed. On a match,
            selects the first candidate codegen style (or "generalized_default"
            when none) and claims the "generalized_cache_codegen_creation"
            family. The model is not inspected.

        Args:
            spell_codegen_model:
                Analyzed spell model (unused; selection is plan-driven).
            spell_codegen_plan:
                Phase-10 plan whose metadata and candidate styles drive the
                claim.

        Returns:
            Optional[CodegenCreationDiscovery]:
                The generalized_cache-family discovery, or None when the plan
                is not generalized.
        """
        _ = spell_codegen_model
        selected_plan_strategy_id = spell_codegen_plan.metadata.get(
            "selected_strategy_id"
        )
        if selected_plan_strategy_id != "generalized_codegen_plan":
            return None
        selected_codegen_style_id = "generalized_default"
        candidate_codegen_style_ids = (
            spell_codegen_plan.candidate_codegen_style_ids
        )
        if candidate_codegen_style_ids:
            selected_codegen_style_id = candidate_codegen_style_ids[0]
        return CodegenCreationDiscovery(
            selected_strategy_ids=(
                "generalized_cache_codegen_creation",
            ),
            discovery_reason="generalized_plan_generalized_cache_family",
            selected_codegen_style_id=selected_codegen_style_id,
        )
