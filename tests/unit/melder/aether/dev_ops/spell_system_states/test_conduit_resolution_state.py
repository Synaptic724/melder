import threading

import pytest

from melder.aether.dev_ops.spell_system_states.conduit_resolution_state import (
    ConduitResolutionState,
)
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)


def _make_diagnostic(*, code: str, message: str) -> SystemDiagnostic:
    """
    Purpose:
        Build a SystemDiagnostic for ConduitResolutionState tests.
    Contract:
        - Uses ERROR severity by default.
        - Sets code and message deterministically.
    Args:
        code: Diagnostic code to set.
        message: Diagnostic message to set.
    Returns:
        SystemDiagnostic: Diagnostic instance for tests.
    """
    return SystemDiagnostic(
        code=code,
        message=message,
        severity=SystemDiagnosticSeverity.ERROR,
    )


def test_init_rejects_empty_conduit_id() -> None:
    """
    Purpose:
        Validate ConduitResolutionState rejects empty conduit ids.
    Contract:
        - Empty conduit_id raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="conduit_id"):
        ConduitResolutionState("")


def test_init_rejects_none_initial_validity() -> None:
    """
    Purpose:
        Validate ConduitResolutionState rejects None initial validity.
    Contract:
        - None initial_validity raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="initial_validity"):
        ConduitResolutionState("cid", initial_validity=None)


def test_spell_validity_defaults_to_initial_validity() -> None:
    """
    Purpose:
        Validate default per-spell validity uses initial validity.
    Contract:
        - Missing spell id returns initial validity value.
    Returns:
        None.
    Raises:
        AssertionError: If default validity is incorrect.
    """
    state = ConduitResolutionState("cid", initial_validity=SpellValidity.gated)

    assert state.get_spell_validity("spell-1") is SpellValidity.gated


def test_root_validity_defaults_to_initial_validity() -> None:
    """
    Purpose:
        Validate default per-root validity uses initial validity.
    Contract:
        - Missing root id returns initial validity value.
    Returns:
        None.
    Raises:
        AssertionError: If default validity is incorrect.
    """
    state = ConduitResolutionState("cid", initial_validity=SpellValidity.unknown)

    assert state.get_root_validity("root-1") is SpellValidity.unknown


def test_empty_ids_return_none_for_validity_getters() -> None:
    """Verify empty spell/root ids return None from validity accessors."""
    state = ConduitResolutionState("cid")

    assert state.get_spell_validity("") is None
    assert state.get_root_validity("") is None


def test_set_spell_validity_marks_dirty_and_reason() -> None:
    """
    Purpose:
        Validate per-spell validity updates mark the state dirty.
    Contract:
        - Setting a new spell validity marks dirty.
        - Change reason is stored when provided.
    Returns:
        None.
    Raises:
        AssertionError: If dirty or reason tracking fails.
    """
    state = ConduitResolutionState("cid")

    state.set_spell_validity(
        "spell-1",
        SpellValidity.valid,
        change_reason=SpellStateChangeReason.validation_passed,
    )

    assert state.is_dirty() is True
    assert state.get_spell_validity("spell-1") is SpellValidity.valid


def test_set_spell_validity_reuses_existing_without_change() -> None:
    """
    Purpose:
        Validate repeat validity assignments do not rewrite state unnecessarily.
    Contract:
        - Setting the same validity preserves stored value.
        - State remains dirty once marked dirty.
    Returns:
        None.
    Raises:
        AssertionError: If validity is not preserved or dirty tracking resets.
    """
    state = ConduitResolutionState("cid")
    state.set_spell_validity("spell-1", SpellValidity.valid)
    state.clear_dirty(123.0)

    state.set_spell_validity("spell-1", SpellValidity.valid)

    assert state.is_dirty() is False
    assert state.get_spell_validity("spell-1") is SpellValidity.valid


def test_set_spell_validity_validates_inputs_and_swallows_risk_callback_errors() -> None:
    """Verify input guards and risk-callback failures do not escape."""
    state = ConduitResolutionState("cid")

    with pytest.raises(ValueError, match="spell_id"):
        state.set_spell_validity("", SpellValidity.valid)
    with pytest.raises(ValueError, match="validity"):
        state.set_spell_validity("spell-1", None)

    class _RiskManager:
        def on_resolution_validity_change(self, conduit_id, spell_id, validity):
            raise RuntimeError("risk boom")

    state._set_risk_manager(_RiskManager())
    state.set_spell_validity("spell-1", SpellValidity.valid)

    assert state.get_spell_validity("spell-1") is SpellValidity.valid


