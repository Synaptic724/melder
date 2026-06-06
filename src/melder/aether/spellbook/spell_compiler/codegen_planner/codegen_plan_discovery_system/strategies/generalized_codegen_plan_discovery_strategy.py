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
        - Emits the same generalized planner result the old discovery facade
          returned directly.
    """

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
        Claim the model and return the generalized planner selection.
        """
        _ = spell_codegen_model
        return CodegenPlanDiscovery(
            selected_strategy_id="generalized_codegen_plan",
            discovery_reason="default_generalized_model_native_strategy",
        )
