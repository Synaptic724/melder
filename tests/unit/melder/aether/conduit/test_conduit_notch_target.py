"""
Unit tests: `Conduit.notch_spell` names its target by `spell=` or `spell_id=` and checks it before it notches
(TASK-2026-10-16-public_notch_target_for_staged_versions).

The Book is the conftest's stub: `_get_owned_spell` answers from a small map of version doubles and `_notch_spell`
returns the Spell it was handed, so each test sees exactly what the facade resolved, which transaction it started
and whether the seam ran. The post-window fan-out is patched where a notch succeeds.
"""
from types import SimpleNamespace
from typing import Dict, Iterator
from unittest.mock import MagicMock, patch

import pytest

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.conduit.conduit import Conduit


class _Lineage:
    """
    The doubles one test works on: two indexes of the Book and the versions it owns.

    Contract:
        - `index` selects "v1" and holds "v1" (active) and "v2" (parked); `other_index` selects "y1" and holds "y2".
        - `owned` is what the stub Book's `_get_owned_spell` answers; a version not in it is not owned.
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
        self.index: SimpleNamespace = SimpleNamespace(_id="index-x", id="index-x", selected_spell_id="v1")
        self.other_index: SimpleNamespace = SimpleNamespace(_id="index-y", id="index-y", selected_spell_id="y1")
        self.v1: SimpleNamespace = SimpleNamespace(spell_id="v1", _key=("default", "k-v1"), spell_index=self.index)
        self.v2: SimpleNamespace = SimpleNamespace(spell_id="v2", _key=("default", "k-v2"), spell_index=self.index)
        self.y2: SimpleNamespace = SimpleNamespace(
            spell_id="y2", _key=("default", "k-y2"), spell_index=self.other_index,
        )
        self.owned: Dict[str, SimpleNamespace] = {"v1": self.v1, "v2": self.v2, "y2": self.y2}
        spellbook_stub._get_owned_spell = MagicMock(side_effect=self.owned.get)
        spellbook_stub._notch_spell = MagicMock(side_effect=lambda **kwargs: kwargs["spell"])
        conduit._conduit_ward = MagicMock()
        self.mediator: MagicMock = spellbook_stub._transaction_mediator

    def assert_nothing_started(self) -> None:
        """Assert a refused call started no transaction and never reached the seam."""
        self.mediator.start_transaction.assert_not_called()
        self.mediator.end_transaction.assert_not_called()
        self.book._notch_spell.assert_not_called()


@pytest.fixture()
def lineage(spellbook_stub: MagicMock, conduit_dynamic_normal: Conduit) -> Iterator[_Lineage]:
    """
    A dynamic normal conduit over a stub Book owning v1 (active), v2 (parked) and y2 (another index).

    Yields:
        _Lineage: The doubles and the conduit.
    """
    with patch.object(Conduit, "_deactivate_borrowed_spell"):
        yield _Lineage(spellbook_stub, conduit_dynamic_normal)


def test_notch_by_spell_id_resolves_the_owned_version_and_notches_it(lineage: _Lineage) -> None:
    """
    `spell_id=` names the version: the Book resolves it and the seam receives that Spell.

    Contract:
        - `_get_owned_spell` is asked for the spell_id; the resolved Spell reaches `_notch_spell` and is returned.
        - The transaction metadata names the resolved version (`spell_id`, `binding_key`).
    """
    result = lineage.conduit.notch_spell(spell_index=lineage.index, spell_id="v2")

    lineage.book._get_owned_spell.assert_any_call("v2")
    lineage.book._notch_spell.assert_called_once_with(
        spell_index=lineage.index,
        spell=lineage.v2,
        change_reason=SpellStateChangeReason.selected_different_spell,
    )
    assert result is lineage.v2
    metadata = lineage.mediator.start_transaction.call_args.kwargs["metadata"]
    assert metadata["spell_id"] == "v2"
    assert metadata["binding_key"] == ("default", "k-v2")
    lineage.mediator.end_transaction.assert_called_once_with(expected_type="notch", success=True)


def test_notch_by_spell_id_fans_out_with_the_resolved_version(lineage: _Lineage) -> None:
    """
    After the window, the borrowers are moved from the outgoing spell_id to the resolved version's spell_id.

    Contract:
        - The outgoing copy is parked on the peers and the index-link receivers move from "v1" to "v2".
    """
    lineage.conduit.notch_spell(spell_index=lineage.index, spell_id="v2")

    Conduit._deactivate_borrowed_spell.assert_called_once_with("v1")
    lineage.conduit._conduit_ward._emit_index_notch.assert_called_once_with(lineage.index, "v1", "v2")


def test_notch_by_spell_passes_an_owned_member_through_unchanged(lineage: _Lineage) -> None:
    """
    `spell=` with a version the Book owns on that index behaves as before: the same object reaches the seam.
    """
    result = lineage.conduit.notch_spell(spell_index=lineage.index, spell=lineage.v2)

    lineage.book._notch_spell.assert_called_once_with(
        spell_index=lineage.index,
        spell=lineage.v2,
        change_reason=SpellStateChangeReason.selected_different_spell,
    )
    assert result is lineage.v2


def test_notch_passes_the_change_reason_through(lineage: _Lineage) -> None:
    """A notch by spell_id keeps the caller's `change_reason`."""
    lineage.conduit.notch_spell(
        spell_index=lineage.index,
        spell_id="v2",
        change_reason=SpellStateChangeReason.mutation_contract_set,
    )

    assert lineage.book._notch_spell.call_args.kwargs["change_reason"] is SpellStateChangeReason.mutation_contract_set


