import threading
from unittest.mock import MagicMock

import pytest

from melder.aether.aether import Aether
from melder.aether.nexus.nexus import Nexus
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.spellbook.spellbook import Spellbook
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.utilities.synchronization.creation_gate_controller import CreationGateController


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each conduit unit test.

    Contract:
        - AetherUtilitySystem, Nexus, and Aether are reset before and after
          each test.
        - Conduit._aether is rebound to a fresh Aether singleton so Conduit
          construction can resolve its owned Nexus reference deterministically.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Conduit._aether = Aether()
    Spellbook._aether = Aether()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Conduit._aether = Aether()
    Spellbook._aether = Aether()


@pytest.fixture()
def configuration_automatic() -> SpellbookConfiguration:
    """
    Provide a SpellbookConfiguration instance with automatic defaults applied.

    Contract:
        - system_state is automatic.
        - default properties required by Conduit are present.

    Returns:
        SpellbookConfiguration: Ready-to-use automatic configuration.
    """
    configuration = SpellbookConfiguration()
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    return configuration


@pytest.fixture()
def configuration_dynamic() -> SpellbookConfiguration:
    """
    Provide a SpellbookConfiguration instance with dynamic defaults applied.

    Contract:
        - system_state is dynamic.
        - default properties required by Conduit are present.

    Returns:
        SpellbookConfiguration: Ready-to-use dynamic configuration.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    return configuration


@pytest.fixture()
def spellbook_stub() -> MagicMock:
    """
    Provide a minimal Spellbook double for Conduit construction.

    Contract:
        - Exposes spell storage maps needed by Meld.
        - Provides spellbook facade methods as MagicMock call targets.

    Returns:
        MagicMock: Configured spellbook stub with required attributes.
    """
    spellbook = MagicMock()
    spellbook._id = "spellbook-1"
    spellbook._lock = threading.RLock()
    spellbook._active_change_request = None
    spellbook._spells = {}
    spellbook._contracted_spells = {}
    spellbook._lookup_spells = {}
    spellbook._lookup_contracted_spells = {}
    spellbook._find_contracted_spell_by_id = MagicMock(return_value=None)
    spellbook.bind = MagicMock()
    spellbook.create_binder = MagicMock()
    spellbook.find_spell_index = MagicMock()
    spellbook._find_spell = MagicMock()
    spellbook.find_spell_key = MagicMock()
    spellbook.inspect_spell = MagicMock()
    spellbook.cleanup = MagicMock()
    spellbook.create_new_preset_spellbook = MagicMock()
    return spellbook


@pytest.fixture()
def aether_stub() -> MagicMock:
    """
    Patch Conduit._aether with a stub for isolation.

    Contract:
        - Restores the original Conduit._aether after the test.
        - Provides no-op methods for Conduit registration and lookup APIs.

    Returns:
        MagicMock: The active Aether stub bound to Conduit._aether.
    """
    stub = MagicMock()
    stub._add_conduit.return_value = None
    stub._remove_conduit.return_value = None
    stub._add_spells_to_aether.return_value = None
    stub._remove_spells_from_aether.return_value = None
    stub._register_conduit_cloud.return_value = None
    stub._unregister_conduit_cloud.return_value = None
    stub._get_conduit_by_spell_id.return_value = None
    stub._check_for_spell.return_value = False
    stub._get_conduit_by_id.return_value = None
    stub._get_conduit_by_name.return_value = None
    stub._get_conduit_cloud.return_value = None
    stub._create_cluster.return_value = None
    stub._remove_cluster.return_value = None
    stub._add_conduit_to_cluster.return_value = None
    stub._remove_conduit_from_cluster.return_value = None
    stub._get_clusters_for_conduit.return_value = []
    stub._refresh_cluster_shares_for_conduit.return_value = None
    stub._get_mutation_research.return_value = MagicMock()
    dev_ops_manager = MagicMock()
    dev_ops_manager.creation_gate_controller = CreationGateController()
    stub._get_devops_manager.return_value = dev_ops_manager
    previous = Conduit._aether
    Conduit._aether = stub
    try:
        yield stub
    finally:
        Conduit._aether = previous


@pytest.fixture()
def conduit_lesser(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> Conduit:
    """
    Build a lesser Conduit for unit tests.

    Contract:
        - Uses automatic configuration defaults.
        - Avoids Aether registration by staying in lesser state.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.

    Returns:
        Conduit: A lesser conduit instance.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    yield conduit
    conduit.cleanup()


@pytest.fixture()
def conduit_normal(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> Conduit:
    """
    Build a normal Conduit for unit tests with Aether isolated.

    Contract:
        - Registers into the Aether stub during construction.
        - Cleans up deterministically after each test.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.
        aether_stub (MagicMock): Aether stub installed on Conduit._aether.

    Returns:
        Conduit: A normal conduit instance.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
    )
    yield conduit
    conduit.cleanup()


@pytest.fixture()
def conduit_dynamic_normal(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> Conduit:
    """
    Build a dynamic, normal Conduit for contract and link tests.

    Contract:
        - Dynamic environment is forced via automatic=False.
        - Normal state enables contract qualification paths.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.
        aether_stub (MagicMock): Aether stub installed on Conduit._aether.

    Returns:
        Conduit: A dynamic normal conduit instance.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        automatic=False,
    )
    yield conduit
    conduit.cleanup()


@pytest.fixture()
def conduit_dynamic_lesser(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> Conduit:
    """
    Build a dynamic, lesser Conduit for upgrade tests.

    Contract:
        - Dynamic environment is forced via automatic=False.
        - Conduit remains in lesser state until upgraded.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.
        aether_stub (MagicMock): Aether stub installed on Conduit._aether.

    Returns:
        Conduit: A dynamic lesser conduit instance.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
        automatic=False,
    )
    yield conduit
    conduit.cleanup()
