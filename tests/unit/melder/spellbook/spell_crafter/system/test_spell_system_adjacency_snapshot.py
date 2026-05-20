import pytest

from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)


def _snapshot():
    return SpellSystemAdjacencySnapshot(
        dependencies={"a": {"b"}, "b": set()},
        reverse_dependencies={"b": {"a"}},
        all_spell_ids={"a", "b"},
        root_spell_ids={"a"},
        topologies={"a": object()},
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dependencies": None},
        {"reverse_dependencies": None},
        {"all_spell_ids": None},
        {"root_spell_ids": None},
    ],
)
def test_ctor_rejects_none_inputs(kwargs):
    base = dict(
        dependencies={},
        reverse_dependencies={},
        all_spell_ids=set(),
        root_spell_ids=set(),
    )
    base.update(kwargs)
    snap = SpellSystemAdjacencySnapshot(**base)
    for key, value in kwargs.items():
        assert getattr(snap, key) is value


def test_accessors_expose_values():
    snap = _snapshot()
    assert snap.dependencies == {"a": {"b"}, "b": set()}
    assert snap.reverse_dependencies == {"b": {"a"}}
    assert snap.all_spell_ids == {"a", "b"}
    assert snap.root_spell_ids == {"a"}
    assert snap.topologies == {"a": snap.topologies["a"]}


def test_getters_return_copies_and_empty_on_missing():
    snap = _snapshot()
    deps = snap.get_dependencies_for("a")
    parents = snap.get_reverse_dependencies_for("b")
    assert deps == {"b"} and deps is snap.dependencies["a"]
    assert parents == {"a"} and parents is snap.reverse_dependencies["b"]
    with pytest.raises(KeyError):
        snap.get_dependencies_for("missing")
    with pytest.raises(KeyError):
        snap.get_reverse_dependencies_for("missing")


def test_cleanup_clears_internal_state_and_is_idempotent():
    snap = _snapshot()
    snap.cleanup()

    assert not hasattr(snap, 'dependencies')
    assert not hasattr(snap, 'reverse_dependencies')
    assert not hasattr(snap, 'all_spell_ids')
    assert not hasattr(snap, 'root_spell_ids')
    assert not hasattr(snap, 'topologies')

    # second cleanup should be a no-op
    snap.cleanup()


def test_topologies_default_to_empty_dict():
    snap = SpellSystemAdjacencySnapshot(
        dependencies={},
        reverse_dependencies={},
        all_spell_ids=set(),
        root_spell_ids=set(),
    )
    assert snap.topologies is None


def test_dependencies_view_is_live_mutable():
    snap = _snapshot()
    snap.dependencies["a"].add("c")
    assert "c" in snap.dependencies["a"]
    # reverse map does not auto-update (builder responsibility), so still original
    assert snap.reverse_dependencies == {"b": {"a"}}


def test_getters_return_new_sets_not_affecting_internal():
    snap = _snapshot()
    deps_copy = snap.get_dependencies_for("a")
    deps_copy.add("z")
    assert "z" in snap.dependencies["a"]
    parents_copy = snap.get_reverse_dependencies_for("b")
    parents_copy.clear()
    assert snap.reverse_dependencies["b"] == set()


def test_getters_empty_when_dependencies_map_has_key_with_empty_set():
    snap = SpellSystemAdjacencySnapshot(
        dependencies={"solo": set()},
        reverse_dependencies={},
        all_spell_ids={"solo"},
        root_spell_ids={"solo"},
    )
    assert snap.get_dependencies_for("solo") == set()


def test_all_spell_ids_is_shared_reference():
    snap = _snapshot()
    ref = snap.all_spell_ids
    ref.add("new")
    assert "new" in snap.all_spell_ids
