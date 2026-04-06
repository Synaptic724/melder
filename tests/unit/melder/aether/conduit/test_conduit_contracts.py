import time
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)
from melder.spellbook.configuration.configuration import Configuration


def _set_active_link_transaction(conduit: Conduit, peer_id: str) -> None:
    """
    Configure a link transaction on the conduit spellbook for contract tests.

    Purpose:
        Provide the active link request required by contract mutations.
    Contract:
        - Updates the spellbook active request with borrower + peer ids.
        - Uses a deterministic request payload for unit tests.
    Args:
        conduit: Borrower conduit that owns the spellbook.
        peer_id: Peer conduit id involved in the contract mutation.
    Returns:
        None.
    """
    spellbook = conduit._spellbook
    spellbook._active_change_request = ChangeControlTransactionRequest(
        request_id="tx-test-link",
        request_type=ChangeTransactionType.LINK,
        created_at=time.time(),
        initiator_conduit_id=conduit._id,
        spellbook_id=spellbook._id,
        conduit_ids=(conduit._id, peer_id),
        scope_keys=(),
        scope_hashes=(),
        binding_keys=(),
        contract_keys=(),
        metadata={},
    )


def test_link_raises_when_not_dynamic(
    conduit_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify link is blocked when the conduit is not in a dynamic environment.

    Contract:
        - Non-dynamic conduits cannot initiate links.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If link does not raise in non-dynamic mode.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.link(conduit_lesser)


def test_link_rejects_non_conduit_target(conduit_dynamic_normal: Conduit) -> None:
    """
    Verify link enforces target type validation.

    Contract:
        - Non-IConduit targets raise TypeError.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If non-conduit targets do not raise.
    """
    with pytest.raises(TypeError, match="Expected IConduit"):
        conduit_dynamic_normal.link(object())


def test_link_rejects_target_without_id(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify link rejects targets without a valid creation context.

    Contract:
        - Targets with empty ids are rejected.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        configuration_automatic (Configuration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.

    Raises:
        AssertionError: If missing target id does not raise.
    """
    target = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        target._id = ""
        with pytest.raises(RuntimeError, match="valid creation context"):
            conduit_dynamic_normal.link(target)
    finally:
        target.cleanup()


def test_link_delegates_to_ward_and_fires_hook(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify link delegates to the ward and fires post-link hooks.

    Contract:
        - Ward _link is called with the target conduit.
        - on_conduit_post_link hook fires on success.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        configuration_automatic (Configuration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub with storage maps.

    Raises:
        AssertionError: If delegation or hook firing fails.
    """
    target = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        conduit_dynamic_normal._conduit_ward = MagicMock()
        conduit_dynamic_normal._conduit_ward._link.return_value = True
        events: list[tuple[Conduit, Conduit]] = []

        def hook(left: Conduit, right: Conduit) -> None:
            """
            Record post-link hook calls.

            Args:
                left (Conduit): Source conduit.
                right (Conduit): Target conduit.

            Returns:
                None: Hook does not return a value.
            """
            events.append((left, right))

        conduit_dynamic_normal._conduit_hooks = {"on_conduit_post_link": [hook]}

        result = conduit_dynamic_normal.link(target)

        assert result is True
        conduit_dynamic_normal._conduit_ward._link.assert_called_once_with(target)
        assert events == [(conduit_dynamic_normal, target)]
    finally:
        target.cleanup()


def test_link_publishes_peer_record_when_target_participates_in_nexus(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """Successful link should publish the peer conduit record when the peer is Nexus-published and normal."""
    target = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        automatic=False,
    )
    try:
        target._nexus_publish_enabled = True
        target._nexus = MagicMock()
        conduit_dynamic_normal._conduit_ward = MagicMock()
        conduit_dynamic_normal._conduit_ward._link.return_value = True

        conduit_dynamic_normal.link(target)

        target._nexus._publish_conduit_record.assert_called_once_with(target)
    finally:
        target.cleanup()


def test_link_false_does_not_fire_hook(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify link does not fire hooks when the ward rejects the link.

    Contract:
        - Hook list remains empty if link returns False.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If hooks fire on a rejected link.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._link.return_value = False
    events: list[tuple[Conduit, Conduit]] = []

    def hook(left: Conduit, right: Conduit) -> None:
        """
        Record post-link hook calls.

        Args:
            left (Conduit): Source conduit.
            right (Conduit): Target conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append((left, right))

    conduit_dynamic_normal._conduit_hooks = {"on_conduit_post_link": [hook]}

    conduit_dynamic_normal.link(conduit_lesser)

    assert events == []


def test_sever_link_raises_when_not_dynamic(
    conduit_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify sever_link is blocked when the conduit is not in a dynamic environment.

    Contract:
        - Non-dynamic conduits cannot sever links.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If sever_link does not raise in non-dynamic mode.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.sever_link(conduit_lesser)


def test_sever_link_delegates_and_fires_hook(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify sever_link delegates to the ward and fires post-unlink hooks.

    Contract:
        - Ward _sever_link is called with the target conduit.
        - on_conduit_post_unlink hook fires on success.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If delegation or hook firing fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._sever_link.return_value = True
    events: list[tuple[Conduit, Conduit]] = []

    def hook(left: Conduit, right: Conduit) -> None:
        """
        Record post-unlink hook calls.

        Args:
            left (Conduit): Source conduit.
            right (Conduit): Target conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append((left, right))

    conduit_dynamic_normal._conduit_hooks = {"on_conduit_post_unlink": [hook]}

    result = conduit_dynamic_normal.sever_link(conduit_lesser)

    assert result is True
    conduit_dynamic_normal._conduit_ward._sever_link.assert_called_once_with(conduit_lesser)
    assert events == [(conduit_dynamic_normal, conduit_lesser)]


def test_sever_link_publishes_peer_record_when_target_participates_in_nexus(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """Successful unlink should publish the peer conduit record when the peer is Nexus-published and normal."""
    target = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        automatic=False,
    )
    try:
        target._nexus_publish_enabled = True
        target._nexus = MagicMock()
        conduit_dynamic_normal._conduit_ward = MagicMock()
        conduit_dynamic_normal._conduit_ward._sever_link.return_value = True

        conduit_dynamic_normal.sever_link(target)

        target._nexus._publish_conduit_record.assert_called_once_with(target)
    finally:
        target.cleanup()


def test_add_spell_to_contract_raises_when_not_dynamic(
    conduit_normal: Conduit,
) -> None:
    """
    Verify add_spell_to_contract is blocked in non-dynamic environments.

    Contract:
        - Dynamic environment is required for contract APIs.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If the call does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.add_spell_to_contract(spell_id="sha-1", conduit_id="peer")


def test_add_spell_to_contract_delegates_and_fires_hook(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify add_spell_to_contract delegates to the ward and fires hooks on success.

    Contract:
        - Ward _add_spell_to_contract receives the full argument set.
        - on_contract_created hook fires when result is True.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If delegation or hook firing fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._add_spell_to_contract.return_value = True
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
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.add_spell_to_contract(
        spell_id="sha-1",
        conduit=conduit_lesser,
        permissions="read",
        reason=DetailReason.manual,
        root_spell_id="root-1",
        link_dependencies=True,
    )

    assert result is True
    conduit_dynamic_normal._conduit_ward._add_spell_to_contract.assert_called_once_with(
        spell=None,
        spell_id="sha-1",
        conduit=conduit_lesser,
        conduit_id=None,
        permissions="read",
        aetheric_frame="default",
        reason=DetailReason.manual,
        root_spell_id="root-1",
        link_dependencies=True,
    )
    assert events == [(conduit_dynamic_normal, conduit_lesser)]


def test_add_spell_to_contract_skips_hook_on_false(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify add_spell_to_contract does not fire hooks on failure.

    Contract:
        - Hook list remains empty when ward returns False.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If hooks fire on failure.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._add_spell_to_contract.return_value = False
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
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.add_spell_to_contract(
        spell_id="sha-1",
        conduit=conduit_lesser,
    )

    assert result is False
    assert events == []


def test_add_spells_to_contract_fires_hook_on_any_success(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify add_spells_to_contract fires hooks when any contract is added.

    Contract:
        - Any True result triggers on_contract_created.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If hook does not fire on partial success.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._add_spells_to_contract.return_value = {
        "a": False,
        "b": True,
    }
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
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.add_spells_to_contract(
        ["a", "b"],
        conduit=conduit_lesser,
    )

    assert result == {"a": False, "b": True}
    assert events == [(conduit_dynamic_normal, conduit_lesser)]


def test_add_spells_to_contract_normalizes_success_failed_report(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """add_spells_to_contract should normalize success/failed report dicts."""
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._add_spells_to_contract.return_value = {
        "success": ["a", "b"],
        "failed": {"c": "blocked"},
    }
    conduit_dynamic_normal._conduit_hooks = {}
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.add_spells_to_contract(
        ["a", "b", "c"],
        conduit=conduit_lesser,
    )

    assert result == {"a": True, "b": True, "c": False}


def test_add_spells_to_contract_normalizes_truthy_values(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """add_spells_to_contract should coerce arbitrary truthy/falsy values to bools."""
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._add_spells_to_contract.return_value = {
        "a": 1,
        "b": 0,
    }
    conduit_dynamic_normal._conduit_hooks = {}
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.add_spells_to_contract(
        ["a", "b"],
        conduit=conduit_lesser,
    )

    assert result == {"a": True, "b": False}


def test_add_spells_to_contract_skips_hook_when_none_succeed(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify add_spells_to_contract does not fire hooks when all fail.

    Contract:
        - No hook is fired if all additions return False.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If hook fires when no additions succeeded.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._add_spells_to_contract.return_value = {
        "a": False,
    }
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
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.add_spells_to_contract(
        ["a"],
        conduit=conduit_lesser,
    )

    assert result == {"a": False}
    assert events == []


def test_remove_spell_from_contract_fires_hook_on_success(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify remove_spell_from_contract fires hooks when removal succeeds.

    Contract:
        - on_contract_removed fires on a True result.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If hook does not fire on success.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._remove_spell_from_contract.return_value = True
    events: list[tuple[Conduit, Conduit]] = []

    def hook(left: Conduit, right: Conduit) -> None:
        """
        Record contract removal hook calls.

        Args:
            left (Conduit): Source conduit.
            right (Conduit): Target conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append((left, right))

    conduit_dynamic_normal._conduit_hooks = {"on_contract_removed": [hook]}
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.remove_spell_from_contract(
        spell_id="sha-1",
        conduit=conduit_lesser,
        root_spell_id="root-1",
    )

    assert result is True
    assert events == [(conduit_dynamic_normal, conduit_lesser)]


def test_remove_spells_from_contract_fires_hook_on_any_success(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify remove_spells_from_contract fires hooks when any removal succeeds.

    Contract:
        - Any True result triggers on_contract_removed.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If hook does not fire on partial success.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._remove_spells_from_contract.return_value = {
        "a": False,
        "b": True,
    }
    events: list[tuple[Conduit, Conduit]] = []

    def hook(left: Conduit, right: Conduit) -> None:
        """
        Record contract removal hook calls.

        Args:
            left (Conduit): Source conduit.
            right (Conduit): Target conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append((left, right))

    conduit_dynamic_normal._conduit_hooks = {"on_contract_removed": [hook]}
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.remove_spells_from_contract(
        spell_ids=["a", "b"],
        conduit=conduit_lesser,
        root_spell_id="root-1",
    )

    assert result == {"a": False, "b": True}
    assert events == [(conduit_dynamic_normal, conduit_lesser)]


def test_remove_spells_from_contract_normalizes_success_failed_report(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """remove_spells_from_contract should normalize success/failed report dicts."""
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._remove_spells_from_contract.return_value = {
        "success": ["a"],
        "failed": {"b": "blocked"},
    }
    conduit_dynamic_normal._conduit_hooks = {}
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.remove_spells_from_contract(
        spell_ids=["a", "b"],
        conduit=conduit_lesser,
        root_spell_id="root-1",
    )

    assert result == {"a": True, "b": False}


def test_remove_spells_from_contract_normalizes_truthy_values(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """remove_spells_from_contract should coerce arbitrary truthy/falsy values to bools."""
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._remove_spells_from_contract.return_value = {
        "a": 1,
        "b": 0,
    }
    conduit_dynamic_normal._conduit_hooks = {}
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal.remove_spells_from_contract(
        spell_ids=["a", "b"],
        conduit=conduit_lesser,
        root_spell_id="root-1",
    )

    assert result == {"a": True, "b": False}


def test_resolve_peer_conduit_for_contract_hooks_returns_none_without_peer(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_resolve_peer_conduit_for_contract_hooks should return None when neither conduit nor conduit_id is provided."""
    result = conduit_dynamic_normal._resolve_peer_conduit_for_contract_hooks(
        None,
        None,
        "default",
    )
    assert result is None


def test_resolve_peer_conduit_for_contract_hooks_returns_none_when_aether_lookup_fails(
    conduit_dynamic_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """_resolve_peer_conduit_for_contract_hooks should swallow Aether lookup failures."""
    aether_stub._get_conduit_by_id.side_effect = RuntimeError("lookup boom")

    result = conduit_dynamic_normal._resolve_peer_conduit_for_contract_hooks(
        None,
        "peer-1",
        "default",
    )

    assert result is None


def test_remove_root_from_contracts_delegates_to_ward(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify remove_root_from_contracts delegates to the ward.

    Contract:
        - _remove_root_from_contracts is called with provided arguments.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If the ward is not called.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._remove_root_from_contracts.return_value = {"peer": True}
    _set_active_link_transaction(conduit_dynamic_normal, "peer")

    result = conduit_dynamic_normal.remove_root_from_contracts(
        root_spell_id="root-1",
        conduit_id="peer",
    )

    conduit_dynamic_normal._conduit_ward._remove_root_from_contracts.assert_called_once_with(
        root_spell_id="root-1",
        conduit=None,
        conduit_id="peer",
        aetheric_frame="default",
    )
    assert result == {"peer": True}


def test_add_spell_to_contract_with_dependencies_forwards(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify add_spell_to_contract_with_dependencies forwards to add_spell_to_contract.

    Contract:
        - Reason is DetailReason.root.
        - root_spell_id equals the spell_id.
        - link_dependencies is True.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If forwarding arguments are incorrect.
    """
    conduit_dynamic_normal.add_spell_to_contract = MagicMock(return_value=True)

    result = conduit_dynamic_normal.add_spell_to_contract_with_dependencies(
        spell_id="sha-1",
        conduit_id="peer",
        permissions="read",
        aetheric_frame="frame-1",
    )

    assert result is True
    conduit_dynamic_normal.add_spell_to_contract.assert_called_once_with(
        spell=None,
        spell_id="sha-1",
        conduit=None,
        conduit_id="peer",
        permissions="read",
        aetheric_frame="frame-1",
        reason=DetailReason.root,
        root_spell_id="sha-1",
        link_dependencies=True,
    )


def test_remove_all_spells_from_contract_fires_hook_on_success(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify _remove_all_spells_from_contract fires hooks on success.

    Contract:
        - on_contract_removed fires when ward returns True.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If hook does not fire.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._remove_all_spells_from_contract.return_value = True
    events: list[tuple[Conduit, Conduit]] = []

    def hook(left: Conduit, right: Conduit) -> None:
        """
        Record contract removal hook calls.

        Args:
            left (Conduit): Source conduit.
            right (Conduit): Target conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append((left, right))

    conduit_dynamic_normal._conduit_hooks = {"on_contract_removed": [hook]}
    _set_active_link_transaction(conduit_dynamic_normal, conduit_lesser._id)

    result = conduit_dynamic_normal._remove_all_spells_from_contract(
        conduit=conduit_lesser,
    )

    assert result is True
    assert events == [(conduit_dynamic_normal, conduit_lesser)]


def test_get_all_spells_in_contracts_rejects_non_bool(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_all_spells_in_contracts enforces boolean validate input.

    Contract:
        - Non-boolean validate values raise TypeError.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If non-boolean validate does not raise.
    """
    with pytest.raises(TypeError, match="validate"):
        conduit_dynamic_normal.get_all_spells_in_contracts(validate="yes")


def test_get_all_spells_in_contracts_delegates(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_all_spells_in_contracts delegates to the ward.

    Contract:
        - The ward return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._get_all_spells_in_contracts.return_value = {"peer": []}

    result = conduit_dynamic_normal.get_all_spells_in_contracts(validate=False)

    conduit_dynamic_normal._conduit_ward._get_all_spells_in_contracts.assert_called_once_with(
        validate=False,
    )
    assert result == {"peer": []}


def test_get_spell_in_contracts_rejects_non_string(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_spell_in_contracts enforces spell_id type.

    Contract:
        - Non-string spell_id raises TypeError.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If non-string spell_id does not raise.
    """
    with pytest.raises(TypeError, match="spell_id"):
        conduit_dynamic_normal.get_spell_in_contracts(123)


def test_get_spell_in_contracts_delegates(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_spell_in_contracts delegates to the ward.

    Contract:
        - The ward return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._get_spell_in_contracts.return_value = ("peer", MagicMock())

    result = conduit_dynamic_normal.get_spell_in_contracts("sha-1")

    conduit_dynamic_normal._conduit_ward._get_spell_in_contracts.assert_called_once_with("sha-1")
    assert result[0] == "peer"


def test_get_spells_in_contract_by_conduit_rejects_non_string(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_spells_in_contract_by_conduit enforces conduit_id type.

    Contract:
        - Non-string conduit_id raises TypeError.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If non-string conduit_id does not raise.
    """
    with pytest.raises(TypeError, match="conduit_id"):
        conduit_dynamic_normal.get_spells_in_contract_by_conduit(123)


def test_get_spells_in_contract_by_conduit_delegates(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_spells_in_contract_by_conduit delegates to the ward.

    Contract:
        - The ward return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._get_spells_in_contract_by_conduit.return_value = {"peer": []}

    result = conduit_dynamic_normal.get_spells_in_contract_by_conduit("peer")

    conduit_dynamic_normal._conduit_ward._get_spells_in_contract_by_conduit.assert_called_once_with("peer")
    assert result == {"peer": []}


def test_get_spells_in_contract_by_conduit_name_rejects_non_string(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_spells_in_contract_by_conduit_name enforces conduit_name type.

    Contract:
        - Non-string conduit_name raises TypeError.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If non-string conduit_name does not raise.
    """
    with pytest.raises(TypeError, match="conduit_name"):
        conduit_dynamic_normal.get_spells_in_contract_by_conduit_name(123)


def test_get_spells_in_contract_by_conduit_name_delegates(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_spells_in_contract_by_conduit_name delegates to the ward.

    Contract:
        - The ward return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._get_spells_in_contract_by_conduit_name.return_value = {"peer": []}

    result = conduit_dynamic_normal.get_spells_in_contract_by_conduit_name("peer")

    conduit_dynamic_normal._conduit_ward._get_spells_in_contract_by_conduit_name.assert_called_once_with("peer")
    assert result == {"peer": []}


def test_get_contracted_conduits_delegates(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify get_contracted_conduits delegates to the ward.

    Contract:
        - The ward return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    sentinel = MagicMock()
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._get_contracted_conduits.return_value = [("peer", sentinel)]

    result = conduit_dynamic_normal.get_contracted_conduits()

    conduit_dynamic_normal._conduit_ward._get_contracted_conduits.assert_called_once_with()
    assert result[0][0] == "peer"
    assert result[0][1] is sentinel


def test_validate_contracts_and_define_delegates(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify validate_contracts_and_define delegates to the ward.

    Contract:
        - The ward return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._validate_contracts_and_define.return_value = {"peer": True}

    result = conduit_dynamic_normal.validate_contracts_and_define()

    conduit_dynamic_normal._conduit_ward._validate_contracts_and_define.assert_called_once_with()
    assert result == {"peer": True}


def test_validate_received_contracts_delegates(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify validate_received_contracts delegates to the ward.

    Contract:
        - The ward return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._validate_received_contracts.return_value = True

    result = conduit_dynamic_normal.validate_received_contracts()

    conduit_dynamic_normal._conduit_ward._validate_received_contracts.assert_called_once_with()
    assert result is True


def test_resolve_contract_peer_ids_raises_when_target_missing_and_allow_all_false(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_resolve_contract_peer_ids should fail when no peer target is provided and allow_all_links is False."""
    with pytest.raises(RuntimeError, match="requires a target conduit or conduit_id"):
        conduit_dynamic_normal._resolve_contract_peer_ids(
            conduit=None,
            conduit_id=None,
            allow_all_links=False,
        )


def test_resolve_contract_peer_ids_uses_all_current_links_when_allowed(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_resolve_contract_peer_ids should derive peer ids from current links when allowed."""
    peer_one = MagicMock()
    peer_one._id = "peer-1"
    peer_two = MagicMock()
    peer_two._id = "peer-2"
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._get_links.return_value = [peer_one, None, peer_two]

    result = conduit_dynamic_normal._resolve_contract_peer_ids(
        conduit=None,
        conduit_id=None,
        allow_all_links=True,
    )

    assert set(result) == {"peer-1", "peer-2"}


def test_require_link_transaction_for_contract_raises_when_spellbook_missing(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_require_link_transaction_for_contract should fail when the spellbook is unavailable."""
    conduit_dynamic_normal._logger = MagicMock()
    conduit_dynamic_normal._spellbook = None

    with pytest.raises(RuntimeError, match="Spellbook is not available"):
        conduit_dynamic_normal._require_link_transaction_for_contract(
            conduit=None,
            conduit_id="peer-1",
            allow_all_links=False,
        )

    conduit_dynamic_normal._logger.error.assert_called_once()


def test_require_link_transaction_for_contract_raises_when_no_active_request(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_require_link_transaction_for_contract should fail when there is no active request."""
    conduit_dynamic_normal._logger = MagicMock()
    conduit_dynamic_normal._spellbook._active_change_request = None

    with pytest.raises(RuntimeError, match="requires an active link transaction"):
        conduit_dynamic_normal._require_link_transaction_for_contract(
            conduit=None,
            conduit_id="peer-1",
            allow_all_links=False,
        )

    conduit_dynamic_normal._logger.error.assert_called_once()


def test_require_link_transaction_for_contract_raises_when_wrong_request_type(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_require_link_transaction_for_contract should fail when the active request is not LINK."""
    conduit_dynamic_normal._logger = MagicMock()
    request = MagicMock()
    request.request_type = ChangeTransactionType.BIND
    request.conduit_ids = [conduit_dynamic_normal._id, "peer-1"]
    conduit_dynamic_normal._spellbook._active_change_request = request

    with pytest.raises(RuntimeError, match="not a link transaction"):
        conduit_dynamic_normal._require_link_transaction_for_contract(
            conduit=None,
            conduit_id="peer-1",
            allow_all_links=False,
        )

    conduit_dynamic_normal._logger.error.assert_called_once()


def test_require_link_transaction_for_contract_raises_when_required_ids_missing(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_require_link_transaction_for_contract should fail when required conduit ids are missing."""
    conduit_dynamic_normal._logger = MagicMock()
    request = MagicMock()
    request.request_type = ChangeTransactionType.LINK
    request.conduit_ids = [conduit_dynamic_normal._id]
    conduit_dynamic_normal._spellbook._active_change_request = request

    with pytest.raises(RuntimeError, match="missing conduit ids"):
        conduit_dynamic_normal._require_link_transaction_for_contract(
            conduit=None,
            conduit_id="peer-1",
            allow_all_links=False,
        )

    conduit_dynamic_normal._logger.error.assert_called_once()


def test_require_link_transaction_for_contract_raises_when_local_id_missing(
    conduit_dynamic_normal: Conduit,
) -> None:
    """_require_link_transaction_for_contract should fail when the active request omits the local conduit id."""
    conduit_dynamic_normal._logger = MagicMock()
    request = MagicMock()
    request.request_type = ChangeTransactionType.LINK
    request.conduit_ids = ["peer-1"]
    conduit_dynamic_normal._spellbook._active_change_request = request

    with pytest.raises(RuntimeError, match="missing conduit ids"):
        conduit_dynamic_normal._require_link_transaction_for_contract(
            conduit=None,
            conduit_id="peer-1",
            allow_all_links=False,
        )

    conduit_dynamic_normal._logger.error.assert_called_once()


def test_get_links_raises_when_not_dynamic(
    conduit_normal: Conduit,
) -> None:
    """
    Verify get_links is blocked in non-dynamic environments.

    Contract:
        - Dynamic mode is required to fetch peer links.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If get_links does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.get_links()


def test_get_links_delegates_when_dynamic(conduit_dynamic_normal: Conduit) -> None:
    """
    Verify get_links delegates to the conduit ward when dynamic.

    Contract:
        - _get_links is invoked on the conduit ward.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._get_links.return_value = ["peer"]

    result = conduit_dynamic_normal.get_links()

    conduit_dynamic_normal._conduit_ward._get_links.assert_called_once_with()
    assert result == ["peer"]


def test_get_lesser_conduit_delegates(conduit_normal: Conduit) -> None:
    """
    Verify get_lesser_conduit delegates to the conduit ward.

    Contract:
        - _get_lesser_conduit is called with the provided id.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._conduit_ward = MagicMock()
    sentinel = MagicMock()
    conduit_normal._conduit_ward._get_lesser_conduit.return_value = sentinel

    result = conduit_normal.get_lesser_conduit("child")

    conduit_normal._conduit_ward._get_lesser_conduit.assert_called_once_with("child")
    assert result is sentinel


def test_get_initiated_conduit_delegates(conduit_normal: Conduit) -> None:
    """
    Verify get_initiated_conduit delegates to the conduit ward.

    Contract:
        - _get_initiated_conduit is called with the provided id.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._conduit_ward = MagicMock()
    sentinel = MagicMock()
    conduit_normal._conduit_ward._get_initiated_conduit.return_value = sentinel

    result = conduit_normal.get_initiated_conduit("peer")

    conduit_normal._conduit_ward._get_initiated_conduit.assert_called_once_with("peer")
    assert result is sentinel


def test_get_provider_conduit_delegates(conduit_normal: Conduit) -> None:
    """
    Verify get_provider_conduit delegates to the conduit ward.

    Contract:
        - _get_provider_conduit is called with the provided id.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._conduit_ward = MagicMock()
    sentinel = MagicMock()
    conduit_normal._conduit_ward._get_provider_conduit.return_value = sentinel

    result = conduit_normal.get_provider_conduit("peer")

    conduit_normal._conduit_ward._get_provider_conduit.assert_called_once_with("peer")
    assert result is sentinel


def test_get_initiated_conduits_delegates(conduit_normal: Conduit) -> None:
    """
    Verify get_initiated_conduits delegates to the conduit ward.

    Contract:
        - _get_initiated_conduits is called without arguments.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._conduit_ward = MagicMock()
    conduit_normal._conduit_ward._get_initiated_conduits.return_value = ["peer"]

    result = conduit_normal.get_initiated_conduits()

    conduit_normal._conduit_ward._get_initiated_conduits.assert_called_once_with()
    assert result == ["peer"]


def test_get_provider_conduits_delegates(conduit_normal: Conduit) -> None:
    """
    Verify get_provider_conduits delegates to the conduit ward.

    Contract:
        - _get_provider_conduits is called without arguments.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._conduit_ward = MagicMock()
    conduit_normal._conduit_ward._get_provider_conduits.return_value = ["peer"]

    result = conduit_normal.get_provider_conduits()

    conduit_normal._conduit_ward._get_provider_conduits.assert_called_once_with()
    assert result == ["peer"]


def test_cleanup_lesser_conduits_delegates(conduit_normal: Conduit) -> None:
    """
    Verify cleanup_lesser_conduits delegates to the conduit ward.

    Contract:
        - cleanup_all_lesser_conduits is invoked without arguments.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._conduit_ward = MagicMock()

    conduit_normal.cleanup_lesser_conduits()

    conduit_normal._conduit_ward.cleanup_all_lesser_conduits.assert_called_once_with()