def test_notch_to_the_active_version_by_id_does_not_fan_out(lineage: _Lineage) -> None:
    """
    Naming the index's active version is a no-op for the borrowers: the outgoing spell_id equals the target's.
    """
    lineage.conduit.notch_spell(spell_index=lineage.index, spell_id="v1")

    lineage.book._notch_spell.assert_called_once()
    Conduit._deactivate_borrowed_spell.assert_not_called()
    lineage.conduit._conduit_ward._emit_index_notch.assert_not_called()


def test_notch_refuses_both_spell_and_spell_id(lineage: _Lineage) -> None:
    """Both forms at once are refused before the Book is asked or a transaction starts."""
    with pytest.raises(ValueError, match="either `spell` or `spell_id`, not both"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell=lineage.v2, spell_id="v2")

    lineage.book._get_owned_spell.assert_not_called()
    lineage.assert_nothing_started()


def test_notch_refuses_a_call_without_a_target(lineage: _Lineage) -> None:
    """Neither form is refused, and the message says where a spell_id comes from."""
    with pytest.raises(ValueError, match="notch_spell needs a spell: pass spell_id=<the spell_id bind or bind_inac"):
        lineage.conduit.notch_spell(spell_index=lineage.index)

    lineage.assert_nothing_started()


def test_notch_refuses_a_spell_id_that_is_not_a_string(lineage: _Lineage) -> None:
    """A non-str `spell_id` raises TypeError naming its type."""
    with pytest.raises(TypeError, match="must be a string; got int"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell_id=42)

    lineage.assert_nothing_started()


def test_notch_refuses_an_id_passed_as_spell(lineage: _Lineage) -> None:
    """A str given as `spell` is refused with the remedy: a spell_id goes in `spell_id=`."""
    with pytest.raises(TypeError, match="to name a spell by its spell_id, pass spell_id='v2'"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell="v2")

    lineage.assert_nothing_started()


def test_notch_refuses_an_id_the_book_does_not_own(lineage: _Lineage) -> None:
    """An unknown spell_id is refused with the spell_id in the message; nothing is started."""
    with pytest.raises(ValueError, match="notch_spell: spell_id 'nope' is not owned by this conduit's Spellbook"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell_id="nope")

    lineage.assert_nothing_started()


def test_notch_refuses_a_version_of_another_index_by_id(lineage: _Lineage) -> None:
    """An owned version of another index, named by spell_id, is refused before anything moves."""
    with pytest.raises(ValueError, match="notch_spell: spell_id 'y2' belongs to another SpellIndex"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell_id="y2")

    lineage.assert_nothing_started()


def test_notch_refuses_a_version_of_another_index_by_object(lineage: _Lineage) -> None:
    """The same refusal for `spell=`: a version of another index used to corrupt both indexes."""
    with pytest.raises(ValueError, match="belongs to another SpellIndex"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell=lineage.y2)

    lineage.assert_nothing_started()


def test_notch_refuses_a_spell_the_book_does_not_own(lineage: _Lineage) -> None:
    """A Spell of another Book is refused as not owned, before its index is read."""
    foreign = SimpleNamespace(spell_id="f1", _key=("default", "k-f1"))

    with pytest.raises(ValueError, match="'f1' is not owned by this conduit's Spellbook"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell=foreign)

    lineage.assert_nothing_started()


def test_notch_refuses_a_stale_spell_whose_id_now_names_another_object(lineage: _Lineage) -> None:
    """A Spell object the Book no longer holds under its spell_id (disposed, rebound) is refused as not owned."""
    stale = SimpleNamespace(spell_id="v2", _key=("default", "k-v2"), spell_index=lineage.index)

    with pytest.raises(ValueError, match="not owned"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell=stale)

    lineage.assert_nothing_started()


def test_notch_refuses_a_target_moved_to_another_index_inside_the_window(lineage: _Lineage) -> None:
    """
    The check runs again under the transaction's seal: a target moved after the first check is refused there.

    Contract:
        - The transaction ends as failed and the seam is never called.
    """
    def move_target(**_kwargs: object) -> None:
        """Simulate an index move that lands between the first check and admission."""
        lineage.v2.spell_index = lineage.other_index

    lineage.mediator.start_transaction.side_effect = move_target

    with pytest.raises(ValueError, match="'v2' belongs to another SpellIndex"):
        lineage.conduit.notch_spell(spell_index=lineage.index, spell_id="v2")

    lineage.mediator.end_transaction.assert_called_once_with(expected_type="notch", success=False)
    lineage.book._notch_spell.assert_not_called()
    Conduit._deactivate_borrowed_spell.assert_not_called()


def test_notch_by_id_on_an_automatic_conduit_raises_the_dynamic_mode_error(
    spellbook_stub: MagicMock,
    conduit_normal: Conduit,
) -> None:
    """The dynamic gate still comes first: an automatic conduit refuses a notch by spell_id with RuntimeError."""
    spellbook_stub._get_owned_spell = MagicMock()

    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.notch_spell(spell_index=SimpleNamespace(_id="i", selected_spell_id="a"), spell_id="v2")

    spellbook_stub._get_owned_spell.assert_not_called()
