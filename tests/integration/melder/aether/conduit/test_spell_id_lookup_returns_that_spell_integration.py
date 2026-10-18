"""
Integration tests - a lookup by spell_id returns the spell that owns that spell_id (0.2.8253).

The owner's rule (2026-10-17): a spell_id - the SHA `bind` and `bind_inactive` return - and a SpellIndex are
separate things. Sharing an index follows whatever spell the index has active; sharing a spell by its spell_id is
exactly that spell. So `Conduit.get_spell_by_spell_id`, `Conduit.get_spell_permissions` and the grant and ungrant of
a version by its spell_id answer with exactly that spell, active or parked, and only a lookup by index answers with
the spell an index has active. Until 0.2.8253 the lookups were `Conduit.get_spell_by_id` and
`Spellbook.find_spell_by_id`, which found a parked spell under its spell_id and returned its index's active spell
instead, so French's spell_id gave English; both were renamed, with no alias.

A transfer and a dependency grant work on the spell an index has active, and keep their answers: they look the
spell up by spell_id and then ask its index. The guards at the end pass before and after 0.2.8253.

Each test builds its own dynamic frame with caching off: a lender Book binds English under (Greeter, "greeter")
and the consumer Polite, conjures, stages French on Greeter's index with `bind_inactive` and links a borrower.
"""

