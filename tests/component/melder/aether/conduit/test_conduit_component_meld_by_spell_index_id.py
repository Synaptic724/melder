"""
Component: a meld names its target by spell index id (TASK-2026-11-28-meld_by_spell_index_id, GitHub #346; item C8
of the correctness-defects epic, #209).

`Conduit.meld`, `SpellSpace.meld` and `Conduit.managed_spell_meld` take `spell_index_id=` beside `spell_id=`. The
conduit's Spellbook resolves the index id - its own index, or one it borrows - to the version the index selects, and
the meld continues as a meld of that spell_id, so a meld by index id builds the version the index has active and
follows a notch. A spell_id meld that misses a version the Book can see parked says so and names its index id. The
Book keeps its own indexes by id in `_spell_indexes_by_id`, the twin of `_spells`' keys, written by every writer of
`_spells`; the invariant tests read the two maps directly because no public call exposes them.

Each test builds a fresh world in the "default" frame with caching off and one phase worker. `Resource` is version 1
and `version_of(Resource, version=2)` version 2 - new code under the same name, bound bare at the class's address.
"""

from collections.abc import Iterator
from typing import Any, Dict, List, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_lease import ManagedSpellLease
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests._spell_identity_test_support import version_of


class Resource:
    """
    Purpose: Version 1 of the resource the tests version.
    Contract: `version` names the version that built an object; no disposal method.
    """

    version: int = 1


class Lone:
    """
    Purpose: A spell alone in its index, removed again by `cleanup_spell`.
    Contract: Plain.
    """


class Anchor:
    """
    Purpose: Give a second Book something of its own to conjure.
    Contract: Plain.
    """


class Pooled:
    """
    Purpose: A managed spell, leased through `managed_spell_meld`.
    Contract: Plain; the pool keeps the object between leases.
    """


class Greeter(Protocol):
    """
    Purpose: The spellframe `English` is bound under, so a class lookup of `English` cannot reach it.
    Contract: One method.
    """

    def greet(self) -> str:
        """
        Purpose: Return a greeting.
        Returns: str: The greeting.
        """
        ...


class English:
    """
    Purpose: Bound only under the `Greeter` spellframe.
    Contract: Implements `Greeter`.
    """

    def greet(self) -> str:
        """
        Purpose: Return the English greeting.
        Returns: str: "hello".
        """
        return "hello"


