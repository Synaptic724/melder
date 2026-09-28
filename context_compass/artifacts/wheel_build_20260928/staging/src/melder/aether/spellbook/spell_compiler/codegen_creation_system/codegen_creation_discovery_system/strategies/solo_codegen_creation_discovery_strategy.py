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


class SoloCodegenCreationDiscoveryStrategy(CodegenCreationDiscoveryStrategy):
    """
    Phase-11 discovery strategy for solo plan-family output.

    Purpose:
        Claim phase-10 solo planner output and route it to the dedicated solo
        creation family instead of collapsing it back into generalized
        creation-family discovery.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable phase-11 solo discovery id.
        """
        return "solo_codegen_creation_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> Optional[CodegenCreationDiscovery]:
        """
        Claim solo planner output and route it to the solo creation family.

        Contract:
            Declines (returns None) unless the plan's
            metadata["selected_strategy_id"] is
            "generalized_solo_codegen_plan". On a match, selects the first
            candidate codegen style (or "generalized_solo" when none) and
            claims the "solo_codegen_creation" family. The model is not
            inspected.

        Args:
            spell_codegen_model:
                Analyzed spell model (unused; selection is plan-driven).
            spell_codegen_plan:
                Phase-10 plan whose metadata and candidate styles drive the
                claim.

        Returns:
            Optional[CodegenCreationDiscovery]:
                The solo-family discovery, or None when the plan is not solo.
        """
        _ = spell_codegen_model
        selected_plan_strategy_id = spell_codegen_plan.metadata.get(
            "selected_strategy_id"
        )
        if selected_plan_strategy_id != "generalized_solo_codegen_plan":
            return None
        selected_codegen_style_id = "generalized_solo"
        candidate_codegen_style_ids = spell_codegen_plan.candidate_codegen_style_ids
        if candidate_codegen_style_ids:
            selected_codegen_style_id = candidate_codegen_style_ids[0]
        return CodegenCreationDiscovery(
            selected_strategy_ids=(
                "solo_codegen_creation",
            ),
            discovery_reason="solo_plan_codegen_creation_family",
            selected_codegen_style_id=selected_codegen_style_id,
        )
