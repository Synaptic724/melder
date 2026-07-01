import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig, BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration():
    """Reset the Aether singleton around each test for isolation."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _dynamic_configuration() -> SpellbookConfiguration:
    """Dynamic configuration suitable for conjure transactions."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _bound_spellbook() -> Spellbook:
    """A spellbook with one bound service, ready to conjure."""
    book = Spellbook(configuration=_dynamic_configuration())
    book.bind(spell=BasicService, existence=Existence.unique, permissions="create")
    return book


# ---------------------------------------------------------------------------
# CONJURE transaction -- genesis admission
# ---------------------------------------------------------------------------
def test_conjure_returns_a_conduit_with_an_id() -> None:
    """Conjure admits and returns a live conduit with a stable id."""
    conduit = _bound_spellbook().conjure(dynamic=True, name="c1")
    try:
        assert isinstance(conduit, Conduit)
        assert conduit.id
    finally:
        conduit.cleanup()


def test_conjure_twice_on_the_same_spellbook_raises() -> None:
    """A spellbook admits exactly one conjure; the second raises."""
    book = _bound_spellbook()
    conduit = book.conjure(dynamic=True, name="c1")
    try:
        with pytest.raises(RuntimeError):
            book.conjure(dynamic=True, name="c2")
    finally:
        conduit.cleanup()


def test_two_spellbooks_conjure_independently() -> None:
    """Different spellbooks conjure in parallel to distinct conduits."""
    book_a = Spellbook(configuration=_dynamic_configuration())
    book_a.bind(spell=BasicService, existence=Existence.unique, permissions="create")
    book_b = Spellbook(configuration=_dynamic_configuration())
    book_b.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    conduit_a = book_a.conjure(dynamic=True, name="a")
    conduit_b = book_b.conjure(dynamic=True, name="b")
    try:
        assert isinstance(conduit_a, Conduit)
        assert isinstance(conduit_b, Conduit)
        assert conduit_a.id != conduit_b.id
    finally:
        conduit_a.cleanup()
        conduit_b.cleanup()


def test_conjured_conduit_can_link_a_peer() -> None:
    """A freshly conjured conduit can immediately open a link transaction."""
    conduit_a = _bound_spellbook().conjure(dynamic=True, name="a")
    conduit_b = Spellbook(configuration=_dynamic_configuration()).conjure(dynamic=True, name="b")
    try:
        assert conduit_a.link(conduit_b) is True
        assert conduit_b in conduit_a.get_links()
    finally:
        conduit_b.cleanup()
        conduit_a.cleanup()


def test_conjure_with_multiple_bound_spells() -> None:
    """Conjure admits a spellbook carrying several bound spells."""
    book = Spellbook(configuration=_dynamic_configuration())
    book.bind(spell=BasicService, existence=Existence.unique, permissions="create")
    book.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    conduit = book.conjure(dynamic=True, name="multi")
    try:
        assert isinstance(conduit, Conduit)
        assert conduit.id
    finally:
        conduit.cleanup()


def test_conjure_then_contract_across_a_link() -> None:
    """End-to-end: conjure two conduits, link, and self-admit a contract add."""
    owner_book = _bound_spellbook()
    # Re-bind so we hold the id for the contract assertion.
    service_id = owner_book.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = Spellbook(configuration=_dynamic_configuration()).conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="read") is True
        snapshot = borrower.get_spells_in_contract_by_conduit(owner.id)
        inbound = [spell_id for spell_id, _spell in (snapshot.get("inbound", []) if snapshot else [])]
        assert service_id in inbound
    finally:
        borrower.cleanup()
        owner.cleanup()