class Host:
    """
    Purpose: A consumer whose class lookup of `English` finds it only under a spellframe, so its late bind is refused.
    Contract: Takes one `English`.
    """

    def __init__(self, greeter: English) -> None:
        """
        Purpose: Keep the greeter.
        Args: greeter: The dependency a class lookup cannot reach.
        Returns: None.
        """
        self.greeter = greeter


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """
    Purpose: Isolate every test: fresh Nexus and Aether, rebound on Spellbook and Conduit.
    Contract: Resets before and after the test.
    Yields: None while the test owns its world.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _book(*, dynamic: bool = True, first: bool = True) -> Spellbook:
    """
    Purpose: Build one Book in the "default" frame with one phase worker.
    Args:
        dynamic: The world's mode, settled by the frame's first Book.
        first: True for the frame's first Book; a later Book inherits the frame's posture.
    Returns:
        Spellbook: The Book, not conjured.
    """
    configuration = SpellbookConfiguration("default")
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame="default", configuration=configuration)
    if first:
        book.configure_aether_frame(
            system_state="dynamic" if dynamic else "automatic", disposal=None, disposal_method_names=None,
            system_caching_enabled=False,
        )
    return book


def _assert_index_map_matches(book: Spellbook) -> None:
    """
    Purpose: Check the Book's index-id map against `_spells`, whose keys it mirrors.
    Contract: The map's keys are exactly the ids of `_spells`' keys, and each maps to that very SpellIndex.
    Args: book: A live Spellbook.
    Returns: None.
    """
    assert set(book._spell_indexes_by_id) == {index.id for index in book._spells}
    for index_id, index in book._spell_indexes_by_id.items():
        assert index.id == index_id
        assert index in book._spells


class _World:
    """
    Purpose: One dynamic lender: `Resource` bound active, its version 2 staged parked on the same index after conjure.
    Contract:
        - `book`, `root`, `index`, `index_id`, `v1_id` and `v2_id` name the world's parts.
        - `notch(spell_id)` moves the index to that version through the public notch.
        - `cleanup()` tears the root and the Book down; extra conduits are the test's to clean first.
    """

    def __init__(self) -> None:
        """
        Purpose: Build the world.
        Returns: None.
        """
        self.book: Spellbook = _book()
        self.v1_id: str = self.book.bind(spell=Resource, existence=Existence.unique, permissions="create")
        self.root: Conduit = self.book.conjure(dynamic=True, name="lender")
        self.index: Any = self.root.get_spell_by_spell_id(self.v1_id).spell_index
        self.index_id: str = self.index.id
        self.v2_id: str = self.root.bind_inactive(
            spell=version_of(Resource, version=2), spell_index=self.index, existence=Existence.unique,
            permissions="create",
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


def _borrower(world: _World) -> Conduit:
    """
    Purpose: Give a second root of the frame an index link to the world's index.
    Args: world: The lender's world.
    Returns: Conduit: The borrower's root, linked to the lender and following its index.
    """
    borrower = _book(first=False).conjure(dynamic=True, name="borrower")
    world.root.link(borrower)
    borrower.add_index_to_contract(index=world.index, conduit=world.root, permissions="create")
    return borrower


# --- the meld doors ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("dynamic", [False, True])
def test_meld_by_spell_index_id_builds_the_version_the_index_has_active(dynamic: bool) -> None:
    """
    Purpose: A meld by index id returns what a meld by the index's selected spell_id returns, warm or cold.
    Contract: For a `unique` spell both forms return the one stored object, in an automatic and a dynamic world.
    Args: dynamic: The world's mode.
    Returns: None.
    """
    book = _book(dynamic=dynamic)
    spell_id = book.bind(spell=Resource, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=dynamic, name="root")
    try:
        index_id = root.get_spell_by_spell_id(spell_id).spell_index.id
        by_index = root.meld(spell_index_id=index_id)
        assert isinstance(by_index, Resource)
        assert by_index is root.meld(spell_id=spell_id)
        assert root.meld(spell_index_id=index_id) is by_index
    finally:
        root.cleanup()
        book.cleanup()


def test_meld_by_spell_index_id_follows_a_notch() -> None:
    """
    Purpose: The index id names whichever version the index has active, through a notch and back.
    Contract: Before the notch it builds version 1, after it version 2, and after the notch back version 1's own
        object again (versions coexist); the Book's index map stays in step throughout.
    Returns: None.
    """
    world = _World()
    try:
        first = world.root.meld(spell_index_id=world.index_id)
        assert first.version == 1
        world.notch(world.v2_id)
        _assert_index_map_matches(world.book)
        second = world.root.meld(spell_index_id=world.index_id)
        assert second.version == 2
        world.notch(world.v1_id)
        _assert_index_map_matches(world.book)
        assert world.root.meld(spell_index_id=world.index_id) is first
    finally:
        world.cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
def test_spellspace_meld_by_spell_index_id_builds_the_index_version(dynamic: bool) -> None:
    """
    Purpose: `SpellSpace.meld` takes the index id as the conduit's meld does.
    Contract: Inside a spellspace the index id returns what the selected spell_id returns.
    Args: dynamic: The world's mode.
    Returns: None.
    """
    book = _book(dynamic=dynamic)
    spell_id = book.bind(spell=Resource, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=dynamic, name="root")
    try:
        index_id = root.get_spell_by_spell_id(spell_id).spell_index.id
        with root.enter_spellspace() as space:
            assert space.meld(spell_index_id=index_id) is space.meld(spell_id=spell_id)
            assert space.meld(spell_index_id=index_id) is space.meld(spell_id=spell_id)
    finally:
        root.cleanup()
        book.cleanup()


def test_spellspace_meld_by_spell_index_id_follows_a_notch() -> None:
    """
    Purpose: A spellspace meld by index id follows the lender's notch.
    Contract: Version 1 before the notch, version 2 after it.
    Returns: None.
    """
    world = _World()
    try:
        with world.root.enter_spellspace() as space:
            assert space.meld(spell_index_id=world.index_id).version == 1
        world.notch(world.v2_id)
        with world.root.enter_spellspace() as space:
            assert space.meld(spell_index_id=world.index_id).version == 2
    finally:
        world.cleanup()


def test_managed_spell_meld_by_spell_index_id_leases_the_index_version() -> None:
    """
    Purpose: `managed_spell_meld` takes the index id and leases the version the index selects.
    Contract: The lease holds a `Pooled` object, and giving it back lets the next lease reuse it.
    Returns: None.
    """
    book = _book()
    spell_id = book.bind(spell=Pooled, existence=Existence.managed_spell_quantity, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        index_id = root.get_spell_by_spell_id(spell_id).spell_index.id
        lease = root.managed_spell_meld(spell_index_id=index_id)
        assert isinstance(lease, ManagedSpellLease) and isinstance(lease.object, Pooled)
        first = lease.object
        lease.release()
        with root.managed_spell_meld(spell_index_id=index_id) as again:
            assert again is first
    finally:
        root.cleanup()
        book.cleanup()


def test_borrower_melds_a_borrowed_index_by_its_id_and_follows_the_lenders_notch() -> None:
    """
    Purpose: A borrower names the lender's index by its id; the Book resolves it through its borrowed indexes.
    Contract: The borrower builds version 1, and version 2 once the lender notches. The lender melds version 2 first:
        a borrower's meld of a version its lender staged after conjure and never melded raises "Cannot build
        CreationContext before spell_codegen_creation exists" in every form - by spell_id, class or name - a defect
        that predates the index form (C9 of the correctness-defects epic, GitHub #209).
    Returns: None.
    """
    world = _World()
    borrower = _borrower(world)
    try:
        assert borrower.meld(spell_index_id=world.index_id).version == 1
        world.notch(world.v2_id)
        assert world.root.meld(spell_index_id=world.index_id).version == 2
        assert borrower.meld(spell_index_id=world.index_id).version == 2
    finally:
        borrower.cleanup()
        world.cleanup()


# --- refusals ---------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "extra",
    [{"spell_id": "0" * 64}, {"spell": Resource}, {"spell": "Resource"}, {"spellframe": "resource"},
     {"binding_name": "main"}],
    ids=["spell_id", "class", "name", "spellframe", "binding_name"],
)
def test_meld_refuses_spell_index_id_with_another_selector(extra: Dict[str, Any]) -> None:
    """
    Purpose: `spell_index_id` names a target on its own; a second selector is a mistake, refused before anything.
    Contract: ValueError naming `spell_index_id`, from `Conduit.meld`, `SpellSpace.meld` and `managed_spell_meld`.
    Args: extra: The second selector.
    Returns: None.
    """
    world = _World()
    try:
        with pytest.raises(ValueError, match="accepts `spell_index_id` alone"):
            world.root.meld(spell_index_id=world.index_id, **extra)
        with world.root.enter_spellspace() as space:
            with pytest.raises(ValueError, match="accepts `spell_index_id` alone"):
                space.meld(spell_index_id=world.index_id, **extra)
        with pytest.raises(ValueError, match="accepts `spell_index_id` alone"):
            world.root.managed_spell_meld(spell_index_id=world.index_id, **extra)
    finally:
        world.cleanup()


def test_meld_refuses_a_spell_index_id_that_is_not_a_string() -> None:
    """
    Purpose: An index id is a string; anything else is refused with the type named.
    Contract: TypeError from each door.
    Returns: None.
    """
    world = _World()
    try:
        with pytest.raises(TypeError, match="`spell_index_id` must be a string; got int"):
            world.root.meld(spell_index_id=7)
        with world.root.enter_spellspace() as space:
            with pytest.raises(TypeError, match="`spell_index_id` must be a string; got int"):
                space.meld(spell_index_id=7)
        with pytest.raises(TypeError, match="`spell_index_id` must be a string; got int"):
            world.root.managed_spell_meld(spell_index_id=7)
    finally:
        world.cleanup()


def test_meld_by_an_unknown_spell_index_id_raises_key_error_naming_it() -> None:
    """
    Purpose: An id no index of the conduit's Book carries - owned or borrowed - is refused by name.
    Contract: KeyError "[MELD] No SpellIndex found with spell_index_id: <id>" from each door.
    Returns: None.
    """
    world = _World()
    try:
        with pytest.raises(KeyError, match="No SpellIndex found with spell_index_id: nope"):
            world.root.meld(spell_index_id="nope")
        with world.root.enter_spellspace() as space:
            with pytest.raises(KeyError, match="No SpellIndex found with spell_index_id: nope"):
                space.meld(spell_index_id="nope")
        with pytest.raises(KeyError, match="No SpellIndex found with spell_index_id: nope"):
            world.root.managed_spell_meld(spell_index_id="nope")
    finally:
        world.cleanup()


def test_meld_by_the_id_of_an_index_with_only_parked_versions_says_so() -> None:
    """
    Purpose: An index `remove_from_spell_index` minted holds a parked version and nothing active.
    Contract: KeyError naming the index as holding only parked versions, with the remedy to notch one active.
    Returns: None.
    """
    world = _World()
    try:
        world.root.remove_from_spell_index(spell_id=world.v2_id, source_index=world.index)
        _assert_index_map_matches(world.book)
        minted_id = world.root.get_spell_by_spell_id(world.v2_id).spell_index.id
        assert minted_id != world.index_id
        with pytest.raises(KeyError, match="holds only parked versions") as refused:
            world.root.meld(spell_index_id=minted_id)
        assert world.v2_id in str(refused.value)
        assert "notch" in str(refused.value)
    finally:
        world.cleanup()


# --- the spell_id miss names a parked version's index -----------------------------------------------------------------

def test_meld_of_a_parked_spell_id_names_its_index() -> None:
    """
    Purpose: A spell_id meld of a version a notch parked explains itself instead of reading as missing.
    Contract: KeyError keeping "No spell found with spell_id" and naming the index id; an unknown spell_id keeps the
        text it had, with no parked sentence.
    Returns: None.
    """
    world = _World()
    try:
        with pytest.raises(KeyError, match="No spell found with spell_id") as parked:
            world.root.meld(spell_id=world.v2_id)
        text = str(parked.value)
        assert "is a parked version of SpellIndex" in text
        assert world.index_id in text
        assert f"spell_index_id='{world.index_id}'" in text
        with pytest.raises(KeyError, match="No spell found with spell_id") as unknown:
            world.root.meld(spell_id="0" * 64)
        assert "parked" not in str(unknown.value)
    finally:
        world.cleanup()


def test_borrower_meld_of_a_parked_borrowed_spell_id_names_its_index() -> None:
    """
    Purpose: A borrower's copy parked by the lender's notch explains itself too.
    Contract: KeyError naming the lender's index id.
    Returns: None.
    """
    world = _World()
    borrower = _borrower(world)
    try:
        world.notch(world.v2_id)
        with pytest.raises(KeyError, match="is a parked version of SpellIndex") as parked:
            borrower.meld(spell_id=world.v1_id)
        assert world.index_id in str(parked.value)
    finally:
        borrower.cleanup()
        world.cleanup()


# --- the index map follows every writer of _spells --------------------------------------------------------------------

def test_index_map_follows_bind_and_cleanup_spell() -> None:
    """
    Purpose: A late bind adds its index to the map, and `cleanup_spell` of the index's only version removes it.
    Contract: The index id melds while the spell is bound and is unknown after its cleanup; the map matches
        `_spells` after each step.
    Returns: None.
    """
    world = _World()
    try:
        lone_id = world.book.bind(spell=Lone, existence=Existence.unique, permissions="create")
        _assert_index_map_matches(world.book)
        lone_index_id = world.root.get_spell_by_spell_id(lone_id).spell_index.id
        assert isinstance(world.root.meld(spell_index_id=lone_index_id), Lone)
        world.root.cleanup_spell(spell=world.book.find_spell_by_spell_id(lone_id))
        _assert_index_map_matches(world.book)
        with pytest.raises(KeyError, match="No SpellIndex found with spell_index_id"):
            world.root.meld(spell_index_id=lone_index_id)
    finally:
        world.cleanup()


def test_index_map_follows_a_refused_late_bind() -> None:
    """
    Purpose: A late bind whose commit is refused is undone, and its index leaves the map with it.
    Contract: The bind raises SpellbookValidationError; the map matches `_spells` afterwards.
    Returns: None.
    """
    world = _World()
    try:
        world.book.bind(spell=English, existence=Existence.unique, spellframe=Greeter, binding_name="english",
                        permissions="create")
        with pytest.raises(SpellbookValidationError):
            world.book.bind(spell=Host, existence=Existence.many, permissions="create")
        _assert_index_map_matches(world.book)
    finally:
        world.cleanup()


def test_index_map_follows_the_index_moves() -> None:
    """
    Purpose: `remove_from_spell_index` and `add_to_spell_index` move a parked version without changing `_spells`.
    Contract: The map matches `_spells` after each move, and the original index id still melds its active version.
    Returns: None.
    """
    world = _World()
    try:
        world.root.remove_from_spell_index(spell_id=world.v2_id, source_index=world.index)
        _assert_index_map_matches(world.book)
        world.root.add_to_spell_index(spell_id=world.v2_id, target_index=world.index)
        _assert_index_map_matches(world.book)
        assert world.root.meld(spell_index_id=world.index_id).version == 1
    finally:
        world.cleanup()


def test_index_map_follows_an_ownership_transfer() -> None:
    """
    Purpose: A transfer moves the index from the source Book's map to the target's.
    Contract: Afterwards the target melds the index id, the source refuses it as unknown, and both maps match
        their Book's `_spells`.
    Returns: None.
    """
    world = _World()
    target_book = _book(first=False)
    target_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        world.root.transfer_spell_ownership(spell=world.v1_id, target_conduit=target)
        _assert_index_map_matches(world.book)
        _assert_index_map_matches(target_book)
        assert target.meld(spell_index_id=world.index_id).version == 1
        with pytest.raises(KeyError, match="No SpellIndex found with spell_index_id"):
            world.root.meld(spell_index_id=world.index_id)
    finally:
        target.cleanup()
        target_book.cleanup()
        world.cleanup()


def test_index_map_is_emptied_with_the_books_spells_at_teardown() -> None:
    """
    Purpose: A Book's teardown clears the map with `_spells`, so a torn-down Book holds no index by id.
    Contract: The live Book maps its index by id; after the root's teardown and the Book's cleanup the map is gone with
        the Book's other maps.
    Returns: None.
    """
    world = _World()
    book = world.book
    assert book._spell_indexes_by_id[world.index_id] is world.index
    world.cleanup()
    with pytest.raises(AttributeError):
        book._spell_indexes_by_id
