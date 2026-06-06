from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery import (
    CodegenPlanDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy_builder import (
    CodegenPlanDiscoveryStrategyBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable


class CodegenPlanDiscoverySystem(Cleanable):
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

    __slots__ = Cleanable.__slots__ + [
        "_strategy_builder",
    ]

    def __init__(self) -> None:
        """
        Build one phase-10 discovery facade with an owned strategy builder.
        """
        super().__init__()
        self._strategy_builder = CodegenPlanDiscoveryStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release discovery-owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategy_builder.cleanup()
        del self._strategy_builder

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
        strategies = self._strategy_builder.get_strategies(
            self._strategy_builder.registered_strategy_names()
        )
        for strategy in strategies:
            discovery = strategy.discover(spell_codegen_model)
            if discovery is not None:
                return discovery
        raise RuntimeError(
            "CodegenPlanDiscoverySystem could not select a plan discovery result."
        )
