from typing import Dict, Tuple

from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable


class SpellAnalyzerStrategyBuilder(Cleanable):
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

    Registration:
        MELDER KERNEL. A compiler registry/builder held by
        `SpellAnalyzer`; not a bind target. (Left untagged as-is; guard classification
        is the owner's call.)

    Subsystem Context:
        The registry holder of the `spell_analyzer` package: `SpellAnalyzer` owns one
        and resolves its named strategy chains from it.

    System Context:
        Phase 8 (occurrence analysis) of the conjure pipeline.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Registry of analyzer strategies keyed by strategy_id: load_defaults / "
        "get_strategy / get_strategies / registered_strategy_names. Owned by SpellAnalyzer; holds "
        "no spells or artifacts."
    )

    __slots__ = Cleanable.__slots__ + [
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Build one empty analyzer strategy registry and load defaults.

        Contract:
            - The registry always starts empty before default loading.
            - Default strategy registration happens through `load_defaults()`.
        """
        super().__init__()
        self._strategies_by_name: Dict[str, SpellAnalyzerStrategy] = {}
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
        Populate the default analyzer strategy registry.

        Purpose:
            Register the built-in analyzer strategies into the named registry
            in one explicit place instead of spreading that wiring across the
            analyzer itself.

        Contract:
            - Clears and rebuilds the registry each time it runs.
            - Keys are the strategies' stable `strategy_id` values.
            - Current defaults include only the primary occurrence graph
              analysis strategy. Derived occurrence consumers belong under the
              artifact processor.
        """
        graph_strategy = SpellOccurrenceGraphAnalyzerStrategy()
        self._strategies_by_name[graph_strategy.strategy_id] = graph_strategy


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
