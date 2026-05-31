from typing import Dict, Tuple

from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_contract_analyzer_strategy import (
    SpellOccurrenceContractAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_instance_analyzer_strategy import (
    SpellOccurrenceInstanceAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_order_analyzer_strategy import (
    SpellOccurrenceOrderAnalyzerStrategy,
)


class SpellAnalyzerStrategyBuilder:
    """
    Registry holder for analyzer strategies.

    Purpose:
        Own the default analyzer strategy objects keyed by stable strategy name
        so the analyzer can consume them later through explicit method
        chains.

    Contract:
        - This object does not consume spells or artifacts.
        - This object does not build or return `SpellAnalyzer`.
        - It owns a single named strategy registry.
        - `load_defaults()` populates the current built-in strategies into that
          registry.
        - Later compiler code can ask for strategies by name or ask for a
          deterministic ordered tuple of strategies for one analysis chain.
    """

    __slots__ = [
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Build one empty analyzer strategy registry and load defaults.

        Contract:
            - The registry always starts empty before default loading.
            - Default strategy registration happens through `load_defaults()`.
        """
        self._strategies_by_name: Dict[str, SpellAnalyzerStrategy] = {}
        self.load_defaults()

    def load_defaults(self) -> None:
        """
        Populate the default analyzer strategy registry.

        Purpose:
            Register the built-in analyzer strategies into the named registry
            in one explicit place instead of spreading that wiring across the
            analyzer itself.

        Contract:
            - Clears and rebuilds the registry each time it runs.
            - Keys are the strategies' stable `strategy_id` values.
            - Current defaults are the 4 occurrence-analysis strategies.
        """
        self._strategies_by_name.clear()
        for strategy_class in self._default_strategy_classes():
            self.register_strategy(strategy_class())

    @staticmethod
    def _default_strategy_classes() -> Tuple[type[SpellAnalyzerStrategy], ...]:
        """
        Return the default analyzer strategy classes in deterministic order.

        Purpose:
            Keep the built-in analyzer strategy list centralized in one place
            so defaults can be extended without rewriting `load_defaults()`
            into a pile of one-off registrations.

        Returns:
            Tuple[type[SpellAnalyzerStrategy], ...]:
                Default strategy classes in the order they should be chained by
                analyzer entrypoints.
        """
        return (
            SpellOccurrenceGraphAnalyzerStrategy,
            SpellOccurrenceOrderAnalyzerStrategy,
            SpellOccurrenceInstanceAnalyzerStrategy,
            SpellOccurrenceContractAnalyzerStrategy,
        )

    def register_strategy(
            self,
            strategy: SpellAnalyzerStrategy,
    ) -> None:
        """
        Register one analyzer strategy under its stable strategy name.

        Purpose:
            Give the builder one explicit registration path for both default
            and future manual strategy wiring.

        Args:
            strategy:
                Concrete analyzer strategy to register.

        Returns:
            None.
        """
        self._strategies_by_name[strategy.strategy_id] = strategy

    def get_strategy(
            self,
            strategy_name: str,
    ) -> SpellAnalyzerStrategy:
        """
        Return one registered analyzer strategy by stable name.

        Args:
            strategy_name:
                Stable strategy name / id.

        Returns:
            SpellAnalyzerStrategy:
                Registered analyzer strategy.

        Raises:
            RuntimeError:
                If no strategy is registered under that name.
        """
        strategy = self._strategies_by_name.get(strategy_name)
        if strategy is not None:
            return strategy
        raise RuntimeError(
            "SpellAnalyzerStrategyBuilder is missing strategy "
            f"'{strategy_name}'."
        )

    def get_strategies(
            self,
            strategy_names: Tuple[str, ...],
    ) -> Tuple[SpellAnalyzerStrategy, ...]:
        """
        Return a deterministic ordered tuple of strategies by stable name.

        Args:
            strategy_names:
                Ordered strategy names to resolve.

        Returns:
            Tuple[SpellAnalyzerStrategy, ...]:
                Ordered strategy tuple for later analyzer chaining.
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
                Sorted registered strategy names.
        """
        return tuple(sorted(self._strategies_by_name.keys()))
