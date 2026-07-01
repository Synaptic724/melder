"""
Integration tests -- owner-op GUARDS + responsibility split (areas A4/A8, E2).

Error-path coverage for the index operations plus the public/private surface
contract:
- A8: notch / add_to_spell_index / remove_from_spell_index raise in NON-dynamic mode.
- A4: the seams reject illegal moves -- moving an ACTIVE spell (must notch away first)
      and separating a SOLE member (must use cleanup_spell instead).
- E2: the index operations are PRIVATE on the Spellbook (`_notch_spell` etc.) and
      PUBLIC only on the Conduit facade (`notch_spell` etc.).

Transactions are OUT OF SCOPE. Runtime: Python 3.14t; the 3.10 sandbox cannot run
these -> user runs on 3.14t.
"""

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
        pass


class _ServiceB:
    def __init__(self) -> None:
        pass


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_guards() -> None:
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


# --- A8 dynamic-mode gating ------------------------------------------------

def test_notch_raises_in_non_dynamic_mode():
    book = _make_spellbook()
    spell_id = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=False, name="static")
    try:
        spell = book.find_spell_by_id(spell_id)
        with pytest.raises(RuntimeError):
            conduit.notch_spell(spell_index=spell.spell_index, spell=spell)
    finally:
        conduit.cleanup()


def test_add_to_spell_index_raises_in_non_dynamic_mode():
    book = _make_spellbook()
    spell_id = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=False, name="static")
    try:
        spell = book.find_spell_by_id(spell_id)
        with pytest.raises(RuntimeError):
            conduit.add_to_spell_index(spell=spell, target_index=spell.spell_index)
    finally:
        conduit.cleanup()


def test_remove_from_spell_index_raises_in_non_dynamic_mode():
    book = _make_spellbook()
    spell_id = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=False, name="static")
    try:
        spell = book.find_spell_by_id(spell_id)
        with pytest.raises(RuntimeError):
            conduit.remove_from_spell_index(spell=spell, source_index=spell.spell_index)
    finally:
        conduit.cleanup()


# --- A4 op guards (dynamic mode) -------------------------------------------

def test_add_to_spell_index_rejects_active_spell():
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    id_b = book.bind(spell=_ServiceB, existence=Existence.unique, permissions="create", binding_name="b")
    conduit = book.conjure(dynamic=True, name="root")
    try:
        active_a = book.find_spell_by_id(id_a)          # active -> not in _inactive_spells
        target_index = book.find_spell_by_id(id_b).spell_index
        with pytest.raises(RuntimeError):
            conduit.add_to_spell_index(spell=active_a, target_index=target_index)
    finally:
        conduit.cleanup()


def test_remove_from_spell_index_rejects_active_spell():
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=True, name="root")
    try:
        active_a = book.find_spell_by_id(id_a)
        with pytest.raises(RuntimeError):
            conduit.remove_from_spell_index(spell=active_a, source_index=active_a.spell_index)
    finally:
        conduit.cleanup()


def test_remove_from_spell_index_rejects_sole_member():
    book = _make_spellbook()
    # In the index model an inactive spell is never the sole member (the active
    # member is always present alongside it), so the only sole member is the
    # ACTIVE one; removing it is rejected (it would empty the index).
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=True, name="root")
    try:
        spell_a = book.find_spell_by_id(id_a)
        with pytest.raises(RuntimeError):
            conduit.remove_from_spell_index(spell=spell_a, source_index=spell_a.spell_index)
    finally:
        conduit.cleanup()


# --- E2 responsibility split (public facade vs private seam) ---------------

def test_index_ops_are_private_on_spellbook():
    # The owner-op seams are internal; the Spellbook exposes no public notch/add/remove.
    assert hasattr(Spellbook, "_notch_spell")
    assert hasattr(Spellbook, "_add_to_spell_index")
    assert hasattr(Spellbook, "_remove_from_spell_index")
    assert not hasattr(Spellbook, "notch_spell")
    assert not hasattr(Spellbook, "add_to_spell_index")
    assert not hasattr(Spellbook, "remove_from_spell_index")


def test_index_ops_are_public_on_conduit():
    # The public surface is the Conduit facade only.
    assert hasattr(Conduit, "notch_spell")
    assert hasattr(Conduit, "add_to_spell_index")
    assert hasattr(Conduit, "remove_from_spell_index")
    assert hasattr(Conduit, "add_index_to_contract")
    assert hasattr(Conduit, "remove_index_from_contract")
