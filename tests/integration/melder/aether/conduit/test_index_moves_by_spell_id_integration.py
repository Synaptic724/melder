"""
Integration: `add_to_spell_index` and `remove_from_spell_index` move a parked spell named by its spell_id
(TASK-2026-10-16-public_notch_target_for_staged_versions, the owner's extension).

Both verbs move only a spell parked in the Book. `bind_inactive` returns the parked spell's spell_id, and the public
lookups answer a parked spell_id with the index's active spell, so until 0.2.8249 neither verb could be called from
public code. Each call resolves the spell_id inside the call, as `notch_spell(spell_id=...)` does; the Book's own
checks (owned, parked, a member of the source index) are unchanged.

Every version of an index is bound the way its first version was (2026-10-25), so a parked version moves only onto an
index bound as it is - here, back onto the index it was split from - and an index bound another way refuses it.
"""
import contextlib
from typing import Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

pytestmark = pytest.mark.integration


class _ServiceA:
    """The spell bound active on index X."""

    def __init__(self) -> None:
        """Tag the object with its spell."""
        self.tag = "A"


class _ServiceB:
    """The spell parked on index X, then moved."""

    def __init__(self) -> None:
        """Tag the object with its spell."""
        self.tag = "B"


class _ServiceY:
    """The spell bound active on index Y."""

    def __init__(self) -> None:
        """Tag the object with its spell."""
        self.tag = "Y"


class _ServiceOther:
    """The spell another Book of the frame owns: one class is one spell, so it is a class of its own."""

    def __init__(self) -> None:
        """Tag the object with its spell."""
        self.tag = "other"


