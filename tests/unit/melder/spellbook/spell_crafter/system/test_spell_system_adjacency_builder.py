import pytest

from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)


class _State:
    def __init__(self, spell_id, deps):
        self.current_spell_id = spell_id
        self.direct_dependencies = deps


class _StatesStub:
    def __init__(self, states, topologies=None):
        self._states = states
        self._topologies = topologies or {}
        self.get_local_topology_calls = []

    def iter_states(self):
        # Builder expects iterable snapshot
        return list(self._states)

    def get_local_topology_by_id(self, spell_id):
        self.get_local_topology_calls.append(spell_id)
        return self._topologies.get(spell_id)


def test_build_raises_on_none_states():
    with pytest.raises(ValueError):
        SpellSystemAdjacencyBuilder.build(None)


def test_build_skips_states_with_null_spell_id():
    states = _StatesStub(
        [
            _State(None, {"x"}),
            _State("a", None),
        ]
    )
    snapshot = SpellSystemAdjacencyBuilder.build(states)
    assert "a" in snapshot.all_spell_ids
    assert None not in snapshot.all_spell_ids
    assert snapshot.dependencies["a"] == set()
    assert snapshot.reverse_dependencies == {}


def test_build_collects_dependencies_reverse_and_roots():
    states = _StatesStub(
        [
            _State("s1", ["s2", "s3"]),
            _State("s2", []),
            _State("s3", None),
        ]
    )
    snap = SpellSystemAdjacencyBuilder.build(states)

    assert snap.dependencies["s1"] == {"s2", "s3"}
    assert snap.dependencies["s2"] == set()
    assert snap.dependencies["s3"] == set()

    assert snap.reverse_dependencies["s2"] == {"s1"}
    assert snap.reverse_dependencies["s3"] == {"s1"}
    assert snap.all_spell_ids == {"s1", "s2", "s3"}
    # Roots are those never used as a dependency
    assert snap.root_spell_ids == {"s1"}


def test_direct_dependencies_normalized_to_sets():
    states = _StatesStub(
        [
            _State("a", ("b", "c")),
        ]
    )
    snap = SpellSystemAdjacencyBuilder.build(states)
    assert snap.dependencies["a"] == {"b", "c"}


def test_topologies_are_collected_per_spell():
    topo_a = object()
    states = _StatesStub(
        [
            _State("a", []),
            _State("b", []),
        ],
        topologies={"a": topo_a},
    )
    snap = SpellSystemAdjacencyBuilder.build(states)
    assert snap.topologies == {"a": topo_a}
    # get_local_topology_by_id consulted for each spell_id
    assert set(states.get_local_topology_calls) == {"a", "b"}


def test_snapshot_is_instance_of_expected_type():
    states = _StatesStub([_State("a", [])])
    snap = SpellSystemAdjacencyBuilder.build(states)
    assert isinstance(snap, SpellSystemAdjacencySnapshot)


def test_builder_handles_empty_states_snapshot():
    states = _StatesStub([])
    snap = SpellSystemAdjacencyBuilder.build(states)
    assert snap.dependencies == {}
    assert snap.reverse_dependencies == {}
    assert snap.all_spell_ids == set()
    assert snap.root_spell_ids == set()
    assert snap.topologies == {}


def test_duplicate_dependencies_are_deduplicated():
    states = _StatesStub([_State("a", ["b", "b", "b"])])
    snap = SpellSystemAdjacencyBuilder.build(states)
    assert snap.dependencies["a"] == {"b"}
    assert snap.reverse_dependencies["b"] == {"a"}


def test_root_calculation_ignores_unknown_dependency_ids():
    states = _StatesStub([_State("a", ["ghost"])])
    snap = SpellSystemAdjacencyBuilder.build(states)
    # "ghost" never added to all_spell_ids, so "a" remains a root
    assert snap.root_spell_ids == {"a"}
    assert "ghost" not in snap.all_spell_ids


def test_topology_absent_results_in_empty_topologies():
    states = _StatesStub([_State("a", [])], topologies={"b": object()})
    snap = SpellSystemAdjacencyBuilder.build(states)
    assert snap.topologies == {}
