"""Unit tests for the analyzer-owned occurrence graph surface."""

from types import SimpleNamespace
from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy as occurrence_graph_strategy_module
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer import (
    SpellAnalyzer,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy_builder import (
    SpellAnalyzerStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


def _make_spellbook_and_spell() -> tuple[Any, Any]:
    """Build a minimal spellbook/spell pair for occurrence analyzer tests."""
    spellbook = SimpleNamespace(
        _spell_id_pool={},
    )
    spell = SimpleNamespace(
        spell_id="spell-1",
        spell_name="spell-1",
        spell_index=SimpleNamespace(current="spell-1", id="lineage-spell-1"),
        is_existing_creation=False,
        mutation_override=None,
        _spellbook=spellbook,
        _spell_system_states=SimpleNamespace(_local_topologies={}),
    )
    spellbook._spell_id_pool["spell-1"] = spell
    return spellbook, spell


def _make_occurrence_graph() -> dict[tuple[str, int], dict[str, list[tuple[str, int]]]]:
    """Build a narrow fake occurrence graph surface for analyzer tests."""
    return {
        ("spell-1", 0): {"dep": [("dep-1", 1), ("dep-2", 2)]},
        ("dep-1", 1): {},
        ("dep-2", 2): {},
    }


def test_occurrence_analyzer_builds_graph_artifact(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The occurrence analyzer should build only the graph-side artifact."""
    _, spell = _make_spellbook_and_spell()
    artifact = SpellCompilerArtifact("spell-1")
    artifact._root_blueprint_phase5 = SimpleNamespace(
        root_spell_id="spell-1",
        dag=object(),
        ordered_node_ids=("dep-1", "dep-2", "spell-1"),
        path_registry=SimpleNamespace(root_path_id=0),
    )
    occurrence_graph = _make_occurrence_graph()

    class _Phase8Stub:
        """Phase 8 helper stub with deterministic cache output."""

        def _build_phase8_occurrence_plan_fast_key(self, **kwargs: Any) -> tuple[str]:
            return ("occ-fast",)

        def _build_phase8_occurrence_plan_input_signature(self, **kwargs: Any) -> str:
            return "occ-sig"

    monkeypatch.setattr(
        occurrence_graph_strategy_module,
        "CompilerPhase8",
        _Phase8Stub,
    )
    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_should_collapse_shared_occurrences",
        lambda self, **kwargs: True,
    )
    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_build_occurrence_graph",
        lambda self, **kwargs: occurrence_graph,
    )
    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_extend_occurrence_graph_with_ordered_nodes",
        lambda self, **kwargs: None,
    )

    analyzer = SpellAnalyzer()
    analyzer.analyze_occurrence(spell, artifact)

    assert artifact._occurrence_analysis_fast_key == ("occ-fast",)
    assert artifact._occurrence_analysis_input_signature == "occ-sig"
    assert artifact._occurrence_graph_analysis is not None
    assert artifact._occurrence_graph_analysis.edge_count == 2


def test_spell_analyzer_strategy_builder_registers_graph_strategy_by_default() -> None:
    """The analyzer builder should install only the graph strategy by default."""
    strategy_builder = SpellAnalyzerStrategyBuilder()

    assert isinstance(
        strategy_builder.get_strategy("spell_occurrence_graph_analyzer"),
        SpellOccurrenceGraphAnalyzerStrategy,
    )
    assert strategy_builder.registered_strategy_names() == (
        "spell_occurrence_graph_analyzer",
    )
