"""
Integration tests -- SpellIndex NOTCH / ADD / REMOVE / DEACTIVATE lifecycle (deep).

Answers the behavioral questions directly:
- does notch change what melds?  (notch -> new active member resolves; old id parked)
- does notch reduce the index?   (NO -- both members stay; notch only repoints active)
- can we deactivate a spell?      (notch-away parks the outgoing spell: `_active` False)
- does the index reduce?          (remove_from_spell_index splits a member out -> source shrinks;
                                    add_to_spell_index moves a member -> source shrinks, target grows)

MULTI-MEMBER SETUP (the part to validate first -- it encodes these assumptions):
  1. bind an ACTIVE spell A  -> mints index I_A (active member = A).
  2. conduit.bind_inactive(spell=B, spell_index=I_A) -> creates B, parks it in _inactive_spells,
     and folds it onto I_A as an inactive member in one call (bind_inactive requires an existing
     target index; it cannot stand alone). I_A = {A, B}; no frame-signature claim for B.
  3. notch_spell(spell_index=I_A, spell=B) -> B becomes active, A is parked.
The parked B object is fetched with `book._get_owned_spell(id_b)` because `find_spell_by_id`
only scans the ACTIVE map.

Transactions are OUT OF SCOPE (another agent); the facades manage their own windows.
Runtime: Python 3.14t. The 3.10 sandbox cannot execute these -> user runs on 3.14t.
"""

import contextlib
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _ServiceA:
    def __init__(self) -> None:
        self.tag = "A"


class _ServiceB:
    def __init__(self) -> None:
        self.tag = "B"


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_notch_lifecycle() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


@contextlib.contextmanager
def _two_member_index() -> Iterator[tuple]:
    """
    Build a dynamic conduit whose index I_A has an ACTIVE member A and an inactive
    member B (staged via conduit.bind_inactive onto I_A). Yields:
    (book, conduit, id_a, id_b, index, spell_b).
    """
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=True, name="root")
    index = book.find_spell_by_id(id_a).spell_index
    id_b = conduit.bind_inactive(
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = book._get_owned_spell(id_b)  # parked -> not in the active map
    try:
        yield (book, conduit, id_a, id_b, index, spell_b)
    finally:
        conduit.cleanup()


# --- add_to_spell_index grows the target -----------------------------------

def test_add_to_spell_index_makes_index_multi_member():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        # After the move, both members live in one index; A is still the active head.
        assert index.spells_in_index() == {id_a, id_b}
        assert index.selected_spell_id == id_a


def test_add_to_spell_index_leaves_active_meld_unchanged():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        # B joined as INACTIVE, so meld still resolves the active member A.
        assert isinstance(conduit.meld(spell=id_a), _ServiceA)


# --- notch repoints the active member --------------------------------------

def test_notch_repoints_selected_member():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.notch_spell(spell_index=index, spell=spell_b)
        assert index.selected_spell_id == id_b


def test_notch_changes_what_melds():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.notch_spell(spell_index=index, spell=spell_b)
        # The index now resolves to B's class.
        assert isinstance(conduit.meld(spell=id_b), _ServiceB)


def test_notch_does_not_reduce_the_index():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.notch_spell(spell_index=index, spell=spell_b)
        # Notch only repoints the active head; both members remain.
        assert index.spells_in_index() == {id_a, id_b}


def test_notch_deactivates_the_outgoing_spell():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.notch_spell(spell_index=index, spell=spell_b)
        # A was the active member; after notch it is parked (deactivated).
        parked_a = book._get_owned_spell(id_a)
        assert parked_a is not None
        assert parked_a._active is False


def test_notch_activates_the_incoming_spell():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.notch_spell(spell_index=index, spell=spell_b)
        assert spell_b._active is True


def test_notch_back_restores_original_active():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.notch_spell(spell_index=index, spell=spell_b)
        # Notch back to A (now parked) -> A active again, B parked.
        spell_a = book._get_owned_spell(id_a)
        conduit.notch_spell(spell_index=index, spell=spell_a)
        assert index.selected_spell_id == id_a
        assert isinstance(conduit.meld(spell=id_a), _ServiceA)


# --- remove_from_spell_index reduces the index -----------------------------

def test_remove_from_spell_index_reduces_source_index():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        # B is an inactive member of the 2-member index; splitting it out shrinks I_A.
        conduit.remove_from_spell_index(spell=spell_b, source_index=index)
        assert index.spells_in_index() == {id_a}


def test_remove_from_spell_index_gives_spell_its_own_index():
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.remove_from_spell_index(spell=spell_b, source_index=index)
        # B now lives in a fresh index of its own (distinct identity from I_A).
        assert spell_b.spell_index is not index
        assert spell_b.spell_index.spells_in_index() == {id_b}
