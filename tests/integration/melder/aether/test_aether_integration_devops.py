from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.incident_manager.incident_status import IncidentStatus
from melder.aether.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.aether.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_configuration(
    *,
    aether_frame: str = "default",
    dynamic: bool = False,
    workers: int = 1,
) -> SpellbookConfiguration:
    """
    Purpose:
        Create a configuration for Aether integration tests.
    Contract:
        - system_state is set to automatic or dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        dynamic: Whether to use dynamic defaults.
        workers: Scheduler workers per spellbook.
    Returns:
        SpellbookConfiguration: Configured instance.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def test_aether_incident_manager_filters_and_transitions() -> None:
    """
    Purpose:
        Validate IncidentManager lifecycle and filter behavior.
    Contract:
        - Incidents can be created and retrieved by id.
        - Status transitions are reflected in list filters.
        - Kind and lineage filters return matching incidents.
    Returns:
        None.
    Raises:
        AssertionError: If incident registry behavior is incorrect.
    """
    frame_name = "frame-incidents"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    spell_index = next(iter(book._spells.keys()))
    aether = Aether()
    manager = aether._get_incident_manager(frame_name)

    inc_a = manager.create_incident(
        kind="validation_failed",
        severity=IncidentSeverity.error,
        summary="validation failed",
        spell_index_id=spell_index.id,
        root_ids=[spell_id],
        details={"ticket": "INC-1"},
    )
    inc_b = manager.create_incident(
        kind="slow_path",
        severity=IncidentSeverity.warning,
        summary="slow path",
        details={"ticket": "INC-2"},
    )

    assert manager.get_incident(inc_a.id) is inc_a
    assert inc_a in manager.list_incidents(kind="validation_failed")
    assert inc_b in manager.list_incidents(kind="slow_path")

    inc_a.acknowledge()
    assert inc_a in manager.list_incidents(status=IncidentStatus.acknowledged)

    inc_a.resolve()
    assert inc_a in manager.list_incidents(status=IncidentStatus.resolved)
    assert inc_a in manager.list_incidents(spell_index_id=spell_index.id)

    book.cleanup()


def test_aether_change_control_pending_changes_round_trip() -> None:
    """
    Purpose:
        Validate ChangeControlManager pending change lifecycle.
    Contract:
        - register_pending_change stores metadata.
        - get_pending_change and list_pending_changes return entries.
        - clear_pending_change removes the entry.
    Returns:
        None.
    Raises:
        AssertionError: If pending change tracking is incorrect.
    """
    frame_name = "frame-changes"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    spell_index = next(iter(book._spells.keys()))
    aether = Aether()
    ccm = aether._get_change_control_manager(frame_name)

    ccm.register_pending_change(
        spell_index,
        reason="mutation_candidate",
        metadata={"ticket": "T-1"},
    )
    entry = ccm.get_pending_change(spell_index.id)
    assert entry is not None
    assert entry["reason"] == "mutation_candidate"
    assert entry["ticket"] == "T-1"
    assert spell_index.id in ccm.list_pending_changes()

    ccm.clear_pending_change(spell_index.id)
    assert ccm.get_pending_change(spell_index.id) is None

    book.cleanup()


def test_aether_spell_system_states_dependency_and_impact_closure() -> None:
    """
    Purpose:
        Validate dependency wiring and impact closure in SpellSystemStates.
    Contract:
        - update_dependencies attaches dependencies and reverse edges.
        - compute_impact_closure marks downstream lineages transitively dirty.
    Returns:
        None.
    Raises:
        AssertionError: If dependency or impact tracking is incorrect.
    """
    frame_name = "frame-states"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    config_id = book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_index = next(
        idx for idx in book._spells.keys() if idx.current == config_id
    )
    service_index = next(
        idx for idx in book._spells.keys() if idx.current == service_id
    )
    aether = Aether()
    states = aether._get_spell_system_states(frame_name)

    states.update_dependencies(service_index, [config_id])
    service_state = states.get_by_index_id(service_index.id)
    config_state = states.get_by_index_id(config_index.id)
    assert service_state is not None
    assert config_state is not None
    assert config_id in service_state.direct_dependencies
    assert service_index.id in config_state.direct_dependents

    impacted = states.compute_impact_closure([config_index.id])
    assert impacted == {config_index.id, service_index.id}
    assert states.get_by_index_id(service_index.id).transitively_dirty is True

    book.cleanup()


def test_aether_spell_system_states_update_dependencies_removes_reverse_edges() -> None:
    """
    Purpose:
        Validate dependency updates remove reverse edges when detached.
    Contract:
        - Removing dependencies clears reverse dependent links.
    Returns:
        None.
    Raises:
        AssertionError: If reverse edges are not removed.
    """
    frame_name = "frame-dep-removal"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    config_id = book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_index = next(
        idx for idx in book._spells.keys() if idx.current == config_id
    )
    service_index = next(
        idx for idx in book._spells.keys() if idx.current == service_id
    )
    aether = Aether()
    states = aether._get_spell_system_states(frame_name)

    states.update_dependencies(service_index, [config_id])
    config_state = states.get_by_index_id(config_index.id)
    assert config_state is not None
    assert service_index.id in config_state.direct_dependents

    states.update_dependencies(service_index, [])
    config_state = states.get_by_index_id(config_index.id)
    assert config_state is not None
    assert service_index.id not in config_state.direct_dependents

    book.cleanup()


def test_aether_spell_system_states_local_topology_round_trip() -> None:
    """
    Purpose:
        Validate local topology registration and retrieval.
    Contract:
        - register_local_topology stores the topology by spell id.
        - get_local_topology and get_local_topology_by_id return it.
    Returns:
        None.
    Raises:
        AssertionError: If topology registration is incorrect.
    """
    frame_name = "frame-topology"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    spell_index = next(
        idx for idx in book._spells.keys() if idx.current == spell_id
    )
    aether = Aether()
    states = aether._get_spell_system_states(frame_name)

    socket = SpellSocketDescriptor(
        spell_id=spell_id,
        param_name="dep",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=(),
    )
    topology = SpellLocalTopology(spell_id=spell_id, sockets=[socket])
    try:
        states.register_local_topology(spell_index, topology)
        assert states.get_local_topology(spell_index) is topology
        assert states.get_local_topology_by_id(spell_id) is topology
    finally:
        topology.cleanup()
        book.cleanup()


def test_aether_spell_system_states_consume_dirty_indexes() -> None:
    """
    Purpose:
        Validate dirty lineage consumption clears the queue.
    Contract:
        - Newly registered lineages appear in the dirty list.
        - consume_dirty_indexes clears the dirty set.
    Returns:
        None.
    Raises:
        AssertionError: If dirty lineage consumption is incorrect.
    """
    frame_name = "frame-dirty"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    aether = Aether()
    states = aether._get_spell_system_states(frame_name)
    expected_ids = {idx.id for idx in book._spells.keys()}

    dirty = set(states.consume_dirty_indexes())
    assert expected_ids.issubset(dirty)
    assert states.consume_dirty_indexes() == []

    book.cleanup()


def test_aether_devops_revalidate_pipeline_from_states() -> None:
    """
    Purpose:
        Validate the devops pipeline from states to dirty-root revalidation.
    Contract:
        - SpellSystemStates dependencies and topologies build root blueprints.
        - ChangeControlManager maps component_of from blueprints.
        - Dirty roots are revalidated through DevOpsManager.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are not revalidated.
    """
    frame_name = "frame-devops-pipeline"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    config_id = book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_index = next(
        idx for idx in book._spells.keys() if idx.current == config_id
    )
    service_index = next(
        idx for idx in book._spells.keys() if idx.current == service_id
    )
    aether = Aether()
    states = aether._get_spell_system_states(frame_name)
    devops = aether._get_devops_manager(frame_name)
    conduit_id = "conduit-1"

    socket = SpellSocketDescriptor(
        spell_id=service_id,
        param_name="config",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=(config_id,),
    )
    topology = SpellLocalTopology(spell_id=service_id, sockets=[socket])
    blueprints: dict[str, object] = {}
    calls: list[set[str]] = []

    def _revalidate(dirty_roots: set[str], _cancel_event) -> None:
        calls.append(set(dirty_roots))

    try:
        states.update_dependencies(service_index, [config_id])
        states.register_local_topology(service_index, topology)
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        devops.change_control_manager.rebuild_component_of(conduit_id, blueprints)
        devops.change_control_manager.set_revalidator(conduit_id, _revalidate)

        devops.change_control_manager.notify_spell_changed(config_id)
        assert devops.change_control_manager.is_root_dirty(conduit_id, service_id) is True

        devops.revalidate_dirty_roots(conduit_id)
        assert calls == [{service_id}]
        assert devops.change_control_manager.is_root_dirty(conduit_id, service_id) is False
    finally:
        for blueprint in blueprints.values():
            blueprint.cleanup()
        topology.cleanup()
        book.cleanup()

