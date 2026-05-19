from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_crafter.dag.dag_index import DagTargetingEngine
from melder.aether.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_crafter.dag.target_spec import TargetSpec
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


class _SpellStub:
    """
    Purpose:
        Provide a minimal spell stub for SpellSystemStates registration.
    Contract:
        - Captures a name for traceability in debugging.
    """
    def __init__(self, name: str) -> None:
        """
        Purpose:
            Store a display name for the stub spell.
        Contract:
            - name is preserved on the instance.
        Args:
            name: Label for the stub spell.
        Returns:
            None.
        """
        self.name = name


def _register_index(states, spell_id: str) -> SpellIndex:
    """
    Purpose:
        Register a SpellIndex lineage in SpellSystemStates for testing.
    Contract:
        - Returns a SpellIndex whose current id matches spell_id.
        - SpellSystemStates stores a state entry for the lineage.
    Args:
        states: SpellSystemStates registry to update.
        spell_id: Version id to register as the current spell id.
    Returns:
        SpellIndex: The registered lineage object.
    """
    index = SpellIndex(spell_id)
    states.register_index(index, _SpellStub(spell_id))
    return index


def _build_blueprint():
    """
    Purpose:
        Build a root blueprint with deep socket paths for targeting tests.
    Contract:
        - Returns a RootResolutionBlueprint with a populated DagIndex.
        - The blueprint contains both shallow and deep socket paths.
    Returns:
        tuple: (blueprint, ids) where ids is a dict of spell ids.
    """
    frame = AethericFrame(Aether(), "component-dag-targeting")
    states = frame.spell_system_states

    root_index = _register_index(states, "root-targeting")
    repo_index = _register_index(states, "repo-targeting")
    logger_index = _register_index(states, "logger-targeting")
    service_root_index = _register_index(states, "service-root-targeting")
    service_repo_index = _register_index(states, "service-repo-targeting")
    contract_root_index = _register_index(states, "contract-root-targeting")
    contract_repo_index = _register_index(states, "contract-repo-targeting")

    root_id = root_index.current
    repo_id = repo_index.current
    logger_id = logger_index.current
    service_root_id = service_root_index.current
    service_repo_id = service_repo_index.current
    contract_root_id = contract_root_index.current
    contract_repo_id = contract_repo_index.current

    states.update_dependencies(
        root_index,
        [repo_id, service_root_id, contract_root_id],
    )
    states.update_dependencies(
        repo_index,
        [logger_id, service_repo_id, contract_repo_id],
    )

    root_topology = SpellLocalTopology(
        spell_id=root_id,
        sockets=[
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="repo",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(repo_id,),
            ),
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="service",
                position=1,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(service_root_id,),
            ),
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="contract",
                position=2,
                socket_kind=SocketKind.SPELL_CONTRACT,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(contract_root_id,),
            ),
        ],
    )
    repo_topology = SpellLocalTopology(
        spell_id=repo_id,
        sockets=[
            SpellSocketDescriptor(
                spell_id=repo_id,
                param_name="logger",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(logger_id,),
            ),
            SpellSocketDescriptor(
                spell_id=repo_id,
                param_name="service",
                position=1,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(service_repo_id,),
            ),
            SpellSocketDescriptor(
                spell_id=repo_id,
                param_name="contract",
                position=2,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(contract_repo_id,),
            ),
        ],
    )

    states.register_local_topology(root_index, root_topology)
    states.register_local_topology(repo_index, repo_topology)

    snapshot = SpellSystemAdjacencyBuilder.build(states)
    blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
    blueprint = blueprints[root_id]
    blueprint.ensure_dag_index_built()

    return blueprint, {
        "root": root_id,
        "repo": repo_id,
        "logger": logger_id,
        "service_root": service_root_id,
        "service_repo": service_repo_id,
        "contract_root": contract_root_id,
        "contract_repo": contract_repo_id,
    }


def test_component_dag_targeting_resolves_deep_path() -> None:
    """
    Purpose:
        Validate DagTargetingEngine resolves deep param paths from a blueprint index.
    Contract:
        - PATH targeting returns the socket with the exact deep path.
        - The resolved socket belongs to the expected node.
    Returns:
        None.
    """
    blueprint, ids = _build_blueprint()
    try:
        engine = DagTargetingEngine(blueprint.dag_index)
        path_registry = blueprint.path_registry
        sockets = engine.resolve(
            TargetSpec.parse("repo>logger"),
            lambda socket: socket.socket_kind is SocketKind.NORMAL,
        )
        assert len(sockets) == 1
        socket = sockets[0]
        assert path_registry.materialize_path(socket.param_path_id) == ("repo", "logger")
        assert socket.node_id == ids["repo"]
    finally:
        blueprint.cleanup()


def test_component_dag_targeting_broadcast_matches_multiple_paths() -> None:
    """
    Purpose:
        Validate broadcast targeting resolves all matching param names.
    Contract:
        - BROADCAST returns sockets from both shallow and deep paths.
    Returns:
        None.
    """
    blueprint, _ids = _build_blueprint()
    try:
        engine = DagTargetingEngine(blueprint.dag_index)
        path_registry = blueprint.path_registry
        sockets = engine.resolve(
            TargetSpec.parse("**service"),
            lambda socket: socket.socket_kind is SocketKind.NORMAL,
        )
        paths = sorted(
            path_registry.materialize_path(socket.param_path_id)
            for socket in sockets
        )
        assert paths == [("repo", "service"), ("service",)]
    finally:
        blueprint.cleanup()


def test_component_dag_targeting_unique_respects_socket_kind_filter() -> None:
    """
    Purpose:
        Validate UNIQUE targeting honors socket-kind filtering.
    Contract:
        - UNIQUE returns only the socket accepted by the filter.
    Returns:
        None.
    """
    blueprint, ids = _build_blueprint()
    try:
        engine = DagTargetingEngine(blueprint.dag_index)
        sockets = engine.resolve(
            TargetSpec.parse("*contract"),
            lambda socket: socket.socket_kind is SocketKind.NORMAL,
        )
        assert len(sockets) == 1
        socket = sockets[0]
        assert socket.param_name == "contract"
        assert socket.node_id == ids["repo"]
    finally:
        blueprint.cleanup()


def test_component_dag_targeting_path_ignores_same_name_elsewhere() -> None:
    """
    Purpose:
        Validate PATH targeting selects the exact param path even when names repeat.
    Contract:
        - PATH "service" resolves the root socket, not the nested one.
    Returns:
        None.
    """
    blueprint, ids = _build_blueprint()
    try:
        engine = DagTargetingEngine(blueprint.dag_index)
        path_registry = blueprint.path_registry
        sockets = engine.resolve(
            TargetSpec.parse("service"),
            lambda socket: socket.socket_kind is SocketKind.NORMAL,
        )
        assert len(sockets) == 1
        socket = sockets[0]
        assert path_registry.materialize_path(socket.param_path_id) == ("service",)
        assert socket.node_id == ids["root"]
    finally:
        blueprint.cleanup()


