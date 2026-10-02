"""
Component tests of the many registration trim through real conjures (2026-10-01).

Scope:
    The registration line the emitters write for a disposal-bearing `many` step now calls
    `Creations.register_many(sid, instance, dm)`; these tests meld such roots through a real
    Conduit and a real SpellSpace (the solo family for a leaf without dependencies, the
    generalized family for a root with one) and check the store shape and the disposal
    order at scope exit.
"""

from typing import List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import ManyDisposalBucket
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    set_frame_system_state_for_spellbook_configuration,
)


class _Log:
    """Shared disposal order log, one per test."""

    def __init__(self) -> None:
        self.entries: List[str] = []


class Leaf:
    """Disposal-bearing transient with no dependencies (solo family)."""

    log: Optional[_Log] = None

    def __init__(self) -> None:
        self.serial = 0

    def cleanup(self) -> None:
        """Record the disposal."""
        assert Leaf.log is not None
        Leaf.log.entries.append(f"leaf{self.serial}")


class Root:
    """Disposal-bearing transient that depends on a Leaf (generalized family)."""

    log: Optional[_Log] = None

    def __init__(self, leaf: Leaf) -> None:
        self.leaf = leaf
        self.serial = 0

    def cleanup(self) -> None:
        """Record the disposal."""
        assert Root.log is not None
        Root.log.entries.append(f"root{self.serial}")


@pytest.fixture(autouse=True)
def reset_aether_singleton() -> None:
    """Fresh Aether per test, as the other component conduit tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _spellbook_with_disposal() -> Spellbook:
    """A Spellbook whose configuration declares `cleanup` as the disposal method."""
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _bind_world() -> Tuple[Spellbook, str, str, _Log]:
    """Bind Leaf and Root as disposal-bearing many spells; return (spellbook, leaf_id, root_id, log)."""
    log = _Log()
    Leaf.log = log
    Root.log = log
    spellbook = _spellbook_with_disposal()
    leaf_id = spellbook.bind(spell=Leaf, existence=Existence.many, permissions="create")
    root_id = spellbook.bind(spell=Root, existence=Existence.many, permissions="create")
    return spellbook, leaf_id, root_id, log


def test_conduit_meld_registers_one_record_per_key_aliasing_the_bucket() -> None:
    """Two melds of the root register leaf and root into one record each, aliased to the live buckets."""
    spellbook, leaf_id, root_id, _log = _bind_world()
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=root_id)
        second = conduit.meld(spell_id=root_id)
        store = conduit._creations
        for spell_id, expected in ((root_id, [first, second]), (leaf_id, [first.leaf, second.leaf])):
            record = store._disposable_creations[spell_id]
            assert isinstance(record, ManyDisposalBucket)
            assert record.entries is store._creations[spell_id]
            assert record.entries == expected
            spell = spellbook.find_spell_by_id(spell_id)
            assert spell is not None
            assert record.methods is spell.disposal_method_names
            assert record.methods == ["cleanup"]
    finally:
        conduit.permanent_cleanup()


def test_conduit_cleanup_disposes_roots_then_leaves_newest_first() -> None:
    """Teardown walks the registry newest key first and each bucket newest entry first."""
    spellbook, _leaf_id, root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    first = conduit.meld(spell_id=root_id)
    second = conduit.meld(spell_id=root_id)
    first.serial, first.leaf.serial = 1, 1
    second.serial, second.leaf.serial = 2, 2

    conduit.permanent_cleanup()

    assert log.entries == ["root2", "root1", "leaf2", "leaf1"]


def test_solo_leaf_registers_through_the_hot_verb_and_is_disposed() -> None:
    """A leaf melded on its own (solo family) is registered and disposed like any many root."""
    spellbook, leaf_id, _root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    leaf_a = conduit.meld(spell_id=leaf_id)
    leaf_b = conduit.meld(spell_id=leaf_id)
    leaf_a.serial, leaf_b.serial = 1, 2
    record = conduit._creations._disposable_creations[leaf_id]
    assert record.entries == [leaf_a, leaf_b]

    conduit.permanent_cleanup()

    assert log.entries == ["leaf2", "leaf1"]


def test_spellspace_exit_disposes_the_space_store_only() -> None:
    """A space-scoped meld registers in the space store; its exit disposes those and nothing else."""
    spellbook, leaf_id, root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    try:
        outer = conduit.meld(spell_id=root_id)
        outer.serial, outer.leaf.serial = 9, 9
        with conduit.enter_spellspace() as space:
            inner = space.meld(spell_id=root_id)
            inner.serial, inner.leaf.serial = 1, 1
            record = space._creations._disposable_creations[root_id]
            assert record.entries is space._creations._creations[root_id]
            assert record.entries == [inner]
            assert conduit._creations._disposable_creations[root_id].entries == [outer]
        assert log.entries == ["root1", "leaf1"]
        assert leaf_id not in space._creations._creations
    finally:
        conduit.permanent_cleanup()
    assert log.entries == ["root1", "leaf1", "root9", "leaf9"]


def test_purge_one_transient_from_a_live_conduit_keeps_the_others() -> None:
    """Purging one instance of a many root disposes it alone and keeps the record over the rest."""
    spellbook, _leaf_id, root_id, log = _bind_world()
    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell_id=root_id)
        second = conduit.meld(spell_id=root_id)
        first.serial, first.leaf.serial = 1, 1
        second.serial, second.leaf.serial = 2, 2

        removed = conduit.purge(first, purge_all=False)

        assert removed == 1
        assert log.entries == ["root1"]
        record = conduit._creations._disposable_creations[root_id]
        assert record.entries == [second]
        assert record.entries is conduit._creations._creations[root_id]
    finally:
        conduit.permanent_cleanup()
    assert log.entries == ["root1", "root2", "leaf2", "leaf1"]
