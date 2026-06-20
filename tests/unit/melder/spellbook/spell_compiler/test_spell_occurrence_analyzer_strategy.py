"""Unit tests for the analyzer-owned occurrence graph surface."""

from types import SimpleNamespace
from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy as occurrence_graph_strategy_module
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
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


class _SpellIndexProbe:
    """Hashable spell-index double for contracted lookup tests."""

    __slots__ = ["selected_spell_id", "id"]

    def __init__(self, spell_id: str) -> None:
        """Store current and lineage ids."""
        self.selected_spell_id = spell_id
        self.id = "lineage-{0}".format(spell_id)

    def __hash__(self) -> int:
        """Keep the probe usable as a dictionary key."""
        return hash((self.selected_spell_id, self.id))


def _make_spellbook_and_spell() -> tuple[Any, Any]:
    """Build a minimal spellbook/spell pair for occurrence analyzer tests."""
    spellbook = SimpleNamespace(
        _spell_id_pool={},
    )
    spell = SimpleNamespace(
        spell_id="spell-1",
        spell_name="spell-1",
        spell_index=SimpleNamespace(selected_spell_id="spell-1", id="lineage-spell-1"),
        existence=Existence.unique,
        has_disposal_methods=False,
        is_existing_creation=False,
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

    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_build_occurrence_graph_fast_key",
        lambda self, **kwargs: ("occ-fast",),
    )
    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_build_occurrence_graph_input_signature",
        lambda self, **kwargs: "occ-sig",
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
    assert (
        artifact._occurrence_graph_analysis.existence_occurrence_analysis.root_existence
        is Existence.unique
    )
    assert (
        artifact._occurrence_graph_analysis.existence_occurrence_analysis.total_spell_count
        == 1
    )
    first_row = (
        artifact._occurrence_graph_analysis.existence_occurrence_analysis
        .spell_existence_rows[0]
    )
    assert first_row.spell_id == "spell-1"
    assert first_row.existence is Existence.unique
    assert first_row.has_disposal_methods is False
    assert (
        artifact._occurrence_graph_analysis.existence_occurrence_analysis
        .disposal_enabled_spell_count
        == 0
    )
    assert (
        artifact._occurrence_graph_analysis.existence_occurrence_analysis
        .existence_disposal_counts
        == (((Existence.unique, False), 1),)
    )


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


def test_occurrence_graph_analyzer_fast_key_serializes_visible_state() -> None:
    """The analyzer fast-key helper should serialize the visible graph state only."""
    strategy = SpellOccurrenceGraphAnalyzerStrategy()
    spellbook = _make_spellbook_and_spell()[0]
    root_spell = spellbook._spell_id_pool["spell-1"]
    dep_spell = SimpleNamespace(
        spell_id="dep",
        spell_name="dep",
        spell_index=_SpellIndexProbe("dep"),
        existence=Existence.unique,
        has_disposal_methods=False,
        is_existing_creation=False,
    )
    spellbook._spell_id_pool["dep"] = dep_spell
    spellbook._lookup_contracted_spells = {
        "peer": {
            ("frame", "binding"): dep_spell.spell_index,
        }
    }
    spellbook._contracted_spells = {
        "peer": {
            dep_spell.spell_index: dep_spell,
        }
    }
    spellbook._aetheric_frame_configuration = SimpleNamespace(
        system_state=SystemState.dynamic,
    )
    spell_system_states = SimpleNamespace(
        _local_topologies={
            "spell-1": SimpleNamespace(
                sockets=[
                    SimpleNamespace(param_name="svc", target_spell_ids=("dep",)),
                ]
            )
        }
    )
    path_registry = object()
    blueprint = SimpleNamespace(
        root_spell_id="spell-1",
        ordered_node_ids=("dep", "spell-1"),
        path_registry=path_registry,
        socket_refs=[
            SimpleNamespace(
                node_id="spell-1",
                param_name="svc",
                param_path_id=7,
                socket_kind=SocketKind.NORMAL,
            )
        ],
    )

    graph_shape = strategy._build_graph_shape_rows(
        spellbook=spellbook,
        spell_system_states=spell_system_states,
    )
    fast_key = strategy._build_occurrence_graph_fast_key(
        root_blueprint=blueprint,
        spell_rows=(
            ("dep", "dep", Existence.unique.name, False),
            ("spell-1", "spell-1", Existence.unique.name, False),
        ),
        graph_shape=graph_shape,
    )

    assert fast_key == (
        "spell-1",
        ("dep", "spell-1"),
        id(path_registry),
        (("spell-1", "svc", 7, SocketKind.NORMAL.value),),
        (
            ("dep", "dep", Existence.unique.name, False),
            ("spell-1", "spell-1", Existence.unique.name, False),
        ),
        (("spell-1", (("svc", ("dep",)),)),),
        SystemState.dynamic,
        (("peer", "frame", "binding", "dep"),),
    )
def test_occurrence_graph_analyzer_reuses_cached_graph_when_fast_key_and_signature_match(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The analyzer strategy should skip rebuild when the cached graph truth still matches."""
    strategy = SpellOccurrenceGraphAnalyzerStrategy()
    spellbook, spell = _make_spellbook_and_spell()
    spellbook._aetheric_frame_configuration = SimpleNamespace(
        system_state=SystemState.dynamic,
    )
    artifact = SpellCompilerArtifact("spell-1")
    cached_graph = object()
    artifact._root_blueprint_phase5 = SimpleNamespace(root_spell_id="spell-1")
    artifact._occurrence_graph_analysis = cached_graph
    artifact._occurrence_analysis_fast_key = ("fast",)
    artifact._occurrence_analysis_input_signature = "sig"

    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_build_occurrence_graph_fast_key",
        lambda self, **kwargs: ("fast",),
    )
    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_build_occurrence_graph_input_signature",
        lambda self, **kwargs: "sig",
    )
    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_build_occurrence_graph",
        lambda self, **kwargs: (_ for _ in ()).throw(
            AssertionError("graph rebuild should not run")
        ),
    )

    strategy.analyze(spell, artifact)

    assert artifact._occurrence_graph_analysis is cached_graph
