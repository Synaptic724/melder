import pytest
import tests.component.melder.spellbook.compiler_test_helpers as compiler_test_helpers

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.core_classes import NamedService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_dag_local_frame() -> None:
    """
    Purpose:
        Reset the Aether singleton for component local-frame DAG tests.
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
        Provide a Spellbook configured for component DAG tests.
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


def test_component_local_frame_dag_records_param_metadata_for_dependencies() -> None:
    """
    Purpose:
        Validate the local frame rows record each dependency under its constructor parameter.
    Contract:
        - The resolution frame lists the dependencies ascending by id, then the root last.
        - `Spell.dependencies` holds exactly the resolved dependency ids.
        - The registered topology maps each DI parameter to its dependency spell id.
        - Plain parameters resolve no dependency; no per-spell graph object is built.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with multiple DI dependencies and a plain param.
        Contract:
            - Declares service and config dependencies.
            - Declares a plain count parameter.
        Args:
            service: Injected BasicService instance.
            config: Injected BasicConfig instance.
            count: Plain parameter with a default.
        """

        def __init__(
            self,
            service: BasicService,
            config: BasicConfig,
            count: int = 1,
        ) -> None:
            """
            Purpose:
                Capture injected dependencies and plain parameters.
            Contract:
                - Stores constructor inputs for diagnostics.
            Args:
                service: Injected BasicService instance.
                config: Injected BasicConfig instance.
                count: Plain parameter with a default.
            Returns:
                None.
            """
            self.service = service
            self.config = config
            self.count = count

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
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        compiler_test_helpers.run_phase_requirements(spell)
        compiler_test_helpers.run_phase_symbolic_graph(spell)
        compiler_test_helpers.run_phase_local_frame(spell)

        root_id = spell.spell_index.selected_spell_id
        assert spell.dependency_graph is None
        assert spell.resolution_frame.ordered_node_ids == sorted([service_id, config_id]) + [root_id]
        assert set(spell.dependencies) == {service_id, config_id}

        topology = spellbook._spell_system_states.get_local_topology(spell.spell_index)
        assert topology is not None
        (service_socket,) = topology.get_sockets_for_param("service")
        (config_socket,) = topology.get_sockets_for_param("config")
        assert service_socket.target_spell_ids == (service_id,)
        assert config_socket.target_spell_ids == (config_id,)
        (count_socket,) = topology.get_sockets_for_param("count")
        assert count_socket.target_spell_ids == ()
    finally:
        spellbook.cleanup()


def test_component_local_frame_dag_supports_collection_dependencies() -> None:
    """
    Purpose:
        Validate collection dependencies register every implementation as a dependency.
    Contract:
        - Each resolved service spell appears in the frame order and in `Spell.dependencies`.
        - The one collection socket targets every implementation.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on a service collection.
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
                - Stores the services for diagnostics.
            Args:
                services: Injected service implementations.
            Returns:
                None.
            """
            self.services = services

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=IService,
        )
        named_id = spellbook.bind(
            spell=NamedService,
            existence=Existence.unique,
            permissions="create",
            spellframe=IService,
            binding_name="secondary",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        compiler_test_helpers.run_phase_requirements(spell)
        compiler_test_helpers.run_phase_symbolic_graph(spell)
        compiler_test_helpers.run_phase_local_frame(spell)

        root_id = spell.spell_index.selected_spell_id
        assert spell.dependency_graph is None
        assert spell.resolution_frame.ordered_node_ids == sorted([service_id, named_id]) + [root_id]
        assert set(spell.dependencies) == {service_id, named_id}

        topology = spellbook._spell_system_states.get_local_topology(spell.spell_index)
        assert topology is not None
        (services_socket,) = topology.get_sockets_for_param("services")
        assert services_socket.is_collection is True
        assert set(services_socket.target_spell_ids) == {service_id, named_id}
    finally:
        spellbook.cleanup()

