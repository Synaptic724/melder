import pytest
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_manager import IncidentManager
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident import Incident
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_status import IncidentStatus
from tests._cleanup_recheck_support import CleanupRecheckHandshake

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def registry():
    registry = DevopsInformationRegistry("test-frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def manager(registry):
    return IncidentManager(registry)

# ----------------------------------------------------------------------
# 1. Initialization
# ----------------------------------------------------------------------

def test_init_success(manager):
    assert len(manager._incidents_by_id) == 0
    assert manager._next_numeric_id == 1
    assert not manager._cleaned

# ----------------------------------------------------------------------
# 2. Creation
# ----------------------------------------------------------------------

def test_create_incident_success(manager):
    """
    Verify creating an incident registers it correctly.

    Contract:
    - Returns a new Incident instance.
    - Incident is added to the internal registry.
    - ID format matches expected pattern.
    """
    inc = manager.create_incident(
        kind="test",
        severity=IncidentSeverity.info,
        summary="A test incident"
    )
    
    assert isinstance(inc, Incident)
    assert inc.id.startswith("inc-")
    assert inc.kind == "test"
    
    # Verify it's in registry
    assert manager.get_incident(inc.id) is inc

def test_create_increments_id(manager):
    """
    Verify incident IDs are unique and incrementing.

    Contract:
    - Each call to `create_incident` generates a unique ID.
    - IDs are strictly increasing.
    """
    i1 = manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s")
    i2 = manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s")
    
    assert i1.id != i2.id
    # Assuming standard numeric increment: inc-1, inc-2
    assert int(i1.id.split("-")[1]) < int(i2.id.split("-")[1])

def test_create_incident_validates_inputs(manager):
    with pytest.raises(ValueError):
        manager.create_incident(kind="", severity=IncidentSeverity.info, summary="s")

# ----------------------------------------------------------------------
# 3. Retrieval & Listing
# ----------------------------------------------------------------------

def test_get_incident_found(manager):
    inc = manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s")
    found = manager.get_incident(inc.id)
    assert found is inc

def test_get_incident_not_found(manager):
    assert manager.get_incident("inc-999") is None

def test_list_incidents_all(manager):
    manager.create_incident(kind="k1", severity=IncidentSeverity.info, summary="s1")
    manager.create_incident(kind="k2", severity=IncidentSeverity.info, summary="s2")
    
    all_incs = manager.list_incidents()
    assert len(all_incs) == 2

def test_list_incidents_filter_status(manager):
    """
    Verify listing incidents filtered by status.

    Contract:
    - Only incidents matching the requested status are returned.
    """
    i1 = manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s")
    i2 = manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s")
    
    i1.resolve() # status = resolved
    # i2 is open
    
    resolved = manager.list_incidents(status=IncidentStatus.resolved)
    assert len(resolved) == 1
    assert resolved[0] is i1
    
    open_incs = manager.list_incidents(status=IncidentStatus.open)
    assert len(open_incs) == 1
    assert open_incs[0] is i2

def test_list_incidents_filter_kind(manager):
    """
    Verify listing incidents filtered by kind.

    Contract:
    - Only incidents matching the requested kind are returned.
    """
    manager.create_incident(kind="k1", severity=IncidentSeverity.info, summary="s")
    manager.create_incident(kind="k2", severity=IncidentSeverity.info, summary="s")
    
    k1_list = manager.list_incidents(kind="k1")
    assert len(k1_list) == 1
    assert k1_list[0].kind == "k1"

def test_list_incidents_filter_spell_index(manager):
    """
    Verify listing incidents filtered by lineage ID.

    Contract:
    - Only incidents associated with the given spell_index_id are returned.
    """
    manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s", spell_index_id="s1")
    manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s", spell_index_id="s2")
    
    s1_list = manager.list_incidents(spell_index_id="s1")
    assert len(s1_list) == 1
    assert s1_list[0].spell_index_id == "s1"

# ----------------------------------------------------------------------
# 4. Cleanup
# ----------------------------------------------------------------------

def test_cleanup_clears_registry_and_incidents(manager):
    """
    Verify cleanup disposes of the manager and all its children.

    Contract:
    - All owned incidents have `cleanup()` called on them.
    - The registry is cleared and nulled.
    - The manager is marked as cleaned.
    """
    inc = manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s")
    
    manager.cleanup()
    
    assert manager._cleaned
    assert not hasattr(manager, '_incidents_by_id')
    
    # Check that the incident itself was cleaned
    assert inc._cleaned

def test_cleanup_idempotent(manager):
    manager.cleanup()
    manager.cleanup()

def test_methods_raise_after_cleanup(manager):
    manager.cleanup()
    
    with pytest.raises((RuntimeError, AttributeError)):
        manager.create_incident(kind="k", severity=IncidentSeverity.info, summary="s")
        
    with pytest.raises((RuntimeError, AttributeError)):
        manager.get_incident("inc-1")
        
    with pytest.raises((RuntimeError, AttributeError)):
        manager.list_incidents()


def test_cleanup_rechecks_cleaned_inside_lock(manager: IncidentManager) -> None:
    """
    Verify the inner cleanup re-check under concurrent teardown.

    Contract:
    - A second cleanup caller may pass the outer `_cleaned` check.
    - The inner `_cleaned` check inside the lock returns safely without error.
    - The handshake holds the first caller inside the lock until the second has passed the outer check and is
      about to block; the first caller then runs the real cleanup, and the second must return at the inner check.
      Without that check the teardown would run twice and a caller would raise on an attribute the other had
      already deleted.
    - Both callers must finish without raising; the manager must read cleaned with its `_lock` dropped.
    - The callers are ordered by the handshake, not by timing: the earlier hand-made lock could lose its signal
      and failed on CI (GitHub #206; TASK-2026-11-08-deterministic_cleanup_recheck_handshake).

    Args:
        manager: A live incident manager from the `manager` fixture.

    Returns:
        None.
    """
    handshake = CleanupRecheckHandshake()
    manager._lock = handshake.lock

    handshake.run(manager.cleanup)

    assert manager._cleaned is True
    assert not hasattr(manager, '_lock')
