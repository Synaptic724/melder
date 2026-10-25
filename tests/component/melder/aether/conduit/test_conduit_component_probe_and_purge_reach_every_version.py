"""
Component: purge and the live-creation probes reach every version by its spell_id
(STORY-2026-10-25-probe_and_purge_reach_every_version).

Versions coexist and keep their objects across a notch: a notch back returns the object a version built while it was
active. The creation stores key every version's entries by its spell_id, so a parked version's objects are there under
their own key. `purge(spell_id=...)`, `has_live_creation(spell=<spell_id>)` and `describe_live_creation_status(spell=
<spell_id>)` build nothing, so they reach any version the conduit can see - its Book's own, active or parked, and a
borrowed copy, active or parked - and act on that version's entries in the store the door authorizes, exactly as for an
active version. Every door that builds stays active-only, and every selector other than a spell_id (a name, a class,
spellframe and binding name, an instance) still names the version an index has active.

Each test builds a fresh dynamic world in the "default" frame: disposal names ["cleanup"], caching off, one phase
worker. `Resource` is version 1 and `version_of(Resource, version=2)` version 2 - new code under the same name, bound
bare at the class's own address, so the worlds stay valid when an index owns its address (option A of
STORY-2026-10-17-notch_moves_signature_by_incoming_key_only). The failure-mode ids (F1-F22) are the story's catalogue.
"""

from collections.abc import Iterator
from typing import Any, Callable, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._spell_identity_test_support import version_of


class Resource:
    """
    Purpose:
        Version 1 of the resource every test versions; its disposal is observable.
    Contract:
        - `cleanup` counts calls on the object and appends the object to `Resource.journal`, so a test can tell which
          object was disposed and in what order.
        - Owns no external resource.
    """

    version: int = 1
    journal: List[Any] = []

    def __init__(self) -> None:
        """
        Purpose: Start each object undisposed.
        Contract: `cleanup_calls` starts at 0.
        Returns: None.
        """
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """
        Purpose: Make every disposal attempt observable.
        Contract: Increments `cleanup_calls` and records the object in `Resource.journal`, once per call.
        Returns: None.
        """
        self.cleanup_calls += 1
        Resource.journal.append(self)


