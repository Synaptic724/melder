import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
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


def test_component_local_frame_dag_records_param_metadata_for_dependencies() -> None:
    """
    Purpose:
        Validate local-frame DAG edges record param metadata for dependencies.
    Contract:
        - Root node incoming params map dependencies to constructor names.
        - Dependency nodes list the root under the same param name.
        - Plain parameters do not appear in the DAG edge metadata.
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
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        dag = spell.dependency_graph
        assert isinstance(dag, DirectedAcyclicWorkGraph)

        root_id = spell.spell_index.current
        root_node = dag.get_node(root_id)
        assert root_node is not None

        service_node = dag.get_node(service_id)
        config_node = dag.get_node(config_id)
        assert service_node is not None
        assert config_node is not None

        assert root_node.incoming_params[service_node] == "service"
        assert root_node.incoming_params[config_node] == "config"
        assert set(root_node.incoming_params.values()) == {"service", "config"}

        assert root_node in service_node.children_by_param["service"]
        assert root_node in config_node.children_by_param["config"]
    finally:
        spellbook.cleanup()


def test_component_local_frame_dag_supports_collection_dependencies() -> None:
    """
    Purpose:
        Validate collection dependencies register multiple incoming edges.
    Contract:
        - Each resolved service spell is registered as a parent of the root.
        - All incoming params map to the same collection parameter name.
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
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        dag = spell.dependency_graph
        assert isinstance(dag, DirectedAcyclicWorkGraph)
        root_id = spell.spell_index.current
        root_node = dag.get_node(root_id)
        assert root_node is not None

        service_node = dag.get_node(service_id)
        named_node = dag.get_node(named_id)
        assert service_node is not None
        assert named_node is not None

        incoming_values = {
            root_node.incoming_params[service_node],
            root_node.incoming_params[named_node],
        }
        assert incoming_values == {"services"}

        assert root_node in service_node.children_by_param["services"]
        assert root_node in named_node.children_by_param["services"]
    finally:
        spellbook.cleanup()
