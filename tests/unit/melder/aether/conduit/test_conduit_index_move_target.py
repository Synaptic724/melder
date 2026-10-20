"""
Unit tests: `Conduit.add_to_spell_index` and `Conduit.remove_from_spell_index` name the spell they move by `spell=`
or `spell_id=` (TASK-2026-10-16-public_notch_target_for_staged_versions, the owner's extension).

Both verbs move only a spell parked in the Book, and no public call returns a parked spell's Spell object, so a
`spell_id` - the one `bind` or `bind_inactive` returned - is resolved inside the call through the Book's
`_get_owned_spell`. The Book is the conftest's stub: `_get_owned_spell` answers from a small map of spell doubles and
the two entries return the Spell they were handed, so each test sees what the facade resolved, which transaction it
started and whether the Book was called. The index-link fan-out goes to a ward double.
"""
from types import SimpleNamespace
from typing import Any, Dict, Iterator

import pytest
from unittest.mock import MagicMock

from melder.aether.conduit.conduit import Conduit


def _index(name: str, selected: str, members: set) -> SimpleNamespace:
    """
    An index double with what the index moves read before admission.

    Args:
        name: Its id.
        selected: The spell_id it selects.
        members: The spell_ids it holds.

    Returns:
        SimpleNamespace: The double.
    """
    return SimpleNamespace(
        _id=name,
        id=name,
        selected_spell_id=selected,
        is_sole_member=lambda spell_id: members == {spell_id},
        spells_in_index=lambda: set(members),
    )


class _Moves:
    """
    The doubles one test works on: two indexes of the Book and the spells it owns.

    Contract:
        - `index` selects "v1" and holds "v1" (active) and "v2" (parked); `other_index` selects "y1" and holds "y1".
        - `owned` is what the stub Book's `_get_owned_spell` answers; a spell_id not in it is not owned.
    """

    def __init__(self, spellbook_stub: MagicMock, conduit: Conduit) -> None:
        """
        Build the doubles and wire them into the stub Book and the conduit.

        Args:
            spellbook_stub: The conftest's Spellbook double the conduit holds.
            conduit: The dynamic normal conduit under test.
        """
        self.book: MagicMock = spellbook_stub
        self.conduit: Conduit = conduit
        self.index: SimpleNamespace = _index("index-x", "v1", {"v1", "v2"})
        self.other_index: SimpleNamespace = _index("index-y", "y1", {"y1"})
        self.v2: SimpleNamespace = SimpleNamespace(spell_id="v2", _key=("default", "k-v2"), spell_index=self.index)
        self.owned: Dict[str, SimpleNamespace] = {"v2": self.v2}
        spellbook_stub._get_owned_spell = MagicMock(side_effect=self.owned.get)
        spellbook_stub._add_to_spell_index = MagicMock(side_effect=lambda **kwargs: kwargs["spell"])
        spellbook_stub._remove_from_spell_index = MagicMock(side_effect=lambda **kwargs: kwargs["spell"])
        conduit._conduit_ward = MagicMock()
        self.mediator: MagicMock = spellbook_stub._transaction_mediator

    def call(self, verb: str, **kwargs: Any) -> Any:
        """
        Call one of the two verbs with its own index keyword.

        Args:
            verb: "add_to_spell_index" (onto `other_index`) or "remove_from_spell_index" (out of `index`).
            **kwargs: `spell` and/or `spell_id`.

        Returns:
            Any: What the verb returned.
        """
        if verb == "add_to_spell_index":
            return self.conduit.add_to_spell_index(target_index=self.other_index, **kwargs)
        return self.conduit.remove_from_spell_index(source_index=self.index, **kwargs)

    def entry(self, verb: str) -> MagicMock:
        """
        The stub Book's entry the verb calls inside its window.

        Args:
            verb: The verb's name.

        Returns:
            MagicMock: `_add_to_spell_index` or `_remove_from_spell_index`.
        """
        if verb == "add_to_spell_index":
            return self.book._add_to_spell_index
        return self.book._remove_from_spell_index

    def assert_nothing_started(self) -> None:
        """Assert a refused call started no transaction, never reached the Book's entries and fanned nothing out."""
        self.mediator.start_transaction.assert_not_called()
        self.mediator.end_transaction.assert_not_called()
        self.book._add_to_spell_index.assert_not_called()
        self.book._remove_from_spell_index.assert_not_called()
        assert self.conduit._conduit_ward.method_calls == []


VERBS = ("add_to_spell_index", "remove_from_spell_index")


@pytest.fixture()
def moves(spellbook_stub: MagicMock, conduit_dynamic_normal: Conduit) -> Iterator[_Moves]:
    """
    A dynamic normal conduit over a stub Book owning v1 (active) and v2 (parked) on one index, y1 on another.

    Yields:
        _Moves: The doubles and the conduit.
    """
    yield _Moves(spellbook_stub, conduit_dynamic_normal)


