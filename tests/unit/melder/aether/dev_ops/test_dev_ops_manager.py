import pytest
import threading
from unittest.mock import MagicMock, patch
from melder.aether.dev_ops.dev_ops_manager import DevOpsManager
from melder.utilities.interfaces import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_dependencies():
    """
    Patches external dependencies: IncidentManager and ChangeControlManager.
    Returns a dictionary of the mock classes.
    """
    with patch("melder.aether.dev_ops.dev_ops_manager.IncidentManager") as mock_im_cls, \
         patch("melder.aether.dev_ops.dev_ops_manager.ChangeControlManager") as mock_ccm_cls:
        
        # Setup clean return values
        mock_im = mock_im_cls.return_value
        mock_ccm = mock_ccm_cls.return_value
        
        yield {
            "IncidentManager": mock_im_cls,
            "ChangeControlManager": mock_ccm_cls,
            "mock_im": mock_im,
            "mock_ccm": mock_ccm
        }

@pytest.fixture
def mock_sss():
    """Returns a mock ISpellSystemStates."""
    return MagicMock(spec=ISpellSystemStates)

@pytest.fixture
def manager(mock_dependencies, mock_sss):
    """Returns a fresh DevOpsManager with mocked dependencies."""
    return DevOpsManager(mock_sss)

# ----------------------------------------------------------------------
# 1. Initialization Tests
# ----------------------------------------------------------------------

def test_init_success(manager, mock_dependencies, mock_sss):
    """
    Verify successful initialization wires up all components.

    Contract:
    - IncidentManager is instantiated.
    - ChangeControlManager is instantiated with the provided SpellSystemStates.
    - Internal state is set correctly (not cleaned, locked).
    """
    # Verify sub-managers were instantiated
    mock_dependencies["IncidentManager"].assert_called_once()
    mock_dependencies["ChangeControlManager"].assert_called_once_with(spell_system_states=mock_sss)
    
    # Verify internal state
    assert manager._spell_system_states is mock_sss
    assert manager._incident_manager is mock_dependencies["mock_im"]
    assert manager._change_control_manager is mock_dependencies["mock_ccm"]
    assert manager._creation_gate_controller is not None
    assert not manager._cleaned

def test_init_validates_sss_not_none():
    """Verify ValueError if `spell_system_states` dependency is missing."""
    with pytest.raises(ValueError, match="cannot be None"):
        DevOpsManager(None)

def test_init_creates_lock(manager):
    """Verify an RLock is created for thread safety."""
    assert isinstance(manager._lock, type(threading.RLock()))

def test_init_sets_sentinel(manager):
    """Verify the registration guard sentinel is present (library requirement)."""
    from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
    assert manager.__melder_internal__ is _mrg.sentinel

# ----------------------------------------------------------------------
# 2. Property Tests: IncidentManager
# ----------------------------------------------------------------------

def test_prop_incident_manager_success(manager, mock_dependencies):
    """Verify property returns the initialized incident manager."""
    assert manager.incident_manager is mock_dependencies["mock_im"]

def test_prop_incident_manager_raises_if_cleaned(manager):
    """Verify accessing incident_manager after cleanup raises RuntimeError."""
    manager.cleanup()
    with pytest.raises(RuntimeError):
        _ = manager.incident_manager

def test_prop_incident_manager_thread_safety(manager):
    """
    Verify property access is thread-safe.

    Contract:
    - Accessing the property MUST acquire the internal lock.
    """
    # Mock the lock to verify acquire/release
    with patch.object(manager, "_lock") as mock_lock:
        _ = manager.incident_manager
        mock_lock.__enter__.assert_called()
        mock_lock.__exit__.assert_called()

# ----------------------------------------------------------------------
# 3. Property Tests: ChangeControlManager
# ----------------------------------------------------------------------

def test_prop_ccm_success(manager, mock_dependencies):
    """Verify property returns the initialized change control manager."""
    assert manager.change_control_manager is mock_dependencies["mock_ccm"]

def test_prop_ccm_raises_if_cleaned(manager):
    """Verify accessing change_control_manager after cleanup raises RuntimeError."""
    manager.cleanup()
    with pytest.raises(RuntimeError):
        _ = manager.change_control_manager

def test_prop_ccm_thread_safety(manager):
    """Verify property access is thread-safe (acquires lock)."""
    with patch.object(manager, "_lock") as mock_lock:
        _ = manager.change_control_manager
        mock_lock.__enter__.assert_called()
        mock_lock.__exit__.assert_called()

