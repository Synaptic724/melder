from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery import (
    CodegenCreationDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy_builder import (
    CodegenCreationDiscoveryStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.utilities.general_base.cleanable import Cleanable


class CodegenCreationDiscoverySystem(Cleanable):
    """
    Select the best current codegen creation strategy for one model/plan pair.

    Purpose:
        Interpret `SpellCodegenModel` plus `SpellCodegenPlan` and choose which
        codegen creation strategy the creation system should use.

    Contract:
        - Reads the model and plan only.
        - Does not produce emitted code or runtime artifacts itself.
        - Chooses the concrete codegen style for the current plan family.
        - Defaults to the first generalized creation chain/style until the
          remaining creation lanes are ported fully.
    """

    __slots__ = Cleanable.__slots__ + [
        "_strategy_builder",
    ]

    def __init__(self) -> None:
        """
        Build one phase-11 discovery facade with an owned strategy builder.
        """
        super().__init__()
        self._strategy_builder = CodegenCreationDiscoveryStrategyBuilder()

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
            spell_codegen_plan: SpellCodegenPlan,
    ) -> CodegenCreationDiscovery:
        """
        Select the current best ordered codegen creation strategy chain.

        Contract:
            - Reads planner metadata only for the current migration selection
              rule.
            - Returns a deterministic strategy tuple in execution order plus
              one selected codegen style.
            - Does not mutate the model or plan.
        """
        strategies = self._strategy_builder.get_strategies(
            self._strategy_builder.registered_strategy_names()
        )
        for strategy in strategies:
            discovery = strategy.discover(
                spell_codegen_model,
                spell_codegen_plan,
            )
            if discovery is not None:
                return discovery
        raise RuntimeError(
            "CodegenCreationDiscoverySystem could not select a creation discovery result."
        )
