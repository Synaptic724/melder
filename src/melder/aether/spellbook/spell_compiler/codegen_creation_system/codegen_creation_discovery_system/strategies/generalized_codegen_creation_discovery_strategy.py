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
        - Emits the same generalized creation-chain result the old discovery
          facade returned directly, minus the removed mutation-specific lane.
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
        Claim generalized planner output and return the current creation chain.
        """
        _ = spell_codegen_model
        selected_plan_strategy_id = spell_codegen_plan.metadata.get(
            "selected_strategy_id"
        )
        if selected_plan_strategy_id != "generalized_codegen_plan":
            return None
        return CodegenCreationDiscovery(
            selected_strategy_ids=(
                "generalized_creation_context_setup_codegen_creation",
                "generalized_no_overrides_codegen_creation",
                "generalized_overrides_codegen_creation",
            ),
            discovery_reason="default_generalized_plan_codegen_creation_chain",
        )
