from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_status import IncidentStatus
from melder.aether.spellbook.bind.spell_index import SpellIndex


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
    frame = AethericFrame(Aether(), "component-incident-cleanup")
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
    frame = AethericFrame(Aether(), "component-incident-shared")
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


def test_component_incident_manager_filters_by_status_kind_and_lineage() -> None:
    """
    Purpose:
        Validate incident filters against real Incident objects.
    Contract:
        - kind and status filters return only matching incidents.
        - spell_index_id filter returns only incidents for that lineage.
    Returns:
        None.
    Raises:
        AssertionError: If filters return incorrect incidents.
    """
    frame = AethericFrame(Aether(), "component-incident-filters")
    manager = frame.dev_ops_manager.incident_manager
    lineage = SpellIndex("spell-incident-filter")
    try:
        inc_a = manager.create_incident(
            kind="validation_failed",
            severity=IncidentSeverity.error,
            summary="validation failed",
            spell_index_id=lineage.id,
        )
        inc_b = manager.create_incident(
            kind="graph_dirty",
            severity=IncidentSeverity.warning,
            summary="graph dirty",
        )
        inc_c = manager.create_incident(
            kind="validation_failed",
            severity=IncidentSeverity.info,
            summary="validation warning",
            spell_index_id=lineage.id,
        )

        inc_a.acknowledge()
        inc_b.resolve()

        by_kind = {inc.id for inc in manager.list_incidents(kind="validation_failed")}
        assert by_kind == {inc_a.id, inc_c.id}

        by_status = {inc.id for inc in manager.list_incidents(status=IncidentStatus.open)}
        assert by_status == {inc_c.id}

        by_lineage = {inc.id for inc in manager.list_incidents(spell_index_id=lineage.id)}
        assert by_lineage == {inc_a.id, inc_c.id}
    finally:
        frame.cleanup()


def test_component_incident_manager_list_is_snapshot() -> None:
    """
    Purpose:
        Validate list_incidents returns a detached snapshot list.
    Contract:
        - Mutating the returned list does not change the registry.
    Returns:
        None.
    Raises:
        AssertionError: If list mutations affect the registry.
    """
    frame = AethericFrame(Aether(), "component-incident-list-snapshot")
    manager = frame.dev_ops_manager.incident_manager
    try:
        incident = manager.create_incident(
            kind="snapshot",
            severity=IncidentSeverity.info,
            summary="snapshot",
        )
        snapshot = manager.list_incidents()
        snapshot.clear()
        current = manager.list_incidents()
        assert current == [incident]
    finally:
        frame.cleanup()


def test_component_incident_manager_get_unknown_returns_none() -> None:
    """
    Purpose:
        Validate get_incident returns None for unknown ids.
    Contract:
        - Missing incident ids return None.
    Returns:
        None.
    Raises:
        AssertionError: If get_incident does not return None.
    """
    frame = AethericFrame(Aether(), "component-incident-missing")
    manager = frame.dev_ops_manager.incident_manager
    try:
        assert manager.get_incident("missing-id") is None
    finally:
        frame.cleanup()


def test_component_incident_manager_allocates_sequential_ids() -> None:
    """
    Purpose:
        Validate manager-owned incident ids advance sequentially.
    Contract:
        - Fresh managers allocate `inc-1`, `inc-2`, ... in order.
    Returns:
        None.
    Raises:
        AssertionError: If incident ids drift from the sequential contract.
    """
    frame = AethericFrame(Aether(), "component-incident-sequence")
    manager = frame.dev_ops_manager.incident_manager
    try:
        inc_a = manager.create_incident(
            kind="first",
            severity=IncidentSeverity.info,
            summary="first",
        )
        inc_b = manager.create_incident(
            kind="second",
            severity=IncidentSeverity.info,
            summary="second",
        )
        assert inc_a.id == "inc-1"
        assert inc_b.id == "inc-2"
    finally:
        frame.cleanup()


def test_component_incident_manager_details_and_root_ids_are_detached_snapshots() -> None:
    """
    Purpose:
        Validate incident details and root ids are detached from caller mutation.
    Contract:
        - The incident copies incoming details/root ids at creation.
        - Returned snapshots are detached from incident-owned state.
    Returns:
        None.
    Raises:
        AssertionError: If caller mutation leaks into incident state.
    """
    frame = AethericFrame(Aether(), "component-incident-detached")
    manager = frame.dev_ops_manager.incident_manager
    details = {"phase": 4}
    root_ids = ["root-a"]
    try:
        incident = manager.create_incident(
            kind="detached",
            severity=IncidentSeverity.warning,
            summary="detached",
            root_ids=root_ids,
            details=details,
        )
        details["phase"] = 5
        root_ids.append("root-b")

        detail_snapshot = incident.details
        roots_snapshot = incident.root_ids
        detail_snapshot["phase"] = 6
        roots_snapshot.append("root-c")

        assert incident.details == {"phase": 4}
        assert incident.root_ids == ["root-a"]
    finally:
        frame.cleanup()


def test_component_incident_manager_status_transitions_flow_through_filters() -> None:
    """
    Purpose:
        Validate incident status transitions flow through real manager filters.
    Contract:
        - Acknowledged, resolved, and suppressed incidents leave the open filter.
    Returns:
        None.
    Raises:
        AssertionError: If status transitions are not reflected in filters.
    """
    frame = AethericFrame(Aether(), "component-incident-status-flow")
    manager = frame.dev_ops_manager.incident_manager
    try:
        inc_open = manager.create_incident(
            kind="open",
            severity=IncidentSeverity.info,
            summary="open",
        )
        inc_ack = manager.create_incident(
            kind="ack",
            severity=IncidentSeverity.info,
            summary="ack",
        )
        inc_resolved = manager.create_incident(
            kind="resolved",
            severity=IncidentSeverity.info,
            summary="resolved",
        )
        inc_suppressed = manager.create_incident(
            kind="suppressed",
            severity=IncidentSeverity.info,
            summary="suppressed",
        )

        inc_ack.acknowledge()
        inc_resolved.resolve()
        inc_suppressed.suppress()

        open_ids = {
            incident.id
            for incident in manager.list_incidents(status=IncidentStatus.open)
        }
        assert open_ids == {inc_open.id}
    finally:
        frame.cleanup()


def test_component_incident_manager_devops_registry_property_matches_frame_registry() -> None:
    """
    Purpose:
        Validate IncidentManager exposes the borrowed frame-owned registry surface.
    Contract:
        - devops_information_registry is the same object owned by the frame.
    Returns:
        None.
    Raises:
        AssertionError: If the borrowed registry reference drifts.
    """
    frame = AethericFrame(Aether(), "component-incident-registry")
    manager = frame.dev_ops_manager.incident_manager
    try:
        assert manager.devops_information_registry is frame.devops_information_registry
    finally:
        frame.cleanup()

