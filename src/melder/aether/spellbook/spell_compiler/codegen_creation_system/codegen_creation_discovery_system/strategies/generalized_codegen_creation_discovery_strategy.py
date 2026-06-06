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


class GeneralizedCodegenCreationDiscoveryStrategy(
    CodegenCreationDiscoveryStrategy
):
    """
    Default generalized phase-11 discovery strategy.

    Purpose:
        Preserve the current codegen-creation discovery behavior while moving
        that behavior behind an explicit discovery-strategy contract.

    Contract:
        - Claims only generalized planner output.
        - Emits the generalized family facade id for generalized planner
          output.
        - Chooses one concrete codegen style from the plan's candidate list.
        - Leaves the runtime contract narrow by choosing only the family and
          style, not any new top-level output fields.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable discovery strategy id.
        """
        return "generalized_codegen_creation_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> Optional[CodegenCreationDiscovery]:
        """
        Claim generalized planner output and return the generalized family facade.
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
                "generalized_codegen_creation",
            ),
            discovery_reason="default_generalized_plan_codegen_creation_family",
            selected_codegen_style_id=selected_codegen_style_id,
        )
