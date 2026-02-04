import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.spellbook.spell_crafter.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spell_system() -> None:
    """
    Purpose:
        Ensure component spell-system tests start with a clean Aether singleton.
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


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook to search.
        spell_id: Versioned spell id to match.
    Returns:
        Spell: The resolved spell or None.
    """
    for spell in spellbook._spells.values():
        if spell.spell_index.current == spell_id:
            return spell
    return None


def _build_system_validation_artifacts(
    spellbook: Spellbook,
) -> tuple[str, str, dict[str, object], SpellSystemIndex, object]:
    """
    Purpose:
        Build shared system-validation artifacts from real spell execution.
    Contract:
        - Returns a root id, dependency id, blueprints, index, and system states.
        - Index dependencies mirror the adjacency snapshot.
    Args:
        spellbook: Spellbook configured for component tests.
    Returns:
        tuple: (root_id, dependency_id, blueprints, index, system_states).
    """

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    service_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
    assert consumer_spell is not None

    consumer_spell.run_phase_requirements()
    consumer_spell.run_phase_symbolic_graph()
    consumer_spell.run_phase_local_frame()

    states = spellbook._spell_system_states
    assert states is not None
    snapshot = SpellSystemAdjacencyBuilder.build(states)
    blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)

    index = SpellSystemIndex()
    spell_index_by_id = {
        spell_index.current: spell_index for spell_index, _spell in spellbook.spells.items()
    }
    for spell_id in snapshot.all_spell_ids:
        spell_index = spell_index_by_id.get(spell_id)
        lineage_id = spell_index.id if spell_index is not None else f"lineage-{spell_id}"
        deps = snapshot.dependencies.get(spell_id, set())
        node = SpellSystemNode(
            spell_id=spell_id,
            lineage_id=lineage_id,
            dependencies=deps,
        )
        index.upsert_node(node)

    return consumer_id, service_id, blueprints, index, states


def test_component_spell_system_builds_snapshot_from_states() -> None:
    """
    Purpose:
        Validate the adjacency snapshot reflects live SpellSystemStates.
    Contract:
        - Direct dependencies for a consumer are captured.
        - Root detection marks the consumer as a root.
        - Local topologies for resolved spells are included.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot data does not reflect system states.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        states = spellbook._spell_system_states
        assert states is not None
        snapshot = SpellSystemAdjacencyBuilder.build(states)

        assert snapshot.dependencies[consumer_id] == {service_id}
        assert snapshot.dependencies[service_id] == set()
        assert snapshot.root_spell_ids == {consumer_id}
        assert consumer_id in snapshot.topologies
    finally:
        spellbook.cleanup()


def test_component_spell_system_builds_root_blueprint_from_snapshot() -> None:
    """
    Purpose:
        Validate root blueprints are compiled from live system snapshots.
    Contract:
        - Deep DAG includes both consumer and dependency nodes.
        - Socket refs and DagIndex are populated from local topology.
    Returns:
        None.
    Raises:
        AssertionError: If blueprint structure or socket indexing is missing.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        states = spellbook._spell_system_states
        assert states is not None
        snapshot = SpellSystemAdjacencyBuilder.build(states)

        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        blueprint = blueprints[consumer_id]
        blueprint.ensure_dag_index_built()

        assert set(blueprint.dag.nodes) == {consumer_id, service_id}
        ordered = blueprint.ordered_node_ids
        assert ordered[-1] == consumer_id

        sockets = blueprint.socket_refs
        assert len(sockets) == 1
        socket = sockets[0]
        assert socket.node_id == consumer_id
        assert socket.param_name == "service"
        path_registry = blueprint.path_registry
        assert path_registry.materialize_path(socket.param_path_id) == ("service",)

        by_path = blueprint.dag_index.get_by_exact_path(("service",))
        assert by_path and by_path[0] == socket
    finally:
        spellbook.cleanup()


def test_component_spell_system_validation_marks_states_valid() -> None:
    """
    Purpose:
        Validate system validation updates conduit resolution entries.
    Contract:
        - Conduit resolution validity is marked valid when no errors exist.
    Returns:
        None.
    Raises:
        AssertionError: If system validity is not updated on the live state.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Provide a minimal leaf spell.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the leaf spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    try:
        leaf_id = spellbook.bind(
            spell=Leaf,
            existence=Existence.unique,
            permissions="create",
        )
        leaf_spell = _get_spell_by_version_id(spellbook, leaf_id)
        assert leaf_spell is not None

        index = SpellSystemIndex()
        node = SpellSystemNode(
            spell_id=leaf_id,
            lineage_id=leaf_spell.spell_index.id,
        )
        index.upsert_node(node)

        states = spellbook._spell_system_states
        assert states is not None

        system = SpellSystemValidationSystem([])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        assert result.is_valid is True
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(leaf_id) is SpellValidity.valid
    finally:
        spellbook.cleanup()


def test_component_spell_system_validation_reports_socket_ref_duplicate() -> None:
    """
    Purpose:
        Validate socket ref duplication is detected by system validation.
    Contract:
        - socket_ref_duplicate is reported when a SocketRef is duplicated.
        - Conduit resolution validity is invalid when an error is present.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate socket refs are not detected.
    """
    spellbook = _make_spellbook()
    try:
        root_id, dependency_id, blueprints, index, states = _build_system_validation_artifacts(
            spellbook
        )
        blueprint = blueprints[root_id]
        socket = blueprint.socket_refs[0]
        blueprint.add_socket_ref(socket)

        system = SpellSystemValidationSystem([SocketRefSanityStrategy()])
        try:
            result = system.validate(
                index=index,
                blueprints=blueprints,
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "socket_ref_duplicate" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dependency_id) is SpellValidity.invalid
    finally:
        spellbook.cleanup()


def test_component_spell_system_validation_reports_orphan_socket_ref() -> None:
    """
    Purpose:
        Validate orphan DagIndex sockets are detected by system validation.
    Contract:
        - dag_index_orphan_socket is reported when the index contains a socket
          absent from socket_refs.
        - Conduit resolution validity is invalid when an error is present.
    Returns:
        None.
    Raises:
        AssertionError: If orphan DagIndex sockets are not detected.
    """
    spellbook = _make_spellbook()
    try:
        root_id, dependency_id, blueprints, index, states = _build_system_validation_artifacts(
            spellbook
        )
        blueprint = blueprints[root_id]
        path_registry = blueprint.path_registry
        orphan_path_id = path_registry.extend_path(path_registry.root_path_id, "orphan")
        orphan = SocketRef(
            node_id=root_id,
            param_name="orphan",
            param_path_id=orphan_path_id,
            socket_kind=SocketKind.NORMAL,
        )
        blueprint.dag_index.add_socket(orphan)

        system = SpellSystemValidationSystem([SocketRefSanityStrategy()])
        try:
            result = system.validate(
                index=index,
                blueprints=blueprints,
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        codes = {diag.code for diag in result.errors}
        assert "dag_index_orphan_socket" in codes

        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
        assert conduit_state.get_spell_validity(dependency_id) is SpellValidity.invalid
    finally:
        spellbook.cleanup()