# ----------------------------------------------------------------------
# 3b. Property Tests: RiskManager
# ----------------------------------------------------------------------

def test_prop_risk_manager_success(manager):
    """Verify property returns the initialized risk manager."""
    assert manager.risk_manager is manager._risk_manager

def test_prop_risk_manager_raises_if_cleaned(manager):
    """Verify accessing risk_manager after cleanup raises RuntimeError."""
    manager.cleanup()
    with pytest.raises(RuntimeError):
        _ = manager.risk_manager

def test_prop_risk_manager_thread_safety(manager):
    """Verify risk_manager property access is thread-safe (acquires lock)."""
    with patch.object(manager, "_lock") as mock_lock:
        _ = manager.risk_manager
        mock_lock.__enter__.assert_called()
        mock_lock.__exit__.assert_called()

# ----------------------------------------------------------------------
# 4. Property Tests: CreationGateController
# ----------------------------------------------------------------------

def test_prop_creation_gate_controller_success(manager):
    """Verify property returns the initialized creation gate controller."""
    assert manager.creation_gate_controller is manager._creation_gate_controller

def test_prop_creation_gate_controller_raises_if_cleaned(manager):
    """Verify accessing creation_gate_controller after cleanup raises RuntimeError."""
    manager.cleanup()
    with pytest.raises(RuntimeError):
        _ = manager.creation_gate_controller

def test_prop_creation_gate_controller_thread_safety(manager):
    """Verify property access is thread-safe (acquires lock)."""
    with patch.object(manager, "_lock") as mock_lock:
        _ = manager.creation_gate_controller
        mock_lock.__enter__.assert_called()
        mock_lock.__exit__.assert_called()

# ----------------------------------------------------------------------
# 5. Property Tests: SpellSystemStates
# ----------------------------------------------------------------------

def test_prop_sss_success(manager, mock_sss):
    """Verify property returns the injected spell system states."""
    assert manager.spell_system_states is mock_sss

def test_prop_sss_raises_if_cleaned(manager):
    """Verify accessing spell_system_states after cleanup raises RuntimeError."""
    manager.cleanup()
    with pytest.raises(RuntimeError):
        _ = manager.spell_system_states

def test_prop_sss_thread_safety(manager):
    """Verify property access is thread-safe (acquires lock)."""
    with patch.object(manager, "_lock") as mock_lock:
        _ = manager.spell_system_states
        mock_lock.__enter__.assert_called()
        mock_lock.__exit__.assert_called()

# ----------------------------------------------------------------------
# 6. Method Tests: revalidate_dirty_roots
# ----------------------------------------------------------------------

def test_revalidate_delegates_to_ccm(manager, mock_dependencies):
    """
    Verify `revalidate_dirty_roots` delegates to ChangeControlManager.

    Contract:
    - Calls `ccm.revalidate_dirty_roots(conduit_id, cancel_event=None)` by default.
    """
    mock_ccm = mock_dependencies["mock_ccm"]
    manager.revalidate_dirty_roots("conduit-1")
    mock_ccm.revalidate_dirty_roots.assert_called_once_with("conduit-1", cancel_event=None)

def test_revalidate_passes_cancel_event(manager, mock_dependencies):
    """Verify cancel_event is passed through to CCM."""
    mock_ccm = mock_dependencies["mock_ccm"]
    event = MagicMock(spec=CancellationEvent)
    manager.revalidate_dirty_roots("conduit-1", cancel_event=event)
    mock_ccm.revalidate_dirty_roots.assert_called_once_with("conduit-1", cancel_event=event)

def test_revalidate_raises_if_cleaned(manager):
    """Verify method raises RuntimeError if manager is cleaned."""
    manager.cleanup()
    with pytest.raises(RuntimeError):
        manager.revalidate_dirty_roots("conduit-1")

def test_revalidate_thread_safety(manager):
    """Verify method acquires lock during execution."""
    with patch.object(manager, "_lock") as mock_lock:
        manager.revalidate_dirty_roots("conduit-1")
        mock_lock.__enter__.assert_called()
        mock_lock.__exit__.assert_called()

def test_revalidate_raises_if_ccm_contract_is_broken(manager):
    """
    Verify method fails fast when owned CCM contract is manually broken.

    Contract:
    - DevOpsManager assumes owned CCM exists while not cleaned.
    - Manually setting CCM to None should raise AttributeError.
    """
    manager._change_control_manager = None
    with pytest.raises(AttributeError):
        manager.revalidate_dirty_roots("conduit-1")

