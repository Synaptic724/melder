"""Proof (melder_1, 2026-10-17): what `get_spell_by_id` answers for a parked version's spell_id.

The owner asked for a test proving that French's spell_id comes back as the English class. Each test builds
its own dynamic frame with caching off: a lender Book binds English under (Greeter, "greeter"), stages French
on the same SpellIndex with `bind_inactive` (which returns French's spell_id), and links to a borrower Book.

Read-only on src/: run it against a copy of src, from a scratch directory, e.g.
    PYTHONPATH=<copy>/src python -m pytest -p no:cacheprovider -v <this file>
"""
import re
from typing import Iterator, Protocol, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract English and French both implement."""

    def greet(self) -> str: ...


class English:
    """Version 1 of the greeter: bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2 of the greeter: staged parked on the same SpellIndex."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Note:
    """A plain spell so the borrower Book has something to conjure."""


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give every test a fresh Aether, rebound on Spellbook and Conduit, and reset it after."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _world(frame: str) -> Tuple[Spellbook, Conduit, Conduit, SpellIndex, str, str]:
    """Lender (English active, French parked on Greeter's index) linked to a borrower; caching off."""
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                       system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                  existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    greeter_index = lender_book.find_spell_by_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=greeter_index, spellframe=Greeter,
                                     binding_name="greeter", existence=Existence.many, permissions="create")
    lender.link(borrower)
    return lender_book, lender, borrower, greeter_index, english_id, french_id


def test_french_has_its_own_spell_id_and_its_own_spell_parked_in_the_lender_book() -> None:
    """The ids differ, and the Book really holds a French Spell under French's spell_id - parked."""
    lender_book, _lender, _borrower, greeter_index, english_id, french_id = _world("proof_ids")
    assert french_id != english_id
    assert greeter_index.selected_spell_id == english_id                 # English is the active version
    assert greeter_index.has_spell(english_id) and greeter_index.has_spell(french_id)
    assert lender_book._spells[greeter_index].spell is English          # the index's ACTIVE spell
    assert lender_book._spells_by_id[english_id].spell is English       # active versions, by spell_id
    assert french_id not in lender_book._spells_by_id
    assert lender_book._inactive_spells[french_id].spell is French      # parked versions, by spell_id
    assert lender_book._inactive_spells[french_id].spell_id == french_id


def test_get_spell_by_id_with_frenchs_spell_id_returns_the_english_spell() -> None:
    """Asked for French's spell_id, the lookup hands back the English Spell - the same object as English's."""
    lender_book, lender, borrower, _index, english_id, french_id = _world("proof_lookup")
    english_spell = lender_book.find_spell_by_id(english_id)
    for answer in (lender.get_spell_by_id(french_id),
                   borrower.get_spell_by_id(french_id),       # the call the contract check makes
                   lender_book.find_spell_by_id(french_id)):
        assert answer.spell is English
        assert answer.spell_id == english_id
        assert answer is english_spell


def test_find_spell_by_id_finds_french_then_returns_its_index_active_spell() -> None:
    """The method's own steps, one by one: it finds French parked, then returns its index's active spell."""
    lender_book, _lender, _borrower, greeter_index, _english_id, french_id = _world("proof_steps")
    assert lender_book._spells_by_id.get(french_id) is None             # step 1: not an active version
    parked = lender_book._inactive_spells.get(french_id)                 # step 2: found - the French Spell
    assert parked.spell is French
    assert parked.spell_index is greeter_index                           # step 3: its index
    assert lender_book._spells.get(greeter_index).spell is English      # step 4: that index's active spell
    assert lender_book.find_spell_by_id(french_id) is lender_book._spells.get(greeter_index)


def test_add_spell_to_contract_by_frenchs_spell_id_refuses_with_the_id_mismatch() -> None:
    """The borrower's grant check looks French's id up, gets English, compares the two ids and refuses."""
    _book, lender, borrower, _index, english_id, french_id = _world("proof_grant_id")
    expected = f"Provided spell_id '{french_id}' does not match inspected ID '{english_id}'."
    with pytest.raises(RuntimeError, match=re.escape(expected)):
        with borrower.transaction("link", conduits=[borrower, lender]):
            borrower.add_spell_to_contract(spell_id=french_id, conduit=lender, permissions="create")


def test_add_spell_to_contract_with_the_french_spell_object_is_accepted() -> None:
    """Control: the same grant given the French Spell object itself goes through."""
    lender_book, lender, borrower, _index, _english_id, french_id = _world("proof_grant_object")
    french_spell = lender_book._inactive_spells[french_id]
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_spell_to_contract(spell=french_spell, conduit=lender, permissions="create") is True


def test_after_the_notch_to_french_englishs_spell_id_returns_the_french_spell() -> None:
    """Whichever id you pass, you get the index's active spell: after a notch to French, English's id gives French."""
    lender_book, lender, _borrower, greeter_index, english_id, french_id = _world("proof_notch")
    lender.notch_spell(spell_index=greeter_index, spell_id=french_id)
    assert greeter_index.selected_spell_id == french_id
    assert lender.get_spell_by_id(english_id).spell is French
    assert lender.get_spell_by_id(english_id).spell_id == french_id
    assert lender.get_spell_by_id(french_id).spell is French
