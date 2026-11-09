"""SpellState string representation and flag-owner boundary regressions."""

import base64
import pickle
from enum import StrEnum

import pytest

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity


def test_flag_values_match_names_and_legacy_ordinals() -> None:
    """All old numeric inputs resolve to the same named flag."""
    names = (
        "new_index", "structure_changed", "dependencies_changed", "impacted_by_dependency",
        "contract_unvalidated", "contract_violation", "mutation_candidate", "mutation_quarantined",
        "mutation_failed", "has_open_incident", "anchored_component", "config_missing",
        "transfer_in_progress", "non_resolvable",
    )
    assert issubclass(SpellState, StrEnum)
    assert tuple(member.name for member in SpellState) == names
    for ordinal, name in enumerate(names, 1):
        member = SpellState[name]
        assert member.value == name
        assert SpellState(name) is member
        assert SpellState(ordinal) is member
        assert SpellState(float(ordinal)) is member


@pytest.mark.parametrize(
    ("payload", "expected"),
    (
        ("gASVXQAAAAAAAACMRG1lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5zcGVsbF9zeXN0ZW1fc3RhdGVzLnNwZWxsX3N0YXRllIwKU3BlbGxTdGF0ZZSTlEsBhZRSlC4=", SpellState.new_index),
        ("gASVXQAAAAAAAACMRG1lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5zcGVsbF9zeXN0ZW1fc3RhdGVzLnNwZWxsX3N0YXRllIwKU3BlbGxTdGF0ZZSTlEsFhZRSlC4=", SpellState.contract_unvalidated),
        ("gASVXQAAAAAAAACMRG1lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5zcGVsbF9zeXN0ZW1fc3RhdGVzLnNwZWxsX3N0YXRllIwKU3BlbGxTdGF0ZZSTlEsOhZRSlC4=", SpellState.non_resolvable),
    ),
)
def test_old_numeric_flag_pickles_preserve_identity(payload: str, expected: SpellState) -> None:
    """Captured pre-migration protocol-4 values remain readable."""
    assert pickle.loads(base64.b64decode(payload)) is expected


@pytest.mark.parametrize("foreign", ("contract_unvalidated", SpellStateChangeReason.contract_unvalidated))
def test_foreign_flag_cannot_read_or_clear_owned_flag(foreign: object) -> None:
    """Equal text from another family cannot impersonate a flag owner."""
    state = SpellSystemState("index-657", "spell-657")
    try:
        assert state.update_flags(flags_to_add=[SpellState.contract_unvalidated]) is True
        assert state.has_flag(foreign) is False
        assert state.update_flags(flags_to_remove=[foreign]) is False
        assert state.has_flag(SpellState.contract_unvalidated) is True
        state.set_validity(SpellValidity.gated, flags_to_remove=[foreign])
        assert state.has_flag(SpellState.contract_unvalidated) is True
        assert state.update_flags(flags_to_remove=[SpellState.contract_unvalidated]) is True
        assert state.has_flag(SpellState.contract_unvalidated) is False
    finally:
        state.cleanup()


@pytest.mark.parametrize("foreign", ("contract_unvalidated", SpellStateChangeReason.contract_unvalidated))
def test_foreign_flag_additions_are_ignored(foreign: object) -> None:
    """A typed flag set never retains a raw string or another enum family."""
    state = SpellSystemState("index-657", "spell-657")
    try:
        assert state.update_flags(flags_to_add=[foreign, None]) is False
        assert state.flags == {SpellState.new_index}
        state.set_validity(SpellValidity.gated, flags_to_add=[foreign, None])
        assert state.flags == {SpellState.new_index}
    finally:
        state.cleanup()
