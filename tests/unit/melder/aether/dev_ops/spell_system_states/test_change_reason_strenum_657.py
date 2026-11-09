"""Contract tests for transition reason names and legacy numeric inputs."""

import base64
import pickle
from enum import StrEnum

import pytest

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState


def test_reason_values_match_names_and_legacy_ordinals() -> None:
    """Every historical ordinal resolves to the same named reason."""
    names = (
        "new_index", "register_or_rebind", "structure_changed", "dependencies_changed",
        "dependency_changed", "impacted_by_dependency", "contract_unvalidated",
        "contract_violation", "mutation_promoted", "mutation_rolled_back",
        "selected_different_spell", "mutation_contract_set", "mutation_contract_cleared",
        "mutation_failed", "mutation_candidate", "mutation_quarantined", "validation_passed",
        "validation_failed", "incident_opened", "incident_resolved", "config_missing",
        "config_supplied", "anchored_component", "transfer_in_progress", "cleaned_up_spell",
        "explicit_mark", "other",
    )
    assert issubclass(SpellStateChangeReason, StrEnum)
    assert tuple(member.name for member in SpellStateChangeReason) == names
    for ordinal, name in enumerate(names, 1):
        member = SpellStateChangeReason[name]
        assert member.value == name
        assert SpellStateChangeReason(name) is member
        assert SpellStateChangeReason(ordinal) is member
        assert SpellStateChangeReason(float(ordinal)) is member
    assert SpellStateChangeReason(True) is SpellStateChangeReason.new_index


@pytest.mark.parametrize(
    ("payload", "expected"),
    (
        (
            "gASVdwAAAAAAAACMUm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5zcGVsbF9zeXN0ZW1fc3RhdGVzLnNwZWxsX3N0YXRlX2NoYW5nZV9yZWFzb26UjBZTcGVsbFN0YXRlQ2hhbmdlUmVhc29ulJOUSwGFlFKULg==",
            SpellStateChangeReason.new_index,
        ),
        (
            "gASVdwAAAAAAAACMUm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5zcGVsbF9zeXN0ZW1fc3RhdGVzLnNwZWxsX3N0YXRlX2NoYW5nZV9yZWFzb26UjBZTcGVsbFN0YXRlQ2hhbmdlUmVhc29ulJOUSxiFlFKULg==",
            SpellStateChangeReason.transfer_in_progress,
        ),
        (
            "gASVdwAAAAAAAACMUm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5zcGVsbF9zeXN0ZW1fc3RhdGVzLnNwZWxsX3N0YXRlX2NoYW5nZV9yZWFzb26UjBZTcGVsbFN0YXRlQ2hhbmdlUmVhc29ulJOUSxuFlFKULg==",
            SpellStateChangeReason.other,
        ),
    ),
)
def test_pre_migration_pickles_resolve_to_original_members(payload: str, expected: SpellStateChangeReason) -> None:
    """Previously recorded protocol-4 numeric pickles retain their identity."""
    assert pickle.loads(base64.b64decode(payload)) is expected


@pytest.mark.parametrize("invalid", (0, 28, 1.5, "not_a_reason", []))
def test_unknown_reason_values_are_rejected(invalid: object) -> None:
    """Unrecognized values do not gain an accidental fallback."""
    with pytest.raises(ValueError):
        SpellStateChangeReason(invalid)


def test_structural_transition_keeps_the_reason_member() -> None:
    """The state still publishes the exact triggering enum member."""
    state = SpellSystemState("index-657", "spell-657")
    try:
        state.mark_structural_change()
        assert state.change_reason is SpellStateChangeReason.structure_changed
    finally:
        state.cleanup()
