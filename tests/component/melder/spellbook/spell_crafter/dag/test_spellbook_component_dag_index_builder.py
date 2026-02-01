import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.dag_index import DagIndexBuilder
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_dag_index_builder() -> None:
    """
    Purpose:
        Reset the Aether singleton for component DagIndexBuilder tests.
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
        Provide a Spellbook configured for component DAG index tests.
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
        - Returns the first spell whose SpellIndex.current matches spell_id.
    Args:
        spellbook: Spellbook to search.
        spell_id: Version id to match.
    Returns:
        Spell or None: Matching spell instance or None if not found.
    """
    for spell in spellbook._spells.values():
        if spell.spell_index.current == spell_id:
            return spell
    return None


def test_component_dag_index_builder_builds_from_local_topology() -> None:
    """
    Purpose:
        Validate DagIndexBuilder builds shallow sockets from real topology.
    Contract:
        - Each socket path is a single-segment param name.
        - Plain parameters still appear in the shallow index.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with a DI socket and a plain parameter.
        Contract:
            - Declares a BasicService dependency.
            - Declares a plain count parameter with default.
        Args:
            service: Injected BasicService dependency.
            count: Plain parameter with a default.
        """

        def __init__(self, service: BasicService, count: int = 1) -> None:
            """
            Purpose:
                Capture injected dependency and plain parameter.
            Contract:
                - Stores constructor inputs for diagnostics.
            Args:
                service: Injected BasicService dependency.
                count: Plain parameter with a default.
            Returns:
                None.
            """
            self.service = service
            self.count = count

    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        states = spell._spell_system_states
        assert states is not None
        topology = states.get_local_topology(spell.spell_index)
        assert topology is not None

        index = DagIndexBuilder.build_shallow(
            spell.spell_index.current,
            topology.sockets,
        )

        service_refs = index.get_by_name("service")
        count_refs = index.get_by_name("count")
        path_registry = index.path_registry
        assert len(service_refs) == 1
        assert len(count_refs) == 1
        assert path_registry.materialize_path(service_refs[0].param_path_id) == ("service",)
        assert path_registry.materialize_path(count_refs[0].param_path_id) == ("count",)
        assert service_refs[0].socket_kind is SocketKind.NORMAL
        assert count_refs[0].socket_kind is SocketKind.NORMAL
    finally:
        spellbook.cleanup()


def test_component_dag_index_builder_preserves_contract_socket_kinds() -> None:
    """
    Purpose:
        Validate DagIndexBuilder preserves contract socket kinds.
    Contract:
        - SpellContract sockets are indexed as SPELL_CONTRACT.
        - MutationContract sockets are indexed as MUTATION_CONTRACT.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with contract sockets.
        Contract:
            - Declares SpellContract and MutationContract parameters.
        Args:
            service: SpellContract socket.
            mutation: MutationContract socket.
        """

        def __init__(
            self,
            service: SpellContract = SpellContract(
                spellframe=IService,
                binding_name="primary",
            ),
            mutation: MutationContract = MutationContract(
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture contract sockets for diagnostics.
            Contract:
                - Stores sockets on the instance.
            Args:
                service: SpellContract socket.
                mutation: MutationContract socket.
            Returns:
                None.
            """
            self.service = service
            self.mutation = mutation

    try:
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        states = spell._spell_system_states
        assert states is not None
        topology = states.get_local_topology(spell.spell_index)
        assert topology is not None

        index = DagIndexBuilder.build_shallow(
            spell.spell_index.current,
            topology.sockets,
        )

        service_refs = index.get_by_name("service")
        mutation_refs = index.get_by_name("mutation")
        path_registry = index.path_registry
        assert len(service_refs) == 1
        assert len(mutation_refs) == 1
        assert service_refs[0].socket_kind is SocketKind.SPELL_CONTRACT
        assert mutation_refs[0].socket_kind is SocketKind.MUTATION_CONTRACT
        assert path_registry.materialize_path(service_refs[0].param_path_id) == ("service",)
        assert path_registry.materialize_path(mutation_refs[0].param_path_id) == ("mutation",)
    finally:
        spellbook.cleanup()


def test_component_dag_index_builder_keeps_collection_paths_shallow() -> None:
    """
    Purpose:
        Validate collection sockets keep shallow param paths in DagIndex.
    Contract:
        - Collection sockets are indexed under a single-segment path.
        - get_by_exact_path returns the collection socket reference.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with a collection dependency.
        Contract:
            - Declares a list[IService] dependency.
        Args:
            services: Injected service implementations.
        """

        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture the injected services.
            Contract:
                - Stores services for diagnostics.
            Args:
                services: Injected service implementations.
            Returns:
                None.
            """
            self.services = services

    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=IService,
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        states = spell._spell_system_states
        assert states is not None
        topology = states.get_local_topology(spell.spell_index)
        assert topology is not None

        index = DagIndexBuilder.build_shallow(
            spell.spell_index.current,
            topology.sockets,
        )
        refs = index.get_by_exact_path(("services",))
        path_registry = index.path_registry
        assert len(refs) == 1
        assert refs[0].param_name == "services"
        assert path_registry.materialize_path(refs[0].param_path_id) == ("services",)
    finally:
        spellbook.cleanup()