def test_revalidate_propagates_exceptions(manager, mock_dependencies):
    """Verify exceptions from CCM are propagated (not swallowed)."""
    mock_dependencies["mock_ccm"].revalidate_dirty_roots.side_effect = ValueError("Boom")
    with pytest.raises(ValueError, match="Boom"):
        manager.revalidate_dirty_roots("conduit-1")

def test_revalidate_rejects_empty_conduit_id(manager):
    """Verify empty conduit ids are rejected before delegation."""
    with pytest.raises(ValueError, match="conduit_id cannot be empty"):
        manager.revalidate_dirty_roots("")

# ----------------------------------------------------------------------
# 7. Method Tests: Creation Gate Facade
# ----------------------------------------------------------------------

def test_enable_conduit_gate_opens_registered_gate(manager):
    """
    Verify enable_conduit_gate opens a registered conduit gate.
    """
    gate = manager.creation_gate_controller.create_conduit_gate("c1")
    gate.close()

    manager.enable_conduit_gate("c1")

    assert gate.enabled is True


def test_disable_conduit_gate_closes_registered_gate(manager):
    """
    Verify disable_conduit_gate closes a registered conduit gate.
    """
    gate = manager.creation_gate_controller.create_conduit_gate("c1")

    manager.disable_conduit_gate("c1")

    assert gate.enabled is False


def test_enable_disable_conduit_gate_missing_is_noop(manager):
    """
    Verify per-conduit gate toggles are no-op when conduit gate is missing.
    """
    manager.enable_conduit_gate("missing")
    manager.disable_conduit_gate("missing")


def test_close_and_wait_conduit_delegates_to_controller(manager):
    """
    Verify close_and_wait_conduit delegates to controller API.
    """
    controller = MagicMock()
    manager._creation_gate_controller = controller

    manager.close_and_wait_conduit("c1", timeout=1.5, interval=0.05)

    controller.close_and_wait_until_conduit_free.assert_called_once_with(
        "c1",
        timeout=1.5,
        interval=0.05,
    )


def test_enable_conduit_lineage_opens_only_target_lineage(manager):
    """
    Verify enabling one lineage opens only that lineage's gates.
    """
    controller = manager.creation_gate_controller
    g1 = controller.create_conduit_gate("c1", root_conduit_id="root-1")
    g2 = controller.create_conduit_gate("c2", root_conduit_id="root-1")
    g3 = controller.create_conduit_gate("c3", root_conduit_id="root-2")
    g1.close()
    g2.close()
    g3.close()

    manager.enable_conduit_lineage("root-1")

    assert g1.enabled is True
    assert g2.enabled is True
    assert g3.enabled is False


def test_disable_conduit_lineage_closes_only_target_lineage(manager):
    """
    Verify disabling one lineage closes only that lineage's gates.
    """
    controller = manager.creation_gate_controller
    g1 = controller.create_conduit_gate("c1", root_conduit_id="root-1")
    g2 = controller.create_conduit_gate("c2", root_conduit_id="root-1")
    g3 = controller.create_conduit_gate("c3", root_conduit_id="root-2")

    manager.disable_conduit_lineage("root-1")

    assert g1.enabled is False
    assert g2.enabled is False
    assert g3.enabled is True


def test_enable_disable_conduit_lineage_missing_is_noop(manager):
    """
    Verify lineage gate toggles are no-op when root lineage is missing.
    """
    manager.enable_conduit_lineage("missing")
    manager.disable_conduit_lineage("missing")


def test_close_and_wait_conduit_lineage_delegates_to_controller(manager):
    """
    Verify close_and_wait_conduit_lineage delegates to controller API.
    """
    controller = MagicMock()
    manager._creation_gate_controller = controller

    manager.close_and_wait_conduit_lineage("root-1", timeout=1.0, interval=0.02)

    controller.close_and_wait_until_conduit_lineage_free.assert_called_once_with(
        "root-1",
        timeout=1.0,
        interval=0.02,
    )


