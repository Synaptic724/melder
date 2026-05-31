"""Direct unit tests for the spell analyzer facade and builder."""

from typing import Any, List, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer import (
    SpellAnalyzer,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy_builder import (
    SpellAnalyzerStrategyBuilder,
)


class _ArtifactProbe:
    """Minimal artifact double recording cleaned-state checks."""

    def __init__(self) -> None:
        """Build one artifact probe with a check counter."""
        self.check_cleaned_calls = 0

    def check_cleaned(self) -> None:
        """Record one cleaned-state check."""
        self.check_cleaned_calls += 1


class _StrategyProbe:
    """Minimal analyzer strategy double recording dispatch order."""

    def __init__(
            self,
            strategy_id: str,
            events: List[str],
    ) -> None:
        """Store the stable id and the shared event sink."""
        self.strategy_id = strategy_id
        self._events = events

    def analyze(
            self,
            spell: Any,
            artifact: Any,
    ) -> None:
        """Record the dispatch event for this strategy."""
        _ = spell
        _ = artifact
        self._events.append(self.strategy_id)


class _BuilderProbe:
    """Minimal builder double for analyzer facade tests."""

    def __init__(
            self,
            strategies: Tuple[Any, ...],
    ) -> None:
        """Store the strategy tuple returned during dispatch."""
        self._strategies = strategies
        self.requested_strategy_ids: Tuple[str, ...] = ()
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True

    def get_strategies(
            self,
            strategy_ids: Tuple[str, ...],
    ) -> Tuple[Any, ...]:
        """Return the configured strategy tuple and record the request."""
        self.requested_strategy_ids = strategy_ids
        return self._strategies


def test_spell_analyzer_analyze_occurrence_dispatches_named_chain_in_order() -> None:
    """The analyzer facade should dispatch the configured occurrence chain in order."""
    analyzer = SpellAnalyzer()
    events: List[str] = []
    analyzer._strategy_builder = _BuilderProbe(
        (
            _StrategyProbe("first", events),
            _StrategyProbe("second", events),
        )
    )
    artifact = _ArtifactProbe()
    spell = object()

    analyzer.analyze_occurrence(spell, artifact)

    assert analyzer._strategy_builder.requested_strategy_ids == (
        "spell_occurrence_graph_analyzer",
    )
    assert artifact.check_cleaned_calls == 1
    assert events == ["first", "second"]


def test_spell_analyzer_cleanup_cleans_builder_and_drops_reference() -> None:
    """Analyzer cleanup should clean the owned builder and drop the reference."""
    analyzer = SpellAnalyzer()
    builder = _BuilderProbe(())
    analyzer._strategy_builder = builder

    analyzer.cleanup()

    assert builder.cleanup_called is True
    assert not hasattr(analyzer, "_strategy_builder")


def test_spell_analyzer_strategy_builder_raises_for_unknown_strategy() -> None:
    """The real analyzer strategy builder should fail hard on unknown strategy ids."""
    builder = SpellAnalyzerStrategyBuilder()

    with pytest.raises(RuntimeError, match="missing strategy 'missing_strategy'"):
        builder.get_strategy("missing_strategy")
