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

FAMILY_SELECTION_METADATA_KEY = "codegen_creation_family"
FAMILY_SELECTION_METADATA_VALUE = "generalized_cache"


class GeneralizedCacheCodegenCreationDiscoveryStrategy(
    CodegenCreationDiscoveryStrategy
):
    """
    Opt-in phase-11 discovery strategy for the generalized_cache family.

    Purpose:
        Route generalized planner output to the experimental manifest-first
        creation family, but only when the plan is explicitly stamped for it.
        Unstamped plans fall through to the existing discovery chain, so
        production selection behavior is untouched.

    Contract:
        - Claims only when `spell_codegen_plan.metadata` carries
          `codegen_creation_family == "generalized_cache"`.
        - Claims only generalized planner output; a stamp on a non-generalized
          plan declines so the owning family can claim it instead.
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
        Claim stamped generalized planner output for the manifest-first family.
        """
        _ = spell_codegen_model
        selected_family = spell_codegen_plan.metadata.get(
            FAMILY_SELECTION_METADATA_KEY
        )
        if selected_family != FAMILY_SELECTION_METADATA_VALUE:
            return None
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
            discovery_reason="metadata_selected_generalized_cache_family",
            selected_codegen_style_id=selected_codegen_style_id,
        )
