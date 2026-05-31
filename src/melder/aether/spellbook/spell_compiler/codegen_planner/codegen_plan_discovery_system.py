from dataclasses import dataclass

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)


@dataclass(frozen=True, slots=True)
class CodegenPlanDiscovery:
    """
    Discovery result for one codegen-plan selection pass.

    Purpose:
        Hold the planner's current selected plan strategy id plus any compact
        reason metadata explaining why that strategy was chosen.
    """

    selected_strategy_id: str
    discovery_reason: str


class CodegenPlanDiscoverySystem:
    """
    Select the best current codegen-plan strategy for one model.

    Purpose:
        Interpret `SpellCodegenModel` and choose which codegen-plan strategy
        should be used by the planner facade.

    Contract:
        - Discovery reads the model only.
        - Discovery does not build plans itself.
        - For now it always selects the generalized model-native strategy.
    """

    __slots__ = ()

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
    ) -> CodegenPlanDiscovery:
        """
        Select the current best codegen-plan strategy for the model.

        Contract:
            - Does not mutate the model.
            - Returns exactly one selected strategy result.
            - Defaults to `generalized_codegen_plan` until real ranking logic
              is implemented.
        """
        _ = spell_codegen_model
        return CodegenPlanDiscovery(
            selected_strategy_id="generalized_codegen_plan",
            discovery_reason="default_generalized_model_native_strategy",
        )
