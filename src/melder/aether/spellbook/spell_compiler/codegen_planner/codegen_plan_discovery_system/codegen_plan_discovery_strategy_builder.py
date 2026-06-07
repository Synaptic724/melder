from typing import Dict, Tuple

from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy import (
    CodegenPlanDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.many_only_codegen_plan_discovery_strategy import (
    ManyOnlyCodegenPlanDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.solo_codegen_plan_discovery_strategy import (
    SoloCodegenPlanDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.generalized_codegen_plan_discovery_strategy import (
    GeneralizedCodegenPlanDiscoveryStrategy,
)


class CodegenPlanDiscoveryStrategyBuilder(Cleanable):
    """
    Registry holder for phase-10 discovery strategies.

    Purpose:
        Own the discovery strategies that the phase-10 discovery facade
        iterates when selecting the planner discovery result.

    Contract:
        - Stores discovery strategies by stable `strategy_id`.
        - Registration order is discovery order.
        - Does not inspect models or emit discovery results itself.
    """

    __slots__ = Cleanable.__slots__ + [
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Build one empty discovery-strategy registry and load defaults.
        """
        super().__init__()
        self._strategies_by_name: Dict[str, CodegenPlanDiscoveryStrategy] = {}
        self._load_defaults()

    def cleanup(self) -> None:
        """
        Deterministically release the owned strategy registry.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategies_by_name.clear()
        del self._strategies_by_name

    def _load_defaults(self) -> None:
        """
        Populate the default phase-10 discovery strategy registry.
        """
        solo_strategy = SoloCodegenPlanDiscoveryStrategy()
        many_only_strategy = ManyOnlyCodegenPlanDiscoveryStrategy()
        generalized_strategy = GeneralizedCodegenPlanDiscoveryStrategy()
        self._strategies_by_name[
            solo_strategy.strategy_id
        ] = solo_strategy
        self._strategies_by_name[
            many_only_strategy.strategy_id
        ] = many_only_strategy
        self._strategies_by_name[
            generalized_strategy.strategy_id
        ] = generalized_strategy

    def get_strategy(
            self,
            strategy_name: str,
    ) -> CodegenPlanDiscoveryStrategy:
        """
        Return one registered discovery strategy by stable name.
        """
        strategy = self._strategies_by_name.get(strategy_name)
        if strategy is not None:
            return strategy
        raise RuntimeError(
            "CodegenPlanDiscoveryStrategyBuilder is missing strategy "
            f"'{strategy_name}'."
        )

    def get_strategies(
            self,
            strategy_names: Tuple[str, ...],
    ) -> Tuple[CodegenPlanDiscoveryStrategy, ...]:
        """
        Return an ordered tuple of discovery strategies by stable name.
        """
        return tuple(
            self.get_strategy(strategy_name)
            for strategy_name in strategy_names
        )

    def registered_strategy_names(self) -> Tuple[str, ...]:
        """
        Return the currently registered discovery strategy names in order.
        """
        return tuple(self._strategies_by_name.keys())
