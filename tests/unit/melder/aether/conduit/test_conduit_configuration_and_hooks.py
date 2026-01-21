import logging
import time
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.utilities.logger.safe_logger import SafeLogger


def test_configure_logger_rejects_invalid_logger(
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify Conduit rejects non-logger values during initialization.

    Contract:
        - Conduit init raises TypeError when the provided logger is invalid.

    Args:
        configuration_automatic (Configuration): Automatic configuration defaults.
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


def test_configure_logger_prefers_explicit_logger_over_factory(
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify explicit logger overrides any configuration logger factory.

    Contract:
        - When logger is supplied, configuration factory is not called.

    Args:
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If the factory is invoked despite explicit logger.
    """
    configuration = Configuration()
    configuration.automatic_defaults()
    factory_called = {"value": False}

    def factory(obj: object) -> logging.Logger:
        """
        Record whether the factory is invoked.

        Args:
            obj (object): Conduit instance passed to the factory.

        Returns:
            logging.Logger: Logger instance for the conduit.
        """
        factory_called["value"] = True
        return logging.Logger("factory")

    configuration.set_logger_factory(factory)
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
        assert factory_called["value"] is False
        assert isinstance(conduit._logger, SafeLogger)
    finally:
        conduit.cleanup()


def test_resolve_logger_from_config_uses_factory_and_passes_conduit(
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify configuration logger factory is used and receives the conduit.

    Contract:
        - Configuration factory is called with the conduit.
        - Conduit stores a SafeLogger instance.

    Args:
        spellbook_stub (MagicMock): Spellbook stub for construction.

    Raises:
        AssertionError: If factory is not called or logger wrapper missing.
    """
    configuration = Configuration()
    configuration.set_property("system_state", "automatic")
    configuration.with_defaults()
    seen: dict[str, object] = {}

    def factory(obj: object) -> logging.Logger:
        """
        Capture the conduit instance for verification.

        Args:
            obj (object): Conduit instance passed to the factory.

        Returns:
            logging.Logger: Logger instance for the conduit.
        """
        seen["obj"] = obj
        return logging.Logger("factory-logger")

    configuration.set_logger_factory(factory)
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


def test_apply_configuration_flags_updates_dynamic_and_debugging(
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> None:
    """
    Verify configuration flags drive dynamic and debugging state.

    Contract:
        - _apply_configuration_flags reads system_state/debugging.
        - Dynamic state enables conduit cloud access.

    Args:
        spellbook_stub (MagicMock): Spellbook stub for construction.
        aether_stub (MagicMock): Aether stub for dynamic access checks.

    Raises:
        AssertionError: If flags do not update internal state.
    """
    configuration = Configuration()
    configuration.set_property("system_state", SystemState.dynamic)
    configuration.set_property("debugging", True)
    configuration.with_defaults()
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
        assert conduit.__debugger_mode__ is True
        aether_stub._get_conduit_cloud.return_value = MagicMock()
        conduit.get_conduit_cloud()
        aether_stub._get_conduit_cloud.assert_called_once_with("default")
    finally:
        conduit.cleanup()


def test_configure_conduit_state_clears_name_for_lesser(
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify lesser conduits discard names during initialization.

    Contract:
        - Lesser conduits cannot retain a name.

    Args:
        configuration_automatic (Configuration): Automatic configuration defaults.
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
    configuration = Configuration()
    configuration.set_property("system_state", "automatic")
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


def test_initialize_conduit_hooks_skips_for_lesser(
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify lesser conduits do not attach configuration hooks.

    Contract:
        - _initialize_conduit_hooks is a no-op for lesser conduits.
        - Cleanup hooks are not fired for lesser conduits.

    Args:
        spellbook_stub (MagicMock): Spellbook stub with id.

    Raises:
        AssertionError: If hooks attach to a lesser conduit.
    """
    configuration = Configuration()
    configuration.set_property("system_state", "automatic")
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
        assert conduit._conduit_hooks is None
        conduit.cleanup()
        assert events == []
    finally:
        if not conduit._cleaned:
            conduit.cleanup()


def test_register_conduit_hooks_on_upgrade_registers_in_config_and_local(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify per-conduit hooks register into configuration and local map.

    Contract:
        - Configuration registry stores hooks under conduit id.
        - Conduit local hook map includes registered hooks.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If hooks are not registered into both stores.
    """
    def hook(conduit: Conduit) -> None:
        """
        No-op hook for registration checks.

        Args:
            conduit (Conduit): Conduit invoking the hook.

        Returns:
            None: Hook does not return a value.
        """
        _ = conduit

    conduit_dynamic_normal._register_conduit_hooks_on_upgrade(
        {"on_conduit_cleanup_start": hook}
    )

    config_hooks = conduit_dynamic_normal._configuration.get_hooks(
        conduit_dynamic_normal._id
    )
    assert config_hooks["on_conduit_cleanup_start"][0] is hook
    assert conduit_dynamic_normal._conduit_hooks is not None
    assert conduit_dynamic_normal._conduit_hooks["on_conduit_cleanup_start"][0] is hook


def test_register_conduit_hooks_on_upgrade_raises_when_not_dynamic(
    conduit_normal: Conduit,
) -> None:
    """
    Verify hook registration is blocked outside dynamic environments.

    Contract:
        - Non-dynamic conduits cannot register per-conduit hooks.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If hook registration does not raise.
    """
    def hook(conduit: Conduit) -> None:
        """
        No-op hook for registration checks.

        Args:
            conduit (Conduit): Conduit invoking the hook.

        Returns:
            None: Hook does not return a value.
        """
        _ = conduit

    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal._register_conduit_hooks_on_upgrade(
            {"on_conduit_cleanup_start": hook}
        )


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
        - Existence.unique spells are registered via add_unique.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If add_unique is not called correctly.
    """
    spell = MagicMock()
    spell.existence = Existence.unique
    spell.spell_id = "spell-1"
    conduit_normal._creations.add_unique = MagicMock()
    instance = object()

    conduit_normal._register_to_creations(spell, instance)

    conduit_normal._creations.add_unique.assert_called_once_with("spell-1", instance)


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


def test_register_to_creations_rejects_lesser_conduits(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify _register_to_creations rejects lesser conduits.

    Contract:
        - Only normal conduits expose Creations registration.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If lesser conduits can register creations.
    """
    spell = MagicMock()
    spell.existence = Existence.unique
    spell.spell_id = "spell-1"

    with pytest.raises(RuntimeError, match="only be called on normal Creations"):
        conduit_lesser._register_to_creations(spell, object())


def test_cleanup_normal_unregisters_from_aether_and_removes_spells(
    configuration_automatic: Configuration,
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
        configuration_automatic (Configuration): Automatic configuration defaults.
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
