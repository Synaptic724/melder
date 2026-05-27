import pytest
import threading
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def state():
    return SpellSystemState("index-1", "spell-sha-1")

# ----------------------------------------------------------------------
# 1. Initialization
# ----------------------------------------------------------------------

def test_init_success(state):
    assert state.spell_index_id == "index-1"
    assert state.current_spell_id == "spell-sha-1"
    assert state.validity == SpellValidity.unknown
    assert SpellState.new_lineage in state.flags
    assert state.change_reason == SpellStateChangeReason.new_lineage
    assert state.direct_dependencies == set()
    assert state.direct_dependents == set()

def test_init_validation():
    with pytest.raises(ValueError):
        SpellSystemState("", "sha")
    with pytest.raises(ValueError):
        SpellSystemState("id", "")

# ----------------------------------------------------------------------
# 2. Properties (Isolation)
# ----------------------------------------------------------------------

def test_direct_dependencies_isolation(state):
    """
    Verify `direct_dependencies` returns a safe copy.

    Contract:
    - Modifying the returned set must NOT affect the internal state.
    """
    state.attach_dependencies(["d1"])
    deps = state.direct_dependencies
    deps.add("hacked")
    assert "hacked" not in state.direct_dependencies

def test_direct_dependents_isolation(state):
    """
    Verify `direct_dependents` returns a safe copy.

    Contract:
    - Modifying the returned set must NOT affect the internal state.
    """
    state.add_dependent("d1")
    deps = state.direct_dependents
    deps.add("hacked")
    assert "hacked" not in state.direct_dependents

def test_flags_isolation(state):
    """
    Verify `flags` returns a safe copy.

    Contract:
    - Modifying the returned set must NOT affect the internal state.
    """
    flags = state.flags
    flags.add(SpellState.has_open_incident)
    assert SpellState.has_open_incident not in state.flags


def test_snapshot_properties_return_empty_after_internal_collections_are_nulled(state):
    """
    Verify snapshot properties return empty collections when internals are already nulled.
    """
    state._direct_dependencies = None
    state._direct_dependents = None
    state._flags = None

    assert state.direct_dependencies == set()
    assert state.direct_dependents == set()
    assert state.flags == set()

# ----------------------------------------------------------------------
# 3. Mutation & Wiring
# ----------------------------------------------------------------------

def test_update_current_spell_id(state):
    state.update_current_spell_id("sha-2")
    assert state.current_spell_id == "sha-2"

def test_update_current_spell_id_validation(state):
    with pytest.raises(ValueError):
        state.update_current_spell_id("")

def test_attach_dependencies(state):
    state.attach_dependencies(["d1", "d2"])
    assert state.direct_dependencies == {"d1", "d2"}
    
    # Verify replacement
    state.attach_dependencies(["d3"])
    assert state.direct_dependencies == {"d3"}

def test_dependents_management(state):
    state.add_dependent("dep-1")
    assert "dep-1" in state.direct_dependents
    
    state.remove_dependent("dep-1")
    assert "dep-1" not in state.direct_dependents

# ----------------------------------------------------------------------
# 4. State Transitions
# ----------------------------------------------------------------------

def test_mark_structural_change(state):
    """
    Verify transition to structural change state.

    Contract:
    - Validity becomes GATED.
    - Change reason is structure_changed.
    - 'structure_changed' flag is added.
    - Transitively dirty flag is False (this is a root change).
    """
    state.mark_structural_change()
    assert state.validity == SpellValidity.gated
    assert SpellState.structure_changed in state.flags
    assert state.change_reason == SpellStateChangeReason.structure_changed
    assert not state.transitively_dirty

def test_mark_dependency_change(state):
    state.mark_dependency_change()
    assert state.validity == SpellValidity.gated
    assert SpellState.dependencies_changed in state.flags
    assert state.change_reason == SpellStateChangeReason.dependencies_changed

def test_mark_transitively_dirty(state):
    """
    Verify transition to transitively dirty state.

    Contract:
    - Validity becomes GATED.
    - Flag 'impacted_by_dependency' is added.
    - `transitively_dirty` property becomes True.
    """
    state.mark_transitively_dirty()
    assert state.validity == SpellValidity.gated
    assert SpellState.impacted_by_dependency in state.flags
    assert state.transitively_dirty

