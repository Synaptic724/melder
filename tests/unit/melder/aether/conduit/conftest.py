import threading
from unittest.mock import MagicMock

import pytest
from types import SimpleNamespace

from melder.aether.aether import Aether
from melder.nexus.nexus import Nexus
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.utilities.synchronization.creation_gate_controller import CreationGateController


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)


def _cleanup_conduit_if_alive(conduit: Conduit) -> None:
    """
    Cleanup a conduit only when the live cleanup surface is still present.

    Purpose:
        Keep shared fixtures resilient when a test directly calls one of the
        internal cleanup helpers that delete owned fields without flipping the
        full public cleanup state.
    """
    if getattr(conduit, "_cleaned", False):
        return
    if not hasattr(conduit, "_creation_gate_controller"):
        return
    conduit.permanent_cleanup()


def _attach_root_pool_stub(
    frame_stub: MagicMock,
    root_conduit_id: str = "root-1",
) -> MagicMock:
    """
    Attach one root-conduit stub carrying a real ConduitPool to the frame stub.
    """
    root = MagicMock()
    root._id = root_conduit_id
    root._conduit_pool = ConduitPool(
        root_conduit=root,
        baseline_idle=10,
        max_idle=10,
    )
    frame_stub._conduits[root_conduit_id] = root
    return root


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each conduit unit test.

    Contract:
        - AetherUtilitySystem, Nexus, and Aether are reset before and after
          each test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
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
    # Real conduits pull a non-owning crystallizer from their spellbook at
    # init; a bare MagicMock attribute is TRUTHY and would let the record
    # seams (conduit twin / contract snapshots) fire inside unit tests.
    # "Present but not recording" keeps every seam gated off.
    spellbook._crystallizer = SimpleNamespace(cleaned=False, activated=False)
    spellbook._lock = threading.RLock()
    spellbook._active_change_request = None
    transaction_mediator = MagicMock()
    transaction_mediator.get_active_request.return_value = None
    transaction_mediator.get_session_for_identity.return_value = None
    transaction_mediator.start_transaction.return_value = None
    transaction_mediator.begin_transaction.return_value = None
    transaction_mediator.end_transaction.return_value = None
    transaction_mediator.end_transaction_by_request_id.return_value = None
    transaction_mediator.update_transaction_for_identity.return_value = False
    spellbook._transaction_mediator = transaction_mediator
    spellbook._get_required_transaction_mediator = MagicMock(
        return_value=transaction_mediator,
    )
    spellbook._spells = {}
    spellbook._contracted_spells = {}
    spellbook._lookup_spells = {}
    spellbook._lookup_contracted_spells = {}
    spellbook._aetheric_frame_configuration = MagicMock(
        system_state="automatic",
        disable_bind=False,
        disable_all_transactions_after_conjure=False,
        disable_linking=False,
        disable_transfer_of_ownership=False,
        disable_conduit_cluster=False,
        disable_mutations=False,
    )
    spellbook._find_contracted_spell_by_id = MagicMock(return_value=None)
    spellbook.bind = MagicMock()
    spellbook.create_binder = MagicMock()
    spellbook.find_spell_index = MagicMock()
    spellbook._find_spell = MagicMock()
    spellbook.find_spell_key = MagicMock()
    spellbook.inspect_spell = MagicMock()
    spellbook.cleanup = MagicMock()
    spellbook.create_new_preset_spellbook = MagicMock()
    spellbook._nexus = MagicMock()
    return spellbook


