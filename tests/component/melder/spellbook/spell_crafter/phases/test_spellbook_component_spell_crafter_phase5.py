import pytest
import tests.component.melder.spellbook.compiler_test_helpers as compiler_test_helpers

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 import (
    CompilerPhase5,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.core_classes import RepositoryWithLogger
from tests.mocks.spellbook.core_classes import ServiceWithRepository
from tests.mocks.spellbook.protocols import ILogger
from tests.mocks.spellbook.protocols import IRepository


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_phase5() -> None:
    """
    Purpose:
        Reset the Aether singleton for component Phase-5 tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a clean singleton after each test.
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
        Provide a Spellbook configured for component Phase-5 tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str):
    """
    Purpose:
        Retrieve a local Spell by its version id.
    Contract:
        - Returns the first spell whose SpellIndex.selected_spell_id matches spell_id.
    Args:
        spellbook: Spellbook to search.
        spell_id: Version id to match.
    Returns:
        Spell or None: Matching spell instance or None if not found.
    """
    for spell in spellbook._spells.values():
        if spell.spell_index.selected_spell_id == spell_id:
            return spell
    return None


def test_component_phase5_blueprint_includes_deep_socket_paths() -> None:
    """
    Purpose:
        Validate Phase 5 builds deep socket paths from real topologies.
    Contract:
        - The root blueprint exists for the root spell.
        - Socket paths include the direct dependency and the nested dependency.
        - Topological order ends with the root spell id.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    try:
        logger_id = spellbook.bind(
            spell=BasicLogger,
            existence=Existence.unique,
            permissions="create",
            spellframe=ILogger,
        )
        repo_id = spellbook.bind(
            spell=RepositoryWithLogger,
            existence=Existence.unique,
            permissions="create",
            spellframe=IRepository,
        )
        root_id = spellbook.bind(
            spell=ServiceWithRepository,
            existence=Existence.unique,
            permissions="create",
        )

        logger_spell = _get_spell_by_version_id(spellbook, logger_id)
        repo_spell = _get_spell_by_version_id(spellbook, repo_id)
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        assert logger_spell is not None
        assert repo_spell is not None
        assert root_spell is not None

        compiler_test_helpers.run_phase_requirements(logger_spell)
        compiler_test_helpers.run_phase_symbolic_graph(logger_spell)
        compiler_test_helpers.run_phase_local_frame(logger_spell)

        compiler_test_helpers.run_phase_requirements(repo_spell)
        compiler_test_helpers.run_phase_symbolic_graph(repo_spell)
        compiler_test_helpers.run_phase_local_frame(repo_spell)

        compiler_test_helpers.run_phase_requirements(root_spell)
        compiler_test_helpers.run_phase_symbolic_graph(root_spell)
        compiler_test_helpers.run_phase_local_frame(root_spell)
        compiler_test_helpers.run_phase_validation(root_spell)
        compiler_test_helpers.run_phase_root_blueprints(root_spell, "cid")

        artifact = root_spell._compiler_artifact
        blueprint = artifact._root_blueprint_phase5
        assert blueprint is not None
        assert blueprint.root_spell_id == root_id
        blueprint.ensure_dag_index_built()

        ordered = blueprint.ordered_node_ids
        assert ordered[-1] == root_id
        assert repo_id in ordered
        assert logger_id in ordered

        repo_refs = blueprint.dag_index.get_by_exact_path(("repository",))
        deep_refs = blueprint.dag_index.get_by_exact_path(("repository", "logger"))
        assert repo_refs
        assert deep_refs
        assert any(ref.node_id == root_id for ref in repo_refs)
        assert any(ref.node_id == repo_id for ref in deep_refs)
    finally:
        spellbook.cleanup()


def test_component_phase5_system_index_marks_root_and_dependencies() -> None:
    """
    Purpose:
        Validate Phase 5 system index marks roots and dependencies correctly.
    Contract:
        - The root node is flagged as root.
        - Dependency nodes are not flagged as roots.
        - Root dependencies include the provider spell id.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with a single dependency for Phase 5 indexing.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected dependency.
            Contract:
                - Stores the service for diagnostics.
            Args:
                service: Injected BasicService instance.
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

        service_spell = _get_spell_by_version_id(spellbook, service_id)
        root_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert service_spell is not None
        assert root_spell is not None

        compiler_test_helpers.run_phase_requirements(service_spell)
        compiler_test_helpers.run_phase_symbolic_graph(service_spell)
        compiler_test_helpers.run_phase_local_frame(service_spell)

        compiler_test_helpers.run_phase_requirements(root_spell)
        compiler_test_helpers.run_phase_symbolic_graph(root_spell)
        compiler_test_helpers.run_phase_local_frame(root_spell)
        compiler_test_helpers.run_phase_validation(root_spell)
        compiler_test_helpers.run_phase_root_blueprints(root_spell, "cid")

        artifact = root_spell._compiler_artifact
        system_index = artifact._spell_system_index_phase5
        assert system_index is not None

        root_node = system_index.get_node(consumer_id)
        dep_node = system_index.get_node(service_id)
        assert root_node is not None
        assert dep_node is not None
        assert root_node.is_root is True
        assert dep_node.is_root is False
        assert root_node.dependencies == {service_id}
    finally:
        spellbook.cleanup()


def test_component_phase5_builds_blueprints_for_multiple_roots() -> None:
    """
    Purpose:
        Validate Phase 5 builds blueprints for each structural root.
    Contract:
        - The root blueprint map includes each root spell id.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        config_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )

        service_spell = _get_spell_by_version_id(spellbook, service_id)
        config_spell = _get_spell_by_version_id(spellbook, config_id)
        assert service_spell is not None
        assert config_spell is not None

        compiler_test_helpers.run_phase_requirements(service_spell)
        compiler_test_helpers.run_phase_symbolic_graph(service_spell)
        compiler_test_helpers.run_phase_local_frame(service_spell)
        compiler_test_helpers.run_phase_validation(service_spell)
        compiler_test_helpers.run_phase_requirements(config_spell)

        compiler_test_helpers.run_phase_root_blueprints(service_spell, "cid")

        blueprints = service_spell._compiler_artifact._entire_dag_blueprint_phase5
        assert blueprints is not None
        assert set(blueprints.keys()) == {service_id, config_id}
    finally:
        spellbook.cleanup()