def test_add_by_spell_id_resolves_the_owned_spell_and_moves_it(moves: _Moves) -> None:
    """
    `spell_id=` names the parked spell: the Book resolves it, and the move, its metadata and its fan-out use it.

    Contract:
        - `_get_owned_spell` is asked for the spell_id; the resolved Spell reaches `_add_to_spell_index`.
        - The transaction metadata names it; the target gains the member and the source loses it.
    """
    result = moves.conduit.add_to_spell_index(spell_id="v2", target_index=moves.other_index)

    moves.book._get_owned_spell.assert_called_once_with("v2")
    moves.book._add_to_spell_index.assert_called_once_with(spell=moves.v2, target_index=moves.other_index)
    assert result is moves.v2
    metadata = moves.mediator.start_transaction.call_args.kwargs["metadata"]
    assert metadata["spell_id"] == "v2"
    assert metadata["binding_key"] == ("default", "k-v2")
    moves.mediator.end_transaction.assert_called_once_with(expected_type="add_to_index", success=True)
    moves.conduit._conduit_ward._emit_index_member_added.assert_called_once_with(moves.other_index, "v2")
    moves.conduit._conduit_ward._emit_index_member_removed.assert_called_once_with("index-x", "v2")


def test_remove_by_spell_id_resolves_the_owned_spell_and_separates_it(moves: _Moves) -> None:
    """
    `spell_id=` names the parked spell to split out: the Book resolves it, and the split and its fan-out use it.
    """
    result = moves.conduit.remove_from_spell_index(spell_id="v2", source_index=moves.index)

    moves.book._get_owned_spell.assert_called_once_with("v2")
    moves.book._remove_from_spell_index.assert_called_once_with(spell=moves.v2, source_index=moves.index)
    assert result is moves.v2
    metadata = moves.mediator.start_transaction.call_args.kwargs["metadata"]
    assert metadata["spell_id"] == "v2"
    moves.mediator.end_transaction.assert_called_once_with(expected_type="remove_from_index", success=True)
    moves.conduit._conduit_ward._emit_index_member_removed.assert_called_once_with("index-x", "v2")


@pytest.mark.parametrize("verb", VERBS)
def test_index_move_by_spell_passes_the_object_through_without_asking_the_book(moves: _Moves, verb: str) -> None:
    """`spell=` behaves as before: the same object reaches the Book's entry, and `_get_owned_spell` is not asked."""
    result = moves.call(verb, spell=moves.v2)

    moves.book._get_owned_spell.assert_not_called()
    assert moves.entry(verb).call_args.kwargs["spell"] is moves.v2
    assert result is moves.v2


@pytest.mark.parametrize("verb", VERBS)
def test_index_move_refuses_both_spell_and_spell_id(moves: _Moves, verb: str) -> None:
    """Both forms at once are refused, in the verb's own words, before the Book is asked or anything starts."""
    with pytest.raises(ValueError, match=f"{verb} accepts either `spell` or `spell_id`, not both"):
        moves.call(verb, spell=moves.v2, spell_id="v2")

    moves.book._get_owned_spell.assert_not_called()
    moves.assert_nothing_started()


@pytest.mark.parametrize("verb", VERBS)
def test_index_move_refuses_a_call_without_a_spell(moves: _Moves, verb: str) -> None:
    """Neither form is refused, and the message says where a spell_id comes from."""
    with pytest.raises(ValueError, match=f"{verb} needs a spell: pass spell_id=<the spell_id bind or bind_inactive"):
        moves.call(verb)

    moves.assert_nothing_started()


@pytest.mark.parametrize("verb", VERBS)
def test_index_move_refuses_a_spell_id_that_is_not_a_string(moves: _Moves, verb: str) -> None:
    """A non-str `spell_id` raises TypeError naming its type."""
    with pytest.raises(TypeError, match=f"{verb} `spell_id` must be a string; got int"):
        moves.call(verb, spell_id=42)

    moves.book._get_owned_spell.assert_not_called()
    moves.assert_nothing_started()


@pytest.mark.parametrize("verb", VERBS)
def test_index_move_refuses_a_spell_id_passed_as_spell(moves: _Moves, verb: str) -> None:
    """A str given as `spell` is refused with the remedy: a spell_id goes in `spell_id=`."""
    with pytest.raises(TypeError, match="pass spell_id='v2'"):
        moves.call(verb, spell="v2")

    moves.assert_nothing_started()


@pytest.mark.parametrize("verb", VERBS)
def test_index_move_refuses_a_spell_id_the_book_does_not_own(moves: _Moves, verb: str) -> None:
    """An unknown spell_id is refused with the spell_id in the message; nothing is started."""
    with pytest.raises(ValueError, match=f"{verb}: spell_id 'nope' is not owned by this conduit's Spellbook"):
        moves.call(verb, spell_id="nope")

    moves.book._get_owned_spell.assert_called_once_with("nope")
    moves.assert_nothing_started()


@pytest.mark.parametrize("verb", VERBS)
def test_index_move_by_spell_id_on_an_automatic_conduit_raises_the_dynamic_mode_error(
    spellbook_stub: MagicMock,
    conduit_normal: Conduit,
    verb: str,
) -> None:
    """The dynamic gate still comes first: an automatic conduit refuses with RuntimeError before the Book is asked."""
    spellbook_stub._get_owned_spell = MagicMock()
    index = _index("i", "a", {"a"})

    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        if verb == "add_to_spell_index":
            conduit_normal.add_to_spell_index(spell_id="v2", target_index=index)
        else:
            conduit_normal.remove_from_spell_index(spell_id="v2", source_index=index)

    spellbook_stub._get_owned_spell.assert_not_called()