@pytest.fixture()
def aether_stub() -> MagicMock:
    """
    Provide an Aether-like stub for test helpers that still consult Aether
    directly through Spellbook-owned paths.

    Contract:
        - Provides no-op methods for spellbook-owned Aether registration and lookup APIs.

    Returns:
        MagicMock: Aether-like stub used by tests.
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
    yield stub


@pytest.fixture()
def dev_ops_manager_stub() -> MagicMock:
    """
    Provide a frame-owned DevOpsManager double for conduit construction.

    Contract:
        - Exposes a real CreationGateController for gate registration flows.

    Returns:
        MagicMock: DevOpsManager-like stub.
    """
    stub = MagicMock()
    stub.creation_gate_controller = CreationGateController()
    return stub


@pytest.fixture()
def conduit_cloud_stub() -> MagicMock:
    """
    Provide a ConduitCloud double for current-frame conduit and cluster flows.

    Contract:
        - Supports current-frame conduit lookup and cluster-management helpers.
        - Acts as the frame-local lookup surface derived by `ConduitWard`.

    Returns:
        MagicMock: ConduitCloud-like stub.
    """
    stub = MagicMock()
    stub.create_cluster.return_value = None
    stub.delete_cluster.return_value = None
    stub.add_conduit_to_cluster.return_value = None
    stub.remove_conduit_from_cluster.return_value = None
    stub.get_clusters_for_conduit.return_value = []
    stub.refresh_cluster_shares_for_conduit.return_value = None
    stub.get_conduit_by_id.return_value = None
    stub.get_conduit_by_name.return_value = None
    return stub


@pytest.fixture()
def aetheric_frame_stub(conduit_cloud_stub: MagicMock) -> MagicMock:
    """
    Provide an AethericFrame-like stub for direct conduit construction.

    Contract:
        - Exposes frame-owned conduit registration helpers.
        - Exposes the frame-local conduit cloud used by `ConduitWard`.

    Returns:
        MagicMock: AethericFrame-like stub.
    """
    stub = MagicMock()
    stub._conduit_cloud = conduit_cloud_stub
    stub._conduits = {}
    stub.devops_information_registry = DevopsInformationRegistry("default")
    stub.register_root_conduit.return_value = None
    stub.unregister_root_conduit.return_value = None
    stub.register_dynamic_conduit.return_value = None
    stub.unregister_dynamic_conduit.return_value = None
    return stub


@pytest.fixture()
def conduit_lesser(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    dev_ops_manager_stub: MagicMock,
    conduit_cloud_stub: MagicMock,
    aetheric_frame_stub: MagicMock,
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
    spellbook_stub._aetheric_frame_configuration.system_state = SystemState.automatic
    aetheric_frame_stub.frame_configuration = (
        spellbook_stub._aetheric_frame_configuration
    )
    _attach_root_pool_stub(aetheric_frame_stub, "root-1")
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame_name="default",
        aetheric_frame=aetheric_frame_stub,
        policy=Policies.default,
        root_conduit_id="root-1",
        creation_gate_controller=dev_ops_manager_stub.creation_gate_controller,
    )
    yield conduit
    _cleanup_conduit_if_alive(conduit)


@pytest.fixture()
def conduit_normal(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
    dev_ops_manager_stub: MagicMock,
    conduit_cloud_stub: MagicMock,
    aetheric_frame_stub: MagicMock,
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
    spellbook_stub._aetheric_frame_configuration.system_state = SystemState.automatic
    aetheric_frame_stub.frame_configuration = (
        spellbook_stub._aetheric_frame_configuration
    )
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame_name="default",
        aetheric_frame=aetheric_frame_stub,
        policy=Policies.default,
        creation_gate_controller=dev_ops_manager_stub.creation_gate_controller,
    )
    aetheric_frame_stub._conduits[conduit._id] = conduit
    yield conduit
    _cleanup_conduit_if_alive(conduit)


@pytest.fixture()
def conduit_dynamic_normal(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
    dev_ops_manager_stub: MagicMock,
    conduit_cloud_stub: MagicMock,
    aetheric_frame_stub: MagicMock,
) -> Conduit:
    """
    Build a dynamic, normal Conduit for contract and link tests.

    Contract:
        - Dynamic environment is forced via dynamic=True.
        - Normal state enables contract qualification paths.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.
        aether_stub (MagicMock): Aether stub installed on Conduit._aether.

    Returns:
        Conduit: A dynamic normal conduit instance.
    """
    spellbook_stub._aetheric_frame_configuration.system_state = SystemState.dynamic
    aetheric_frame_stub.frame_configuration = (
        spellbook_stub._aetheric_frame_configuration
    )
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame_name="default",
        aetheric_frame=aetheric_frame_stub,
        policy=Policies.default,
        dynamic=True,
        creation_gate_controller=dev_ops_manager_stub.creation_gate_controller,
    )
    aetheric_frame_stub._conduits[conduit._id] = conduit
    yield conduit
    _cleanup_conduit_if_alive(conduit)


@pytest.fixture()
def conduit_dynamic_lesser(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
    dev_ops_manager_stub: MagicMock,
    conduit_cloud_stub: MagicMock,
    aetheric_frame_stub: MagicMock,
) -> Conduit:
    """
    Build a dynamic, lesser Conduit for upgrade tests.

    Contract:
        - Dynamic environment is forced via dynamic=True.
        - Conduit remains in lesser state until upgraded.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.
        aether_stub (MagicMock): Aether stub installed on Conduit._aether.

    Returns:
        Conduit: A dynamic lesser conduit instance.
    """
    spellbook_stub._aetheric_frame_configuration.system_state = SystemState.dynamic
    aetheric_frame_stub.frame_configuration = (
        spellbook_stub._aetheric_frame_configuration
    )
    _attach_root_pool_stub(aetheric_frame_stub, "root-1")
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame_name="default",
        aetheric_frame=aetheric_frame_stub,
        policy=Policies.default,
        dynamic=True,
        root_conduit_id="root-1",
        creation_gate_controller=dev_ops_manager_stub.creation_gate_controller,
    )
    yield conduit
    _cleanup_conduit_if_alive(conduit)