def test_clear_dirty(state):
    """
    Verify clearing dirty state after successful validation.

    Contract:
    - Validity becomes VALID.
    - Topology/dirty flags are removed.
    - `last_validated_at` is updated.
    - `transitively_dirty` becomes False.
    """
    # Setup dirty state
    state.mark_structural_change()
    
    state.clear_dirty(last_validated_at=100.0)
    
    assert state.validity == SpellValidity.valid
    assert not state.dirty
    assert state.last_validated_at == 100.0
    
    # Flags cleared?
    assert SpellState.structure_changed not in state.flags
    # new_lineage should also be cleared
    assert SpellState.new_lineage not in state.flags

def test_set_validity_generic(state):
    """
    Verify low-level validity setter handles complex updates.

    Contract:
    - Updates validity, reason, and flags (add/remove) in one atomic-like operation.
    """
    state.set_validity(
        SpellValidity.invalid,
        change_reason=SpellStateChangeReason.validation_failed,
        flags_to_add=[SpellState.has_open_incident],
        flags_to_remove=[SpellState.new_lineage]
    )
    
    assert state.validity == SpellValidity.invalid
    assert state.change_reason == SpellStateChangeReason.validation_failed
    assert SpellState.has_open_incident in state.flags
    assert SpellState.new_lineage not in state.flags


def test_set_validity_handles_missing_flags_and_swallows_risk_callback_errors(state):
    """
    Verify set_validity no-ops safely when flags are already nulled and swallows
    risk-manager callback failures.
    """

    class _RiskManager:
        def on_structural_validity_change(self, lineage_id, validity):
            raise RuntimeError("risk boom")

    state._set_risk_manager(_RiskManager())
    state.set_validity(SpellValidity.valid)

    state._flags = None
    state.set_validity(SpellValidity.invalid)

# ----------------------------------------------------------------------
# 5. Cleanup
# ----------------------------------------------------------------------

def test_cleanup_clears_state(state):
    """
    Verify cleanup resets internal state.

    Contract:
    - All collections are nulled.
    - Flags and IDs are cleared.
    """
    state.attach_dependencies(["d1"])
    state.cleanup()
    
    assert state._cleaned
    assert not hasattr(state, '_direct_dependencies')
    assert not hasattr(state, '_flags')
    assert not hasattr(state, '_spell_index_id')

def test_cleanup_idempotent(state):
    state.cleanup()
    state.cleanup()


def test_cleanup_rechecks_cleaned_inside_lock(state):
    """
    Verify the inner cleanup re-check under concurrent teardown.
    """

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

    state._lock = _CoordinatedLock()
    failures = []

    def _run_cleanup():
        try:
            state.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = threading.Thread(target=_run_cleanup, name="sss-cleanup-first")
    second = threading.Thread(target=_run_cleanup, name="sss-cleanup-second")

    first.start()
    assert state._lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
    assert state._cleaned is True
    assert not hasattr(state, '_lock')


def test_add_and_remove_dependent_ignore_empty_ids(state):
    """
    Verify dependent-edge helpers no-op on empty identifiers.
    """
    state.add_dependent("")
    state.remove_dependent("")

    assert state.direct_dependents == set()


def test_clear_dirty_swallows_risk_callback_errors(state):
    """
    Verify clear_dirty tolerates risk-manager callback failures.
    """

    class _RiskManager:
        def on_structural_validity_change(self, lineage_id, validity):
            raise RuntimeError("risk boom")

    state._set_risk_manager(_RiskManager())
    state.mark_structural_change()

    state.clear_dirty(last_validated_at=123.0)

    assert state.validity is SpellValidity.valid
    assert state.last_validated_at == 123.0

def test_access_after_cleanup_raises(state):
    """
    Verify public accessors raise RuntimeError after cleanup.
    """
    state.cleanup()
    
    with pytest.raises((RuntimeError, AttributeError)):
        _ = state.spell_index_id
        
    with pytest.raises((RuntimeError, AttributeError)):
        state.mark_structural_change()
