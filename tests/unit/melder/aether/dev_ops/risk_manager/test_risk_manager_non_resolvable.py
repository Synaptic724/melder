"""Unit coverage for RiskManager's handling of `SpellState.non_resolvable` (meld_state_gate_2026_10_15).

RiskManager keeps tracking every lineage's risk exactly as before; only the Book's validation flag ignores the risk of
a lineage whose state carries `non_resolvable` - its selected version is a resolvable=False definition, refused at every
meld door before the gate. These tests run the manager against a real SpellSystemStates registry, so the flag the
registry writes at registration is the flag the manager reads when it distils the Book flag.
"""

import time
from collections.abc import Iterator
from typing import Dict, List, Optional, Set, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex


class _SpellDouble:
    """
    Spell double carrying what RiskManager reads from a Spell.

    Purpose:
        A real SpellIndex (lineage id and selected version id) and the lineage's state read from the registry, as
        `Spell.system_state` reads it, so the manager sees the registry's validity and flags.
    """

    def __init__(self, spell_index: SpellIndex, states: SpellSystemStates) -> None:
        """Bind the index and the registry the state is read from."""
        self._cleaned: bool = False
        self.spell_index: SpellIndex = spell_index
        self._states: SpellSystemStates = states

    @property
    def system_state(self) -> Optional[SpellSystemState]:
        """The lineage's registered state, or None when it has none."""
        return self._states.get_by_index_id(self.spell_index.id)


class _BookDouble:
    """
    Spellbook double: the maps `register_conduit` seeds from, and every flag value RiskManager writes.

    Purpose:
        Record each `_set_spellbook_validation_required` call so a test can assert the flag and how often it was
        written.
    """

    def __init__(self) -> None:
        """Start with no spells and no recorded writes."""
        self._spells: Dict[SpellIndex, _SpellDouble] = {}
        self._contracted_spells: Dict[str, Dict[SpellIndex, _SpellDouble]] = {}
        self.flag_writes: List[bool] = []

    def _set_spellbook_validation_required(self, required: bool) -> None:
        """Record one write of the Book's validation flag."""
        self.flag_writes.append(required)

    @property
    def validation_required(self) -> Optional[bool]:
        """The last value written, or None before any write."""
        return self.flag_writes[-1] if self.flag_writes else None


