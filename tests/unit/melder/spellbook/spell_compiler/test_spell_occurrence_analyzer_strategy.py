"""Unit tests for the analyzer-owned occurrence graph surface."""

from types import SimpleNamespace
from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy as occurrence_graph_strategy_module
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
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


def _make_keyed_fixture() -> tuple[Any, Any, Any, Any, Any]:
    """
    Build the shared fast-key fixture: a two-spell pool with one contracted provider.

    Returns:
        tuple: `(strategy, spellbook, spell_system_states, blueprint, path_registry)`.
    """
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
                    SimpleNamespace(
                        param_name="svc", target_spell_ids=("dep",), socket_kind=SocketKind.NORMAL,
                        position=0, parameter_kind="POSITIONAL_OR_KEYWORD", is_collection=False,
                        is_optional=False, referenced_spell_ids=(),
                    ),
                ]
            )
        }
    )
    path_registry = object()
    blueprint = SimpleNamespace(
        root_spell_id="spell-1",
        ordered_node_ids=("dep", "spell-1"),
        path_registry=path_registry,
    )
    return strategy, spellbook, spell_system_states, blueprint, path_registry


def _fixture_spell_rows() -> tuple[tuple[Any, ...], ...]:
    """Return the spell walk rows the keyed fixture's pool produces."""
    return (
        ("dep", "dep", Existence.unique.name, False),
        ("spell-1", "spell-1", Existence.unique.name, False),
    )


def test_occurrence_graph_analyzer_fast_key_serializes_visible_state() -> None:
    """
    The fast key carries the root's own rows plus ONE pool digest: the digest is the
    signature of exactly the pool-wide rows the old flat key carried, and the input
    signature is the hash of the four key parts.
    """
    strategy, spellbook, spell_system_states, blueprint, path_registry = _make_keyed_fixture()
    spell_rows = _fixture_spell_rows()

    graph_shape = strategy._build_graph_shape_rows(
        spellbook=spellbook,
        spell_system_states=spell_system_states,
    )
    pool_digest = strategy._get_pool_digest(
        spell_rows=spell_rows,
        graph_shape=graph_shape,
        analysis_pass_cache=None,
    )
    root_rows = strategy._build_root_blueprint_rows(blueprint)
    fast_key = strategy._build_occurrence_graph_fast_key(
        root_blueprint=blueprint,
        root_rows=root_rows,
        pool_digest=pool_digest,
    )
    input_signature = strategy._build_occurrence_graph_input_signature(
        root_blueprint=blueprint,
        root_rows=root_rows,
        pool_digest=pool_digest,
    )

    expected_digest = SharedCompilerExecutions.hash_codegen_signature(
        spell_rows,
        (("spell-1", (("svc", ("dep",), SocketKind.NORMAL.value, 0, "POSITIONAL_OR_KEYWORD", False, False, ()),)),),
        SystemState.dynamic,
        (("peer", "frame", "binding", "dep"),),
    )
    assert pool_digest == expected_digest
    assert fast_key == (
        "spell-1",
        ("dep", "spell-1"),
        id(path_registry),
        expected_digest,
    )
    assert input_signature == SharedCompilerExecutions.hash_codegen_signature(*fast_key)


def test_occurrence_graph_pool_digest_is_memoized_once_per_pass() -> None:
    """
    With a pass cache the pool digest is computed once and every later root reads the
    memo (even with different rows in hand); without a cache each call hashes its inputs.
    """
    strategy, spellbook, spell_system_states, _blueprint, _registry = _make_keyed_fixture()
    spell_rows = _fixture_spell_rows()
    graph_shape = strategy._build_graph_shape_rows(
        spellbook=spellbook,
        spell_system_states=spell_system_states,
    )
    changed_shape = (graph_shape[0], (), graph_shape[2])
    pass_cache: dict[str, Any] = {}

    first = strategy._get_pool_digest(
        spell_rows=spell_rows, graph_shape=graph_shape, analysis_pass_cache=pass_cache,
    )
    second = strategy._get_pool_digest(
        spell_rows=spell_rows, graph_shape=changed_shape, analysis_pass_cache=pass_cache,
    )
    uncached = strategy._get_pool_digest(
        spell_rows=spell_rows, graph_shape=changed_shape, analysis_pass_cache=None,
    )

    assert pass_cache["phase8_pool_digest"] == first
    assert second == first
    assert uncached != first