class Anchor:
    """
    Purpose: Give a second Book something of its own to conjure.
    Contract: Plain; no disposal method.
    """


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """
    Purpose: Isolate every test: fresh Nexus and Aether, rebound on Spellbook and Conduit, and an empty journal.
    Contract: Resets before and after the test.
    Yields: None while the test owns its world.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    Resource.journal = []
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    Resource.journal = []


def _book(*, first: bool = True) -> Spellbook:
    """
    Purpose: Build one Book in the "default" frame with disposal names ["cleanup"] and one phase worker.
    Args:
        first: True for the frame's first Book, which settles the frame dynamic with caching off; a later Book of
            the same frame inherits that posture.
    Returns:
        Spellbook: The Book, not conjured.
    """
    configuration = SpellbookConfiguration("default")
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame="default", configuration=configuration)
    if first:
        book.configure_aether_frame(
            system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
        )
    return book


class _World:
    """
    Purpose:
        One lender: `Resource` bound active, its version 2 staged parked on the same index after conjure.
    Contract:
        - `book`, `root`, `index`, `v1_id`, `v2_id` and `v2_class` name the world's parts.
        - `notch(spell_id)` moves the index to that version through the public notch.
        - `cleanup()` tears the root and the Book down; extra conduits are the test's to clean first.
    """

    def __init__(self, existence: Existence, *, stage_before_conjure: bool = False) -> None:
        """
        Purpose: Build the world.
        Args:
            existence: The existence both versions are bound with.
            stage_before_conjure: Stage version 2 with `Spellbook.bind_inactive` before conjure instead of
                `Conduit.bind_inactive` after it.
        Returns: None.
        """
        self.book: Spellbook = _book()
        self.v2_class: type = version_of(Resource, version=2)
        self.v1_id: str = self.book.bind(spell=Resource, existence=existence, permissions="create")
        if stage_before_conjure:
            self.index: Any = self.book.find_spell_by_spell_id(self.v1_id).spell_index
            self.v2_id: str = self.book.bind_inactive(
                spell=self.v2_class, spell_index=self.index, existence=existence, permissions="create",
            )
            self.root: Conduit = self.book.conjure(dynamic=True, name="lender")
        else:
            self.root = self.book.conjure(dynamic=True, name="lender")
            self.index = self.root.get_spell_by_spell_id(self.v1_id).spell_index
            self.v2_id = self.root.bind_inactive(
                spell=self.v2_class, spell_index=self.index, existence=existence, permissions="create",
            )

    def notch(self, spell_id: str) -> None:
        """
        Purpose: Make `spell_id` the index's active version.
        Args: spell_id: A version of the world's index.
        Returns: None.
        """
        self.root.notch_spell(spell_index=self.index, spell_id=spell_id)

    def cleanup(self) -> None:
        """
        Purpose: Tear the world down: the root, then the Book.
        Returns: None.
        """
        self.root.cleanup()
        self.book.cleanup()


def _count(scope: Any, spell_id: str) -> int:
    """
    Purpose: Read a version's live-creation count through the probe a scope offers.
    Args:
        scope: A Conduit, or a Meld door (a SpellSpace has no public probe; its door is `space._meld`).
        spell_id: The version to probe.
    Returns:
        int: The status payload's `creation_count`.
    """
    status = scope.describe_live_creation_status(spell=spell_id)
    assert status["spell_id"] == spell_id
    return status["creation_count"]


_SLOTTED_AND_MANY = [
    Existence.unique,
    Existence.unique_per_conduit,
    Existence.unique_per_conduit_lineage,
    Existence.many,
]


# --- F1, F2, F3: a parked version's own entries ---------------------------------------------------------------------

@pytest.mark.parametrize("existence", _SLOTTED_AND_MANY)
def test_parked_version_is_probed_and_purged_by_spell_id(existence: Existence) -> None:
    """
    Purpose: F1/F3 - a version built while active, then parked by a notch, is probed and purged by its spell_id.
    Contract: The probe counts the parked version's own objects; purge disposes exactly them and returns their count;
        the active version's object is untouched; a second purge returns 0. Before the story every call raised
        KeyError "[MELD] No spell found with spell_id".
    Args: existence: The lifetime both versions are bound with.
    Returns: None.
    """
    world = _World(existence)
    try:
        built = 2 if existence is Existence.many else 1
        old_objects = [world.root.meld(spell_id=world.v1_id) for _ in range(built)]
        world.notch(world.v2_id)
        active_object = world.root.meld(spell_id=world.v2_id)

        assert world.root.has_live_creation(spell=world.v1_id) is True
        assert _count(world.root, world.v1_id) == built
        assert world.root.purge(spell_id=world.v1_id) == built
        assert [obj.cleanup_calls for obj in old_objects] == [1] * built
        assert active_object.cleanup_calls == 0
        assert world.root.has_live_creation(spell=world.v1_id) is False
        assert world.root.has_live_creation(spell=world.v2_id) is True
        assert world.root.purge(spell_id=world.v1_id) == 0
    finally:
        world.cleanup()


@pytest.mark.parametrize("purge_first", [True, False])
def test_notch_back_after_purging_builds_a_fresh_object(purge_first: bool) -> None:
    """
    Purpose: F1 - a notch back returns the object the version kept, unless it was purged while parked.
    Contract: Without a purge the notch back returns the same `unique` object (versions keep their objects); after a
        purge of the parked version the notch back builds a fresh one and the purged object stays disposed once.
    Args: purge_first: Purge the parked version before the notch back.
    Returns: None.
    """
    world = _World(Existence.unique)
    try:
        first = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        if purge_first:
            assert world.root.purge(spell_id=world.v1_id) == 1
        world.notch(world.v1_id)
        again = world.root.meld(spell_id=world.v1_id)
        if purge_first:
            assert again is not first
            assert (first.cleanup_calls, again.cleanup_calls) == (1, 0)
        else:
            assert again is first
            assert first.cleanup_calls == 0
    finally:
        world.cleanup()


@pytest.mark.parametrize("existence", _SLOTTED_AND_MANY)
def test_parked_version_never_built_probes_false_and_purges_zero(existence: Existence) -> None:
    """
    Purpose: F2 - a version staged parked and never active has no entries; the doors answer instead of raising.
    Contract: The probe is False with a count of 0, purge returns 0, and the active version's object is untouched.
    Args: existence: The lifetime both versions are bound with.
    Returns: None.
    """
    world = _World(existence)
    try:
        active_object = world.root.meld(spell_id=world.v1_id)
        assert world.root.has_live_creation(spell=world.v2_id) is False
        assert _count(world.root, world.v2_id) == 0
        assert world.root.purge(spell_id=world.v2_id) == 0
        assert active_object.cleanup_calls == 0
        assert world.root.has_live_creation(spell=world.v1_id) is True
    finally:
        world.cleanup()


def test_parked_many_purge_disposes_newest_first_and_keeps_the_active_versions() -> None:
    """
    Purpose: F3 - purging a parked `many` version disposes its objects newest first and nothing of the active one.
    Contract: Three objects of version 1 are disposed in reverse build order; version 2's two objects stay counted.
    Returns: None.
    """
    world = _World(Existence.many)
    try:
        old_objects = [world.root.meld(spell_id=world.v1_id) for _ in range(3)]
        world.notch(world.v2_id)
        new_objects = [world.root.meld(spell_id=world.v2_id) for _ in range(2)]
        assert world.root.purge(spell_id=world.v1_id) == 3
        assert Resource.journal == list(reversed(old_objects))
        assert [obj.cleanup_calls for obj in new_objects] == [0, 0]
        assert _count(world.root, world.v2_id) == 2
    finally:
        world.cleanup()


# --- F4, F5, F6, F7, F8, F9: store selection and authority are unchanged --------------------------------------------

@pytest.mark.parametrize("existence", [Existence.unique_per_conduit, Existence.many])
def test_lesser_purges_only_its_own_entries_of_a_parked_version(existence: Existence) -> None:
    """
    Purpose: F4 - per-conduit and `many` lifetimes use the caller's own store, for a parked version too.
    Contract: A lesser's purge of the parked version retires the lesser's object and leaves the root's; the root's
        purge then retires its own.
    Args: existence: A caller-local lifetime.
    Returns: None.
    """
    world = _World(existence)
    lesser = world.root.create_lesser_conduit()
    try:
        root_object = world.root.meld(spell_id=world.v1_id)
        lesser_object = lesser.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        assert lesser.purge(spell_id=world.v1_id) == 1
        assert (lesser_object.cleanup_calls, root_object.cleanup_calls) == (1, 0)
        assert world.root.has_live_creation(spell=world.v1_id) is True
        assert world.root.purge(spell_id=world.v1_id) == 1
        assert root_object.cleanup_calls == 1
    finally:
        lesser.cleanup()
        world.cleanup()


def test_lineage_root_alone_purges_a_parked_lineage_version() -> None:
    """
    Purpose: F4 - a lineage version's object lives in the lineage root's store; only the root may purge it.
    Contract: The lesser sees the object and is refused naming the lineage root; the root purges it once.
    Returns: None.
    """
    world = _World(Existence.unique_per_conduit_lineage)
    lesser = world.root.create_lesser_conduit()
    try:
        obj = lesser.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        assert lesser.has_live_creation(spell=world.v1_id) is True
        with pytest.raises(RuntimeError, match="lineage root conduit"):
            lesser.purge(spell_id=world.v1_id)
        assert obj.cleanup_calls == 0
        assert world.root.purge(spell_id=world.v1_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        lesser.cleanup()
        world.cleanup()


def test_lesser_cannot_purge_a_parked_unique_version() -> None:
    """
    Purpose: F5 - a parked `unique` version's object is its owner's; a lesser sees it but may not purge it.
    Contract: The lesser's probe is True; its purge raises RuntimeError naming the spell-owning conduit and disposes
        nothing; the owner root's purge retires it.
    Returns: None.
    """
    world = _World(Existence.unique)
    lesser = world.root.create_lesser_conduit()
    try:
        obj = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        assert lesser.has_live_creation(spell=world.v1_id) is True
        with pytest.raises(RuntimeError, match="spell-owning conduit"):
            lesser.purge(spell_id=world.v1_id)
        assert obj.cleanup_calls == 0
        assert world.root.purge(spell_id=world.v1_id) == 1
    finally:
        lesser.cleanup()
        world.cleanup()


@pytest.mark.parametrize("existence", [Existence.unique_per_spell_space, Existence.many])
def test_spellspace_purges_its_entries_of_a_parked_version(existence: Existence) -> None:
    """
    Purpose: F6 - a SpellSpace probes and purges its own entries of a parked version.
    Contract: The space's door counts the parked version's objects in the space's store and its purge retires them.
    Args: existence: A lifetime a SpellSpace retires.
    Returns: None.
    """
    world = _World(existence)
    space = world.root.create_spellspace()
    try:
        built = 2 if existence is Existence.many else 1
        objects = [space.meld(spell_id=world.v1_id) for _ in range(built)]
        world.notch(world.v2_id)
        assert space._meld.has_live_creation(spell=world.v1_id) is True
        assert _count(space._meld, world.v1_id) == built
        assert space.purge(spell_id=world.v1_id) == built
        assert [obj.cleanup_calls for obj in objects] == [1] * built
    finally:
        space.cleanup()
        world.cleanup()


def test_conduit_still_refuses_a_parked_spellspace_version() -> None:
    """
    Purpose: F6 - the conduit door keeps refusing a spellspace lifetime, for a parked version too.
    Contract: Conduit.purge raises RuntimeError "call purge on the specific SpellSpace" and the probe refuses it as a
        spellspace-request spell; the space's object is untouched.
    Returns: None.
    """
    world = _World(Existence.unique_per_spell_space)
    space = world.root.create_spellspace()
    try:
        obj = space.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        with pytest.raises(RuntimeError, match="call purge on the specific SpellSpace"):
            world.root.purge(spell_id=world.v1_id)
        with pytest.raises(RuntimeError, match="must be built from a spellspace"):
            world.root.has_live_creation(spell=world.v1_id)
        assert obj.cleanup_calls == 0
    finally:
        space.cleanup()
        world.cleanup()


def test_cluster_leader_purges_a_parked_cluster_version() -> None:
    """
    Purpose: F7 - a parked cluster version's object stays in the cluster's team store; only the elected leader purges.
    Contract: The binding owner is refused naming the leader; the leader, which borrows the version through the
        cluster's share, probes it and purges it once.
    Returns: None.
    """
    world = _World(Existence.unique_per_conduit_cluster)
    leader = _book(first=False).conjure(dynamic=True, name="leader")
    try:
        world.root.link(leader)
        cloud = world.root.get_conduit_cloud()
        cloud.create_cluster("versions")
        cloud.add_conduit_to_cluster(world.root, "versions")
        cloud.add_conduit_to_cluster(leader, "versions")
        cloud.refresh_cluster_shares_for_conduit(world.root)
        cloud.get_cluster("versions").elect_leader(leader.id)
        obj = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        with pytest.raises(RuntimeError, match="leader"):
            world.root.purge(spell_id=world.v1_id)
        assert leader.has_live_creation(spell=world.v1_id) is True
        assert leader.purge(spell_id=world.v1_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        leader.cleanup()
        world.cleanup()


def test_parked_managed_version_reports_its_own_pool_and_purges_nothing() -> None:
    """
    Purpose: F8 - a parked managed version's probe reads that version's own pool; purge stays outside the design.
    Contract: The probe counts the object still out from version 1's pool (storage scope "managed_pool"); purge
        returns 0 and disposes nothing.
    Returns: None.
    """
    world = _World(Existence.managed_spell_quantity)
    try:
        leased = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        status = world.root.describe_live_creation_status(spell=world.v1_id)
        assert (status["is_live"], status["storage_scope_kind"], status["creation_count"]) == (True, "managed_pool", 1)
        assert world.root.purge(spell_id=world.v1_id) == 0
        assert leased.cleanup_calls == 0
    finally:
        world.cleanup()


def test_parked_existing_object_is_live_and_purge_retires_nothing() -> None:
    """
    Purpose: F9 - a version staged as an existing object is live (its object exists) but holds no store entry.
    Contract: The probe is True with storage scope "existing_creation"; purge returns 0 (a parked existing object is
        not registered in the store) and the supplied object is never disposed.
    Returns: None.
    """
    book = _book()
    first = Resource()
    v1_id = book.bind(spell=first, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=True, name="lender")
    try:
        index = root.get_spell_by_spell_id(v1_id).spell_index
        second = version_of(Resource, version=2)()
        v2_id = root.bind_inactive(spell=second, spell_index=index, existence=Existence.unique, permissions="create")
        status = root.describe_live_creation_status(spell=v2_id)
        assert (status["is_live"], status["storage_scope_kind"], status["creation_count"]) == (
            True, "existing_creation", 1,
        )
        assert root.purge(spell_id=v2_id) == 0
        assert second.cleanup_calls == 0
    finally:
        root.cleanup()
        book.cleanup()


# --- F10: borrowed copies ---------------------------------------------------------------------------------------------

def _borrow(world: _World, how: str) -> Conduit:
    """
    Purpose: Give a second root of the frame a copy of version 1, by an index link or by a version grant.
    Args:
        world: The lender's world, version 1 active.
        how: "index_link" (the borrower follows the index) or "grant" (the borrower holds version 1 itself).
    Returns:
        Conduit: The borrower's root, linked to the lender.
    """
    borrower = _book(first=False).conjure(dynamic=True, name="borrower")
    world.root.link(borrower)
    if how == "index_link":
        borrower.add_index_to_contract(index=world.index, conduit=world.root, permissions="create")
    else:
        borrower.add_spell_to_contract(spell_id=world.v1_id, conduit=world.root, permissions="create")
    return borrower


@pytest.mark.parametrize("how", ["index_link", "grant"])
def test_borrower_reaches_its_parked_copy_of_a_unique_version(how: str) -> None:
    """
    Purpose: F10 - a borrower's copy parked by the lender's notch is probed, and its purge keeps the unique rule.
    Contract: The borrower reads the lender's store (True) and is refused naming the spell-owning conduit; the lender
        purges the object once.
    Args: how: How the borrower holds version 1.
    Returns: None.
    """
    world = _World(Existence.unique)
    borrower = _borrow(world, how)
    try:
        obj = borrower.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        assert borrower.has_live_creation(spell=world.v1_id) is True
        with pytest.raises(RuntimeError, match="spell-owning conduit"):
            borrower.purge(spell_id=world.v1_id)
        assert obj.cleanup_calls == 0
        assert world.root.purge(spell_id=world.v1_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        borrower.cleanup()
        world.cleanup()


@pytest.mark.parametrize("how", ["index_link", "grant"])
def test_borrower_purges_its_own_many_entries_of_a_parked_copy(how: str) -> None:
    """
    Purpose: F10 - `many` objects a borrower built from its copy are in the borrower's store; it purges them.
    Contract: After the lender's notch the borrower counts and purges its two objects; the lender holds none.
    Args: how: How the borrower holds version 1.
    Returns: None.
    """
    world = _World(Existence.many)
    borrower = _borrow(world, how)
    try:
        objects = [borrower.meld(spell_id=world.v1_id) for _ in range(2)]
        world.notch(world.v2_id)
        assert _count(borrower, world.v1_id) == 2
        assert _count(world.root, world.v1_id) == 0
        assert borrower.purge(spell_id=world.v1_id) == 2
        assert [obj.cleanup_calls for obj in objects] == [1, 1]
    finally:
        borrower.cleanup()
        world.cleanup()


# --- F11, F12, F13: what does not change -------------------------------------------------------------------------------

@pytest.mark.parametrize("which", ["unknown", "disposed", "foreign"])
def test_spell_ids_no_visible_version_carries_still_raise_key_error(which: str) -> None:
    """
    Purpose: F11 - a spell_id no version the conduit can see carries keeps today's KeyError.
    Contract: An unknown spell_id, a disposed version's and another Book's (not borrowed) raise KeyError "[MELD] No
        spell found with spell_id: <id>" from the probe and from purge.
    Args: which: The kind of spell_id.
    Returns: None.
    """
    world = _World(Existence.unique)
    other: Optional[Conduit] = None
    try:
        if which == "unknown":
            spell_id = "0" * 64
        elif which == "disposed":
            spell_id = world.v2_id
            world.root.cleanup_spell(spell=world.root.get_spell_by_spell_id(world.v2_id))
        else:
            other_book = _book(first=False)
            spell_id = other_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
            other = other_book.conjure(dynamic=True, name="other")
        with pytest.raises(KeyError, match="No spell found with spell_id"):
            world.root.has_live_creation(spell=spell_id)
        with pytest.raises(KeyError, match="No spell found with spell_id"):
            world.root.purge(spell_id=spell_id)
    finally:
        if other is not None:
            other.cleanup()
        world.cleanup()


def test_meld_doors_stay_active_only() -> None:
    """
    Purpose: F12 - the doors that build or hand out an object never reach a parked version.
    Contract: meld(spell_id=<parked>) and meld_existing_spell(spell=<parked>) raise KeyError, before and after a notch.
    Returns: None.
    """
    world = _World(Existence.unique)
    try:
        with pytest.raises(KeyError, match="No spell found with spell_id"):
            world.root.meld(spell_id=world.v2_id)
        world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        with pytest.raises(KeyError, match="No spell found with spell_id"):
            world.root.meld(spell_id=world.v1_id)
        with pytest.raises(KeyError, match="No spell found with spell_id"):
            world.root.meld_existing_spell(spell=world.v1_id)
    finally:
        world.cleanup()


def test_spell_id_purge_still_needs_purge_all() -> None:
    """
    Purpose: F13 - single-object retirement still needs an instance, for a parked version too.
    Contract: purge(spell_id=<parked>, purge_all=False) raises ValueError and disposes nothing.
    Returns: None.
    """
    world = _World(Existence.unique)
    try:
        obj = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        with pytest.raises(ValueError, match="requires an object instance"):
            world.root.purge(spell_id=world.v1_id, purge_all=False)
        assert obj.cleanup_calls == 0
    finally:
        world.cleanup()


# --- F14, F17, F19, F20, F21, F22 -------------------------------------------------------------------------------------

def test_instance_of_a_parked_version_resolves_through_its_address() -> None:
    """
    Purpose: F14 - an instance names its class's address, which serves the active version (a documented limit).
    Contract: purge(spell=<version 1 object>, purge_all=False) looks in the active version's entry, finds another
        object and returns 0; purge(spell=<version 1 object>) retires the ACTIVE version's object, not version 1's;
        purge(spell_id=<version 1>) is the way to retire version 1's object.
    Returns: None.
    """
    world = _World(Existence.unique)
    try:
        old = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        new = world.root.meld(spell_id=world.v2_id)
        assert world.root.purge(spell=old, purge_all=False) == 0
        assert (old.cleanup_calls, new.cleanup_calls) == (0, 0)
        assert world.root.purge(spell=old) == 1
        assert (old.cleanup_calls, new.cleanup_calls) == (0, 1)
        assert world.root.purge(spell_id=world.v1_id) == 1
        assert old.cleanup_calls == 1
    finally:
        world.cleanup()


def test_purge_refuses_a_unique_version_with_no_owner_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: F17 - a `unique` version whose owner stamp failed at conjure is refused by purge with a clear error.
    Contract: Version 2 is staged before conjure and its stamp raises (conjure logs it and goes on). Parked and then
        active, the probe answers False and purge raises RuntimeError naming the missing owner store, where an
        active one raised AttributeError "'NoneType' object has no attribute 'owner_conduit_id'".
    Args: monkeypatch: Makes the owner stamp raise for version 2 during conjure only.
    Returns: None.
    """
    original: Callable[..., Any] = Spell._add_owned_conduit
    refused: List[str] = []

    def refusing_stamp(spell: Spell, *args: Any, **kwargs: Any) -> Any:
        """Raise for the version named in `refused`; stamp every other version as conjure does."""
        if spell.spell_id in refused:
            raise RuntimeError("test: the owner stamp raised")
        return original(spell, *args, **kwargs)

    book = _book()
    v1_id = book.bind(spell=Resource, existence=Existence.unique, permissions="create")
    index = book.find_spell_by_spell_id(v1_id).spell_index
    v2_id = book.bind_inactive(
        spell=version_of(Resource, version=2), spell_index=index, existence=Existence.unique, permissions="create",
    )
    refused.append(v2_id)
    monkeypatch.setattr(Spell, "_add_owned_conduit", refusing_stamp, raising=True)
    root = book.conjure(dynamic=True, name="lender")
    monkeypatch.undo()
    try:
        assert root.has_live_creation(spell=v2_id) is False
        with pytest.raises(RuntimeError, match="no owner store"):
            root.purge(spell_id=v2_id)
        root.notch_spell(spell_index=index, spell_id=v2_id)
        with pytest.raises(RuntimeError, match="no owner store"):
            root.purge(spell_id=v2_id)
    finally:
        root.cleanup()
        book.cleanup()


