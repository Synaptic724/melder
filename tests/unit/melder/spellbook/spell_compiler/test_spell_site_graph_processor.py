"""Unit contracts for the Phase-9 site-graph section and its processor strategy (override design S1)."""

from types import SimpleNamespace
from typing import Dict, Optional, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
    SpellInjectionAnalysis,
    SpellInjectionInstanceSpec,
    SpellInjectionParamSource,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (
    SpellSite,
    SpellSiteGraphAnalysis,
    SpellSiteParam,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_site_graph_processor_strategy import (
    SpellSiteGraphProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)

Key = Tuple[str, Optional[int]]


def _socket(
        spell_id: str,
        name: str,
        position: int,
        *,
        kind: str = "POSITIONAL_OR_KEYWORD",
        socket_kind: SocketKind = SocketKind.NORMAL,
        optional: bool = False,
        collection: bool = False,
) -> SpellSocketDescriptor:
    """Build one Phase-3 socket descriptor for a test topology."""
    return SpellSocketDescriptor(
        spell_id=spell_id,
        param_name=name,
        position=position,
        socket_kind=socket_kind,
        is_collection=collection,
        is_optional=optional,
        target_spell_ids=(),
        parameter_kind=kind,
    )


def _dependency(*keys: Key, collection: bool = False) -> SpellInjectionParamSource:
    """Build one dependency injection source over instance keys."""
    return SpellInjectionParamSource(kind="dependency", dependency_keys=tuple(keys), is_collection=collection)


def _spec(**sources: SpellInjectionParamSource) -> SpellInjectionInstanceSpec:
    """Build one injection spec from keyword parameter sources."""
    return SpellInjectionInstanceSpec(
        param_sources=dict(sources),
        allow_list_aggregation=False,
        uses_positional_override=False,
    )


def _build(
        root: Key,
        specs: Dict[Key, SpellInjectionInstanceSpec],
        topologies: Dict[str, SpellLocalTopology],
) -> SpellSiteGraphAnalysis:
    """Run the strategy's graph builder over hand-built sections."""
    injection = SpellInjectionAnalysis(
        root_spell_id=root[0],
        root_instance_key=root,
        instance_specs_by_instance_key=specs,
    )
    return SpellSiteGraphProcessorStrategy.build_site_graph(
        root_instance_key=root,
        injection_shape=injection,
        topology_for=topologies.get,
    )


def _topology(spell_id: str, *sockets: SpellSocketDescriptor) -> SpellLocalTopology:
    """Build one local topology."""
    return SpellLocalTopology(spell_id, sockets)


def _shallow() -> SpellSiteGraphAnalysis:
    """Root(a: A, b: B), all many."""
    root, a, b = ("root", 0), ("a", 1), ("b", 2)
    specs = {root: _spec(a=_dependency(a), b=_dependency(b)), a: _spec(), b: _spec()}
    topologies = {
        "root": _topology("root", _socket("root", "a", 0), _socket("root", "b", 1)),
        "a": _topology("a"),
        "b": _topology("b"),
    }
    return _build(root, specs, topologies)


def _shared_diamond() -> SpellSiteGraphAnalysis:
    """Root(l: L, r: R); L(s: S); R(s: S); S shared with S(x: X)."""
    root, left, right, shared, leaf = ("root", 0), ("l", 1), ("r", 2), ("s", None), ("x", 4)
    specs = {
        root: _spec(l=_dependency(left), r=_dependency(right)),
        left: _spec(s=_dependency(shared)),
        right: _spec(s=_dependency(shared)),
        shared: _spec(x=_dependency(leaf)),
        leaf: _spec(),
    }
    topologies = {
        "root": _topology("root", _socket("root", "l", 0), _socket("root", "r", 1)),
        "l": _topology("l", _socket("l", "s", 0)),
        "r": _topology("r", _socket("r", "s", 0)),
        "s": _topology("s", _socket("s", "x", 0)),
        "x": _topology("x"),
    }
    return _build(root, specs, topologies)


def test_many_graph_lists_root_first_with_one_path_per_site() -> None:
    """Sites follow the reversed DFS post-order (parents first) and every many site is reached once."""
    graph = _shallow()

    assert [site.instance_key for site in graph.sites] == [("root", 0), ("b", 2), ("a", 1)]
    assert graph.root_site_index == 0
    assert graph.path_counts == (1, 1, 1)
    assert [(p.name, p.source_kind, p.dependency_sites) for p in graph.sites[0].params] == [
        ("a", "dependency", (2,)),
        ("b", "dependency", (1,)),
    ]
    assert graph.shared_site_count == 0
    assert graph.site_index_by_instance_key[("b", 2)] == 1


def test_shared_site_appears_once_and_counts_every_logical_path() -> None:
    """A shared existence is one site; its path count is the number of root paths to it."""
    graph = _shared_diamond()
    shared = graph.site_index_by_instance_key[("s", None)]
    leaf = graph.site_index_by_instance_key[("x", 4)]

    assert graph.sites[shared].shared is True
    assert graph.path_counts[shared] == 2
    assert graph.path_counts[leaf] == 2
    assert shared > graph.site_index_by_instance_key[("l", 1)]
    assert shared > graph.site_index_by_instance_key[("r", 2)]
    assert graph.param_index["s"] == ((1, "s"), (2, "s"))
    assert graph.shared_site_count == 1


def test_collection_parameter_fans_out_to_every_member() -> None:
    """A collection socket keeps every member site, in injection order."""
    root, first, second = ("root", 0), ("m1", 1), ("m2", 2)
    specs = {root: _spec(items=_dependency(first, second, collection=True)), first: _spec(), second: _spec()}
    topologies = {"root": _topology("root", _socket("root", "items", 0, collection=True))}
    graph = _build(root, specs, topologies)

    items = graph.param(0, "items")
    assert items is not None
    assert items.is_collection is True
    assert [graph.sites[index].instance_key for index in items.dependency_sites] == [first, second]
    assert graph.path_counts == (1, 1, 1)


def test_every_constructor_parameter_is_listed_with_its_source() -> None:
    """Plain, unresolved, required and contract parameters are rows too, in position order."""
    root, a = ("root", 0), ("a", 1)
    specs = {
        root: _spec(
            a=SpellInjectionParamSource(kind="dependency", dependency_keys=(a,), contract_key="a"),
            work=SpellInjectionParamSource(kind="unresolved_input", position=1, parameter_kind="POSITIONAL_OR_KEYWORD"),
            ref=SpellInjectionParamSource(
                kind="override_required",
                position=2,
                parameter_kind="POSITIONAL_OR_KEYWORD",
                referenced_spell_ids=("p",),
            ),
        ),
        a: _spec(),
    }
    topologies = {
        "root": _topology(
            "root",
            _socket("root", "k", 4, kind="KEYWORD_ONLY", optional=True),
            _socket("root", "a", 0, kind="POSITIONAL_ONLY"),
            _socket("root", "work", 1, socket_kind=SocketKind.UNRESOLVED_INPUT),
            _socket("root", "ref", 2, socket_kind=SocketKind.OVERRIDE_REQUIRED),
            _socket("root", "n", 3, optional=True),
        ),
    }
    graph = _build(root, specs, topologies)

    assert [param.as_row()[:8] for param in graph.sites[0].params] == [
        ("a", 0, "POSITIONAL_ONLY", SocketKind.NORMAL.value, False, False, "dependency", "a"),
        ("work", 1, "POSITIONAL_OR_KEYWORD", SocketKind.UNRESOLVED_INPUT.value, False, False, "unresolved_input", None),
        ("ref", 2, "POSITIONAL_OR_KEYWORD", SocketKind.OVERRIDE_REQUIRED.value, False, False, "override_required", None),
        ("n", 3, "POSITIONAL_OR_KEYWORD", SocketKind.NORMAL.value, False, True, "plain", None),
        ("k", 4, "KEYWORD_ONLY", SocketKind.NORMAL.value, False, True, "plain", None),
    ]


def test_site_without_topology_takes_rows_from_injection_sources() -> None:
    """A missing topology never fails Phase 9; the injection sources describe the parameters."""
    root, a = ("root", 0), ("a", 1)
    specs = {
        root: _spec(
            a=_dependency(a),
            work=SpellInjectionParamSource(kind="unresolved_input", position=1, parameter_kind="KEYWORD_ONLY"),
        ),
        a: _spec(),
    }
    graph = _build(root, specs, {})

    assert [param.as_row() for param in graph.sites[0].params] == [
        ("a", -1, None, SocketKind.NORMAL.value, False, False, "dependency", None, (1,)),
        ("work", 1, "KEYWORD_ONLY", SocketKind.UNRESOLVED_INPUT.value, False, False, "unresolved_input", None, ()),
    ]
    assert graph.sites[1].params == ()


def test_missing_injection_spec_for_a_reachable_site_raises() -> None:
    """An inconsistent injection section fails loudly instead of dropping a site."""
    root = ("root", 0)
    specs = {root: _spec(a=_dependency(("a", 1)))}

    with pytest.raises(RuntimeError, match="missing the injection spec"):
        _build(root, specs, {})


def test_analysis_rejects_malformed_rows() -> None:
    """The section validates positions, alignment and dependency direction."""
    param = SpellSiteParam(
        name="a", position=0, parameter_kind=None, socket_kind_value=1, is_collection=False,
        is_optional=False, source_kind="dependency", contract_key=None, dependency_sites=(0,),
    )
    root = SpellSite(index=0, instance_key=("root", 0), spell_id="root", shared=False, params=(param,))
    misplaced = SpellSite(index=1, instance_key=("root", 0), spell_id="root", shared=False, params=())

    with pytest.raises(ValueError, match="at least the root"):
        SpellSiteGraphAnalysis(sites=(), path_counts=())
    with pytest.raises(ValueError, match="align"):
        SpellSiteGraphAnalysis(sites=(misplaced,), path_counts=())
    with pytest.raises(ValueError, match="does not match its position"):
        SpellSiteGraphAnalysis(sites=(misplaced,), path_counts=(1,))
    with pytest.raises(ValueError, match="later sites"):
        SpellSiteGraphAnalysis(sites=(root,), path_counts=(1,))


def test_analysis_cleanup_is_idempotent_and_releases_fields() -> None:
    """Cleanup releases the lookup state and may run twice."""
    graph = _shallow()

    graph.cleanup()
    graph.cleanup()

    assert graph.is_cleaned
    assert not hasattr(graph, "sites")
    assert not hasattr(graph, "param_index")


def test_param_lookup_returns_none_for_unknown_parameter() -> None:
    """Lookups by (site, name) are exact."""
    graph = _shallow()

    assert graph.param(0, "a") is graph.sites[0].params[0]
    assert graph.param(0, "zzz") is None
    assert graph.param(1, "a") is None


def test_process_requires_instance_and_injection_sections() -> None:
    """The strategy runs only after the instance and injection strategies."""
    strategy = SpellSiteGraphProcessorStrategy()
    spell = SimpleNamespace()

    with pytest.raises(RuntimeError, match="instance_shape"):
        strategy.process(spell, SimpleNamespace(), SpellCodegenModel())
    model = SpellCodegenModel()
    model.instance_shape = SimpleNamespace(root_instance_key=("root", 0))
    with pytest.raises(RuntimeError, match="injection_shape"):
        strategy.process(spell, SimpleNamespace(), model)


def test_process_publishes_section_and_cleans_superseded_one() -> None:
    """A refit publishes the new section and cleans the previous one."""
    root = ("root", 0)
    topologies = {"root": _topology("root", _socket("root", "n", 0, optional=True))}
    spell = SimpleNamespace(
        _spellbook=SimpleNamespace(_spell_system_states=SimpleNamespace(get_local_topology_by_id=topologies.get))
    )
    model = SpellCodegenModel()
    model.instance_shape = SimpleNamespace(root_instance_key=root)
    model.injection_shape = SpellInjectionAnalysis(
        root_spell_id="root", root_instance_key=root, instance_specs_by_instance_key={root: _spec()},
    )
    previous = _shallow()
    model.site_graph_shape = previous
    strategy = SpellSiteGraphProcessorStrategy()

    strategy.process(spell, SimpleNamespace(), model)

    assert strategy.strategy_id == "spell_site_graph_processor"
    assert model.site_graph_shape is not previous
    assert [param.name for param in model.site_graph_shape.sites[0].params] == ["n"]
    assert previous.is_cleaned