def test_occurrence_graph_pool_digest_tracks_topology_changes() -> None:
    """A changed topology socket row changes the pool digest, the fast key and the signature."""
    strategy, spellbook, spell_system_states, blueprint, _registry = _make_keyed_fixture()
    spell_rows = _fixture_spell_rows()
    changed_states = SimpleNamespace(
        _local_topologies={
            "spell-1": SimpleNamespace(
                sockets=[
                    SimpleNamespace(
                        param_name="svc", target_spell_ids=("dep",), socket_kind=SocketKind.NORMAL,
                        position=0, parameter_kind="POSITIONAL_OR_KEYWORD", is_collection=False,
                        is_optional=True, referenced_spell_ids=(),
                    ),
                ]
            )
        }
    )
    root_rows = strategy._build_root_blueprint_rows(blueprint)
    keys = []
    signatures = []
    for states in (spell_system_states, changed_states):
        graph_shape = strategy._build_graph_shape_rows(
            spellbook=spellbook, spell_system_states=states,
        )
        pool_digest = strategy._get_pool_digest(
            spell_rows=spell_rows, graph_shape=graph_shape, analysis_pass_cache=None,
        )
        keys.append(strategy._build_occurrence_graph_fast_key(
            root_blueprint=blueprint, root_rows=root_rows, pool_digest=pool_digest,
        ))
        signatures.append(strategy._build_occurrence_graph_input_signature(
            root_blueprint=blueprint, root_rows=root_rows, pool_digest=pool_digest,
        ))

    assert keys[0][:3] == keys[1][:3]
    assert keys[0][3] != keys[1][3]
    assert signatures[0] != signatures[1]


def test_occurrence_graph_key_builders_return_none_without_a_pool_digest() -> None:
    """Missing pool inputs yield no digest, no key and no signature, and leave the memo empty."""
    strategy, _spellbook, _states, blueprint, _registry = _make_keyed_fixture()
    pass_cache: dict[str, Any] = {}

    assert strategy._get_pool_digest(
        spell_rows=None, graph_shape=((), (), SystemState.dynamic), analysis_pass_cache=pass_cache,
    ) is None
    assert strategy._get_pool_digest(
        spell_rows=_fixture_spell_rows(), graph_shape=None, analysis_pass_cache=pass_cache,
    ) is None
    assert pass_cache == {}
    root_rows = strategy._build_root_blueprint_rows(blueprint)
    assert strategy._build_occurrence_graph_fast_key(
        root_blueprint=blueprint, root_rows=root_rows, pool_digest=None,
    ) is None
    assert strategy._build_occurrence_graph_input_signature(
        root_blueprint=blueprint, root_rows=None, pool_digest="digest",
    ) is None


def test_occurrence_graph_analyzer_rebuilds_when_no_analysis_is_retained(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A matching key and signature never short-circuit the build while the analysis slot is
    None (phase 5's attach nulls it every pass): the graph is rebuilt and republished.
    """
    _, spell = _make_spellbook_and_spell()
    artifact = SpellCompilerArtifact("spell-1")
    artifact._root_blueprint_phase5 = SimpleNamespace(
        root_spell_id="spell-1",
        dag=object(),
        ordered_node_ids=("dep-1", "dep-2", "spell-1"),
        path_registry=SimpleNamespace(root_path_id=0),
    )
    artifact._occurrence_graph_analysis = None
    artifact._occurrence_analysis_fast_key = ("occ-fast",)
    artifact._occurrence_analysis_input_signature = "occ-sig"
    build_calls: list[int] = []

    def _build_graph(self: Any, **kwargs: Any) -> Any:
        """Record the rebuild and return the fixture graph."""
        build_calls.append(1)
        return _make_occurrence_graph()

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
        SpellOccurrenceGraphAnalyzerStrategy, "_build_occurrence_graph", _build_graph,
    )
    monkeypatch.setattr(
        SpellOccurrenceGraphAnalyzerStrategy,
        "_extend_occurrence_graph_with_ordered_nodes",
        lambda self, **kwargs: None,
    )

    SpellOccurrenceGraphAnalyzerStrategy().analyze(spell, artifact)

    assert build_calls == [1]
    assert artifact._occurrence_graph_analysis is not None
    assert artifact._occurrence_analysis_fast_key == ("occ-fast",)


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