def test_component_filter_snapshot_to_visible_spells_excludes_hidden() -> None:
    """
    Purpose:
        Validate snapshot filtering removes hidden dependencies and topologies.
    Contract:
        - Hidden spell ids are removed from dependencies and topologies.
        - Root ids are recomputed after filtering.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        compiler_test_helpers.run_phase_requirements(spell)

        root_id = "root-visible"
        dep_id = "dep-visible"
        hidden_id = "hidden"

        root_topology = SpellLocalTopology(
            spell_id=root_id,
            sockets=(
                SpellSocketDescriptor(
                    spell_id=root_id,
                    param_name="service",
                    position=0,
                    socket_kind=SocketKind.NORMAL,
                    is_collection=False,
                    is_optional=False,
                    target_spell_ids=(dep_id,),
                ),
            ),
        )
        hidden_topology = SpellLocalTopology(
            spell_id=hidden_id,
            sockets=(),
        )

        snapshot = SpellSystemAdjacencySnapshot(
            dependencies={
                root_id: {dep_id, hidden_id},
                dep_id: set(),
                hidden_id: set(),
            },
            reverse_dependencies={
                dep_id: {root_id},
                hidden_id: {root_id},
            },
            all_spell_ids={root_id, dep_id, hidden_id},
            root_spell_ids={root_id},
            topologies={
                root_id: root_topology,
                hidden_id: hidden_topology,
            },
        )

        filtered = CompilerPhase5()._filter_snapshot_to_visible_spells(
            snapshot=snapshot,
            visible_spell_ids={root_id, dep_id},
        )

        assert filtered.all_spell_ids == {root_id, dep_id}
        assert filtered.dependencies[root_id] == {dep_id}
        assert hidden_id not in filtered.dependencies
        assert filtered.reverse_dependencies[dep_id] == {root_id}
        assert hidden_id not in filtered.reverse_dependencies
        assert filtered.root_spell_ids == {root_id}
        assert set(filtered.topologies.keys()) == {root_id}
    finally:
        spellbook.cleanup()

