from melder.aether.aetheric_frame import AethericFrame
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.incident_manager.incident_status import IncidentStatus


def test_component_incident_manager_cleanup_through_frame_cleans_incident() -> None:
    """
    Purpose:
        Validate incidents are cleaned when the owning frame is cleaned.
    Contract:
        - Frame cleanup cascades to DevOpsManager and IncidentManager.
        - Created incidents are cleaned as part of IncidentManager cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clean incident objects.
    """
    frame = AethericFrame("component-incident-cleanup")
    incident_manager = frame.dev_ops_manager.incident_manager
    incident = incident_manager.create_incident(
        kind="validation_failed",
        severity=IncidentSeverity.error,
        summary="validation failed",
    )
    frame.cleanup()
    assert incident_manager.cleaned is True
    assert incident.cleaned is True


def test_component_incident_manager_shared_reference_in_devops() -> None:
    """
    Purpose:
        Validate DevOpsManager exposes a stable IncidentManager reference.
    Contract:
        - Multiple accesses return the same IncidentManager instance.
        - Incidents created via one reference are visible via another.
    Returns:
        None.
    Raises:
        AssertionError: If incident manager references diverge.
    """
    frame = AethericFrame("component-incident-shared")
    devops = frame.dev_ops_manager
    manager_a = devops.incident_manager
    manager_b = devops.incident_manager
    incident = manager_a.create_incident(
        kind="graph_dirty",
        severity=IncidentSeverity.warning,
        summary="graph dirty",
    )
    try:
        assert manager_a is manager_b
        incidents = manager_b.list_incidents(status=IncidentStatus.open)
        assert incidents == [incident]
    finally:
        frame.cleanup()
