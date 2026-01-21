import pytest

from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _socket(name: str, pos: int, targets=()):
    return SpellSocketDescriptor(
        spell_id="sid",
        param_name=name,
        position=pos,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=tuple(targets),
    )


def test_ctor_rejects_none_spell_id():
    with pytest.raises(ValueError):
        SpellLocalTopology(None, sockets=())  # type: ignore[arg-type]


def test_sockets_stored_as_tuple_and_grouped_by_param_name():
    s1 = _socket("a", 0, targets=("x",))
    s2 = _socket("dup", 1)
    s3 = _socket("dup", 2)
    topo = SpellLocalTopology(spell_id="root", sockets=[s1, s2, s3])

    # Sockets materialized as tuple and ordering preserved
    assert topo.sockets == (s1, s2, s3)
    assert topo.iter_sockets() == topo.sockets

    # Grouping by name collects all matching sockets
    dup_group = topo.get_sockets_for_param("dup")
    assert dup_group == (s2, s3)
    assert topo.get_sockets_for_param("a") == (s1,)
    assert topo.get_sockets_for_param("missing") == ()

    # Descriptor attributes are intact
    assert s1.target_spell_ids == ("x",)
    assert s1.position == 0


def test_group_lookup_returns_new_tuple_not_internal_list():
    s = _socket("a", 0)
    topo = SpellLocalTopology("root", [s])
    result = topo.get_sockets_for_param("a")
    assert isinstance(result, tuple)
    # Mutating returned tuple is impossible; ensure underlying map still intact
    assert topo.get_sockets_for_param("a") == (s,)


def test_cleanup_clears_maps_and_is_idempotent():
    topo = SpellLocalTopology("root", [_socket("a", 0), _socket("b", 1)])
    topo.cleanup()

    # Internal structures cleared
    assert topo._by_param_name is None  # noqa: SLF001
    assert topo._sockets is None  # noqa: SLF001

    # Idempotent
    topo.cleanup()


def test_cleanup_preserves_spell_id():
    topo = SpellLocalTopology("root", [_socket("a", 0)])
    topo.cleanup()
    # spell_id remains available even after cleanup
    assert topo.spell_id == "root"


def test_empty_sockets_allowed_and_lookup_returns_empty():
    topo = SpellLocalTopology("root", [])
    assert topo.sockets == ()
    assert topo.iter_sockets() == ()
    assert topo.get_sockets_for_param("anything") == ()


def test_duplicate_param_grouping_preserves_original_order():
    s1 = _socket("dup", 0, targets=("a",))
    s2 = _socket("dup", 1, targets=("b",))
    topo = SpellLocalTopology("root", [s1, s2])
    group = topo.get_sockets_for_param("dup")
    assert group == (s1, s2)
    # order is the same as provided, even with duplicate names
    assert [s.position for s in group] == [0, 1]


def test_socket_flags_and_targets_preserved():
    custom = SpellSocketDescriptor(
        spell_id="sid",
        param_name="col_opt",
        position=3,
        socket_kind=SocketKind.MUTATION_CONTRACT,
        is_collection=True,
        is_optional=True,
        target_spell_ids=("t1", "t2"),
    )
    topo = SpellLocalTopology("root", [custom])
    (recorded,) = topo.sockets
    assert recorded.is_collection is True
    assert recorded.is_optional is True
    assert recorded.socket_kind is SocketKind.MUTATION_CONTRACT
    assert recorded.target_spell_ids == ("t1", "t2")


def test_input_sequence_copied_and_original_list_mutation_does_not_propagate():
    sockets = [_socket("x", 0)]
    topo = SpellLocalTopology("root", sockets)
    sockets.append(_socket("y", 1))
    assert topo.sockets == (sockets[0],)
    assert topo.get_sockets_for_param("y") == ()


def test_get_sockets_returns_new_tuple_each_call():
    s = _socket("a", 0)
    topo = SpellLocalTopology("root", [s])
    first = topo.get_sockets_for_param("a")
    second = topo.get_sockets_for_param("a")
    assert first == second == (s,)
    assert first is not second  # separate tuple objects


def test_cleanup_sets_cleaned_flag_and_blocks_internal_maps():
    topo = SpellLocalTopology("root", [_socket("a", 0)])
    topo.cleanup()
    assert topo._cleaned is True  # noqa: SLF001
    with pytest.raises(AttributeError):
        topo.get_sockets_for_param("a")


def test_descriptor_is_frozen():
    desc = _socket("a", 0)
    from dataclasses import FrozenInstanceError

    with pytest.raises(FrozenInstanceError):
        setattr(desc, "param_name", "mutated")


def test_iter_sockets_returns_same_tuple_instance():
    s1, s2 = _socket("a", 0), _socket("b", 1)
    topo = SpellLocalTopology("root", [s1, s2])
    assert topo.iter_sockets() is topo.sockets
