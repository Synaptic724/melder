from typing import Dict, Tuple

from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy import (
    SpellCodegenPlanStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_many_only_codegen_plan_strategy import (
    SpellGeneralizedManyOnlyCodegenPlanStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_codegen_plan_strategy import (
    SpellGeneralizedCodegenPlanStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.strategies.spell_generalized_solo_codegen_plan_strategy import (
    SpellGeneralizedSoloCodegenPlanStrategy,
)


class SpellCodegenPlanStrategyBuilder(Cleanable):
    """
    Registry holder for codegen-plan strategies.

    Purpose:
        Own the default plan strategy objects keyed by stable strategy name so
        the planner can consume them later through explicit strategy-chain
        selection.

    Contract:
        - This object does not consume models or artifacts.
        - This object does not build or return `SpellCodegenPlan`.
        - It owns a single named strategy registry.
        - `_load_defaults()` populates the current built-in strategies into
          that registry.
        - Later compiler code can ask for strategies by name or ask for a
          deterministic ordered tuple of strategies for one planner chain.
    """

    __slots__ = Cleanable.__slots__ + [
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Build one empty plan strategy registry and load defaults.

        Contract:
            - The registry always starts empty before default loading.
            - Default strategy registration happens through `_load_defaults()`.
        """
        super().__init__()
        self._strategies_by_name: Dict[str, SpellCodegenPlanStrategy] = {}
        self._load_defaults()

    def cleanup(self) -> None:
        """
        Clean up internal references.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategies_by_name.clear()
        del self._strategies_by_name

    def _load_defaults(self) -> None:
        """
        Populate the default plan strategy registry.

        Purpose:
            Keep the built-in plan strategy wiring in one explicit place
            instead of spreading that registration across planner call sites.

        Contract:
            - Clears and rebuilds the registry each time it runs.
            - Keys are the strategies' stable `strategy_id` values.
            - Current defaults are the solo, many-only, and generalized
              model-native strategies.
        """
        generalized_solo_codegen_plan_strategy = (
            SpellGeneralizedSoloCodegenPlanStrategy()
        )
        self._strategies_by_name[
            generalized_solo_codegen_plan_strategy.strategy_id
        ] = generalized_solo_codegen_plan_strategy
        generalized_many_only_codegen_plan_strategy = (
            SpellGeneralizedManyOnlyCodegenPlanStrategy()
        )
        self._strategies_by_name[
            generalized_many_only_codegen_plan_strategy.strategy_id
        ] = generalized_many_only_codegen_plan_strategy
        generalized_codegen_plan_strategy = SpellGeneralizedCodegenPlanStrategy()
        self._strategies_by_name[
            generalized_codegen_plan_strategy.strategy_id
        ] = generalized_codegen_plan_strategy

    def get_strategy(
            self,
            strategy_name: str,
    ) -> SpellCodegenPlanStrategy:
        """
        Return one registered plan strategy by stable name.

        Args:
            strategy_name:
                Stable strategy name / id.

        Returns:
            SpellCodegenPlanStrategy:
                Registered plan strategy.

        Raises:
            RuntimeError:
                If no strategy is registered under that name.
        """
        strategy = self._strategies_by_name.get(strategy_name)
        if strategy is not None:
            return strategy
        raise RuntimeError(
            "SpellCodegenPlanStrategyBuilder is missing strategy "
            f"'{strategy_name}'."
        )

    def get_strategies(
            self,
            strategy_names: Tuple[str, ...],
    ) -> Tuple[SpellCodegenPlanStrategy, ...]:
        """
        Return a deterministic ordered tuple of strategies by stable name.

        Args:
            strategy_names:
                Ordered strategy names to resolve.

        Returns:
            Tuple[SpellCodegenPlanStrategy, ...]:
                Ordered strategy tuple for later planner chaining.
        """
        return tuple(
            self.get_strategy(strategy_name)
            for strategy_name in strategy_names
        )

    def registered_strategy_names(self) -> Tuple[str, ...]:
        """
        Return the currently registered strategy names in deterministic order.

        Returns:
            Tuple[str, ...]:
                Registered strategy names in execution order.
        """
        return tuple(self._strategies_by_name.keys())