def _reset_world() -> None:
    """Fresh Aether and utility-system singletons for one test."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """Isolate each test behind fresh singletons."""
    _reset_world()
    yield
    _reset_world()


def _make_spellbook() -> Spellbook:
    """
    A Book in a dynamic world.

    Returns:
        Spellbook: A new Book on the default frame.
    """
    configuration = SpellbookConfiguration(aether_frame="default")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame="default", configuration=configuration)


@contextlib.contextmanager
def _two_indexes() -> Iterator[Tuple[Spellbook, Conduit, str, str, str, SpellIndex, SpellIndex]]:
    """
    A root with index X (A active, B parked) and index Y (Y active).

    X's versions share one binding, spellframe 'service' and binding name 'a'; Y is bound another way, spellframe
    'other' and binding name 'y', so a version of X cannot join it (2026-10-25).

    Yields:
        Tuple: (book, root, id_a, id_b, id_y, index_x, index_y).
    """
    book = _make_spellbook()
    id_a = book.bind(
        spell=_ServiceA, existence=Existence.unique, permissions="create", spellframe="service", binding_name="a",
    )
    id_y = book.bind(
        spell=_ServiceY, existence=Existence.unique, permissions="create", spellframe="other", binding_name="y",
    )
    root = book.conjure(dynamic=True, name="root")
    index_x = book.find_spell_by_spell_id(id_a).spell_index
    index_y = book.find_spell_by_spell_id(id_y).spell_index
    id_b = root.bind_inactive(
        spell=_ServiceB, spell_index=index_x, existence=Existence.unique, permissions="create",
        spellframe="service", binding_name="a",
    )
    try:
        yield book, root, id_a, id_b, id_y, index_x, index_y
    finally:
        root.cleanup()


def _assert_indexes_intact(
        root: Conduit, index_x: SpellIndex, index_y: SpellIndex, id_a: str, id_b: str, id_y: str,
) -> None:
    """
    Assert both indexes are as `_two_indexes` built them and their active spells meld.

    Args:
        root: The conduit that melds.
        index_x: Index X (A active, B parked).
        index_y: Index Y (Y active).
        id_a: A's spell_id.
        id_b: B's spell_id.
        id_y: Y's spell_id.
    """
    assert index_x.selected_spell_id == id_a
    assert index_x.spells_in_index() == {id_a, id_b}
    assert index_y.selected_spell_id == id_y
    assert index_y.spells_in_index() == {id_y}
    assert root.meld(spell_id=id_a).tag == "A"
    assert root.meld(spell_id=id_y).tag == "Y"


def test_add_to_spell_index_by_spell_id_moves_a_parked_spell_onto_another_index() -> None:
    """
    The spell_id `bind_inactive` returned is enough to move the parked spell; a notch to it then melds it.

    Contract:
        - B split out of X into an index of its own moves back onto X by its spell_id as a parked member - the index
          it moves onto keeps B's binding (2026-10-25): its own index empties and goes, X keeps A active, and the
          call returns B's Spell.
    """
    with _two_indexes() as (book, root, id_a, id_b, id_y, index_x, index_y):
        own_index = root.remove_from_spell_index(spell_id=id_b, source_index=index_x).spell_index

        moved = root.add_to_spell_index(spell_id=id_b, target_index=index_x)

        assert moved.spell_id == id_b
        assert moved.spell_index is index_x
        assert own_index.cleaned
        assert index_x.spells_in_index() == {id_a, id_b}
        assert index_x.selected_spell_id == id_a
        assert root.meld(spell_id=id_a).tag == "A"

        root.notch_spell(spell_index=index_x, spell_id=id_b)
        assert root.meld(spell_id=id_b).tag == "B"


def test_add_to_spell_index_by_spell_id_refuses_an_index_bound_another_way() -> None:
    """
    Regression for the strict rule (2026-10-25): B, bound as X's versions are, cannot join Y, which is bound another
    way; until then it joined Y, and a notch to it there moved Y's address.

    Contract:
        - ValueError "add_to_spell_index refused: SpellIndex <Y> keeps the binding its first version was bound
          with ..."; nothing moves.
    """
    with _two_indexes() as (book, root, id_a, id_b, id_y, index_x, index_y):
        with pytest.raises(ValueError, match="add_to_spell_index refused: SpellIndex .* keeps the binding"):
            root.add_to_spell_index(spell_id=id_b, target_index=index_y)

        _assert_indexes_intact(root, index_x, index_y, id_a, id_b, id_y)


def test_remove_from_spell_index_by_spell_id_splits_a_parked_spell_into_a_fresh_index() -> None:
    """
    The spell_id is enough to split the parked spell out: it becomes the only member of a fresh index.

    Contract:
        - X keeps A active and loses B; B's new index holds B alone; the call returns B's Spell.
    """
    with _two_indexes() as (book, root, id_a, id_b, id_y, index_x, index_y):
        separated = root.remove_from_spell_index(spell_id=id_b, source_index=index_x)

        assert separated.spell_id == id_b
        assert separated.spell_index is not index_x
        assert separated.spell_index.spells_in_index() == {id_b}
        assert index_x.spells_in_index() == {id_a}
        assert index_x.selected_spell_id == id_a
        assert root.meld(spell_id=id_a).tag == "A"


@pytest.mark.parametrize("verb", ["add_to_spell_index", "remove_from_spell_index"])
def test_index_move_refuses_an_unknown_spell_id_and_changes_nothing(verb: str) -> None:
    """A spell_id the Book does not own is refused with ValueError before anything moves."""
    with _two_indexes() as (book, root, id_a, id_b, id_y, index_x, index_y):
        with pytest.raises(ValueError, match=f"{verb}: spell_id 'no-such-spell-id' is not owned"):
            if verb == "add_to_spell_index":
                root.add_to_spell_index(spell_id="no-such-spell-id", target_index=index_y)
            else:
                root.remove_from_spell_index(spell_id="no-such-spell-id", source_index=index_x)

        _assert_indexes_intact(root, index_x, index_y, id_a, id_b, id_y)


@pytest.mark.parametrize("verb", ["add_to_spell_index", "remove_from_spell_index"])
def test_index_move_refuses_another_books_spell_id(verb: str) -> None:
    """A spell_id another Book of the frame owns is not this conduit's Book's, so it is refused as not owned."""
    with _two_indexes() as (book, root, id_a, id_b, id_y, index_x, index_y):
        other_book = _make_spellbook()
        id_other = other_book.bind(
            spell=_ServiceOther, existence=Existence.unique, permissions="create", binding_name="other_b",
        )
        with pytest.raises(ValueError, match="is not owned by this conduit's Spellbook"):
            if verb == "add_to_spell_index":
                root.add_to_spell_index(spell_id=id_other, target_index=index_y)
            else:
                root.remove_from_spell_index(spell_id=id_other, source_index=index_x)

        _assert_indexes_intact(root, index_x, index_y, id_a, id_b, id_y)


@pytest.mark.parametrize("verb", ["add_to_spell_index", "remove_from_spell_index"])
def test_index_move_refuses_both_and_neither(verb: str) -> None:
    """Both forms at once, and no spell at all, are refused with ValueError; nothing moves."""
    with _two_indexes() as (book, root, id_a, id_b, id_y, index_x, index_y):
        spell_b = book._get_owned_spell(id_b)
        index_keyword = {"target_index": index_y} if verb == "add_to_spell_index" else {"source_index": index_x}
        with pytest.raises(ValueError, match="not both"):
            getattr(root, verb)(spell=spell_b, spell_id=id_b, **index_keyword)
        with pytest.raises(ValueError, match="needs a spell"):
            getattr(root, verb)(**index_keyword)

        _assert_indexes_intact(root, index_x, index_y, id_a, id_b, id_y)


@pytest.mark.parametrize("verb", ["add_to_spell_index", "remove_from_spell_index"])
def test_index_move_by_spell_id_of_an_active_spell_is_refused_by_the_book(verb: str) -> None:
    """
    An active spell's spell_id resolves, and the Book refuses to move it, as it refuses the Spell object.

    Contract:
        - RuntimeError "... is active in its index; notch away from it before moving it."; nothing moves.
    """
    with _two_indexes() as (book, root, id_a, id_b, id_y, index_x, index_y):
        with pytest.raises(RuntimeError, match="is active in its index; notch away from it before moving it"):
            if verb == "add_to_spell_index":
                root.add_to_spell_index(spell_id=id_a, target_index=index_y)
            else:
                root.remove_from_spell_index(spell_id=id_a, source_index=index_x)

        _assert_indexes_intact(root, index_x, index_y, id_a, id_b, id_y)
