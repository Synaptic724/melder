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


class ManyOnlyCodegenCreationDiscoveryStrategy(CodegenCreationDiscoveryStrategy):
    """
    Phase-11 discovery strategy for many-only plan-family output.

    Purpose:
        Claim phase-10 many-only planner output and route it to the dedicated
        many-only creation family instead of collapsing it back into
        generalized creation-family discovery.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable phase-11 many-only discovery id.
        """
        return "many_only_codegen_creation_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> Optional[CodegenCreationDiscovery]:
        """
        Claim many-only planner output and return the many-only creation family id.
        """
        _ = spell_codegen_model
        selected_plan_strategy_id = spell_codegen_plan.metadata.get(
            "selected_strategy_id"
        )
        if selected_plan_strategy_id != "many_only_codegen_plan":
            return None
        selected_codegen_style_id = "many_only"
        candidate_codegen_style_ids = spell_codegen_plan.candidate_codegen_style_ids
        if candidate_codegen_style_ids:
            selected_codegen_style_id = candidate_codegen_style_ids[0]
        return CodegenCreationDiscovery(
            selected_strategy_ids=(
                "many_only_codegen_creation",
            ),
            discovery_reason="many_only_plan_codegen_creation_family",
            selected_codegen_style_id=selected_codegen_style_id,
        )
