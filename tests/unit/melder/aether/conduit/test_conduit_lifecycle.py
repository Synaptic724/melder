import logging
from unittest.mock import MagicMock

import pytest

from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.synchronization.creation_gate_controller import CreationGateController


@pytest.fixture(autouse=True)
def fresh_utility_system() -> None:
    """
    Reset the utility-system singleton around each test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()


def _build_conduit(
    *,
    spellbook: MagicMock,
    configuration: object,
    conduit_state: ConduitState,
    aetheric_frame: str = "default",
    policy: Policies = Policies.default,
    automatic: bool = True,
    name: str | None = None,
    logger: object | None = None,
    conduit_id: str | None = None,
    root_conduit_id: str | None = None,
    creation_gate: object | None = None,
) -> Conduit:
    """
    Build a Conduit with the current injected-service constructor contract.
    """
    dynamic = not automatic
    creation_gate_controller = CreationGateController()
    aetheric_frame_object = MagicMock()
    aetheric_frame_object._conduits = {}
    conduit_cloud = MagicMock()
    conduit_cloud.create_cluster.return_value = None
    conduit_cloud.delete_cluster.return_value = None
    conduit_cloud.add_conduit_to_cluster.return_value = None
    conduit_cloud.remove_conduit_from_cluster.return_value = None
    conduit_cloud.get_clusters_for_conduit.return_value = []
    conduit_cloud.refresh_cluster_shares_for_conduit.return_value = None
    conduit_cloud.get_conduit_by_id.return_value = None
    conduit_cloud.get_conduit_by_name.return_value = None
    aetheric_frame_object._conduit_cloud = conduit_cloud
    aetheric_frame_object.devops_information_registry = DevopsInformationRegistry(
        aetheric_frame
    )
    aetheric_frame_object.register_root_conduit.return_value = None
    aetheric_frame_object.unregister_root_conduit.return_value = None
    transaction_mediator = MagicMock()
    transaction_mediator.get_active_request.return_value = None
    transaction_mediator.get_session_for_identity.return_value = None
    transaction_mediator.start_transaction.return_value = None
    transaction_mediator.begin_transaction.return_value = None
    transaction_mediator.end_transaction.return_value = None
    transaction_mediator.end_transaction_by_request_id.return_value = None
    transaction_mediator.update_transaction_for_identity.return_value = False
    spellbook._get_required_transaction_mediator = MagicMock(
        return_value=transaction_mediator,
    )
    if conduit_state is ConduitState.lesser and root_conduit_id is None:
        root_conduit_id = "root-1"
    if conduit_state is ConduitState.lesser:
        root = MagicMock()
        root._id = root_conduit_id
        root._conduit_pool = ConduitPool(
            root_conduit=root,
            baseline_idle=10,
            max_idle=10,
        )
        aetheric_frame_object._conduits[root_conduit_id] = root
    conduit = Conduit(
        spellbook=spellbook,
        configuration=configuration,
        conduit_state=conduit_state,
        aetheric_frame_name=aetheric_frame,
        aetheric_frame=aetheric_frame_object,
        policy=policy,
        creation_gate_controller=creation_gate_controller,
        dynamic=dynamic,
        name=name,
        logger=logger,
        conduit_id=conduit_id,
        root_conduit_id=root_conduit_id,
        creation_gate=creation_gate,
    )
    if conduit_state is ConduitState.normal:
        aetheric_frame_object._conduits[conduit._id] = conduit
    return conduit


class _LockProbe:
    """
    Minimal lock probe used to verify Conduit context management.

    Contract:
        - acquire() increments acquire_calls and returns True.
        - release() increments release_calls.
    """

    def __init__(self) -> None:
        """
        Initialize the probe with zeroed counters.

        Returns:
            None: This constructor has no return value.
        """
        self.acquire_calls = 0
        self.release_calls = 0

    def acquire(self) -> bool:
        """
        Record a lock acquire and return True.

        Returns:
            bool: Always True to emulate a successful acquire.
        """
        self.acquire_calls += 1
        return True

    def release(self) -> None:
        """
        Record a lock release.

        Returns:
            None: This method only updates internal counters.
        """
        self.release_calls += 1

    def __enter__(self) -> "_LockProbe":
        """
        Enter the probe as a context manager.

        Contract:
            - Calls acquire() once and returns self.

        Returns:
            _LockProbe: The lock probe instance.
        """
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the probe as a context manager.

        Contract:
            - Calls release() once.
            - Does not suppress exceptions.

        Args:
            exc_type: Exception type, if any.
            exc_value: Exception value, if any.
            traceback: Traceback object, if any.

        Returns:
            None: Always returns None to avoid suppressing exceptions.
        """
        self.release()