@pytest.fixture
def information_registry() -> Iterator[DevopsInformationRegistry]:
    """A live DevOps information registry, cleaned after the test."""
    registry = DevopsInformationRegistry("non-resolvable-risk-frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def states(information_registry: DevopsInformationRegistry) -> Iterator[SpellSystemStates]:
    """A SpellSystemStates registry over a mocked frame, cleaned after the test."""
    frame = MagicMock()
    frame.name = "non-resolvable-risk-frame"
    registry = SpellSystemStates(frame, information_registry)
    yield registry
    if not registry._cleaned:
        registry.cleanup()


@pytest.fixture
def risk_manager(
        states: SpellSystemStates,
        information_registry: DevopsInformationRegistry,
) -> Iterator[RiskManager]:
    """A RiskManager wired into the registry the way DevOpsManager wires it, cleaned after the test."""
    manager = RiskManager(states, information_registry)
    states.set_risk_manager(manager)
    yield manager
    if not states._cleaned:
        states.set_risk_manager(None)
    manager.cleanup()


def _bind(states: SpellSystemStates, book: _BookDouble, spell_id: str, *, resolvable: bool) -> _SpellDouble:
    """Register a lineage as bind does (`register_index` with the capability) and put its spell in the Book."""
    index = SpellIndex(spell_id)
    states.register_index(index, "book", resolvable=resolvable)
    spell = _SpellDouble(index, states)
    book._spells[index] = spell
    return spell


def _risk(manager: RiskManager, conduit_id: str) -> Tuple[Set[str], Set[str]]:
    """Return the conduit's structural and resolution risk sets (the tracking the change must leave alone)."""
    bucket = manager._conduit_states[conduit_id]
    return set(bucket.risky_structural), set(bucket.risky_resolution)


def test_a_non_resolvable_lineage_alone_leaves_the_book_flag_down_while_its_risk_is_kept(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A gated, never-resolved definition is still tracked on both axes but does not hold the Book flag up."""
    book = _BookDouble()
    definition = _bind(states, book, "definition-v1", resolvable=False)

    risk_manager.register_conduit("conduit-1", book)

    lineage = definition.spell_index.id
    assert book.validation_required is False
    assert _risk(risk_manager, "conduit-1") == ({lineage}, {lineage})


def test_an_unflagged_risky_lineage_still_raises_the_book_flag(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A resolvable lineage that needs validation raises the flag beside a flagged one."""
    book = _BookDouble()
    _bind(states, book, "definition-v1", resolvable=False)
    _bind(states, book, "implementation-v1", resolvable=True)

    risk_manager.register_conduit("conduit-1", book)

    assert book.validation_required is True


def test_a_registration_that_clears_the_flag_raises_the_book_flag_at_the_gated_event(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A validated definition notched to a resolvable version counts again at once, with no register_spell."""
    book = _BookDouble()
    definition = _bind(states, book, "definition-v1", resolvable=False)
    states.get_by_index_id(definition.spell_index.id).clear_dirty(time.time())
    risk_manager.register_conduit("conduit-1", book)
    assert book.validation_required is False

    definition.spell_index.update("implementation-v2")
    states.register_index(definition.spell_index, "book", resolvable=True)

    assert book.validation_required is True


def test_a_lineage_already_gated_counts_again_in_a_borrower_after_a_notch_back(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A notch back from a never-validated False version raises a borrower's flag although the borrower is not told."""
    owner_book = _BookDouble()
    borrower_book = _BookDouble()
    spell = _bind(states, owner_book, "implementation-v1", resolvable=True)
    spell.spell_index.update("definition-v2")
    states.register_index(spell.spell_index, "book", resolvable=False)
    borrower_book._contracted_spells["owner-conduit"] = {spell.spell_index: spell}
    risk_manager.register_conduit("owner-conduit", owner_book)
    risk_manager.register_conduit("borrower-conduit", borrower_book)
    assert (owner_book.validation_required, borrower_book.validation_required) == (False, False)

    # The notch back, as `_apply_notch` does it: re-register the index, then register_spell for the owner only.
    spell.spell_index.update("implementation-v1")
    states.register_index(spell.spell_index, "book", resolvable=True)
    risk_manager.register_spell("owner-conduit", spell)

    assert owner_book.validation_required is True
    assert borrower_book.validation_required is True


def test_a_registration_to_a_non_resolvable_version_lowers_the_book_flag(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A validated implementation notched to a definition stops holding the flag up."""
    book = _BookDouble()
    implementation = _bind(states, book, "implementation-v1", resolvable=True)
    states.get_by_index_id(implementation.spell_index.id).clear_dirty(time.time())
    risk_manager.register_conduit("conduit-1", book)
    assert book.validation_required is True

    implementation.spell_index.update("definition-v2")
    states.register_index(implementation.spell_index, "book", resolvable=False)

    lineage = implementation.spell_index.id
    assert book.validation_required is False
    assert _risk(risk_manager, "conduit-1") == ({lineage}, {lineage})


def test_a_resolution_verdict_on_a_resolvable_lineage_still_lowers_the_flag(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """Valid verdicts on the resolvable lineage leave only the flagged one, and the flag goes down."""
    book = _BookDouble()
    _bind(states, book, "definition-v1", resolvable=False)
    implementation = _bind(states, book, "implementation-v1", resolvable=True)
    risk_manager.register_conduit("conduit-1", book)
    assert book.validation_required is True

    states.get_by_index_id(implementation.spell_index.id).clear_dirty(time.time())
    states.set_conduit_spell_validity("conduit-1", "implementation-v1", SpellValidity.valid)

    assert book.validation_required is False


def test_a_spell_key_still_counts_beside_a_flagged_lineage(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A resolution verdict the manager cannot fold onto a lineage still raises the flag."""
    book = _BookDouble()
    _bind(states, book, "definition-v1", resolvable=False)
    risk_manager.register_conduit("conduit-1", book)
    assert book.validation_required is False

    risk_manager.on_resolution_validity_change("conduit-1", "unregistered-version", SpellValidity.invalid)

    assert book.validation_required is True


def test_a_removed_flagged_lineage_counts_until_it_is_unregistered(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A lineage whose state is gone counts as risky until RiskManager drops it, as before the change."""
    book = _BookDouble()
    definition = _bind(states, book, "definition-v1", resolvable=False)
    risk_manager.register_conduit("conduit-1", book)
    assert book.validation_required is False

    states.unregister_index(definition.spell_index)
    assert book.validation_required is True

    risk_manager.unregister_spell("conduit-1", definition)
    assert book.validation_required is False


def test_register_conduit_writes_the_book_flag_once(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """Seeding a conduit refreshes once at the end, not once per seeded spell."""
    book = _BookDouble()
    _bind(states, book, "definition-v1", resolvable=False)
    _bind(states, book, "implementation-v1", resolvable=True)
    _bind(states, book, "implementation-v2", resolvable=True)

    risk_manager.register_conduit("conduit-1", book)

    assert book.flag_writes == [True]


def test_register_spell_still_writes_the_book_flag_once(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A single registration refreshes once, as before."""
    book = _BookDouble()
    implementation = _bind(states, book, "implementation-v1", resolvable=True)
    risk_manager.register_conduit("conduit-1", book)
    book.flag_writes.clear()

    risk_manager.register_spell("conduit-1", implementation)

    assert book.flag_writes == [True]


def test_register_spell_for_an_unknown_conduit_writes_nothing(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A registration that tracks nothing refreshes nothing, as before."""
    book = _BookDouble()
    implementation = _bind(states, book, "implementation-v1", resolvable=True)

    risk_manager.register_spell("unknown-conduit", implementation)

    assert book.flag_writes == []