def test_set_spell_validity_same_value_updates_reason_without_dirtying() -> None:
    """Verify unchanged spell validity can still refresh the last change reason."""
    state = ConduitResolutionState("cid")
    state.set_spell_validity("spell-1", SpellValidity.valid)
    state.clear_dirty(1.0)

    state.set_spell_validity(
        "spell-1",
        SpellValidity.valid,
        change_reason=SpellStateChangeReason.validation_passed,
    )

    assert state.is_dirty() is False
    assert state._last_change_reason is SpellStateChangeReason.validation_passed


def test_bulk_set_spell_validity_marks_dirty_on_change() -> None:
    """
    Purpose:
        Validate bulk spell validity updates mark dirty when needed.
    Contract:
        - Changes in the bulk map mark the state dirty.
        - Unchanged updates do not mark dirty when clean.
    Returns:
        None.
    Raises:
        AssertionError: If dirty tracking is incorrect.
    """
    state = ConduitResolutionState("cid")
    state.bulk_set_spell_validity(
        {
            "spell-1": SpellValidity.valid,
            "spell-2": SpellValidity.invalid,
        }
    )

    assert state.is_dirty() is True
    state.clear_dirty(1.0)

    state.bulk_set_spell_validity(
        {
            "spell-1": SpellValidity.valid,
            "spell-2": SpellValidity.invalid,
        }
    )

    assert state.is_dirty() is False


def test_bulk_set_spell_validity_validates_none_and_skips_invalid_entries() -> None:
    """Verify bulk spell updates reject None maps and ignore invalid entries."""
    state = ConduitResolutionState("cid")

    with pytest.raises(ValueError, match="validity_map"):
        state.bulk_set_spell_validity(None)

    class _RiskManager:
        def on_resolution_validity_change(self, conduit_id, spell_id, validity):
            raise RuntimeError("risk boom")

    state._set_risk_manager(_RiskManager())
    state.bulk_set_spell_validity(
        {
            "": SpellValidity.valid,
            "spell-none": None,
            "spell-1": SpellValidity.valid,
        }
    )

    assert state.snapshot_spell_validity() == {"spell-1": SpellValidity.valid}


def test_bulk_set_spell_validity_same_values_updates_reason_without_dirtying() -> None:
    """Verify unchanged bulk spell updates can still refresh the last change reason."""
    state = ConduitResolutionState("cid")
    state.bulk_set_spell_validity({"spell-1": SpellValidity.valid})
    state.clear_dirty(1.0)

    state.bulk_set_spell_validity(
        {"spell-1": SpellValidity.valid},
        change_reason=SpellStateChangeReason.validation_passed,
    )

    assert state.is_dirty() is False
    assert state._last_change_reason is SpellStateChangeReason.validation_passed


def test_snapshot_spell_validity_returns_copy() -> None:
    """
    Purpose:
        Validate snapshot_spell_validity returns a copy.
    Contract:
        - Snapshot is a dict copy and does not mutate state when changed.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot is not isolated.
    """
    state = ConduitResolutionState("cid")
    state.set_spell_validity("spell-1", SpellValidity.valid)

    snapshot = state.snapshot_spell_validity()
    snapshot["spell-1"] = SpellValidity.invalid

    assert state.get_spell_validity("spell-1") is SpellValidity.valid


def test_bulk_set_root_validity_marks_dirty_on_change() -> None:
    """
    Purpose:
        Validate bulk root validity updates mark dirty when needed.
    Contract:
        - Changes in the bulk map mark the state dirty.
    Returns:
        None.
    Raises:
        AssertionError: If dirty tracking is incorrect.
    """
    state = ConduitResolutionState("cid")
    state.bulk_set_root_validity(
        {
            "root-1": SpellValidity.valid,
            "root-2": SpellValidity.invalid,
        }
    )

    assert state.is_dirty() is True


def test_set_root_validity_validates_inputs_and_swallows_risk_callback_errors() -> None:
    """Verify root validity guards and risk-callback failures do not escape."""
    state = ConduitResolutionState("cid")

    with pytest.raises(ValueError, match="root_id"):
        state.set_root_validity("", SpellValidity.valid)
    with pytest.raises(ValueError, match="validity"):
        state.set_root_validity("root-1", None)

    class _RiskManager:
        def on_resolution_validity_change(self, conduit_id, root_id, validity):
            raise RuntimeError("risk boom")

    state._set_risk_manager(_RiskManager())
    state.set_root_validity("root-1", SpellValidity.valid)

    assert state.get_root_validity("root-1") is SpellValidity.valid