def test_init_rejects_non_configuration(spellbook_stub: MagicMock) -> None:
    """
    Verify Conduit rejects non-SpellbookConfiguration inputs.

    Contract:
        - __init__ raises TypeError when configuration is not SpellbookConfiguration.

    Args:
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If the expected TypeError is not raised.
    """
    with pytest.raises(TypeError, match="SpellbookConfiguration"):
        _build_conduit(
            spellbook=spellbook_stub,
            configuration=object(),
            conduit_state=ConduitState.lesser,
            aetheric_frame="default",
            policy=Policies.default,
        )


def test_lesser_conduit_drops_name(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify lesser conduits do not retain names assigned at construction.

    Contract:
        - A name passed to a lesser conduit is discarded.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If the name is preserved for a lesser conduit.
    """
    conduit = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
        name="alpha",
    )
    try:
        assert conduit.name is None
    finally:
        conduit.cleanup()


def test_name_setter_allows_initial_assignment(conduit_normal: Conduit) -> None:
    """
    Verify a normal conduit allows a one-time name assignment.

    Contract:
        - Setting name when unset succeeds.
        - The assigned name is visible via the property.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If the name is not stored after assignment.
    """
    conduit_normal.name = "primary"
    assert conduit_normal.name == "primary"


def test_name_setter_rejects_second_assignment(conduit_normal: Conduit) -> None:
    """
    Verify a conduit name cannot be reassigned.

    Contract:
        - Attempting to set name twice raises RuntimeError.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If the second assignment does not raise.
    """
    conduit_normal.name = "first"
    with pytest.raises(RuntimeError, match="name is set"):
        conduit_normal.name = "second"


def test_get_conduit_cloud_returns_aetheric_frame_cloud(conduit_normal: Conduit) -> None:
    """
    Verify get_conduit_cloud returns the conduit frame’s ConduitCloud.

    Contract:
        - The method returns the same object owned by the owning frame.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If the returned cloud is not the frame cloud.
    """
    expected_cloud = conduit_normal._aetheric_frame._conduit_cloud
    assert conduit_normal.get_conduit_cloud() is expected_cloud


def test_get_conduit_cloud_raises_after_cleanup(
    conduit_normal: Conduit,
) -> None:
    """
    Verify get_conduit_cloud is blocked once the conduit is cleaned.

    Contract:
        - cleanup marks the Conduit as cleaned.
        - Accessor calls that include `check_cleaned()` raise.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        RuntimeError: When accessing the conduit cloud after cleanup.
    """
    conduit_normal.permanent_cleanup()
    with pytest.raises(RuntimeError):
        conduit_normal.get_conduit_cloud()


def test_get_active_spellspace_returns_none_when_empty(conduit_lesser: Conduit) -> None:
    """
    Verify get_active_spellspace returns None with an empty stack.

    Contract:
        - No active SpellSpace is reported when none were entered.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If a non-None SpellSpace is returned.
    """
    assert conduit_lesser.get_active_spellspace() is None


def test_create_spellspace_returns_owned_space_without_activation(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify create_spellspace returns a SpellSpace owned by the conduit.

    Contract:
        - The returned SpellSpace is associated with the conduit.
        - Creating a SpellSpace does not make it active.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If ownership or activation expectations fail.
    """
    space = conduit_lesser.create_spellspace()
    assert isinstance(space, SpellSpace)
    assert space.owner_conduit_id == conduit_lesser._id
    assert conduit_lesser.get_active_spellspace() is None


def test_normal_conduit_owns_root_conduit_pool(
    conduit_normal: Conduit,
) -> None:
    """
    Verify a normal/root conduit creates and owns a root conduit pool.
    """
    assert conduit_normal._conduit_pool is not None
    assert conduit_normal._conduit_pool.root_conduit is conduit_normal
    assert conduit_normal._conduit_pool.root_conduit_id == conduit_normal._id


def test_lesser_conduit_inherits_root_conduit_pool(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify a lesser conduit always has the shared root conduit pool.
    """
    assert conduit_lesser._conduit_pool is not None


def test_enter_spellspace_pushes_active_and_cleans_on_exit(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify enter_spellspace activates a SpellSpace and cleans it on exit.

    Contract:
        - The yielded SpellSpace is active during the context.
        - The SpellSpace is returned to its pool after leaving the context.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If activation or cleanup expectations fail.
    """
    with conduit_lesser.enter_spellspace() as space:
        assert conduit_lesser.get_active_spellspace() is space
        assert space.cleaned is False
    assert conduit_lesser.get_active_spellspace() is None
    assert space.cleaned is False


def test_enter_spellspace_nested_restores_previous_active(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify nested spellspaces restore the previous active space.

    Contract:
        - Inner contexts supersede the active spellspace.
        - Exiting inner context restores the prior active spellspace.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If the active spellspace does not restore correctly.
    """
    with conduit_lesser.enter_spellspace() as outer:
        assert conduit_lesser.get_active_spellspace() is outer
        with conduit_lesser.enter_spellspace() as inner:
            assert conduit_lesser.get_active_spellspace() is inner
        assert conduit_lesser.get_active_spellspace() is outer
        assert inner.cleaned is False
    assert conduit_lesser.get_active_spellspace() is None
    assert outer.cleaned is False


def test_enter_spellspace_cleans_on_exception(conduit_lesser: Conduit) -> None:
    """
    Verify spellspace cleanup occurs even when the body raises.

    Contract:
        - The spellspace is returned to its pool on exit even if an
          exception occurs.
        - The active stack is cleared after the context.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If cleanup does not occur after an exception.
    """
    with pytest.raises(ValueError, match="boom"):
        with conduit_lesser.enter_spellspace() as space:
            raise ValueError("boom")
    assert conduit_lesser.get_active_spellspace() is None
    assert space.cleaned is False


def test_enter_spellspace_raises_on_stack_corruption(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify exiting a corrupted spellspace stack raises SpellSpaceScopeError.

    Contract:
        - Stack integrity checks run on context exit.
        - Corruption triggers SpellSpaceScopeError.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If stack corruption does not raise.
    """
    with pytest.raises(SpellSpaceScopeError, match="stack corruption"):
        with conduit_lesser.enter_spellspace():
            conduit_lesser._spellspace_stack.set([])


def test_context_manager_acquires_and_releases_lock(conduit_lesser: Conduit) -> None:
    """
    Verify Conduit context manager acquires and releases the lock.

    Contract:
        - __enter__ acquires the lock.
        - __exit__ releases the lock.
        - The context returns the same Conduit instance.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If acquire/release behavior is incorrect.
    """
    lock = _LockProbe()
    conduit_lesser._lock = lock
    with conduit_lesser as ctx:
        assert ctx is conduit_lesser
    assert lock.acquire_calls == 1
    assert lock.release_calls == 1


def test_provider_used_when_logger_missing(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify the provider is used when no logger is provided.

    Contract:
        - Provider resolver is called with the conduit instance.
        - The resulting SafeLogger is assigned to the conduit.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If provider usage or logger assignment fails.
    """
    seen = []

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Produce a logger for the given object and record the call.

        Args:
            registrant (object): The object requesting a logger.

        Returns:
            logging.Logger: A standard library logger instance.
        """
        seen.append(registrant)
        return logging.getLogger("conduit-factory")

    utility_system = AetherUtilitySystem()
    utility_system.set_channel_logger_activation_enabled(True)
    utility_system.register_channel_logger_resolver(resolver)
    conduit = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        assert seen == [conduit]
        assert isinstance(conduit._logger, SafeLogger)
    finally:
        conduit.cleanup()


def test_explicit_logger_skips_provider(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify an explicit logger bypasses the provider.

    Contract:
        - Provider resolver is not called when logger is provided.
        - The conduit receives a SafeLogger wrapper.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If the factory is used or logger is missing.
    """
    seen = []

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Produce a logger for the given object and record the call.

        Args:
            registrant (object): The object requesting a logger.

        Returns:
            logging.Logger: A standard library logger instance.
        """
        seen.append(registrant)
        return logging.getLogger("unused-factory")

    AetherUtilitySystem().register_channel_logger_resolver(resolver)
    explicit_logger = logging.getLogger("explicit")
    conduit = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
        logger=explicit_logger,
    )
    try:
        assert seen == []
        assert isinstance(conduit._logger, SafeLogger)
    finally:
        conduit.cleanup()


def test_cleanup_is_idempotent_for_lesser_conduit(conduit_lesser: Conduit) -> None:
    """
    Verify soft cleanup is idempotent for a lesser conduit.

    Contract:
        - Multiple cleanup calls do not raise.
        - cleaned flag remains unset because the lesser is prepared for pooling.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    conduit_lesser._nexus = MagicMock()
    conduit_lesser._nexus_publish_enabled = True
    conduit_lesser._conduit_ward = MagicMock()
    conduit_lesser._meld = MagicMock()
    conduit_lesser._creations = MagicMock()
    conduit_lesser.cleanup()
    conduit_lesser.cleanup()
    assert conduit_lesser.cleaned is False
    assert conduit_lesser._conduit_state is ConduitState.pooled_lesser
    assert (
        conduit_lesser._transaction_identity.metadata["conduit_state"]
        == ConduitState.lesser.value
    )
    conduit_lesser._nexus._publish_conduit_record.assert_not_called()
    assert hasattr(conduit_lesser, "_nexus")


def test_create_fresh_lesser_conduit_publishes_once_when_nexus_enabled(
    conduit_normal: Conduit,
) -> None:
    """
    Verify fresh lesser creation still publishes into Nexus when enabled.

    Contract:
        - Fresh lesser creation retains the original passive-ingest publish.
        - The publish target is the newly created lesser conduit instance.
    """
    conduit_normal._nexus_publish_enabled = True
    conduit_normal._spellbook._nexus = MagicMock()
    conduit_normal._nexus = conduit_normal._spellbook._nexus

    lesser = conduit_normal.create_lesser_conduit()

    conduit_normal._spellbook._nexus._publish_conduit_record.assert_called_once_with(
        lesser
    )


def test_create_lesser_conduit_from_pool_skips_nexus_publish_and_identity_refresh(
    conduit_normal: Conduit,
) -> None:
    """
    Verify pooled lesser reactivation stays local.

    Contract:
        - A retained pooled lesser returns to active `lesser` state.
        - Reactivation does not republish to Nexus.
        - Reactivation does not refresh dev-ops identity metadata.
    """
    conduit_normal._nexus_publish_enabled = True
    conduit_normal._nexus = MagicMock()

    pooled = Conduit(
        spellbook=conduit_normal._spellbook,
        configuration=conduit_normal._configuration,
        conduit_state=ConduitState.lesser,
        aetheric_frame_name=conduit_normal._aetheric_frame_name,
        aetheric_frame=conduit_normal._aetheric_frame,
        policy=Policies.default,
        root_conduit_id=conduit_normal._id,
        creation_gate_controller=conduit_normal._creation_gate_controller,
    )
    pooled._nexus = MagicMock()
    pooled._nexus_publish_enabled = True
    pooled._conduit_state = ConduitState.pooled_lesser
    pooled._conduit_ward._conduit_type = ConduitState.pooled_lesser
    pooled._transaction_identity.update_metadata(
        conduit_state=ConduitState.pooled_lesser.value
    )
    conduit_normal._conduit_pool.return_lesser_conduit(pooled)

    reused = conduit_normal.create_lesser_conduit()

    assert reused is pooled
    assert reused._conduit_state is ConduitState.lesser
    assert (
        reused._transaction_identity.metadata["conduit_state"]
        == ConduitState.pooled_lesser.value
    )
    reused._nexus._publish_conduit_record.assert_not_called()


def test_cleanup_raises_for_unknown_conduit_state(conduit_normal: Conduit) -> None:
    """
    Verify cleanup fails loudly when the conduit state is invalid.

    Contract:
        - Unknown conduit states raise RuntimeError.
        - The logger records the invalid-state error.
    """
    conduit_normal._conduit_state = object()
    conduit_normal._logger = MagicMock()

    with pytest.raises(RuntimeError, match="unknown during cleanup"):
        conduit_normal.permanent_cleanup()

    conduit_normal._logger.error.assert_called_once()


def test_cleanup_lesser_conduit_tolerates_child_cleanup_errors(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify hard cleanup for a lesser conduit tolerates child cleanup failures and nulls state.

    Contract:
        - unregister gate, meld, ward, and creations failures are logged and do not abort cleanup.
        - Key owned references are nulled after cleanup.
    """
    conduit_lesser._logger = MagicMock()
    conduit_lesser._creation_gate_controller = MagicMock()
    conduit_lesser._meld = MagicMock()
    conduit_lesser._conduit_ward = MagicMock()
    conduit_lesser._creations = MagicMock()
    conduit_lesser._creation_gate_controller.unregister_conduit_gate.side_effect = RuntimeError("gate boom")
    conduit_lesser._meld.cleanup.side_effect = RuntimeError("meld boom")
    conduit_lesser._conduit_ward.cleanup.side_effect = RuntimeError("ward boom")
    conduit_lesser._creations.cleanup.side_effect = RuntimeError("creations boom")
    logger = conduit_lesser._logger

    conduit_lesser.permanent_cleanup()

    assert not hasattr(conduit_lesser, "_conduit_ward")
    assert not hasattr(conduit_lesser, "_meld")
    assert not hasattr(conduit_lesser, "_creation_gate")
    assert not hasattr(conduit_lesser, "_creation_gate_controller")
    assert not hasattr(conduit_lesser, "_creations")
    assert not hasattr(conduit_lesser, "_spellbook")
    assert logger.error.call_count >= 4


def test_cleanup_normal_conduit_tolerates_child_cleanup_errors(
    conduit_normal: Conduit,
) -> None:
    """
    Verify normal conduit cleanup tolerates child cleanup failures and nulls state.

    Contract:
        - unregister gate, meld, ward, creations, root-conduit unregister, state drop,
          and spellbook cleanup failures are logged and do not abort cleanup.
        - Key owned references are deleted after cleanup.
    """
    conduit_normal._logger = MagicMock()
    conduit_normal._creation_gate_controller = MagicMock()
    conduit_normal._meld = MagicMock()
    conduit_normal._conduit_ward = MagicMock()
    conduit_normal._creations = MagicMock()
    conduit_normal._spellbook = MagicMock()
    conduit_normal._spellbook._spells = {}
    conduit_normal._spellbook._spell_system_states = MagicMock()
    conduit_normal._creation_gate_controller.unregister_conduit_gate.side_effect = RuntimeError("gate boom")
    conduit_normal._meld.cleanup.side_effect = RuntimeError("meld boom")
    conduit_normal._conduit_ward.cleanup.side_effect = RuntimeError("ward boom")
    conduit_normal._creations.cleanup.side_effect = RuntimeError("creations boom")
    conduit_normal._spellbook._spell_system_states.drop_conduit_resolution_state.side_effect = RuntimeError("state boom")
    conduit_normal._spellbook.cleanup.side_effect = RuntimeError("spellbook boom")
    conduit_normal._aetheric_frame.unregister_root_conduit.side_effect = RuntimeError("frame boom")

    conduit_normal._cleanup_normal_conduit()

    assert not hasattr(conduit_normal, "_conduit_ward")
    assert not hasattr(conduit_normal, "_meld")
    assert not hasattr(conduit_normal, "_creation_gate")
    assert not hasattr(conduit_normal, "_creation_gate_controller")
    assert not hasattr(conduit_normal, "_creations")
    assert not hasattr(conduit_normal, "_spellbook")
    assert conduit_normal._logger.error.call_count >= 6


def test_cleanup_calls_spellbook_cleanup_for_normal_conduit(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify normal conduit cleanup invokes spellbook cleanup.

    Contract:
        - Normal conduit cleanup calls spellbook.cleanup().
        - Cleanup completes without raising when Aether is stubbed.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used during cleanup.

    Raises:
        AssertionError: If spellbook cleanup is not invoked.
    """
    conduit_normal._conduit_ward = MagicMock()
    conduit_normal._meld = MagicMock()
    conduit_normal._creations = MagicMock()
    conduit_normal._conduit_pool = MagicMock()
    conduit_normal._nexus_publish_enabled = True
    conduit_normal._nexus = MagicMock()
    nexus = conduit_normal._nexus
    spellbook = conduit_normal._spellbook
    conduit_pool = conduit_normal._conduit_pool
    conduit_normal.permanent_cleanup()
    assert spellbook.cleanup.called is True
    conduit_pool.cleanup.assert_called_once()
    nexus._publish_frame_record.assert_called_once_with(spellbook)
    assert not hasattr(conduit_normal, "_nexus")


def test_cleanup_returns_early_when_cleaned_flips_inside_lock(
    conduit_lesser: Conduit,
) -> None:
    """cleanup should return safely if another path marks the conduit cleaned inside the lock."""
    conduit_lesser._logger = MagicMock()
    conduit_lesser._conduit_hooks = {"on_conduit_cleanup_start": [MagicMock()]}
    original_lock = conduit_lesser._lock

    class _LockThatMarksCleaned:
        def __enter__(self_inner):
            conduit_lesser._cleaned = True
            return self_inner

        def __exit__(self_inner, exc_type, exc_value, traceback):
            return False

    try:
        conduit_lesser._lock = _LockThatMarksCleaned()
        conduit_lesser.cleanup()
    finally:
        conduit_lesser._lock = original_lock

    assert conduit_lesser._conduit_hooks is not None


def test_cleanup_swallows_logger_cleanup_failures(
    conduit_lesser: Conduit,
) -> None:
    """permanent_cleanup should swallow logger cleanup failures and still clear the logger reference."""
    conduit_lesser._conduit_ward = MagicMock()
    conduit_lesser._meld = MagicMock()
    conduit_lesser._creations = MagicMock()
    conduit_lesser._logger = MagicMock()
    conduit_lesser._logger.cleanup.side_effect = RuntimeError("logger boom")
    logger = conduit_lesser._logger

    conduit_lesser.permanent_cleanup()

    assert logger.cleanup.called is True
    assert not hasattr(conduit_lesser, "_logger")


def test_publish_conduit_record_to_nexus_skips_when_disabled(
    conduit_normal: Conduit,
) -> None:
    """_publish_conduit_record_to_nexus should no-op when Nexus publication is disabled."""
    conduit_normal._nexus = MagicMock()
    conduit_normal._nexus_publish_enabled = False

    conduit_normal._publish_conduit_record_to_nexus()

    conduit_normal._nexus._publish_conduit_record.assert_not_called()


def test_publish_conduit_record_to_nexus_publishes_for_lesser(
    conduit_lesser: Conduit,
) -> None:
    """_publish_conduit_record_to_nexus should publish for lesser conduits."""
    conduit_lesser._nexus = MagicMock()
    conduit_lesser._nexus_publish_enabled = True

    conduit_lesser._publish_conduit_record_to_nexus()

    conduit_lesser._nexus._publish_conduit_record.assert_called_once_with(
        conduit_lesser
    )


def test_publish_frame_record_to_nexus_skips_when_spellbook_missing(
    conduit_normal: Conduit,
) -> None:
    """_publish_frame_record_to_nexus should no-op when the spellbook is missing."""
    conduit_normal._nexus = MagicMock()
    conduit_normal._nexus_publish_enabled = True
    conduit_normal._spellbook = None

    conduit_normal._publish_frame_record_to_nexus()

    conduit_normal._nexus._publish_frame_record.assert_not_called()


def test_remove_conduit_record_from_nexus_publishes_for_lesser(
    conduit_lesser: Conduit,
) -> None:
    """_remove_conduit_record_from_nexus should remove lesser conduit records."""
    conduit_lesser._nexus = MagicMock()
    conduit_lesser._nexus_publish_enabled = True

    conduit_lesser._remove_conduit_record_from_nexus()

    conduit_lesser._nexus._remove_conduit_record.assert_called_once_with(
        conduit_lesser._id,
        conduit_lesser._aetheric_frame_name,
    )


def test_cleanup_spellspaces_logs_and_continues_when_space_cleanup_fails(
    conduit_lesser: Conduit,
) -> None:
    """_cleanup_spellspaces should log permanent cleanup failures and still drain the stack."""
    conduit_lesser._logger = MagicMock()
    bad_space = MagicMock()
    bad_space.permanent_cleanup.side_effect = RuntimeError("space boom")
    conduit_lesser._spellspace_stack.set([bad_space])

    conduit_lesser._cleanup_spellspaces()

    conduit_lesser._logger.error.assert_called()
    assert conduit_lesser._spellspace_stack.get() == []


def test_cleanup_spellspaces_logs_registry_cleanup_failures(
    conduit_lesser: Conduit,
) -> None:
    """_cleanup_spellspaces should log registry permanent cleanup failures and still clear the registry."""
    conduit_lesser._logger = MagicMock()
    good_space = MagicMock()
    bad_space = MagicMock()
    bad_space.permanent_cleanup.side_effect = RuntimeError("registry space boom")
    conduit_lesser._spellspace_registry = {good_space, bad_space}

    conduit_lesser._cleanup_spellspaces()

    conduit_lesser._logger.error.assert_called()
    assert conduit_lesser._spellspace_registry == set()


def test_cleanup_spellspaces_logs_stack_flush_failure(
    conduit_lesser: Conduit,
) -> None:
    """_cleanup_spellspaces should log failures from the stack context variable access itself."""
    conduit_lesser._logger = MagicMock()
    broken_stack = MagicMock()
    broken_stack.get.side_effect = RuntimeError("stack boom")
    conduit_lesser._spellspace_stack = broken_stack

    conduit_lesser._cleanup_spellspaces()

    conduit_lesser._logger.error.assert_called()


