import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig, BasicService
from tests.mocks.spellbook.protocols import IService


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


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for SpellCrafter integration tests.
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
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_spell_crafter_phase3_requires_phase1_and_phase2() -> None:
    """
    Purpose:
        Validate Phase 3 refuses to run before Phases 1 and 2.
    Contract:
        - run_phase_local_frame raises RuntimeError without requirements/graph.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 3 runs without prerequisites.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        with pytest.raises(RuntimeError):
            spell.run_phase_local_frame()
    finally:
        spellbook.cleanup()


def test_spell_crafter_run_all_phases_builds_dependencies_and_state() -> None:
    """
    Purpose:
        Validate run_all_phases builds the local frame, dependencies, and state.
    Contract:
        - dependencies include the resolved spell_id for constructor deps.
        - SpellSystemState records direct dependencies.
        - Phase artifacts are cleaned after Phase 7.
    Returns:
        None.
    Raises:
        AssertionError: If Phase artifacts or state are missing/incorrect.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Root dependency for the test spell.
        Contract:
            - Declares no constructor parameters.
        """

    class Root:
        """
        Purpose:
            Spell with a single DI dependency on Leaf.
        Contract:
            - Requires a Leaf instance during construction.
        Args:
            leaf: Injected Leaf dependency.
        """
        def __init__(self, leaf: Leaf) -> None:
            """
            Purpose:
                Capture the injected Leaf dependency.
            Contract:
                - Stores the Leaf instance for assertions.
            Args:
                leaf: Injected Leaf dependency.
            Returns:
                None.
            """
            self.leaf = leaf

    leaf_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )
    root_id = spellbook.bind(
        spell=Root,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        root_spell = conduit.get_spell_by_id(root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")

        assert set(root_spell.dependencies) == {leaf_id}
        assert root_spell.dependency_graph is not None
        assert root_spell.requirements is None
        assert root_spell.symbolic_graph is None
        assert root_spell.resolution_frame is None

        state = root_spell.system_state
        assert state is not None
        assert state.direct_dependencies == {leaf_id}
    finally:
        conduit.cleanup()


def test_spell_crafter_collection_di_resolves_multiple_dependencies() -> None:
    """
    Purpose:
        Validate collection DI resolves multiple spell ids in Phase 3.
    Contract:
        - list[IService] binds all IService implementations in the Spellbook.
        - dependencies include all matching spell ids.
    Returns:
        None.
    Raises:
        AssertionError: If collection dependencies are missing.
    """
    spellbook = _make_spellbook()

    class ServiceA:
        """
        Purpose:
            First IService implementation.
        Contract:
            - Declares no constructor parameters.
        """

    class ServiceB:
        """
        Purpose:
            Second IService implementation.
        Contract:
            - Declares no constructor parameters.
        """

    class Consumer:
        """
        Purpose:
            Spell consuming all IService implementations.
        Contract:
            - Expects a collection of IService implementations.
        Args:
            services: Collection of IService implementations.
        """
        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture the injected IService implementations.
            Contract:
                - Stores the services collection for assertions.
            Args:
                services: Collection of IService implementations.
            Returns:
                None.
            """
            self.services = services

    service_a_id = spellbook.bind(
        spell=ServiceA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="a",
    )
    service_b_id = spellbook.bind(
        spell=ServiceB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="b",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        consumer_spell = conduit.get_spell_by_id(consumer_id)
        assert consumer_spell is not None
        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        assert set(consumer_spell.dependencies) == {service_a_id, service_b_id}
        state = consumer_spell.system_state
        assert state is not None
        assert state.direct_dependencies == {service_a_id, service_b_id}
    finally:
        conduit.cleanup()


def test_spell_crafter_spellmap_default_resolves_dependency() -> None:
    """
    Purpose:
        Validate SpellMap defaults resolve during Phase 3.
    Contract:
        - SpellMap default yields a concrete dependency spell id.
    Returns:
        None.
    Raises:
        AssertionError: If SpellMap default is not resolved.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell using a SpellMap default for BasicConfig.
        Contract:
            - Declares a SpellMap default for BasicConfig.
        Args:
            config: SpellMap default pointing to BasicConfig.
        """
        def __init__(self, config: BasicConfig = SpellMap(BasicConfig)) -> None:
            """
            Purpose:
                Capture the SpellMap-resolved config dependency.
            Contract:
                - Stores the config instance for assertions.
            Args:
                config: SpellMap default pointing to BasicConfig.
            Returns:
                None.
            """
            self.config = config

    config_id = spellbook.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        consumer_spell = conduit.get_spell_by_id(consumer_id)
        assert consumer_spell is not None
        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        assert set(consumer_spell.dependencies) == {config_id}
    finally:
        conduit.cleanup()


def test_spell_crafter_contract_shapes_register_topology_without_dependencies() -> None:
    """
    Purpose:
        Validate SpellContract and MutationContract sockets are metadata-only in Phase 3.
    Contract:
        - dependencies remain empty for contract-only parameters.
        - local topology records contract socket kinds with no targets.
    Returns:
        None.
    Raises:
        AssertionError: If contract sockets create dependencies or targets.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell declaring contract sockets only.
        Contract:
            - Declares SpellContract and MutationContract sockets.
        Args:
            service: SpellContract socket.
            mutation: MutationContract socket.
        """
        def __init__(
            self,
            service: SpellContract = SpellContract(spellframe=IService, binding_name="primary"),
            mutation: MutationContract = MutationContract(spellframe=IService, binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Capture contract socket defaults without resolution.
            Contract:
                - Stores the contract placeholders as-is.
            Args:
                service: SpellContract socket.
                mutation: MutationContract socket.
            Returns:
                None.
            """
            self.service = service
            self.mutation = mutation

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        consumer_spell = conduit.get_spell_by_id(consumer_id)
        assert consumer_spell is not None
        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        assert consumer_spell.dependencies == []
        state = consumer_spell.system_state
        assert state is not None
        assert state.direct_dependencies == set()

        topology = consumer_spell._spell_system_states.get_local_topology(
            consumer_spell.spell_index
        )
        assert topology is not None
        service_sockets = topology.get_sockets_for_param("service")
        mutation_sockets = topology.get_sockets_for_param("mutation")
        assert len(service_sockets) == 1
        assert len(mutation_sockets) == 1
        assert service_sockets[0].socket_kind is SocketKind.SPELL_CONTRACT
        assert mutation_sockets[0].socket_kind is SocketKind.MUTATION_CONTRACT
        assert service_sockets[0].target_spell_ids == ()
        assert mutation_sockets[0].target_spell_ids == ()
    finally:
        conduit.cleanup()


def test_spell_crafter_phase2_requires_phase1() -> None:
    """
    Purpose:
        Validate Phase 2 refuses to run before Phase 1 requirements.
    Contract:
        - run_phase_symbolic_graph raises RuntimeError without requirements.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 2 runs without Phase 1 data.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        with pytest.raises(RuntimeError):
            spell.run_phase_symbolic_graph()
    finally:
        spellbook.cleanup()


def test_spell_crafter_phase4_requires_phase1_to_3() -> None:
    """
    Purpose:
        Validate Phase 4 refuses to run before Phases 1-3.
    Contract:
        - run_phase_validation raises RuntimeError without local frame data.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 4 runs without Phases 1-3.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        with pytest.raises(RuntimeError):
            spell.run_phase_validation()
    finally:
        spellbook.cleanup()


def test_spell_crafter_phase5_requires_phase4() -> None:
    """
    Purpose:
        Validate Phase 5 refuses to run before Phase 4 validation.
    Contract:
        - run_phase_root_blueprints raises RuntimeError without Phase 4.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 5 runs without Phase 4.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        with pytest.raises(RuntimeError):
            spell.run_phase_root_blueprints("cid")
    finally:
        spellbook.cleanup()


def test_spell_crafter_phase6_requires_phase5() -> None:
    """
    Purpose:
        Validate Phase 6 refuses to run before Phase 5 artifacts.
    Contract:
        - run_phase_system_validation raises RuntimeError without Phase 5.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 6 runs without Phase 5 artifacts.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()
        with pytest.raises(RuntimeError):
            spell.run_phase_system_validation("cid")
    finally:
        spellbook.cleanup()


def test_spell_crafter_spellmap_frame_only_resolves_dependency() -> None:
    """
    Purpose:
        Validate frame-only SpellMap defaults resolve during Phase 3.
    Contract:
        - SpellMap(spell=None, spellframe=..., binding_name=...) resolves a spell id.
        - Local topology records the resolved target spell id.
    Returns:
        None.
    Raises:
        AssertionError: If frame-only SpellMap resolution is missing.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell that uses a frame-only SpellMap default.
        Contract:
            - Declares a SpellMap pointing to IService "primary".
        Args:
            service: SpellMap default for IService "primary".
        """
        def __init__(
            self,
            service: IService = SpellMap(
                spell=None,
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the frame-only SpellMap dependency.
            Contract:
                - Stores the resolved service for assertions.
            Args:
                service: SpellMap default for IService "primary".
            Returns:
                None.
            """
            self.service = service

    service_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        consumer_spell = conduit.get_spell_by_id(consumer_id)
        assert consumer_spell is not None
        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        assert set(consumer_spell.dependencies) == {service_id}
        topology = consumer_spell._spell_system_states.get_local_topology(
            consumer_spell.spell_index
        )
        assert topology is not None
        sockets = topology.get_sockets_for_param("service")
        assert len(sockets) == 1
        assert sockets[0].socket_kind is SocketKind.NORMAL
        assert set(sockets[0].target_spell_ids) == {service_id}
    finally:
        conduit.cleanup()


def test_spell_crafter_local_topology_records_plain_and_collection_sockets() -> None:
    """
    Purpose:
        Validate local topology records normal, collection, and plain sockets.
    Contract:
        - NORMAL sockets capture resolved spell ids.
        - Plain parameter sockets are metadata-only with no targets.
    Returns:
        None.
    Raises:
        AssertionError: If socket metadata or targets are incorrect.
    """
    spellbook = _make_spellbook()

    class ServiceA:
        """
        Purpose:
            First IService implementation for collection DI.
        Contract:
            - Declares no constructor parameters.
        """

    class ServiceB:
        """
        Purpose:
            Second IService implementation for collection DI.
        Contract:
            - Declares no constructor parameters.
        """

    class Consumer:
        """
        Purpose:
            Spell that combines normal, collection, and plain sockets.
        Contract:
            - Requires BasicConfig.
            - Requires list[IService].
            - Includes a plain parameter with a default.
        Args:
            config: BasicConfig dependency.
            services: Collection of IService implementations.
            count: Plain parameter with a default value.
        """
        def __init__(
            self,
            config: BasicConfig,
            services: list[IService],
            count: int = 1,
        ) -> None:
            """
            Purpose:
                Capture injected dependencies and plain parameter.
            Contract:
                - Stores config, services, and count for assertions.
            Args:
                config: Injected configuration instance.
                services: Collection of IService implementations.
                count: Plain parameter value.
            Returns:
                None.
            """
            self.config = config
            self.services = services
            self.count = count

    config_id = spellbook.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    service_a_id = spellbook.bind(
        spell=ServiceA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="a",
    )
    service_b_id = spellbook.bind(
        spell=ServiceB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="b",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        consumer_spell = conduit.get_spell_by_id(consumer_id)
        assert consumer_spell is not None
        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()

        assert set(consumer_spell.dependencies) == {
            config_id,
            service_a_id,
            service_b_id,
        }
        topology = consumer_spell._spell_system_states.get_local_topology(
            consumer_spell.spell_index
        )
        assert topology is not None

        config_socket = topology.get_sockets_for_param("config")
        services_socket = topology.get_sockets_for_param("services")
        count_socket = topology.get_sockets_for_param("count")

        assert len(config_socket) == 1
        assert config_socket[0].socket_kind is SocketKind.NORMAL
        assert not config_socket[0].is_collection
        assert set(config_socket[0].target_spell_ids) == {config_id}

        assert len(services_socket) == 1
        assert services_socket[0].socket_kind is SocketKind.NORMAL
        assert services_socket[0].is_collection
        assert set(services_socket[0].target_spell_ids) == {service_a_id, service_b_id}

        assert len(count_socket) == 1
        assert count_socket[0].socket_kind is SocketKind.NORMAL
        assert not count_socket[0].is_collection
        assert count_socket[0].is_optional
        assert count_socket[0].target_spell_ids == ()
    finally:
        conduit.cleanup()


def test_spell_crafter_validation_sets_flags_and_result() -> None:
    """
    Purpose:
        Validate Phase 4 stores validation results and flags.
    Contract:
        - validation_result_phase4 is populated after validation.
        - validated is True and is_broken is False for a healthy spell.
    Returns:
        None.
    Raises:
        AssertionError: If validation flags or result are missing.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        spell = conduit.get_spell_by_id(spell_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()

        assert spell.validation_result_phase4 is not None
        assert spell.validated
        assert not spell.is_broken
    finally:
        conduit.cleanup()


def test_spell_crafter_run_all_phases_records_phase6_state() -> None:
    """
    Purpose:
        Validate run_all_phases records Phase 6 results in conduit state.
    Contract:
        - ConduitResolutionState marks the root spell as valid.
        - Phase artifacts are cleaned after Phase 7.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 6 validity is missing.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Dependency spell for the root spell.
        Contract:
            - Declares no constructor parameters.
        """

    class Root:
        """
        Purpose:
            Root spell that depends on Leaf.
        Contract:
            - Requires a Leaf instance during construction.
        Args:
            leaf: Injected Leaf dependency.
        """
        def __init__(self, leaf: Leaf) -> None:
            """
            Purpose:
                Capture the injected Leaf dependency.
            Contract:
                - Stores the Leaf instance for assertions.
            Args:
                leaf: Injected Leaf dependency.
            Returns:
                None.
            """
            self.leaf = leaf

    spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )
    root_id = spellbook.bind(
        spell=Root,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        root_spell = conduit.get_spell_by_id(root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")

        assert root_spell.validation_result_phase6 is None
        conduit_state = spellbook._spell_system_states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.valid
        assert conduit_state.get_root_validity(root_id) is SpellValidity.valid
    finally:
        conduit.cleanup()


def test_spell_cleanup_after_run_all_phases_clears_phase_artifacts() -> None:
    """
    Purpose:
        Validate Spell.cleanup clears phase artifacts after a full run.
    Contract:
        - Phase artifacts are cleaned after run_all_phases.
        - cleanup() drops the crafter and nulls dependency artifacts.
    Returns:
        None.
    Raises:
        AssertionError: If phase artifacts are not cleared by cleanup.
    """
    spellbook = _make_spellbook()

    class Leaf:
        """
        Purpose:
            Dependency spell for cleanup verification.
        Contract:
            - Declares no constructor parameters.
        """

    class Root:
        """
        Purpose:
            Spell that depends on Leaf and runs all phases.
        Contract:
            - Requires a Leaf instance during construction.
        Args:
            leaf: Injected Leaf dependency.
        """
        def __init__(self, leaf: Leaf) -> None:
            """
            Purpose:
                Capture the injected Leaf dependency.
            Contract:
                - Stores the Leaf instance for assertions.
            Args:
                leaf: Injected Leaf dependency.
            Returns:
                None.
            """
            self.leaf = leaf

    leaf_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )
    root_id = spellbook.bind(
        spell=Root,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        root_spell = conduit.get_spell_by_id(root_id)
        assert root_spell is not None
        root_spell.run_all_phases("cid")

        assert root_spell.requirements is None
        assert root_spell.symbolic_graph is None
        assert root_spell.resolution_frame is None
        assert root_spell.validation_result_phase4 is None
        assert root_spell.validation_result_phase6 is None
        assert set(root_spell.dependencies) == {leaf_id}
        assert root_spell.dependency_graph is not None

        root_spell.cleanup()

        assert root_spell._cleaned is True
        assert root_spell._crafter is None
        assert root_spell.spell is None
        assert root_spell.spell_index is None
        assert root_spell.dependencies is None
        assert root_spell.dependency_graph is None
        assert root_spell.requirements is None
        assert root_spell.symbolic_graph is None
        assert root_spell.resolution_frame is None
    finally:
        conduit.cleanup()
