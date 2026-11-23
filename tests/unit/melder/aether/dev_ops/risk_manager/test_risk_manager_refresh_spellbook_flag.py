"""Unit coverage for `RiskManager.refresh_spellbook_flag` (failed_late_bind_is_undone, #330, 2026-11-23).

A late-bind window holds its Book's validation flag up while it is open. When the window ends, the Book asks the
manager to recompute the flag from the conduit's risk sets - with no risk event - so the flag drops when nothing
else keeps it up. These tests run the manager against a real SpellSystemStates registry and a Book double that
records every flag write.
"""

from collections.abc import Iterator
from typing import Dict, List, Optional, Set, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.spellbook.bind.spell_index import SpellIndex


class _SpellDouble:
    """Spell double carrying what RiskManager reads from a Spell: its index and its registered state."""

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
    """Spellbook double: the maps `register_conduit` seeds from, and every flag value RiskManager writes."""

    def __init__(self) -> None:
        """Start with no spells and no recorded writes."""
        self._spells: Dict[SpellIndex, _SpellDouble] = {}
        self._contracted_spells: Dict[str, Dict[SpellIndex, _SpellDouble]] = {}
        self.flag_writes: List[bool] = []

    def _set_spellbook_validation_required(self, required: bool) -> None:
        """Record one write of the Book's validation flag."""
        self.flag_writes.append(required)


@pytest.fixture
def information_registry() -> Iterator[DevopsInformationRegistry]:
    """A live DevOps information registry, cleaned after the test."""
    registry = DevopsInformationRegistry("refresh-flag-frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def states(information_registry: DevopsInformationRegistry) -> Iterator[SpellSystemStates]:
    """A SpellSystemStates registry over a mocked frame, cleaned after the test."""
    frame = MagicMock()
    frame.name = "refresh-flag-frame"
    registry = SpellSystemStates(frame, information_registry)
    yield registry
    if not registry._cleaned:
        registry.cleanup()


@pytest.fixture
def risk_manager(
        states: SpellSystemStates,
        information_registry: DevopsInformationRegistry,
) -> Iterator[RiskManager]:
    """A RiskManager wired into the registry the way DevOpsManager wires it, cleaned after the test unless cleaned."""
    manager = RiskManager(states, information_registry)
    states.set_risk_manager(manager)
    yield manager
    if not states._cleaned:
        states.set_risk_manager(None)
    if not manager._cleaned:
        manager.cleanup()


def _bind(states: SpellSystemStates, book: _BookDouble, spell_id: str, *, resolvable: bool) -> _SpellDouble:
    """Register a lineage as bind does and put its spell in the Book."""
    index = SpellIndex(spell_id)
    states.register_index(index, "book", resolvable=resolvable)
    spell = _SpellDouble(index, states)
    book._spells[index] = spell
    return spell


def _risk(manager: RiskManager, conduit_id: str) -> Tuple[Set[str], Set[str]]:
    """Return the conduit's structural and resolution risk sets."""
    bucket = manager._conduit_states[conduit_id]
    return set(bucket.risky_structural), set(bucket.risky_resolution)


def test_a_refresh_writes_the_flag_the_risk_sets_call_for(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """With a risky lineage in the conduit the refresh writes True once more, and changes no risk set."""
    book = _BookDouble()
    risky = _bind(states, book, "risky-v1", resolvable=True)
    risk_manager.register_conduit("conduit-1", book)
    writes_before = len(book.flag_writes)
    risk_before = _risk(risk_manager, "conduit-1")

    risk_manager.refresh_spellbook_flag("conduit-1")

    assert book.flag_writes[writes_before:] == [True]
    assert _risk(risk_manager, "conduit-1") == risk_before
    assert risky.spell_index.id in risk_before[0]


def test_a_refresh_writes_false_when_nothing_keeps_the_flag_up(
        states: SpellSystemStates,
        risk_manager: RiskManager,
) -> None:
    """A conduit holding only a non-resolvable definition gets False: the window's end lets the flag drop."""
    book = _BookDouble()
    _bind(states, book, "definition-v1", resolvable=False)
    risk_manager.register_conduit("conduit-1", book)
    writes_before = len(book.flag_writes)

    risk_manager.refresh_spellbook_flag("conduit-1")

    assert book.flag_writes[writes_before:] == [False]


@pytest.mark.parametrize("conduit_id", ["", "conduit-unknown"], ids=["empty-id", "no-bucket"])
def test_a_refresh_of_no_registered_conduit_writes_nothing(
        risk_manager: RiskManager,
        conduit_id: str,
) -> None:
    """An empty id, or a conduit the manager never registered, is a no-op."""
    book = _BookDouble()
    risk_manager.register_conduit("conduit-1", book)
    writes_before = len(book.flag_writes)

    risk_manager.refresh_spellbook_flag(conduit_id)

    assert len(book.flag_writes) == writes_before


def test_a_refresh_after_cleanup_raises(states: SpellSystemStates, risk_manager: RiskManager) -> None:
    """A cleaned manager refuses the refresh."""
    states.set_risk_manager(None)
    risk_manager.cleanup()

    with pytest.raises(RuntimeError):
        risk_manager.refresh_spellbook_flag("conduit-1")
