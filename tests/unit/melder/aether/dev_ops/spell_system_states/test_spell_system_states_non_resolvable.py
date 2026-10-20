"""Unit coverage for `SpellState.non_resolvable` in the spell-state model (meld_state_gate_2026_10_15).

A lineage whose selected version is bound resolvable=False owes no resolution verdict. `register_index` records that
on the lineage's `SpellSystemState` from the capability its caller passes, before it gates the index, so the
RiskManager callback that the gate publishes already sees it. Validation never clears it, and it changes neither the
gate nor any other flag. The registry also publishes the flagged lineages as one immutable set,
`non_resolvable_index_ids`, replaced whole where the flag changes and read by RiskManager without a lock.
"""

import time
from collections.abc import Iterator
from typing import List, Optional, Tuple, Union
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex


class _FlagReadingRiskManager:
    """
    Risk-manager double that reads the lineage's `non_resolvable` flag and the published set in every callback.

    Purpose:
        Prove the ordering contract of `register_index`: the capability and the published set are written
        before the gate publishes, so a reader that runs inside the published callback already sees the flag
        and the set membership that match the selection.
    """

    def __init__(self, states: SpellSystemStates) -> None:
        """Bind the registry the callbacks read through and start with no recorded events."""
        self.states: SpellSystemStates = states
        self.seen: List[Tuple[str, Optional[SpellValidity], bool, bool]] = []

    def on_structural_validity_change(self, lineage_id: str, validity: Optional[SpellValidity]) -> None:
        """Record the event with the flag and the published-set membership the registry reports then."""
        self.seen.append((
            lineage_id,
            validity,
            self.states.index_has_flag(lineage_id, SpellState.non_resolvable),
            lineage_id in self.states.non_resolvable_index_ids,
        ))

    def on_resolution_validity_change(
            self,
            conduit_id: str,
            spell_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """Resolution events are not part of these cases."""


@pytest.fixture
def information_registry() -> Iterator[DevopsInformationRegistry]:
    """A live DevOps information registry, cleaned after the test."""
    registry = DevopsInformationRegistry("non-resolvable-frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def states(information_registry: DevopsInformationRegistry) -> Iterator[SpellSystemStates]:
    """A SpellSystemStates registry over a mocked frame, cleaned after the test."""
    frame = MagicMock()
    frame.name = "non-resolvable-frame"
    registry = SpellSystemStates(frame, information_registry)
    yield registry
    if not registry._cleaned:
        registry.cleanup()


@pytest.fixture
def watcher(states: SpellSystemStates) -> _FlagReadingRiskManager:
    """A flag-reading risk-manager double wired into the registry."""
    manager = _FlagReadingRiskManager(states)
    states.set_risk_manager(manager)
    return manager


def _snapshot(state: SpellSystemState) -> Tuple[SpellValidity, Optional[SpellStateChangeReason], bool, Optional[float]]:
    """Return the gate-side fields that a flag-only update must leave alone."""
    return state.validity, state.change_reason, state.transitively_dirty, state.last_validated_at


def test_update_flags_changes_only_the_flags_and_publishes_nothing() -> None:
    """Adding and removing a flag leaves validity, reason, dirt and timestamp as they were, with no callback."""
    state = SpellSystemState("lineage", "version-a")
    manager = MagicMock()
    state._set_risk_manager(manager)
    before = _snapshot(state)

    state.update_flags(flags_to_add=[SpellState.non_resolvable, None])
    assert state.has_flag(SpellState.non_resolvable) is True
    assert state.has_flag(SpellState.new_index) is True
    assert _snapshot(state) == before

    state.update_flags(flags_to_remove=[SpellState.non_resolvable, None])
    assert state.has_flag(SpellState.non_resolvable) is False
    assert _snapshot(state) == before
    manager.on_structural_validity_change.assert_not_called()


def test_update_flags_adds_before_it_removes_like_set_validity() -> None:
    """A flag named in both lists ends removed: the add-then-remove order `set_validity` applies."""
    state = SpellSystemState("lineage", "version-a")

    state.update_flags(flags_to_add=[SpellState.non_resolvable], flags_to_remove=[SpellState.non_resolvable])

    assert state.has_flag(SpellState.non_resolvable) is False


def test_update_flags_is_idempotent() -> None:
    """Adding a present flag or removing an absent one changes nothing."""
    state = SpellSystemState("lineage", "version-a")

    state.update_flags(flags_to_add=[SpellState.non_resolvable])
    state.update_flags(flags_to_add=[SpellState.non_resolvable])
    assert state.flags == {SpellState.new_index, SpellState.non_resolvable}

    state.update_flags(flags_to_remove=[SpellState.non_resolvable])
    state.update_flags(flags_to_remove=[SpellState.non_resolvable])
    assert state.flags == {SpellState.new_index}


def test_update_flags_and_has_flag_refuse_a_cleaned_state() -> None:
    """A cleaned state raises the standard use-after-clean error instead of an attribute error."""
    state = SpellSystemState("lineage", "version-a")
    state.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        state.update_flags(flags_to_add=[SpellState.non_resolvable])
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        state.has_flag(SpellState.non_resolvable)


def test_validation_keeps_the_non_resolvable_declaration() -> None:
    """`clear_dirty` clears only the topology flags; the declaration survives a successful validation."""
    state = SpellSystemState("lineage", "version-a")
    state.update_flags(flags_to_add=[SpellState.non_resolvable])
    state.mark_structural_change()

    state.clear_dirty(time.time())

    assert state.validity is SpellValidity.valid
    assert state.has_flag(SpellState.structure_changed) is False
    assert state.has_flag(SpellState.new_index) is False
    assert state.has_flag(SpellState.non_resolvable) is True


def test_register_index_flags_a_non_resolvable_selection_before_the_gate_publishes(
        states: SpellSystemStates,
        watcher: _FlagReadingRiskManager,
) -> None:
    """The gated event of a resolvable=False registration already reads the flag through the registry."""
    index = SpellIndex("definition-v1")

    state = states.register_index(index, "book", resolvable=False)

    assert watcher.seen == [(index.id, SpellValidity.gated, True, True)]
    assert state.has_flag(SpellState.non_resolvable) is True


def test_register_index_still_gates_a_non_resolvable_selection(states: SpellSystemStates) -> None:
    """The declaration changes nothing on the gate: the index is gated and dirty like any registration."""
    index = SpellIndex("definition-v1")

    state = states.register_index(index, "book", resolvable=False)

    assert state.validity is SpellValidity.gated
    assert state.change_reason is SpellStateChangeReason.register_or_rebind
    assert state.has_flag(SpellState.structure_changed) is True
    assert states.consume_dirty_indexes() == [index.id]


def test_register_index_clears_the_flag_for_a_resolvable_selection_before_the_gate_publishes(
        states: SpellSystemStates,
        watcher: _FlagReadingRiskManager,
) -> None:
    """A notch to a resolvable version removes the flag before its gated event publishes."""
    index = SpellIndex("definition-v1")
    states.register_index(index, "book", resolvable=False).clear_dirty(time.time())
    watcher.seen.clear()

    index.update("implementation-v2")
    states.register_index(index, "book", resolvable=True)

    assert watcher.seen == [(index.id, SpellValidity.gated, False, False)]


def test_register_index_without_a_capability_keeps_the_flag_while_the_selection_is_unchanged(
        states: SpellSystemStates,
) -> None:
    """A re-registration of the same selection (a transfer's disable step) keeps the declaration."""
    index = SpellIndex("definition-v1")
    states.register_index(index, "book", resolvable=False)

    states.register_index(index, "book")

    assert states.index_has_flag(index.id, SpellState.non_resolvable) is True


def test_register_index_without_a_capability_clears_the_flag_when_the_selection_changed(
        states: SpellSystemStates,
) -> None:
    """An unknown capability for a new selection never keeps an exclusion recorded for the old one."""
    index = SpellIndex("definition-v1")
    states.register_index(index, "book", resolvable=False)

    index.update("unknown-capability-v2")
    states.register_index(index, "book")

    assert states.index_has_flag(index.id, SpellState.non_resolvable) is False


def test_register_index_without_a_capability_leaves_a_new_lineage_unflagged(states: SpellSystemStates) -> None:
    """A first registration with no capability is today's registration."""
    index = SpellIndex("plain-v1")

    states.register_index(index, "book")

    assert states.index_has_flag(index.id, SpellState.non_resolvable) is False


def test_register_index_with_true_on_a_new_lineage_leaves_it_unflagged(states: SpellSystemStates) -> None:
    """A resolvable first registration is unflagged."""
    index = SpellIndex("plain-v1")

    states.register_index(index, "book", resolvable=True)

    assert states.index_has_flag(index.id, SpellState.non_resolvable) is False


@pytest.mark.parametrize("capability", [0, 1, "False", []])
def test_register_index_refuses_a_non_bool_capability_and_registers_nothing(
        states: SpellSystemStates,
        capability: Union[int, str, list],
) -> None:
    """Only None or a bool is a capability; anything else raises before the registry changes."""
    index = SpellIndex("definition-v1")

    with pytest.raises(TypeError, match="Spell.resolvable"):
        states.register_index(index, "book", resolvable=capability)

    assert states.get_by_index_id(index.id) is None
    assert states.consume_dirty_indexes() == []


def test_unregister_index_takes_the_flag_with_the_state(states: SpellSystemStates) -> None:
    """A removed lineage reports no flag: the declaration lives and dies with its state."""
    index = SpellIndex("definition-v1")
    states.register_index(index, "book", resolvable=False)

    states.unregister_index(index)

    assert states.get_by_index_id(index.id) is None
    assert states.index_has_flag(index.id, SpellState.non_resolvable) is False
    assert index.id not in states.non_resolvable_index_ids


def test_index_has_flag_answers_false_for_empty_and_unknown_ids(states: SpellSystemStates) -> None:
    """An empty id or an id with no registered state carries no flag."""
    assert states.index_has_flag("", SpellState.non_resolvable) is False
    assert states.index_has_flag("no-such-lineage", SpellState.non_resolvable) is False


def test_index_has_flag_reads_each_flag_independently(states: SpellSystemStates) -> None:
    """The probe answers for the flag it is asked about, not for the lineage as a whole."""
    index = SpellIndex("definition-v1")
    states.register_index(index, "book", resolvable=False)

    assert states.index_has_flag(index.id, SpellState.non_resolvable) is True
    assert states.index_has_flag(index.id, SpellState.structure_changed) is True
    assert states.index_has_flag(index.id, SpellState.transfer_in_progress) is False


def test_index_has_flag_refuses_a_cleaned_registry(states: SpellSystemStates) -> None:
    """A cleaned registry raises the standard use-after-clean error."""
    states.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        states.index_has_flag("any-lineage", SpellState.non_resolvable)


def test_update_flags_reports_whether_the_flag_set_changed() -> None:
    """The result is True exactly when a flag was added or removed."""
    state = SpellSystemState("lineage", "version-a")

    assert state.update_flags(flags_to_add=[SpellState.non_resolvable]) is True
    assert state.update_flags(flags_to_add=[SpellState.non_resolvable]) is False
    assert state.update_flags(flags_to_remove=[SpellState.non_resolvable]) is True
    assert state.update_flags(flags_to_remove=[SpellState.non_resolvable]) is False
    assert state.update_flags() is False


def test_republish_validity_publishes_the_current_validity_and_changes_nothing() -> None:
    """The stand-in publication sends the stored validity once and leaves the state as it was."""
    state = SpellSystemState("lineage", "version-a")
    manager = MagicMock()
    state._set_risk_manager(manager)
    state.mark_structural_change()
    manager.reset_mock()
    before = (_snapshot(state), state.flags)

    state._republish_validity()

    manager.on_structural_validity_change.assert_called_once_with("lineage", SpellValidity.gated)
    assert (_snapshot(state), state.flags) == before


def test_republish_validity_without_a_risk_manager_does_nothing() -> None:
    """A state with no risk manager attached has nobody to publish to."""
    state = SpellSystemState("lineage", "version-a")

    state._republish_validity()

    assert state.validity is SpellValidity.unknown


def test_republish_validity_contains_a_failing_callback() -> None:
    """A callback failure is contained exactly as `set_validity` contains it."""
    state = SpellSystemState("lineage", "version-a")
    manager = MagicMock()
    manager.on_structural_validity_change.side_effect = RuntimeError("risk manager gone")
    state._set_risk_manager(manager)

    state._republish_validity()

    manager.on_structural_validity_change.assert_called_once_with("lineage", SpellValidity.unknown)


def test_republish_validity_refuses_a_cleaned_state() -> None:
    """A cleaned state raises the standard use-after-clean error."""
    state = SpellSystemState("lineage", "version-a")
    state.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        state._republish_validity()


def test_register_index_republishes_a_flag_change_on_a_lineage_already_gated(
        states: SpellSystemStates,
        watcher: _FlagReadingRiskManager,
) -> None:
    """A notch back from a never-validated False version publishes one event that carries the cleared flag."""
    index = SpellIndex("implementation-v1")
    states.register_index(index, "book", resolvable=False)
    watcher.seen.clear()

    index.update("implementation-v2")
    states.register_index(index, "book", resolvable=True)

    assert watcher.seen == [(index.id, SpellValidity.gated, False, False)]


def test_register_index_republishes_a_new_exclusion_on_a_lineage_already_gated(
        states: SpellSystemStates,
        watcher: _FlagReadingRiskManager,
) -> None:
    """A notch to a False version while the lineage is gated publishes one event that carries the new flag."""
    index = SpellIndex("implementation-v1")
    states.register_index(index, "book", resolvable=True)
    watcher.seen.clear()

    index.update("definition-v2")
    states.register_index(index, "book", resolvable=False)

    assert watcher.seen == [(index.id, SpellValidity.gated, True, True)]


def test_register_index_publishes_nothing_extra_when_the_flag_is_unchanged(
        states: SpellSystemStates,
        watcher: _FlagReadingRiskManager,
) -> None:
    """Registering a gated lineage again with the same capability publishes nothing."""
    index = SpellIndex("definition-v1")
    states.register_index(index, "book", resolvable=False)
    watcher.seen.clear()

    states.register_index(index, "book", resolvable=False)
    states.register_index(index, "book")

    assert watcher.seen == []
    assert states.index_has_flag(index.id, SpellState.non_resolvable) is True


def test_non_resolvable_index_ids_follows_each_registration_path(states: SpellSystemStates) -> None:
    """The published set holds a lineage exactly while its selected version is flagged."""
    index = SpellIndex("definition-v1")
    assert states.non_resolvable_index_ids == frozenset()

    states.register_index(index, "book", resolvable=False)
    assert states.non_resolvable_index_ids == frozenset({index.id})

    states.register_index(index, "book")
    assert states.non_resolvable_index_ids == frozenset({index.id})

    index.update("implementation-v2")
    states.register_index(index, "book", resolvable=True)
    assert states.non_resolvable_index_ids == frozenset()

    index.update("definition-v3")
    states.register_index(index, "book", resolvable=False)
    assert states.non_resolvable_index_ids == frozenset({index.id})

    index.update("unknown-capability-v4")
    states.register_index(index, "book")
    assert states.non_resolvable_index_ids == frozenset()


def test_non_resolvable_index_ids_holds_exactly_the_flagged_lineages(states: SpellSystemStates) -> None:
    """Definitions are in, resolvable and capability-less registrations are out, and the set agrees with each flag."""
    definitions = [SpellIndex(f"definition-{number}") for number in range(3)]
    plain = [SpellIndex(f"plain-{number}") for number in range(3)]
    for index in definitions:
        states.register_index(index, "book", resolvable=False)
    states.register_index(plain[0], "book", resolvable=True)
    states.register_index(plain[1], "book")
    states.register_index(plain[2], "other-book", resolvable=True)

    assert states.non_resolvable_index_ids == frozenset(index.id for index in definitions)
    for index in definitions + plain:
        flagged = states.index_has_flag(index.id, SpellState.non_resolvable)
        assert (index.id in states.non_resolvable_index_ids) is flagged


def test_non_resolvable_index_ids_is_replaced_never_mutated(states: SpellSystemStates) -> None:
    """A reader's snapshot never changes under it, and a registration that keeps the membership replaces nothing."""
    index = SpellIndex("definition-v1")
    before = states.non_resolvable_index_ids

    states.register_index(index, "book", resolvable=False)
    after = states.non_resolvable_index_ids

    assert isinstance(after, frozenset)
    assert before == frozenset()
    assert after == frozenset({index.id})
    states.register_index(index, "book", resolvable=False)
    states.register_index(index, "book")
    assert states.non_resolvable_index_ids is after


def test_unregister_index_takes_the_lineage_out_of_the_published_set(states: SpellSystemStates) -> None:
    """A removed lineage leaves the set; registering it again as a definition (a transfer's flip) puts it back."""
    index = SpellIndex("definition-v1")
    plain = SpellIndex("plain-v1")
    states.register_index(index, "book", resolvable=False)
    states.register_index(plain, "book", resolvable=True)
    published = states.non_resolvable_index_ids

    states.unregister_index(plain)
    states.unregister_index(SpellIndex("never-registered"))
    assert states.non_resolvable_index_ids is published

    states.unregister_index(index)
    assert states.non_resolvable_index_ids == frozenset()

    states.register_index(index, "other-book", resolvable=False)
    assert states.non_resolvable_index_ids == frozenset({index.id})


def test_non_resolvable_index_ids_refuses_a_cleaned_registry(states: SpellSystemStates) -> None:
    """A cleaned registry raises the standard use-after-clean error."""
    states.register_index(SpellIndex("definition-v1"), "book", resolvable=False)
    states.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        _ = states.non_resolvable_index_ids


def test_cleanup_leaves_an_empty_published_set_for_racing_readers(states: SpellSystemStates) -> None:
    """The documented tombstone: after cleanup the lock-free field holds an empty set, never a missing attribute."""
    states.register_index(SpellIndex("definition-v1"), "book", resolvable=False)

    states.cleanup()

    assert states._non_resolvable_index_ids == frozenset()