from collections.abc import Iterator
from typing import Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract English and French both implement."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class English:
    """Greeter version 1: bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Greeter version 2: staged parked on the same SpellIndex."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Polite:
    """A consumer of Greeter, compiled at conjure against the version active then (English)."""

    def __init__(self, greeter: Greeter) -> None:
        """Keep the injected greeter."""
        self.greeter = greeter


class Note:
    """A plain spell so the borrower Book has something to conjure."""


class _World:
    """
    A lender (English active, French parked on Greeter's index, Polite) linked to a borrower; caching off.

    Attributes are the two Books, their root conduits, Greeter's index and the three spell_ids.
    """

    def __init__(self, frame: str, *, french_permissions: str = "create", link: bool = True) -> None:
        """Build the world in its own frame; `french_permissions` is the permission French is bound with."""
        self.lender_book = Spellbook(
            aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults(),
        )
        self.lender_book.configure_aether_frame(
            system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
        )
        self.borrower_book = Spellbook(
            aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults(),
        )
        self.english_id: str = self.lender_book.bind(
            spell=English, spellframe=Greeter, binding_name="greeter",
            existence=Existence.many, permissions="create",
        )
        self.polite_id: str = self.lender_book.bind(spell=Polite, existence=Existence.many, permissions="create")
        self.borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
        self.lender: Conduit = self.lender_book.conjure(dynamic=True, name="lender")
        self.borrower: Conduit = self.borrower_book.conjure(dynamic=True, name="borrower")
        # The Book's active map, so the world builds on the trees before and after the rename.
        self.index: SpellIndex = self.lender_book._spells_by_id[self.english_id].spell_index
        self.french_id: str = self.lender.bind_inactive(
            spell=French, spell_index=self.index, spellframe=Greeter, binding_name="greeter",
            existence=Existence.many, permissions=french_permissions,
        )
        if link:
            self.lender.link(self.borrower)


@pytest.fixture(autouse=True)
def _fresh_aether() -> Iterator[None]:
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


def test_get_spell_by_spell_id_with_a_parked_spell_id_returns_that_parked_spell() -> None:
    """French's spell_id gives the French Spell - on the lender that owns it and on the linked borrower."""
    world = _World("lookup_parked")
    for conduit in (world.lender, world.borrower):
        french = conduit.get_spell_by_spell_id(world.french_id)
        assert french is not None
        assert french.spell is French
        assert french.spell_id == world.french_id
        english = conduit.get_spell_by_spell_id(world.english_id)
        assert english is not None
        assert english.spell is English
        assert english.spell_id == world.english_id


def test_after_a_notch_each_spell_id_still_returns_its_own_spell() -> None:
    """A notch moves which spell the index has active; it never changes what a spell_id names."""
    world = _World("lookup_after_notch")
    world.lender.notch_spell(spell_index=world.index, spell_id=world.french_id)
    assert world.index.selected_spell_id == world.french_id
    english = world.lender.get_spell_by_spell_id(world.english_id)
    french = world.lender.get_spell_by_spell_id(world.french_id)
    assert english is not None and english.spell is English
    assert french is not None and french.spell is French


def test_get_spell_permissions_returns_the_permissions_that_spell_was_bound_with() -> None:
    """French bound "read" beside English bound "create": each spell_id answers its own version's permissions."""
    world = _World("lookup_permissions", french_permissions="read")
    assert world.lender.get_spell_permissions(world.french_id) == "read"
    assert world.lender.get_spell_permissions(world.english_id) == "create"


def test_an_unknown_spell_id_still_raises_value_error() -> None:
    """No conduit claims the id, so the `get_*` lookup raises."""
    world = _World("lookup_unknown")
    with pytest.raises(ValueError):
        world.lender.get_spell_by_spell_id("no-such-spell-id")


def test_the_old_lookup_names_are_gone() -> None:
    """The renamed lookups keep no alias (the owner's no-fallback rule): the old names raise AttributeError."""
    world = _World("lookup_old_names", link=False)
    with pytest.raises(AttributeError):
        world.lender.get_spell_by_id(world.english_id)
    with pytest.raises(AttributeError):
        world.lender_book.find_spell_by_id(world.english_id)


def test_add_spell_to_contract_by_the_parked_spell_id_grants_that_spell_parked() -> None:
    """
    The borrower takes French by its spell_id; like a grant of the French Spell, the copy waits parked.

    The lender's outbound listing names the French Spell it granted. (The borrower's inbound listing resolves a
    parked copy through `Spellbook._find_contracted_spell_by_id`, which still answers by index and finds no active
    copy here; that lookup waits for the owner with the other contract-side lookups.)
    """
    world = _World("lookup_grant_by_id")
    with world.borrower.transaction("link", conduits=[world.borrower, world.lender]):
        assert world.borrower.add_spell_to_contract(
            spell_id=world.french_id, conduit=world.lender, permissions="create",
        ) is True
    outbound = dict(world.lender.get_spells_in_contract_by_conduit(world.borrower._id)["outbound"])
    assert set(outbound) == {world.french_id}
    assert outbound[world.french_id].spell is French
    parked_copies = world.borrower_book._inactive_contracted_spells[world.lender._id]
    assert parked_copies[world.french_id].spell is French


def test_remove_spell_from_contract_by_the_parked_spell_id_removes_that_grant() -> None:
    """A French grant is released by French's spell_id, and the borrower's parked copy goes with it."""
    world = _World("lookup_ungrant_by_id")
    french_spell = world.lender.get_spell_by_spell_id(world.french_id)
    with world.borrower.transaction("link", conduits=[world.borrower, world.lender]):
        assert world.borrower.add_spell_to_contract(
            spell=french_spell, conduit=world.lender, permissions="create",
        ) is True
    with world.borrower.transaction("link", conduits=[world.borrower, world.lender]):
        assert world.borrower.remove_spell_from_contract(
            spell_id=world.french_id, conduit=world.lender,
        ) is True
    parked_copies = world.borrower_book._inactive_contracted_spells.get(world.lender._id, {})
    assert world.french_id not in parked_copies


def test_guard_a_transfer_by_the_parked_spell_id_moves_the_whole_index_unchanged() -> None:
    """A transfer moves the index that holds the spell_id, with English still the active version."""
    world = _World("guard_transfer", link=False)
    world.lender.transfer_spell_ownership(spell=world.french_id, target_conduit=world.borrower)
    assert world.lender.get_conduit_by_spell_id(world.english_id) is world.borrower
    assert world.lender.get_conduit_by_spell_id(world.french_id) is world.borrower
    assert world.index.selected_spell_id == world.english_id
    assert world.borrower.meld(spell_id=world.english_id).greet() == "hello"


def test_guard_a_dependency_grant_after_the_notch_contracts_the_version_now_active() -> None:
    """Polite was compiled against English; after a notch to French its dependency grant contracts French."""
    world = _World("guard_dependency_grant")
    world.lender.notch_spell(spell_index=world.index, spell_id=world.french_id)
    with world.borrower.transaction("link", conduits=[world.borrower, world.lender]):
        assert world.borrower.add_spell_to_contract(
            spell_id=world.polite_id, conduit=world.lender, permissions="create", link_dependencies=True,
        ) is True
    inbound = dict(world.borrower.get_spells_in_contract_by_conduit(world.lender._id)["inbound"])
    assert set(inbound) == {world.polite_id, world.french_id}
    assert inbound[world.french_id].spell is French


def test_guard_a_transfer_with_dependencies_after_the_notch_moves_the_dependency_index() -> None:
    """Polite's transfer brings Greeter's index along - French still active, English still parked."""
    world = _World("guard_transfer_dependencies", link=False)
    world.lender.notch_spell(spell_index=world.index, spell_id=world.french_id)
    world.lender.transfer_spell_ownership(
        spell=world.polite_id, target_conduit=world.borrower, include_dependencies=True,
    )
    assert world.lender.get_conduit_by_spell_id(world.polite_id) is world.borrower
    assert world.lender.get_conduit_by_spell_id(world.french_id) is world.borrower
    assert world.lender.get_conduit_by_spell_id(world.english_id) is world.borrower
    assert world.index.selected_spell_id == world.french_id
