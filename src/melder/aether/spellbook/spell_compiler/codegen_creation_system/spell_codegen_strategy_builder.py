from typing import Dict, Tuple

from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_strategy import (
    GeneralizedCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.fallback_no_overrides.fallback_no_overrides_codegen_creation_strategy import (
    FallbackNoOverridesCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_strategy import (
    ManyOnlyCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_strategy import (
    SoloCodegenCreationStrategy,
)


class SpellCodegenStrategyBuilder(Cleanable):
    """
    Registry holder for codegen creation strategies.

    Purpose:
        Own the default codegen creation strategies keyed by stable strategy
        id so `CodegenCreationSystem` can resolve them after discovery.
    """

    __slots__ = Cleanable.__slots__ + [
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Build one empty codegen strategy registry and load defaults.
        """
        super().__init__()
        self._strategies_by_name: Dict[str, SpellCodegenStrategy] = {}
        self._load_defaults()

    def cleanup(self) -> None:
        """
        Deterministically release builder-owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategies_by_name.clear()
        del self._strategies_by_name

    def _load_defaults(self) -> None:
        """
        Populate the default codegen creation strategy registry.

        Contract:
            - Generalized planner output now resolves to one family facade.
            - The standalone generalized no-overrides strategy remains
              registered as the fallback public creation strategy.
            - Older generalized step wrappers remain importable for
              compatibility, but are no longer discovery-selected public
              strategies here.
            - Registration order is execution order.
        """
        solo_codegen_creation_strategy = SoloCodegenCreationStrategy()
        self._strategies_by_name[
            solo_codegen_creation_strategy.strategy_id
        ] = solo_codegen_creation_strategy
        many_only_codegen_creation_strategy = ManyOnlyCodegenCreationStrategy()
        self._strategies_by_name[
            many_only_codegen_creation_strategy.strategy_id
        ] = many_only_codegen_creation_strategy
        generalized_codegen_creation_strategy = (
            GeneralizedCodegenCreationStrategy()
        )
        self._strategies_by_name[
            generalized_codegen_creation_strategy.strategy_id
        ] = generalized_codegen_creation_strategy
        generalized_no_overrides_codegen_creation_strategy = (
            FallbackNoOverridesCodegenCreationStrategy()
        )
        self._strategies_by_name[
            generalized_no_overrides_codegen_creation_strategy.strategy_id
        ] = generalized_no_overrides_codegen_creation_strategy

    def get_strategy(
            self,
            strategy_name: str,
    ) -> SpellCodegenStrategy:
        """
        Return one registered codegen creation strategy by stable name.

        Args:
            strategy_name:
                Stable `strategy_id` the strategy was registered under.

        Returns:
            SpellCodegenStrategy: The registered strategy.

        Raises:
            RuntimeError: If no strategy is registered under that name.
        """
        strategy = self._strategies_by_name.get(strategy_name)
        if strategy is not None:
            return strategy
        raise RuntimeError(
            "SpellCodegenStrategyBuilder is missing strategy "
            f"'{strategy_name}'."
        )

    def get_strategies(
            self,
            strategy_names: Tuple[str, ...],
    ) -> Tuple[SpellCodegenStrategy, ...]:
        """
        Return one deterministic ordered tuple of creation strategies.

        Args:
            strategy_names:
                Ordered stable strategy ids to resolve.

        Returns:
            Tuple[SpellCodegenStrategy, ...]:
                Ordered strategy tuple for later execution.
        """
        return tuple(
            self.get_strategy(strategy_name)
            for strategy_name in strategy_names
        )

    def registered_strategy_names(self) -> Tuple[str, ...]:
        """
        Return currently registered strategy ids in execution order.
        """
        return tuple(self._strategies_by_name.keys())