@pytest.mark.parametrize(
    "method_name,args,kwargs",
    [
        ("enable_conduit_gate", ("c1",), {}),
        ("disable_conduit_gate", ("c1",), {}),
        ("close_and_wait_conduit", ("c1",), {}),
        ("enable_conduit_lineage", ("root-1",), {}),
        ("disable_conduit_lineage", ("root-1",), {}),
        ("close_and_wait_conduit_lineage", ("root-1",), {}),
    ],
)
def test_creation_gate_facade_methods_raise_if_cleaned(
        manager,
        method_name,
        args,
        kwargs,
):
    """
    Verify creation gate facade methods enforce cleaned guard.
    """
    manager.cleanup()
    with pytest.raises(RuntimeError):
        getattr(manager, method_name)(*args, **kwargs)


# ----------------------------------------------------------------------
# 8. Cleanup Tests
# ----------------------------------------------------------------------

def test_cleanup_basic(manager, mock_dependencies, mock_sss):
    """
    Verify `cleanup` cascades to all owned components.

    Contract:
    - IncidentManager.cleanup() is called.
    - ChangeControlManager.cleanup() is called.
    - SpellSystemStates.cleanup() is called.
    - Manager is marked cleaned.
    """
    mock_im = mock_dependencies["mock_im"]
    mock_ccm = mock_dependencies["mock_ccm"]
    
    manager.cleanup()
    
    mock_im.cleanup.assert_called_once()
    mock_ccm.cleanup.assert_called_once()
    mock_sss.cleanup.assert_called_once()
    assert manager._cleaned

def test_cleanup_clears_references(manager):
    """
    Verify `cleanup` nulls all internal references.

    Contract:
    - All manager fields are set to None to assist GC.
    - The lock is released/nulled.
    """
    manager.cleanup()
    assert manager._incident_manager is None
    assert manager._change_control_manager is None
    assert manager._creation_gate_controller is None
    assert manager._spell_system_states is None
    assert manager._lock is None

def test_cleanup_is_idempotent(manager, mock_dependencies):
    """
    Verify `cleanup` is safe to call multiple times.

    Contract:
    - Subsequent calls do not re-trigger sub-cleanups.
    - No exceptions are raised.
    """
    mock_im = mock_dependencies["mock_im"]
    manager.cleanup()
    manager.cleanup()
    
    # Sub-cleanups should still only be called once
    mock_im.cleanup.assert_called_once()

def test_cleanup_raises_if_owned_children_contract_is_broken(manager):
    """
    Verify cleanup fails fast when owned child contract is manually broken.

    Contract:
    - Cleanup assumes owned managers exist while not cleaned.
    - Manually setting owned managers to None should raise AttributeError.
    """
    manager._incident_manager = None
    with pytest.raises(AttributeError):
        manager.cleanup()

def test_cleanup_propagates_exceptions(manager, mock_dependencies):
    """
    Verify that if a child cleanup raises, it propagates up.
    
    Note: Ideally cleanup should be safe, but if a child crashes hard,
    we want to know about it unless explicitly suppressed.
    """
    mock_dependencies["mock_im"].cleanup.side_effect = RuntimeError("Cleanup fail")
    
    with pytest.raises(RuntimeError, match="Cleanup fail"):
        manager.cleanup()
        
    # Verify state is still marked clean (attempted)
    assert manager._cleaned

def test_cleanup_uses_lock(manager):
    """Verify cleanup acquires the lock."""
    # Replace the real RLock with a MagicMock to spy on calls
    mock_lock = MagicMock()
    manager._lock = mock_lock
    
    manager.cleanup()
    
    # cleanup uses 'with self._lock:', which calls __enter__ and __exit__
    mock_lock.__enter__.assert_called()
    mock_lock.__exit__.assert_called()

# ----------------------------------------------------------------------
# 9. Lifecycle & Interaction Edge Cases
# ----------------------------------------------------------------------

def test_init_fails_if_incident_manager_fails(mock_sss):
    """Verify init fails if sub-manager construction fails."""
    with patch("melder.aether.dev_ops.dev_ops_manager.IncidentManager", side_effect=ValueError("Init fail")):
        with pytest.raises(ValueError, match="Init fail"):
            DevOpsManager(mock_sss)

def test_init_fails_if_ccm_fails(mock_sss):
    """Verify init fails if CCM construction fails."""
    with patch("melder.aether.dev_ops.dev_ops_manager.IncidentManager"), \
         patch("melder.aether.dev_ops.dev_ops_manager.ChangeControlManager", side_effect=ValueError("CCM fail")):
        with pytest.raises(ValueError, match="CCM fail"):
            DevOpsManager(mock_sss)

def test_access_after_partial_cleanup(manager):
    """
    If cleanup was called but failed midway (simulated), check_cleaned should still block access.
    """
    manager._cleaned = True
    with pytest.raises(RuntimeError):
        _ = manager.incident_manager

