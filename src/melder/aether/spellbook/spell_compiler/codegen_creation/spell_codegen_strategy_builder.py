from typing import Dict, Tuple

from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.strategies.spell_generalized_codegen_creation_strategy import (
    SpellGeneralizedCodegenCreationStrategy,
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
            - Current default is the generalized placeholder strategy only.
            - Registration order is execution order.
        """
        generalized_codegen_creation_strategy = (
            SpellGeneralizedCodegenCreationStrategy()
        )
        self._strategies_by_name[
            generalized_codegen_creation_strategy.strategy_id
        ] = generalized_codegen_creation_strategy

    def get_strategy(
            self,
            strategy_name: str,
    ) -> SpellCodegenStrategy:
        """
        Return one registered codegen creation strategy by stable name.
        """
        strategy = self._strategies_by_name.get(strategy_name)
        if strategy is not None:
            return strategy
        raise RuntimeError(
            "SpellCodegenStrategyBuilder is missing strategy "
            f"'{strategy_name}'."
        )

    def registered_strategy_names(self) -> Tuple[str, ...]:
        """
        Return currently registered strategy ids in execution order.
        """
        return tuple(self._strategies_by_name.keys())