def test_split_version_is_reached_by_spell_id() -> None:
    """
    Purpose: F19 - a version split into an index of its own by remove_from_spell_index is reached as a parked version.
    Contract: Version 2 builds an object while active, is parked by a notch back, then split off; its probe is True
        and its purge retires the object.
    Returns: None.
    """
    world = _World(Existence.unique)
    try:
        world.notch(world.v2_id)
        obj = world.root.meld(spell_id=world.v2_id)
        world.notch(world.v1_id)
        world.root.remove_from_spell_index(spell_id=world.v2_id, source_index=world.index)
        assert world.root.get_spell_by_spell_id(world.v2_id).spell_index is not world.index
        assert world.root.has_live_creation(spell=world.v2_id) is True
        assert world.root.purge(spell_id=world.v2_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        world.cleanup()


def test_transfer_moves_the_reach_with_the_versions() -> None:
    """
    Purpose: F20 - after an ownership transfer the source no longer sees the moved versions and the target does.
    Contract: The source's probe of either version raises KeyError; the target probes the parked version it received
        (its object moved with it) and purges it once.
    Returns: None.
    """
    world = _World(Existence.unique)
    target_book = _book(first=False)
    target_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        old = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        world.root.meld(spell_id=world.v2_id)
        world.root.transfer_spell_ownership(spell=world.v2_id, target_conduit=target)
        for spell_id in (world.v1_id, world.v2_id):
            with pytest.raises(KeyError, match="No spell found with spell_id"):
                world.root.has_live_creation(spell=spell_id)
        assert target.has_live_creation(spell=world.v1_id) is True
        assert target.purge(spell_id=world.v1_id) == 1
        assert old.cleanup_calls == 1
    finally:
        target.cleanup()
        world.cleanup()


def test_other_selectors_still_name_the_active_version() -> None:
    """
    Purpose: F21 - a name, a class and the address name the index's active version, as meld does.
    Contract: describe by name answers version 2; purge by class retires version 2's object only; purge by name
        string after a rebuild does the same; version 1's object survives both.
    Returns: None.
    """
    world = _World(Existence.unique)
    try:
        old = world.root.meld(spell_id=world.v1_id)
        world.notch(world.v2_id)
        new = world.root.meld(spell_id=world.v2_id)
        assert world.root.describe_live_creation_status(spell_name="Resource")["spell_id"] == world.v2_id
        assert world.root.purge(spell=Resource) == 1
        assert (old.cleanup_calls, new.cleanup_calls) == (0, 1)
        rebuilt = world.root.meld(spell_id=world.v2_id)
        assert world.root.purge("Resource") == 1
        assert (old.cleanup_calls, rebuilt.cleanup_calls) == (0, 1)
        assert world.root.has_live_creation(spell=world.v1_id) is True
    finally:
        world.cleanup()


def test_a_spell_object_is_not_a_selector_for_its_version() -> None:
    """
    Purpose: F22 - the Spell object `get_spell_by_spell_id` returns is treated as an application instance, unchanged.
    Contract: Its class `Spell` is looked up as an address and raises KeyError naming frame 'spell'; the handle for a
        version is its spell_id.
    Returns: None.
    """
    world = _World(Existence.unique)
    try:
        world.root.meld(spell_id=world.v1_id)
        version_1 = world.root.get_spell_by_spell_id(world.v1_id)
        with pytest.raises(KeyError, match="frame='spell'"):
            world.root.has_live_creation(spell=version_1)
        with pytest.raises(KeyError, match="frame='spell'"):
            world.root.purge(spell=version_1)
        assert world.root.has_live_creation(spell=world.v1_id) is True
    finally:
        world.cleanup()


def test_versions_staged_before_conjure_are_reached_like_those_staged_after() -> None:
    """
    Purpose: F2 for a Book that staged version 2 before conjure: the same answers as one staged after.
    Contract: The parked version is probed False and purged 0 before a notch; after a notch to it, a build, and a
        notch back, it is probed True and purged once.
    Returns: None.
    """
    world = _World(Existence.unique, stage_before_conjure=True)
    try:
        assert world.root.has_live_creation(spell=world.v2_id) is False
        assert world.root.purge(spell_id=world.v2_id) == 0
        world.notch(world.v2_id)
        obj = world.root.meld(spell_id=world.v2_id)
        world.notch(world.v1_id)
        assert world.root.has_live_creation(spell=world.v2_id) is True
        assert world.root.purge(spell_id=world.v2_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        world.cleanup()