def test_set_root_validity_same_value_updates_reason_without_dirtying() -> None:
    """Verify unchanged root validity can still refresh the last change reason."""
    state = ConduitResolutionState("cid")
    state.set_root_validity("root-1", SpellValidity.valid)
    state.clear_dirty(1.0)

    state.set_root_validity(
        "root-1",
        SpellValidity.valid,
        change_reason=SpellStateChangeReason.validation_passed,
    )

    assert state.is_dirty() is False
    assert state._last_change_reason is SpellStateChangeReason.validation_passed


def test_bulk_set_root_validity_validates_none_and_skips_invalid_entries() -> None:
    """Verify bulk root updates reject None maps and ignore invalid entries."""
    state = ConduitResolutionState("cid")

    with pytest.raises(ValueError, match="validity_map"):
        state.bulk_set_root_validity(None)

    class _RiskManager:
        def on_resolution_validity_change(self, conduit_id, root_id, validity):
            raise RuntimeError("risk boom")

    state._set_risk_manager(_RiskManager())
    state.bulk_set_root_validity(
        {
            "": SpellValidity.valid,
            "root-none": None,
            "root-1": SpellValidity.valid,
        }
    )

    assert state.snapshot_root_validity() == {"root-1": SpellValidity.valid}


def test_bulk_set_root_validity_same_values_updates_reason_without_dirtying() -> None:
    """Verify unchanged bulk root updates can still refresh the last change reason."""
    state = ConduitResolutionState("cid")
    state.bulk_set_root_validity({"root-1": SpellValidity.valid})
    state.clear_dirty(1.0)

    state.bulk_set_root_validity(
        {"root-1": SpellValidity.valid},
        change_reason=SpellStateChangeReason.validation_passed,
    )

    assert state.is_dirty() is False
    assert state._last_change_reason is SpellStateChangeReason.validation_passed


def test_snapshot_root_validity_returns_copy() -> None:
    """
    Purpose:
        Validate snapshot_root_validity returns a copy.
    Contract:
        - Snapshot is a dict copy and does not mutate state when changed.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot is not isolated.
    """
    state = ConduitResolutionState("cid")
    state.set_root_validity("root-1", SpellValidity.valid)

    snapshot = state.snapshot_root_validity()
    snapshot["root-1"] = SpellValidity.invalid

    assert state.get_root_validity("root-1") is SpellValidity.valid


def test_record_diagnostics_replaces_on_change() -> None:
    """
    Purpose:
        Validate diagnostics are replaced when the signature changes.
    Contract:
        - Different diagnostic signatures replace the stored list.
        - Old diagnostics are cleaned during replacement.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are not replaced or cleaned.
    """
    state = ConduitResolutionState("cid")
    original = _make_diagnostic(code="A", message="one")
    replacement = _make_diagnostic(code="B", message="two")

    state.record_diagnostics([original])
    stored_original = state.list_diagnostics()
    assert [diag.code for diag in stored_original] == ["A"]
    assert original.cleaned is False

    state.record_diagnostics([replacement])
    stored_replacement = state.list_diagnostics()
    assert [diag.code for diag in stored_replacement] == ["B"]
    assert stored_original[0].cleaned is True
    assert original.cleaned is False


def test_record_diagnostics_skips_on_same_signature() -> None:
    """
    Purpose:
        Validate diagnostics are not replaced when signatures are identical.
    Contract:
        - Identical diagnostic signatures are ignored.
        - Existing diagnostics remain intact and not cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are replaced unnecessarily.
    """
    state = ConduitResolutionState("cid")
    original = _make_diagnostic(code="A", message="one")
    duplicate = _make_diagnostic(code="A", message="one")

    state.record_diagnostics([original])
    stored = state.list_diagnostics()
    state.record_diagnostics([duplicate])

    stored_after = state.list_diagnostics()
    assert stored_after[0] is stored[0]
    assert stored_after[0].code == "A"
    assert original.cleaned is False
    assert duplicate.cleaned is False


