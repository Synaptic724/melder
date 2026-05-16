import logging
import time
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.utilities.logger.safe_logger import SafeLogger


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
def fresh_utility_system() -> None:
    """
    Reset the utility-system singleton around each test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()


def test_configure_logger_rejects_invalid_logger(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify Conduit rejects non-logger values during initialization.

    Contract:
        - Conduit init raises TypeError when the provided logger is invalid.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If invalid logger input does not raise.
    """
    with pytest.raises(TypeError, match="Expected logger"):
        Conduit(
            spellbook=spellbook_stub,
            configuration=configuration_automatic,
            conduit_state=ConduitState.lesser,
            aetheric_frame="default",
            policy=Policies.default,
            logger=object(),
        )


def test_init_rejects_non_string_conduit_id(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify Conduit rejects non-string explicit conduit ids.

    Contract:
        - __init__ raises TypeError when conduit_id is provided as a non-string.
    """
    with pytest.raises(TypeError, match="conduit_id must be a string"):
        Conduit(
            spellbook=spellbook_stub,
            configuration=configuration_automatic,
            conduit_state=ConduitState.lesser,
            aetheric_frame="default",
            policy=Policies.default,
            conduit_id=123,
        )


def test_init_rejects_empty_conduit_id(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify Conduit rejects empty explicit conduit ids.

    Contract:
        - __init__ raises ValueError when conduit_id is an empty string.
    """
    with pytest.raises(ValueError, match="conduit_id cannot be empty"):
        Conduit(
            spellbook=spellbook_stub,
            configuration=configuration_automatic,
            conduit_state=ConduitState.lesser,
            aetheric_frame="default",
            policy=Policies.default,
            conduit_id="",
        )


def test_init_registers_existing_creation_gate_for_current_root(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify constructor uses the explicit creation_gate registration branch.

    Contract:
        - When an explicit gate is supplied, _register_existing_gate_for_current_root
          is called and the same gate is retained on the conduit.
    """
    gate = MagicMock()

    with patch.object(
        Conduit,
        "_register_existing_gate_for_current_root",
        autospec=True,
    ) as register_existing_gate:
        conduit = Conduit(
            spellbook=spellbook_stub,
            configuration=configuration_automatic,
            conduit_state=ConduitState.lesser,
            aetheric_frame="default",
            policy=Policies.default,
            creation_gate=gate,
        )
    try:
        register_existing_gate.assert_called_once_with(conduit, conduit._id, gate)
        assert conduit._creation_gate is gate
    finally:
        conduit.cleanup()


def test_configure_logger_prefers_explicit_logger_over_provider(
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify explicit logger overrides the provider.

    Contract:
        - When logger is supplied, provider resolver is not called.

    Args:
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If the factory is invoked despite explicit logger.
    """
    configuration = SpellbookConfiguration()
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    resolver_called = {"value": False}

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Record whether the resolver is invoked.

        Args:
            registrant (object): Conduit instance passed to the resolver.

        Returns:
            logging.Logger: Logger instance for the conduit.
        """
        resolver_called["value"] = True
        return logging.Logger("factory")

    AetherUtilitySystem().register_channel_logger_resolver(resolver)
    explicit_logger = logging.Logger("explicit")
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
        logger=explicit_logger,
    )
    try:
        assert resolver_called["value"] is False
        assert isinstance(conduit._logger, SafeLogger)
    finally:
        conduit.cleanup()


def test_resolve_logger_uses_provider_and_passes_conduit(
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify the provider resolver is used and receives the conduit.

    Contract:
        - The provider resolver is called with the conduit.
        - Conduit stores a SafeLogger instance.

    Args:
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If resolver is not called or logger wrapper missing.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.with_defaults()
    seen: dict[str, object] = {}

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Capture the conduit instance for verification.

        Args:
            registrant (object): Conduit instance passed to the resolver.

        Returns:
            logging.Logger: Logger instance for the conduit.
        """
        seen["obj"] = registrant
        return logging.Logger("factory-logger")

    utility_system = AetherUtilitySystem()
    utility_system.set_channel_logger_activation_enabled(True)
    utility_system.register_channel_logger_resolver(resolver)
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        assert seen["obj"] is conduit
        assert isinstance(conduit._logger, SafeLogger)
    finally:
        conduit.cleanup()


def test_apply_configuration_flags_updates_dynamic_environment(
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> None:
    """
    Verify configuration flags drive dynamic-environment state.

    Contract:
        - _apply_configuration_flags reads system_state.
        - Dynamic state enables conduit cloud access.

    Args:
        spellbook_stub (MagicMock): Spellbook stub for construction.
        aether_stub (MagicMock): Aether stub for dynamic access checks.

    Raises:
        AssertionError: If flags do not update internal state.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, SystemState.dynamic)
    configuration.with_defaults()
    spellbook_stub._aetheric_frame_configuration = (
        build_aetheric_frame_configuration_for_spellbook_configuration(configuration, )
    )
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        conduit._apply_configuration_flags()
        assert conduit.__dynamic_environment__ is True
        aether_stub._get_conduit_cloud.return_value = MagicMock()
        conduit.get_conduit_cloud()
        aether_stub._get_conduit_cloud.assert_called_once_with("default")
    finally:
        conduit.cleanup()


def test_configure_conduit_state_clears_name_for_lesser(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify lesser conduits discard names during initialization.

    Contract:
        - Lesser conduits cannot retain a name.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If the name remains set for a lesser conduit.
    """
    conduit = Conduit(
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


def test_configure_conduit_state_logs_warning_when_lesser_name_is_overridden(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify lesser conduit name override emits a warning.

    Contract:
        - Lesser conduits log a warning when a provided name is discarded.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
        name="alpha",
    )
    try:
        conduit._name = "alpha"
        conduit._logger = MagicMock()
        conduit._configure_conduit_state()
        conduit._logger.warning.assert_called()
        assert conduit.name is None
    finally:
        conduit.cleanup()


def test_configure_conduit_state_logs_and_reraises_normal_registration_failure(
    conduit_normal: Conduit,
) -> None:
    """
    Verify normal conduit registration failures are logged and re-raised.

    Contract:
        - _configure_conduit_state logs the failure.
        - The original error is propagated.
    """
    conduit_normal._logger = MagicMock()
    conduit_normal._add_conduit_to_aether = MagicMock(side_effect=RuntimeError("register boom"))
    conduit_normal._add_spells_to_aether = MagicMock()

    with pytest.raises(RuntimeError, match="register boom"):
        conduit_normal._configure_conduit_state()

    conduit_normal._logger.error.assert_called_once()


def test_initialize_conduit_hooks_attaches_configured_hooks_and_fires_on_cleanup(
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> None:
    """
    Verify configuration hooks attach to normal conduits and fire on cleanup.

    Contract:
        - Hooks registered under spellbook id are attached.
        - Cleanup triggers on_conduit_cleanup_start hooks.

    Args:
        spellbook_stub (MagicMock): Spellbook stub with id.
        aether_stub (MagicMock): Aether stub for normal conduit setup.

    Raises:
        AssertionError: If hooks are not attached or fired.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.with_defaults()
    events: list[Conduit] = []

    def hook(conduit: Conduit) -> None:
        """
        Record cleanup hook invocations.

        Args:
            conduit (Conduit): Conduit being cleaned.

        Returns:
            None: Hook does not return a value.
        """
        events.append(conduit)

    configuration.add_hook(
        spellbook_stub._id,
        "on_conduit_cleanup_start",
        hook,
    )
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        assert conduit._conduit_hooks is not None
        assert conduit._conduit_hooks["on_conduit_cleanup_start"][0] is hook
        conduit.cleanup()
        assert events == [conduit]
    finally:
        if not conduit._cleaned:
            conduit.cleanup()


def test_initialize_conduit_hooks_attaches_for_lesser(
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify lesser conduits attach copied configuration hooks.

    Contract:
        - Lesser conduits receive detached hook-map copies.
        - Cleanup hooks fire for lesser conduits.

    Args:
        spellbook_stub (MagicMock): Spellbook stub with id.

    Raises:
        AssertionError: If hooks fail to attach to a lesser conduit.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.with_defaults()
    events: list[Conduit] = []

    def hook(conduit: Conduit) -> None:
        """
        Record cleanup hook invocations.

        Args:
            conduit (Conduit): Conduit being cleaned.

        Returns:
            None: Hook does not return a value.
        """
        events.append(conduit)

    configuration.add_hook(
        spellbook_stub._id,
        "on_conduit_cleanup_start",
        hook,
    )
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        assert conduit._conduit_hooks is not None
        assert conduit._conduit_hooks == configuration.get_hooks(spellbook_stub._id)
        assert conduit._conduit_hooks is not configuration.get_hooks(spellbook_stub._id)
        conduit.cleanup()
        assert events == [conduit]
    finally:
        if not conduit._cleaned:
            conduit.cleanup()


def test_initialize_conduit_hooks_copies_hook_lists_from_configuration(
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify Conduit snapshots hook lists from SpellbookConfiguration.

    Contract:
        - Conduit keeps detached list copies for conduit and meld hook maps.
        - Later SpellbookConfiguration list mutations do not mutate Conduit maps.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.with_defaults()

    def conduit_hook(conduit: Conduit) -> None:
        """
        No-op conduit hook for copy checks.
        """
        _ = conduit

    def conduit_hook_2(conduit: Conduit) -> None:
        """
        Secondary no-op conduit hook for copy checks.
        """
        _ = conduit

    def meld_hook(conduit: Conduit) -> None:
        """
        No-op meld hook for copy checks.
        """
        _ = conduit

    def meld_hook_2(conduit: Conduit) -> None:
        """
        Secondary no-op meld hook for copy checks.
        """
        _ = conduit

    configuration.add_hook(spellbook_stub._id, "on_conduit_cleanup_start", conduit_hook)
    configuration.add_hook(spellbook_stub._id, "on_meld_pre_resolve", meld_hook)

    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        config_hooks = configuration.get_hooks(spellbook_stub._id)
        config_hooks["on_conduit_cleanup_start"].append(conduit_hook_2)
        config_hooks["on_meld_pre_resolve"].append(meld_hook_2)

        assert conduit._conduit_hooks is not None
        assert conduit._meld_hooks is not None
        assert conduit._conduit_hooks["on_conduit_cleanup_start"] == [conduit_hook]
        assert conduit._meld_hooks["on_meld_pre_resolve"] == [meld_hook]
    finally:
        conduit.cleanup()


def test_snapshot_split_hook_maps_from_configuration_uses_static_hook_lists(
    spellbook_stub: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify Conduit pulls only static hook names from SpellbookConfiguration hook maps.

    Contract:
        - Unknown hook keys are ignored.
        - Known hook keys are copied into the proper conduit/meld maps.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.with_defaults()

    def known_conduit_hook(conduit: Conduit) -> None:
        """
        No-op known conduit hook.
        """
        _ = conduit

    def known_meld_hook(conduit: Conduit) -> None:
        """
        No-op known meld hook.
        """
        _ = conduit

    def unknown_hook(conduit: Conduit) -> None:
        """
        No-op unknown hook.
        """
        _ = conduit

    monkeypatch.setattr(
        configuration,
        "get_hooks",
        lambda owner_id: {
            "on_conduit_cleanup_start": [known_conduit_hook],
            "on_meld_pre_resolve": [known_meld_hook],
            "unknown_hook_name": [unknown_hook],
        },
    )

    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        assert conduit._conduit_hooks is not None
        assert conduit._meld_hooks is not None
        assert "on_conduit_cleanup_start" in conduit._conduit_hooks
        assert "on_meld_pre_resolve" in conduit._meld_hooks
        assert "unknown_hook_name" not in conduit._conduit_hooks
        assert "unknown_hook_name" not in conduit._meld_hooks
    finally:
        conduit.cleanup()


def test_register_conduit_hooks_registers_locally_only(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify hook registration is local-only and does not mutate SpellbookConfiguration.

    Contract:
        - Registered conduit hooks land in _local_conduit_hooks.
        - Shared configuration hook map remains unchanged.
    """
    def hook(conduit: Conduit) -> None:
        """
        No-op hook for local registration checks.
        """
        _ = conduit

    conduit_dynamic_normal.register_conduit_hooks(
        {"on_conduit_cleanup_start": hook}
    )

    spellbook_id = conduit_dynamic_normal._spellbook._id
    config_hooks = conduit_dynamic_normal._configuration.get_hooks(spellbook_id)
    assert "on_conduit_cleanup_start" not in config_hooks
    assert conduit_dynamic_normal._local_conduit_hooks is not None
    assert conduit_dynamic_normal._local_conduit_hooks["on_conduit_cleanup_start"][0] is hook


def test_merge_conduit_hooks_rejects_unknown_hook_name(
    conduit_normal: Conduit,
) -> None:
    """_merge_conduit_hooks should reject unknown hook names."""
    with pytest.raises(ValueError, match="Unknown hook name"):
        conduit_normal._merge_conduit_hooks({}, {"unknown_hook": lambda conduit: None})


def test_merge_conduit_hooks_rejects_invalid_hook_container(
    conduit_normal: Conduit,
) -> None:
    """_merge_conduit_hooks should reject non-callable, non-sequence hook values."""
    with pytest.raises(TypeError, match="callable or a list/tuple"):
        conduit_normal._merge_conduit_hooks({}, {"on_conduit_cleanup_start": "invalid"})


def test_merge_conduit_hooks_rejects_non_callable_entries(
    conduit_normal: Conduit,
) -> None:
    """_merge_conduit_hooks should reject non-callable entries inside sequences."""
    with pytest.raises(TypeError, match="must be callable"):
        conduit_normal._merge_conduit_hooks(
            {},
            {"on_conduit_cleanup_start": [lambda conduit: None, "invalid"]},
        )


def test_collect_conduit_hook_chain_merges_shared_then_local(
    conduit_normal: Conduit,
) -> None:
    """_collect_conduit_hook_chain should preserve shared-before-local ordering."""
    shared = lambda conduit: None
    local = lambda conduit: None
    conduit_normal._conduit_hooks = {"on_conduit_cleanup_start": [shared]}
    conduit_normal._local_conduit_hooks = {"on_conduit_cleanup_start": [local]}

    chain = conduit_normal._collect_conduit_hook_chain("on_conduit_cleanup_start")

    assert chain == [shared, local]


def test_merge_conduit_hooks_extends_sequence_of_callables_in_order(
    conduit_normal: Conduit,
) -> None:
    """_merge_conduit_hooks should extend sequence hook values in order."""
    first = lambda conduit: None
    second = lambda conduit: None
    hook_map: dict[str, list[object]] = {}

    conduit_normal._merge_conduit_hooks(
        hook_map,
        {"on_conduit_cleanup_start": [first, second]},
    )

    assert hook_map["on_conduit_cleanup_start"] == [first, second]


def test_register_conduit_hooks_local_allowed_after_configuration_freeze(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify local meld hook registration remains available after configuration freeze.

    Contract:
        - Local registration succeeds after freeze.
        - Shared hook map remains unchanged.
    """
    conduit_dynamic_normal._configuration.freeze()

    def hook(conduit: Conduit) -> None:
        """
        No-op hook for frozen local registration checks.
        """
        _ = conduit

    conduit_dynamic_normal.register_conduit_hooks(
        {"on_meld_pre_resolve": hook}
    )

    spellbook_id = conduit_dynamic_normal._spellbook._id
    config_hooks = conduit_dynamic_normal._configuration.get_hooks(spellbook_id)
    assert "on_meld_pre_resolve" not in config_hooks
    assert conduit_dynamic_normal._local_conduit_hooks is not None
    assert conduit_dynamic_normal._local_conduit_hooks["on_meld_pre_resolve"][0] is hook
    assert conduit_dynamic_normal._meld._meld_hooks is not None
    assert "on_meld_pre_resolve" not in conduit_dynamic_normal._meld._meld_hooks


def test_register_conduit_hooks_local_does_not_wire_non_meld_hooks_to_meld(
    conduit_normal: Conduit,
) -> None:
    """
    Verify non-meld local hooks remain conduit-only.

    Contract:
        - Non-meld hook stores in _local_conduit_hooks.
        - Meld hook map does not include non-meld hook names.
        - SpellbookConfiguration hook registry is not modified.
    """
    def hook(conduit: Conduit) -> None:
        """
        No-op hook for local registration checks.
        """
        _ = conduit

    conduit_normal.register_conduit_hooks(
        {"on_conduit_cleanup_start": hook}
    )

    assert conduit_normal._local_conduit_hooks is not None
    assert conduit_normal._local_conduit_hooks["on_conduit_cleanup_start"][0] is hook
    assert conduit_normal._meld._meld_hooks is not None
    assert "on_conduit_cleanup_start" not in conduit_normal._meld._meld_hooks

    spellbook_id = conduit_normal._spellbook._id
    config_hooks = conduit_normal._configuration.get_hooks(spellbook_id)
    assert "on_conduit_cleanup_start" not in config_hooks


def test_register_conduit_hooks_noop_for_empty_mapping(
    conduit_normal: Conduit,
) -> None:
    """register_conduit_hooks should no-op for an empty mapping."""
    conduit_normal.register_conduit_hooks({})

    assert conduit_normal._local_conduit_hooks is None


def test_register_conduit_hooks_local_does_not_propagate_to_lesser(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> None:
    """
    Verify local hook registration does not affect other conduits.

    Contract:
        - Local-only hooks remain invisible to other conduits.
    """
    normal = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
    )
    lesser = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        def hook(conduit: Conduit) -> None:
            """
            No-op hook for propagation checks.
            """
            _ = conduit

        normal.register_conduit_hooks(
            {"on_conduit_cleanup_start": hook}
        )

        assert normal._local_conduit_hooks is not None
        assert normal._local_conduit_hooks["on_conduit_cleanup_start"][0] is hook
        assert lesser._conduit_hooks is not None
        assert "on_conduit_cleanup_start" not in lesser._conduit_hooks
    finally:
        lesser.cleanup()
        normal.cleanup()


def test_register_conduit_hooks_local_preserves_shared_map(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> None:
    """
    Verify local hook registration preserves shared configuration hooks.

    Contract:
        - Conduit hook map remains detached from configuration hook map.
        - Local hooks are stored separately.
        - SpellbookConfiguration hook map retains only shared hooks.
    """
    configuration_automatic.add_hook(
        spellbook_stub._id,
        "on_conduit_cleanup_start",
        lambda conduit: None,
    )

    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        def local_hook(conduit: Conduit) -> None:
            """
            No-op hook for local detachment checks.
            """
            _ = conduit

        shared_hooks = configuration_automatic.get_hooks(spellbook_stub._id)
        conduit.register_conduit_hooks(
            {"on_conduit_cleanup_start": local_hook}
        )

        assert conduit._conduit_hooks is not shared_hooks
        assert conduit._conduit_hooks["on_conduit_cleanup_start"][0] is shared_hooks["on_conduit_cleanup_start"][0]
        assert conduit._local_conduit_hooks is not None
        assert conduit._local_conduit_hooks["on_conduit_cleanup_start"][-1] is local_hook
        assert shared_hooks["on_conduit_cleanup_start"][-1] is not local_hook
        assert len(shared_hooks["on_conduit_cleanup_start"]) == 1
        assert conduit._meld._meld_hooks is not None
        assert "on_conduit_cleanup_start" not in conduit._meld._meld_hooks
    finally:
        conduit.cleanup()


def test_fire_conduit_hooks_swallows_exceptions_and_continues(
    conduit_normal: Conduit,
) -> None:
    """
    Verify hook execution continues after an exception.

    Contract:
        - Hook exceptions are logged and suppressed.
        - Later hooks still run.

    Args:
        conduit_normal (Conduit): Conduit used to fire hooks.

    Raises:
        AssertionError: If the healthy hook is not executed.
    """
    events: list[Conduit] = []

    def bad(conduit: Conduit) -> None:
        """
        Hook that always raises.

        Args:
            conduit (Conduit): Conduit invoking the hook.

        Raises:
            RuntimeError: Always raised to test suppression.
        """
        raise RuntimeError("boom")

    def good(conduit: Conduit) -> None:
        """
        Hook that records successful execution.

        Args:
            conduit (Conduit): Conduit invoking the hook.

        Returns:
            None: Hook does not return a value.
        """
        events.append(conduit)

    conduit_normal._conduit_hooks = {
        "on_conduit_cleanup_start": [bad, good],
    }

    conduit_normal._fire_conduit_hooks("on_conduit_cleanup_start", conduit_normal)

    assert events == [conduit_normal]


def test_apply_configuration_flags_logs_and_reraises_on_configuration_failure(
    conduit_normal: Conduit,
) -> None:
    """_apply_configuration_flags should log and re-raise configuration lookup failures."""
    conduit_normal._logger = MagicMock()

    class _BrokenFrameConfiguration:
        @property
        def system_state(self):
            raise RuntimeError("config boom")

    conduit_normal._spellbook._aetheric_frame_configuration = _BrokenFrameConfiguration()

    with pytest.raises(RuntimeError, match="config boom"):
        conduit_normal._apply_configuration_flags()

    conduit_normal._logger.error.assert_called_once()


def test_repr_includes_name_and_id(conduit_normal: Conduit) -> None:
    """__repr__ should include the conduit name and id."""
    conduit_normal._name = "alpha"
    text = repr(conduit_normal)

    assert "Conduit" in text
    assert "alpha" in text
    assert conduit_normal._id in text


def test_resolve_peer_conduit_for_contract_hooks_uses_aether_for_ids(
    conduit_dynamic_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify contract hooks resolve peers by id using Aether.

    Contract:
        - Aether is queried for conduit_id resolution.
        - Hook receives the resolved peer conduit.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        aether_stub (MagicMock): Aether stub for resolution.

    Raises:
        AssertionError: If peer resolution or hook firing fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._add_spell_to_contract.return_value = True
    peer = MagicMock()
    aether_stub._get_conduit_by_id.return_value = peer
    events: list[tuple[Conduit, Conduit]] = []

    def hook(left: Conduit, right: Conduit) -> None:
        """
        Record contract creation hook calls.

        Args:
            left (Conduit): Source conduit.
            right (Conduit): Target conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append((left, right))

    conduit_dynamic_normal._conduit_hooks = {"on_contract_created": [hook]}
    spellbook = conduit_dynamic_normal._spellbook
    spellbook._active_change_request = ChangeControlTransactionRequest(
        request_id="tx-test-link",
        request_type=ChangeTransactionType.LINK,
        created_at=time.time(),
        initiator_conduit_id=conduit_dynamic_normal._id,
        spellbook_id=spellbook._id,
        conduit_ids=(conduit_dynamic_normal._id, "peer-1"),
        scope_keys=(),
        scope_hashes=(),
        binding_keys=(),
        contract_keys=(),
        metadata={},
    )

    result = conduit_dynamic_normal.add_spell_to_contract(
        spell_id="sha-1",
        conduit_id="peer-1",
        permissions="read",
        aetheric_frame="frame-2",
    )

    assert result is True
    aether_stub._get_conduit_by_id.assert_called_once_with("peer-1", "frame-2")
    assert events == [(conduit_dynamic_normal, peer)]


def test_add_spell_to_contract_rejects_lesser_conduits(
    conduit_dynamic_lesser: Conduit,
) -> None:
    """
    Verify contract APIs reject lesser conduits even in dynamic mode.

    Contract:
        - Only normal conduits can create spell contracts.

    Args:
        conduit_dynamic_lesser (Conduit): Dynamic lesser conduit instance.

    Raises:
        AssertionError: If lesser conduit does not raise.
    """
    with pytest.raises(RuntimeError, match="Only normal conduits"):
        conduit_dynamic_lesser.add_spell_to_contract(
            spell_id="sha-1",
            conduit_id="peer-1",
        )


def test_describe_contract_delegates_and_returns_payload(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify _describe_contract delegates to the conduit ward.

    Contract:
        - Ward _describe_contract is called with conduit id.
        - Payload is returned unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    payload = {"ok": True}
    conduit_dynamic_normal._conduit_ward._describe_contract.return_value = payload

    result = conduit_dynamic_normal._describe_contract("peer-1")

    assert result is payload
    conduit_dynamic_normal._conduit_ward._describe_contract.assert_called_once_with(
        "peer-1"
    )


def test_register_to_creations_adds_unique_spell(
    conduit_normal: Conduit,
) -> None:
    """
    Verify _register_to_creations registers unique existing-object spells.

    Contract:
        - Existence.unique spells are registered via add_creation.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If add_unique is not called correctly.
    """
    spell = MagicMock()
    spell.existence = Existence.unique
    spell.spell_id = "spell-1"
    spell.has_disposal_methods = True
    spell.disposal_method_names = ["cleanup"]
    conduit_normal._creations.add_creation = MagicMock()
    instance = object()

    conduit_normal._register_to_creations(spell, instance)

    conduit_normal._creations.add_creation.assert_called_once_with(
        "spell-1",
        instance,
        has_disposal_methods=True,
        disposal_methods=["cleanup"],
    )


def test_register_to_creations_rejects_non_unique_spells(
    conduit_normal: Conduit,
) -> None:
    """
    Verify _register_to_creations rejects non-unique existence modes.

    Contract:
        - Existing-object spells must use Existence.unique.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If non-unique spells are accepted.
    """
    spell = MagicMock()
    spell.existence = Existence.many
    spell.spell_id = "spell-1"

    with pytest.raises(RuntimeError, match="Existing-object spells must use Existence.unique"):
        conduit_normal._register_to_creations(spell, object())


def test_register_to_creations_accepts_lesser_conduits(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify _register_to_creations accepts lesser conduits with Creations.

    Contract:
        - Lesser conduits also register through Creations.add_creation.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If lesser conduits fail to register creations.
    """
    spell = MagicMock()
    spell.existence = Existence.unique
    spell.spell_id = "spell-1"
    spell.has_disposal_methods = False
    spell.disposal_method_names = []
    conduit_lesser._creations.add_creation = MagicMock()

    conduit_lesser._register_to_creations(spell, object())
    conduit_lesser._creations.add_creation.assert_called_once()


def test_register_to_creations_rejects_non_creations_manager(
    conduit_normal: Conduit,
) -> None:
    """
    Verify _register_to_creations fails fast when the creations manager is invalid.

    Contract:
        - Non-Creations managers raise RuntimeError and log the failure.
    """
    spell = MagicMock()
    spell.existence = Existence.unique
    spell.spell_id = "spell-1"
    conduit_normal._creations = object()
    conduit_normal._logger = MagicMock()

    with pytest.raises(RuntimeError, match="requires a Creations manager"):
        conduit_normal._register_to_creations(spell, object())

    conduit_normal._logger.error.assert_called_once()


def test_cleanup_normal_unregisters_from_aether_and_removes_spells(
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> None:
    """
    Verify normal cleanup removes spell registrations and unregisters cloud.

    Contract:
        - Spell registrations are removed from Aether.
        - Conduit is removed from Aether.
        - Dynamic cloud registration is removed when named.

    Args:
        configuration_automatic (SpellbookConfiguration): Automatic configuration defaults.
        spellbook_stub (MagicMock): Spellbook stub with spell registry.
        aether_stub (MagicMock): Aether stub for removal checks.

    Raises:
        AssertionError: If Aether unregister calls are missing.
    """
    spellbook_stub._spells = {"spell-1": MagicMock()}
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        automatic=False,
        name="alpha",
    )
    try:
        aether_stub.reset_mock()
        conduit.cleanup()
        aether_stub._remove_spells_from_aether.assert_called_once_with(
            conduit._id,
            {"spell-1"},
            "default",
        )
        aether_stub._remove_conduit.assert_called_once_with(
            conduit,
            "default",
        )
        aether_stub._unregister_conduit_cloud.assert_called_once_with(
            conduit,
            "default",
        )
    finally:
        if not conduit._cleaned:
            conduit.cleanup()


def test_cleanup_spellspaces_flushes_stack(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify _cleanup_spellspaces drains and disposes lingering spellspaces.

    Contract:
        - Spellspaces on the stack are cleaned and the stack is cleared.

    Args:
        conduit_lesser (Conduit): Lesser conduit used for cleanup.

    Raises:
        AssertionError: If spellspace cleanup is skipped.
    """
    space = MagicMock()
    conduit_lesser._spellspace_stack.set([space])

    conduit_lesser._cleanup_spellspaces()

    assert space.cleanup.called is True
    assert conduit_lesser._spellspace_stack.get() == []
