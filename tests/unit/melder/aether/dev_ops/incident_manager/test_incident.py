import pytest
import threading
from threading import Thread
from melder.aether.dev_ops.incident_manager.incident import Incident
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.incident_manager.incident_status import IncidentStatus

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def valid_args():
    return {
        "incident_id": "inc-1",
        "kind": "validation_error",
        "severity": IncidentSeverity.error,
        "summary": "Something went wrong",
        "spell_index_id": "spell-123",
        "root_ids": ["root-A", "root-B"],
        "details": {"error_code": 500}
    }

@pytest.fixture
def incident(valid_args):
    return Incident(**valid_args)

# ----------------------------------------------------------------------
# 1. Initialization
# ----------------------------------------------------------------------

def test_init_success(incident, valid_args):
    """
    Verify successful initialization populates all fields.

    Contract:
    - ID, kind, severity, summary, and linkage fields match inputs.
    - Status defaults to 'open'.
    - Collections are populated correctly.
    """
    assert incident.id == valid_args["incident_id"]
    assert incident.kind == valid_args["kind"]
    assert incident.severity == valid_args["severity"]
    assert incident.summary == valid_args["summary"]
    assert incident.spell_index_id == valid_args["spell_index_id"]
    assert incident.status == IncidentStatus.open
    
    # Check collections
    assert incident.root_ids == valid_args["root_ids"]
    assert incident.details == valid_args["details"]

def test_init_validates_required_fields(valid_args):
    """
    Verify input validation during initialization.

    Contract:
    - incident_id, kind, and summary are mandatory non-empty strings.
    - ValueError is raised if any are missing/empty.
    """
    # Missing ID
    args = valid_args.copy()
    args["incident_id"] = ""
    with pytest.raises(ValueError, match="incident_id cannot be empty"):
        Incident(**args)
        
    # Missing Kind
    args = valid_args.copy()
    args["kind"] = ""
    with pytest.raises(ValueError, match="kind cannot be empty"):
        Incident(**args)
        
    # Missing Summary
    args = valid_args.copy()
    args["summary"] = ""
    with pytest.raises(ValueError, match="summary cannot be empty"):
        Incident(**args)

def test_init_handles_defaults():
    inc = Incident(
        incident_id="inc-2",
        kind="info",
        severity=IncidentSeverity.info,
        summary="Just info"
    )
    assert inc.spell_index_id is None
    assert inc.root_ids == []
    assert inc.details == {}

# ----------------------------------------------------------------------
# 2. Properties & Snapshots
# ----------------------------------------------------------------------

def test_root_ids_returns_copy(incident):
    """
    Verify `root_ids` property returns a safe copy.

    Contract:
    - Modifying the returned list must NOT affect the internal state.
    """
    roots = incident.root_ids
    roots.append("mutated")
    assert "mutated" not in incident.root_ids

def test_details_returns_copy(incident):
    """
    Verify `details` property returns a safe copy.

    Contract:
    - Modifying the returned dictionary must NOT affect the internal state.
    """
    details = incident.details
    details["mutated"] = True
    assert "mutated" not in incident.details

# ----------------------------------------------------------------------
# 3. State Transitions
# ----------------------------------------------------------------------

def test_acknowledge(incident):
    """Verify transition to 'acknowledged' status."""
    assert incident.status == IncidentStatus.open
    incident.acknowledge()
    assert incident.status == IncidentStatus.acknowledged

def test_resolve(incident):
    """Verify transition to 'resolved' status."""
    incident.resolve()
    assert incident.status == IncidentStatus.resolved

def test_suppress(incident):
    """Verify transition to 'suppressed' status."""
    incident.suppress()
    assert incident.status == IncidentStatus.suppressed

def test_acknowledge_idempotent(incident):
    """Verify `acknowledge` is safe to call multiple times."""
    incident.acknowledge()
    incident.acknowledge()
    assert incident.status == IncidentStatus.acknowledged

def test_resolve_idempotent(incident):
    """Verify `resolve` is safe to call multiple times."""
    incident.resolve()
    incident.resolve()
    assert incident.status == IncidentStatus.resolved

def test_suppress_idempotent(incident):
    """Verify `suppress` is safe to call multiple times."""
    incident.suppress()
    incident.suppress()
    assert incident.status == IncidentStatus.suppressed

def test_concurrency_state_change(incident):
    def worker():
        for _ in range(100):
            incident.acknowledge()
            incident.resolve()
    
    threads = [Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    # Final state is deterministic only if we control order, but here just checking no crashes
    assert incident.status in (IncidentStatus.acknowledged, IncidentStatus.resolved)

def test_status_reopen(incident):
    """Verify we can technically move between states (no enforcement logic)."""
    incident.resolve()
    incident.acknowledge()
    assert incident.status == IncidentStatus.acknowledged

def test_init_optional_lists_none():
    inc = Incident("id", "k", IncidentSeverity.info, "s", root_ids=None, details=None)
    assert inc.root_ids == []
    assert inc.details == {}

def test_repr_smoke(incident):
    """Verify repr does not crash."""
    r = repr(incident)
    assert isinstance(r, str)
    # Default repr includes class name
    assert "Incident" in r

# ----------------------------------------------------------------------
# 4. Cleanup
# ----------------------------------------------------------------------

def test_cleanup_clears_state(incident):
    """
    Verify `cleanup` resets all internal state.

    Contract:
    - cleaned flag is True.
    - internal collections are nulled.
    """
    incident.cleanup()
    
    assert incident._cleaned
    assert not hasattr(incident, '_root_ids')
    assert not hasattr(incident, '_details')
    assert not hasattr(incident, '_id')

def test_cleanup_is_idempotent(incident):
    incident.cleanup()
    incident.cleanup() # Should be safe

def test_access_after_cleanup_raises(incident):
    """
    Verify public accessors raise RuntimeError after cleanup.
    """
    incident.cleanup()
    
    with pytest.raises(RuntimeError):
        _ = incident.id
        
    with pytest.raises(RuntimeError):
        _ = incident.summary
        
    with pytest.raises(RuntimeError):
        incident.acknowledge()

# ----------------------------------------------------------------------
# 5. Thread Safety (Basic)
# ----------------------------------------------------------------------

def test_lock_creation(incident):
    from threading import RLock
    assert isinstance(incident._lock, type(RLock()))


def test_cleanup_rechecks_cleaned_inside_lock(incident):
    """
    Verify the inner cleanup re-check under concurrent teardown.

    Contract:
    - A second cleanup caller may pass the outer `_cleaned` check.
    - The inner `_cleaned` check inside the lock returns safely without error.
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

    incident._lock = _CoordinatedLock()
    failures = []

    def _run_cleanup():
        try:
            incident.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = Thread(target=_run_cleanup, name="incident-cleanup-first")
    second = Thread(target=_run_cleanup, name="incident-cleanup-second")

    first.start()
    assert incident._lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
    assert incident._cleaned is True
    assert not hasattr(incident, '_lock')
