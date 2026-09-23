"""Characterize existing stores and warm execution; this file implements no purge API."""

from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_component_creations import _make_spellbook


class PlainProbe:
    """Ordinary factory result with no disposal contract."""

    def __init__(self, marker: int = 0) -> None:
        """Retain a plain default or explicit override for routing experiments."""
        self.marker = marker


class ManagedProbe(PlainProbe):
    """Factory result whose cleanup count reveals which scope retained it."""

    def __init__(self, marker: int = 0) -> None:
        """Initialize observable state without external resources."""
        super().__init__(marker)
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """Record each explicit disposal attempt; keep the object inspectable."""
        self.cleanup_calls += 1


class Dependent:
    """Retain the injected reference so clearing its store cannot hide that reference."""

    def __init__(self, dependency: ManagedProbe) -> None:
        """Store the required dependency supplied by real generated execution."""
        self.dependency = dependency


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Reset runtime singletons around each characterization, matching suite isolation."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("existence", [
    Existence.unique,
    Existence.unique_per_conduit,
    Existence.unique_per_conduit_lineage,
    Existence.unique_per_spell_space,
])
def test_clear_existing_store_reuses_compiled_context(
    existence: Existence, dynamic: bool,
) -> None:
    """Clear an isolated store, then prove warm execution constructs afresh without recompilation."""
    book = _make_spellbook(dynamic=dynamic, disposal=True)
    spell_id = book.bind(spell=ManagedProbe, existence=existence, permissions="create")
    root = book.conjure(dynamic=dynamic, name="characterization-root")
    lesser = root.create_lesser_conduit()
    space = lesser.create_spellspace()
    try:
        door = space if existence is Existence.unique_per_spell_space else lesser
        store = space._creations if existence is Existence.unique_per_spell_space else (
            lesser._creations if existence is Existence.unique_per_conduit else root._creations
        )
        old = door.meld(spell_id=spell_id)
        assert door.meld(spell_id=spell_id) is old
        context = book._spells_by_id[spell_id]._creation_context
        assert store.get_creation(spell_id) is old
        store.clear_all()
        assert old.cleanup_calls == 1
        new = door.meld(spell_id=spell_id)
        assert new is not old
        assert store.get_creation(spell_id) is new
        assert book._spells_by_id[spell_id]._creation_context is context
    finally:
        space.cleanup()
        lesser.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("disposable", [False, True])
@pytest.mark.parametrize("with_override", [False, True])
def test_many_retention_and_spellspace_routing(disposable: bool, with_override: bool) -> None:
    """Observe disposable-only many retention and separation of conduit/SpellSpace buckets."""
    book = _make_spellbook(disposal=True)
    target = ManagedProbe if disposable else PlainProbe
    spell_id = book.bind(spell=target, existence=Existence.many, permissions="create")
    root = book.conjure(name="many-root")
    try:
        override = {"marker": 7} if with_override else None
        root_instance = root.meld(spell_id=spell_id, override=override)
        with root.enter_spellspace() as space:
            scoped_instance = space.meld(spell_id=spell_id, override=override)
            assert scoped_instance is not root_instance
            if disposable:
                assert root._creations.get_creation(spell_id) == [root_instance]
                assert space._creations.get_creation(spell_id) == [scoped_instance]
            else:
                assert root._creations.get_creation(spell_id) is None
                assert space._creations.get_creation(spell_id) is None
        if disposable:
            assert scoped_instance.cleanup_calls == 1
            assert root_instance.cleanup_calls == 0
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("linked", [False, True])
def test_cluster_store_owner_can_differ_from_spell_owner(linked: bool) -> None:
    """Separate elected-store ownership from binding visibility, then clear and recreate."""
    book = _make_spellbook(dynamic=True, disposal=True)
    spell_id = book.bind(
        spell=ManagedProbe, existence=Existence.unique_per_conduit_cluster, permissions="create",
    )
    owner = book.conjure(dynamic=True, name="binding-owner")
    leader = Spellbook(aetheric_frame=owner._aetheric_frame_name).conjure(
        dynamic=True, name="elected-leader",
    )
    try:
        if linked:
            owner.link(leader)
        cloud = owner.get_conduit_cloud()
        cloud.create_cluster("purge-study")
        cloud.add_conduit_to_cluster(owner, "purge-study")
        cloud.add_conduit_to_cluster(leader, "purge-study")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("purge-study").elect_leader(leader.id)
        old = owner.meld(spell_id=spell_id)
        assert book._spells_by_id[spell_id]._owner_conduit_id == owner.id
        assert owner._creations.get_creation(spell_id) is None
        assert leader._creations.get_creation(spell_id) is old
        if linked:
            assert leader.meld(spell_id=spell_id) is old
        else:
            with pytest.raises(KeyError):
                leader.meld(spell_id=spell_id)
        context = book._spells_by_id[spell_id]._creation_context
        leader._creations.clear_all()
        new = owner.meld(spell_id=spell_id)
        assert new is not old
        if linked:
            assert leader.meld(spell_id=spell_id) is new
        assert old.cleanup_calls == 1
        assert book._spells_by_id[spell_id]._creation_context is context
    finally:
        leader.permanent_cleanup()
        owner.permanent_cleanup()


def test_existing_object_remains_resolvable_after_store_clear() -> None:
    """Show why removing a store slot cannot withdraw a supplied object's Spell reference."""
    book = _make_spellbook()
    supplied = PlainProbe()
    spell_id = book.bind(spell=supplied, existence=Existence.unique, permissions="create")
    root = book.conjure(name="existing-root")
    try:
        assert root.meld(spell_id=spell_id) is supplied
        root._creations.clear_all()
        assert root._creations.get_creation(spell_id) is None
        assert root.meld(spell_id=spell_id) is supplied
    finally:
        root.permanent_cleanup()


def test_existing_dependent_keeps_reference_after_provider_store_clear() -> None:
    """Demonstrate target-store clearing does not replace a reference inside an existing consumer."""
    book = _make_spellbook(disposal=True)
    leaf_id = book.bind(spell=ManagedProbe, existence=Existence.unique, permissions="create")
    parent_id = book.bind(spell=Dependent, existence=Existence.unique_per_conduit, permissions="create")
    root = book.conjure(name="dependency-root")
    lesser = root.create_lesser_conduit()
    try:
        parent = lesser.meld(spell_id=parent_id)
        old_leaf = parent.dependency
        root._creations.clear_all()
        new_leaf = root.meld(spell_id=leaf_id)
        assert new_leaf is not old_leaf
        assert old_leaf.cleanup_calls == 1
        assert lesser.meld(spell_id=parent_id) is parent
        assert parent.dependency is old_leaf
    finally:
        lesser.cleanup()
        root.permanent_cleanup()
