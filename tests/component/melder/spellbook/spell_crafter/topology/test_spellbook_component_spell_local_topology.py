import pytest
import tests.component.melder.spellbook.compiler_test_helpers as compiler_test_helpers

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.core_classes import NamedService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_topology() -> None:
    """
    Purpose:
        Reset the Aether singleton for component topology tests.
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
        Provide a Spellbook configured for component topology tests.
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


def test_component_topology_records_positions_and_optional_flags() -> None:
    """
    Purpose:
        Validate topology descriptors preserve positions and optional flags.
    Contract:
        - Positions match constructor order.
        - Optional parameters are marked as optional.
        - Target spell ids include resolved dependencies.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with required and optional dependencies.
        Contract:
            - Declares a required service and an optional config.
        Args:
            service: Injected BasicService dependency.
            config: BasicConfig dependency with a default fallback.
        """

        def __init__(
            self,
            service: BasicService,
            config: BasicConfig = None,
        ) -> None:
            """
            Purpose:
                Capture injected dependencies for diagnostics.
            Contract:
                - Stores the service and config on the instance.
            Args:
                service: Injected BasicService dependency.
                config: BasicConfig dependency with a default fallback.
            Returns:
                None.
            """
            self.service = service
            self.config = config

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

        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        assert topology is not None
        by_param = {socket.param_name: socket for socket in topology.sockets}
        assert set(by_param.keys()) == {"service", "config"}

        service_socket = by_param["service"]
        config_socket = by_param["config"]
        assert service_socket.position == 0
        assert config_socket.position == 1
        assert service_socket.is_optional is False
        assert config_socket.is_optional is True
        assert service_socket.socket_kind is SocketKind.NORMAL
        assert config_socket.socket_kind is SocketKind.NORMAL
        assert set(service_socket.target_spell_ids) == {service_id}
        assert set(config_socket.target_spell_ids) == {config_id}
    finally:
        spellbook.cleanup()


def test_component_topology_collection_targets_include_all_spell_ids() -> None:
    """
    Purpose:
        Validate collection sockets record all resolved target ids.
    Contract:
        - Collection sockets are marked as collections.
        - target_spell_ids contains all implementations.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with a service collection dependency.
        Contract:
            - Declares a list[IService] dependency.
        Args:
            services: Injected service implementations.
        """

        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture injected services for diagnostics.
            Contract:
                - Stores services on the instance.
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

        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        assert topology is not None
        sockets = topology.get_sockets_for_param("services")
        assert len(sockets) == 1
        socket = sockets[0]
        assert socket.is_collection is True
        assert socket.is_optional is False
        assert socket.socket_kind is SocketKind.NORMAL
        assert set(socket.target_spell_ids) == {service_id, named_id}
    finally:
        spellbook.cleanup()

