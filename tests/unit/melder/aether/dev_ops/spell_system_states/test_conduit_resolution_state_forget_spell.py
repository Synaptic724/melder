"""Unit coverage for `ConduitResolutionState.forget_spell` (rebind-after-first-meld repair).

A spell id that leaves the frame, or re-enters it under the same content-stable id, must leave no
verdict behind in a conduit: the next read answers `initial_validity` again, as for an id the conduit
never resolved, so Meld reruns phases 5-11 before it builds the id.
"""

from typing import List, Optional, Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import (
    ConduitResolutionState,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)


class _RecordingRiskManager:
    """Risk-manager double that records every resolution-validity callback it receives."""

    def __init__(self) -> None:
        """Start with no recorded callbacks."""
        self.calls: List[Tuple[str, str, Optional[SpellValidity]]] = []

    def on_resolution_validity_change(
            self,
            conduit_id: str,
            spell_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """Record the callback arguments."""
        self.calls.append((conduit_id, spell_id, validity))


def _state_with_verdicts() -> ConduitResolutionState:
    """Build a state holding a spell and a root verdict for 'spell-a' and a spell verdict for 'spell-b'."""
    state = ConduitResolutionState("conduit-1")
    state.set_spell_validity("spell-a", SpellValidity.valid)
    state.set_root_validity("spell-a", SpellValidity.valid)
    state.set_spell_validity("spell-b", SpellValidity.valid)
    state.clear_dirty(validated_at=1.0)
    return state


def test_forget_spell_drops_both_verdicts_and_reports_a_hit() -> None:
    """Both the spell-level and the root-level verdict for the id are gone; the call returns True."""
    state = _state_with_verdicts()

    assert state.forget_spell("spell-a") is True

    assert state.get_spell_validity("spell-a") is SpellValidity.unknown
    assert state.get_root_validity("spell-a") is SpellValidity.unknown


def test_forget_spell_leaves_other_ids_untouched() -> None:
    """Forgetting one id does not disturb another id's verdict."""
    state = _state_with_verdicts()

    state.forget_spell("spell-a")

    assert state.get_spell_validity("spell-b") is SpellValidity.valid
    assert state.snapshot_spell_validity() == {"spell-b": SpellValidity.valid}
    assert state.snapshot_root_validity() == {}


def test_forget_spell_with_only_a_spell_verdict_is_a_hit() -> None:
    """An id that holds a spell-level verdict and no root verdict is still a hit."""
    state = ConduitResolutionState("conduit-1")
    state.set_spell_validity("spell-s", SpellValidity.valid)

    assert state.forget_spell("spell-s") is True
    assert state.get_spell_validity("spell-s") is SpellValidity.unknown


def test_forget_spell_with_only_a_root_verdict_is_a_hit() -> None:
    """An id that holds a root-level verdict and no spell verdict is still a hit."""
    state = ConduitResolutionState("conduit-1")
    state.set_root_validity("spell-r", SpellValidity.invalid)

    assert state.forget_spell("spell-r") is True
    assert state.get_root_validity("spell-r") is SpellValidity.unknown


def test_forget_spell_marks_dirty_with_the_reason_on_a_hit() -> None:
    """A hit marks the state dirty and records the supplied change reason."""
    state = _state_with_verdicts()
    assert state.is_dirty() is False

    state.forget_spell("spell-a", change_reason=SpellStateChangeReason.cleaned_up_spell)

    assert state.is_dirty() is True
    assert state._last_change_reason is SpellStateChangeReason.cleaned_up_spell
    assert state.last_validated_at() == 1.0


def test_forget_spell_miss_returns_false_and_changes_nothing() -> None:
    """An id with no verdict is a miss: False, still clean, reason unchanged."""
    state = _state_with_verdicts()

    assert state.forget_spell("never-resolved", change_reason=SpellStateChangeReason.cleaned_up_spell) is False

    assert state.is_dirty() is False
    assert state._last_change_reason is None
    assert state.get_spell_validity("spell-a") is SpellValidity.valid


def test_forget_spell_is_idempotent() -> None:
    """A second call for the same id is a miss."""
    state = _state_with_verdicts()

    assert state.forget_spell("spell-a") is True
    assert state.forget_spell("spell-a") is False


def test_forget_spell_answers_the_configured_initial_validity_afterwards() -> None:
    """After forgetting, the getters fall back to `initial_validity`, whatever it is."""
    state = ConduitResolutionState("conduit-1", initial_validity=SpellValidity.gated)
    state.set_spell_validity("spell-a", SpellValidity.valid)
    state.set_root_validity("spell-a", SpellValidity.valid)

    state.forget_spell("spell-a")

    assert state.get_spell_validity("spell-a") is SpellValidity.gated
    assert state.get_root_validity("spell-a") is SpellValidity.gated


def test_forget_spell_does_not_notify_the_risk_manager() -> None:
    """Forgetting is a change of scope, not of verdict: no resolution-validity callback fires."""
    state = _state_with_verdicts()
    risk_manager = _RecordingRiskManager()
    state._set_risk_manager(risk_manager)

    state.forget_spell("spell-a", change_reason=SpellStateChangeReason.register_or_rebind)
    state.forget_spell("spell-b")

    assert risk_manager.calls == []


def test_forget_spell_rejects_an_empty_id() -> None:
    """An empty id is a contract violation."""
    state = _state_with_verdicts()

    with pytest.raises(ValueError, match="spell_id"):
        state.forget_spell("")


def test_forget_spell_refuses_a_cleaned_state() -> None:
    """A cleaned state fails through `check_cleaned()`."""
    state = _state_with_verdicts()
    state.cleanup()

    with pytest.raises(RuntimeError):
        state.forget_spell("spell-a")


def test_forget_spell_preserves_diagnostics() -> None:
    """The diagnostics snapshot belongs to the last validation pass and is not pruned by forgetting."""
    state = _state_with_verdicts()
    state.record_diagnostics(
        [SystemDiagnostic(code="X", message="m", severity=SystemDiagnosticSeverity.WARNING, spell_id="spell-a")]
    )

    state.forget_spell("spell-a")

    assert len(state.list_diagnostics()) == 1
    assert state.has_warnings() is True