def test_record_diagnostics_validates_none_and_preserves_clean_state_on_same_signature() -> None:
    """Verify diagnostics rejects None and same-signature updates are a no-op."""
    state = ConduitResolutionState("cid")

    with pytest.raises(ValueError, match="diagnostics"):
        state.record_diagnostics(None)

    original = _make_diagnostic(code="A", message="one")
    duplicate = _make_diagnostic(code="A", message="one")
    state.record_diagnostics([original])
    state.clear_dirty(1.0)
    state.record_diagnostics([duplicate])

    assert state.is_dirty() is False


def test_clear_diagnostics_cleans_entries() -> None:
    """
    Purpose:
        Validate clear_diagnostics cleans and clears stored diagnostics.
    Contract:
        - Stored diagnostics are cleaned and removed.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are not cleared.
    """
    state = ConduitResolutionState("cid")
    diag = _make_diagnostic(code="A", message="one")

    state.record_diagnostics([diag])
    stored = state.list_diagnostics()
    state.clear_diagnostics()

    assert state.list_diagnostics() == []
    assert stored[0].cleaned is True
    assert diag.cleaned is False


def test_has_errors_and_warnings_reflect_severity() -> None:
    """
    Purpose:
        Validate error/warning helpers reflect diagnostic severity.
    Contract:
        - has_errors is True when ERROR diagnostics exist.
        - has_warnings is True when WARNING diagnostics exist.
    Returns:
        None.
    Raises:
        AssertionError: If severity flags are incorrect.
    """
    state = ConduitResolutionState("cid")
    error_diag = SystemDiagnostic(
        code="E1",
        message="error",
        severity=SystemDiagnosticSeverity.ERROR,
    )
    warning_diag = SystemDiagnostic(
        code="W1",
        message="warn",
        severity=SystemDiagnosticSeverity.WARNING,
    )

    state.record_diagnostics([error_diag, warning_diag])

    assert state.has_errors() is True
    assert state.has_warnings() is True


def test_clear_dirty_records_validation_timestamp() -> None:
    """
    Purpose:
        Validate clear_dirty stores validation timestamp.
    Contract:
        - clear_dirty sets dirty False and stores timestamp.
    Returns:
        None.
    Raises:
        AssertionError: If dirty tracking does not update.
    """
    state = ConduitResolutionState("cid")
    state.set_root_validity("root-1", SpellValidity.valid)

    state.clear_dirty(42.0)

    assert state.is_dirty() is False
    assert state.last_validated_at() == 42.0


def test_cleanup_marks_state_unusable() -> None:
    """
    Purpose:
        Validate cleanup renders the state unusable.
    Contract:
        - Cleanup is idempotent.
        - Accessors raise RuntimeError after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not enforced.
    """
    state = ConduitResolutionState("cid")
    state.set_spell_validity("spell-1", SpellValidity.valid)
    state.cleanup()
    state.cleanup()

    with pytest.raises(RuntimeError):
        state.get_spell_validity("spell-1")


def test_internal_helpers_cover_none_and_exception_tolerance() -> None:
    """Verify helper no-op paths and defensive exception swallowing branches."""
    state = ConduitResolutionState("cid")
    diag = _make_diagnostic(code="A", message="one")

    class _BrokenDiagnostic:
        code = "B"
        message = "boom"
        severity = SystemDiagnosticSeverity.ERROR
        spell_id = None
        root_id = None
        source = None
        details = None

        def cleanup(self):
            raise RuntimeError("cleanup boom")

    class _Unrepr:
        def __repr__(self):
            raise RuntimeError("repr boom")

    assert state._diagnostics_signature([None, diag])[0][0] == "A"
    clones = state._clone_diagnostics([None, diag])
    assert len(clones) == 1
    assert state._details_signature(None) is None
    assert state._details_signature({"x": _Unrepr()}) == (("x", "<unrepr>"),)

    state._diagnostics = [_BrokenDiagnostic()]
    state._cleanup_diagnostics_locked()
    assert state._diagnostics == []
    state._set_risk_manager(object())
    assert state._risk_manager is not None


def test_cleanup_rechecks_cleaned_inside_lock() -> None:
    """Verify the inner cleanup re-check under concurrent teardown."""

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    state = ConduitResolutionState("cid")
    state._lock = _CoordinatedLock()
    failures = []

    def _run_cleanup():
        try:
            state.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = threading.Thread(target=_run_cleanup, name="crs-cleanup-first")
    second = threading.Thread(target=_run_cleanup, name="crs-cleanup-second")

    first.start()
    assert state._lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
    assert state._cleaned is True
    assert not hasattr(state, '_lock')