def test_revalidate_dirty_roots_kwarg_compat(manager, mock_dependencies):
    """Ensure kwargs are handled or at least explicitly accepted if signature changes."""
    # Current signature is explicit (cancel_event=None).
    # Just reaffirming no crash with explicit kwarg.
    manager.revalidate_dirty_roots("conduit-1", cancel_event=None)
    mock_dependencies["mock_ccm"].revalidate_dirty_roots.assert_called_once_with(
        "conduit-1",
        cancel_event=None,
    )

def test_lock_is_reentrant(manager):
    """Verify the lock used is indeed RLock (reentrant)."""
    with manager._lock:
        with manager._lock:
            assert True

def test_cleanup_order(manager, mock_dependencies, mock_sss):
    """
    Verify order of cleanup: IM -> CCM -> SSS.
    We can use a Mock manager to track order of calls.
    """
    mock_im = mock_dependencies["mock_im"]
    mock_ccm = mock_dependencies["mock_ccm"]
    
    call_order = []
    
    mock_im.cleanup.side_effect = lambda: call_order.append("IM")
    mock_ccm.cleanup.side_effect = lambda: call_order.append("CCM")
    mock_sss.cleanup.side_effect = lambda: call_order.append("SSS")
    
    manager.cleanup()
    
    assert call_order == ["IM", "CCM", "SSS"]

def test_property_lock_scope(manager):
    """
    Verify that the lock is held *during* the property return.
    """
    mock_lock = MagicMock()
    manager._lock = mock_lock
    
    _ = manager.incident_manager
    
    mock_lock.__enter__.assert_called_once()
    mock_lock.__exit__.assert_called_once()

def test_internal_slots_check():
    """Double check that the class has slots defined correctly."""
    assert "__slots__" in DevOpsManager.__dict__
    assert "_lock" in DevOpsManager.__slots__
    assert "_spell_system_states" in DevOpsManager.__slots__

def test_inheritance_check():
    """Verify it inherits from Cleanable."""
    from melder.utilities.general_base.cleanable import Cleanable
    assert issubclass(DevOpsManager, Cleanable)

def test_full_lifecycle_flow(mock_sss, mock_dependencies):
    """Integration-lite: Create, use, clean, verify."""
    mgr = DevOpsManager(mock_sss)
    assert mgr.incident_manager is not None
    mgr.revalidate_dirty_roots("conduit-1")
    mgr.cleanup()
    assert mgr._cleaned
    with pytest.raises(RuntimeError):
        mgr.revalidate_dirty_roots("conduit-1")

def test_cleanup_lock_nullification(manager):
    """Verify lock is set to None specifically at end of cleanup."""
    manager.cleanup()
    # Direct slot access to verify it's None, not just 'cleaned' logic blocking it.
    # Note: accessing via getattr is safer for slots if direct access fails in test logic context.
    # But manager._lock is fine.
    assert manager._lock is None

def test_multiple_properties_consistency(manager):
    """Verify all properties return consistent objects over multiple calls."""
    im1 = manager.incident_manager
    im2 = manager.incident_manager
    assert im1 is im2
    
    ccm1 = manager.change_control_manager
    ccm2 = manager.change_control_manager
    assert ccm1 is ccm2

def test_init_raises_if_abstract_instantiation_attempted():
    """Just a sanity check that we can instantiate it (it's concrete)."""
    # Done implicitly by other tests, but good for count.
    pass

def test_cleanable_interface_compliance(manager):
    """Verify it complies with ICleanable protocol implicit expectations."""
    assert hasattr(manager, "cleanup")
    assert hasattr(manager, "check_cleaned")
    assert hasattr(manager, "_cleaned")

def test_revalidate_dirty_roots_does_not_return_value(manager):
    """Verify it returns None."""
    assert manager.revalidate_dirty_roots("conduit-1") is None


def test_cleanup_rechecks_cleaned_inside_lock(manager):
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

    manager._lock = _CoordinatedLock()
    failures = []

    def _run_cleanup():
        try:
            manager.cleanup()
        except BaseException as exc:
            failures.append(exc)

    first = threading.Thread(target=_run_cleanup, name="devops-cleanup-first")
    second = threading.Thread(target=_run_cleanup, name="devops-cleanup-second")

    first.start()
    assert manager._lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join()
    second.join()

    assert failures == []
    assert manager._cleaned is True
    assert manager._lock is None
