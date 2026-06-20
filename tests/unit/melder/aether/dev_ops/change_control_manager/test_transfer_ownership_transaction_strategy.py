from typing import Any, Dict, Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transfer_ownership_transaction_strategy import (
    TransferOwnershipTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _manager_registry_source() -> Tuple[
    ChangeControlTransactionManager, DevopsInformationRegistry, DevopsIdentity
]:
    """Build a transaction manager + registry + a registered conduit submitter identity."""
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    source_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-1"},
        available_transactions=("transfer_ownership",),
    )
    registry.register_identity(source_identity)
    return transaction_manager, registry, source_identity


def _footprint_metadata(**overrides: Any) -> Dict[str, object]:
    """
    Build the conduit-built footprint metadata the envelope strategy plans from.

    The defaults model a same-frame transfer of one spell from conduit-1 (spellbook-1)
    to conduit-2 (spellbook-2) with no extra cluster/borrower participants. Callers
    override individual keys to exercise specific scope branches.
    """
    base: Dict[str, object] = {
        "target_conduit_id": "conduit-2",
        "source_conduit_id": "conduit-1",
        "source_spellbook_id": "spellbook-1",
        "spell_id": "spell-1",
        "binding_keys": (("frame", "__default__"),),
        "participant_conduit_ids": ("conduit-1", "conduit-2"),
        "affected_cluster_ids": (),
        "affected_identity_keys": (
            ("conduit", "conduit-1"),
            ("conduit", "conduit-2"),
            ("conduit_ward", "conduit-1"),
            ("conduit_ward", "conduit-2"),
            ("spellbook", "spellbook-1"),
            ("spellbook", "spellbook-2"),
        ),
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------
def test_transfer_strategy_requires_conduit_identity() -> None:
    """
    Purpose:
        Verify only a conduit identity may originate an ownership transfer.
    Contract:
        - A non-conduit submitter raises RuntimeError before any footprint read.
    Returns:
        None.
    Raises:
        AssertionError: If a non-conduit identity is accepted.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    spellbook_identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=("transfer_ownership",),
    )
    registry.register_identity(spellbook_identity)

    with pytest.raises(RuntimeError, match="must originate from a conduit identity"):
        TransferOwnershipTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=spellbook_identity,
            metadata=_footprint_metadata(),
        )


def test_transfer_strategy_requires_participant_footprint() -> None:
    """
    Purpose:
        Verify the strategy fails fast when the conduit-built footprint is absent
        (it no longer discovers participants itself).
    Contract:
        - Missing participant_conduit_ids raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If a footprint-less transfer is accepted.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    with pytest.raises(RuntimeError, match="participant_conduit_ids"):
        TransferOwnershipTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=source_identity,
            metadata={"target_conduit_id": "conduit-2"},
        )


# ---------------------------------------------------------------------------
# Scope assembly from the footprint
# ---------------------------------------------------------------------------
def test_transfer_strategy_builds_conduit_and_ward_scopes() -> None:
    """
    Purpose:
        Verify every participant conduit contributes a conduit + ward scope.
    Contract:
        - Each participant id yields scope:conduit:<id> and scope:conduit_ward:<id>.
    Returns:
        None.
    Raises:
        AssertionError: If a participant conduit/ward scope is missing.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(
            participant_conduit_ids=("conduit-1", "conduit-2", "borrower-9"),
        ),
    )

    scope_keys = set(plan["scope_keys"])
    assert "scope:conduit:conduit-1" in scope_keys
    assert "scope:conduit:conduit-2" in scope_keys
    assert "scope:conduit:borrower-9" in scope_keys
    assert "scope:conduit_ward:conduit-1" in scope_keys
    assert "scope:conduit_ward:borrower-9" in scope_keys


def test_transfer_strategy_builds_spellbook_scopes_from_identity_keys() -> None:
    """
    Purpose:
        Verify spellbook scopes come from the affected identity keys.
    Contract:
        - Each ("spellbook", id) identity key yields scope:spellbook:<id>.
    Returns:
        None.
    Raises:
        AssertionError: If a spellbook scope is missing.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(),
    )

    scope_keys = set(plan["scope_keys"])
    assert "scope:spellbook:spellbook-1" in scope_keys
    assert "scope:spellbook:spellbook-2" in scope_keys


def test_transfer_strategy_builds_cluster_scopes() -> None:
    """
    Purpose:
        Verify affected clusters become cluster scopes.
    Contract:
        - Each affected_cluster_id yields scope:cluster:<id>.
    Returns:
        None.
    Raises:
        AssertionError: If a cluster scope is missing.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(affected_cluster_ids=("cluster-1", "cluster-2")),
    )

    scope_keys = set(plan["scope_keys"])
    assert "scope:cluster:cluster-1" in scope_keys
    assert "scope:cluster:cluster-2" in scope_keys


def test_transfer_strategy_builds_binding_scope_from_binding_keys() -> None:
    """
    Purpose:
        Verify the transferred spell's binding key becomes a binding scope.
    Contract:
        - Each binding key yields the manager's binding scope key.
    Returns:
        None.
    Raises:
        AssertionError: If the binding scope is missing.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(),
    )

    binding_scope = transaction_manager.make_scope_key_binding("frame", "__default__")
    assert binding_scope in set(plan["scope_keys"])


def test_transfer_strategy_adds_transaction_owner_scopes_for_affected_identities() -> None:
    """
    Purpose:
        Verify each resolvable affected identity contributes its transaction-owner scopes.
    Contract:
        - The source conduit (registered, supports transfer_ownership) yields its
          transaction-owner scope.
    Returns:
        None.
    Raises:
        AssertionError: If the transaction-owner scope is missing.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(),
    )

    expected = transaction_manager.make_scope_key_transaction_owner(
        owner_kind="conduit",
        owner_id="conduit-1",
        transaction_name="transfer_ownership",
    )
    assert expected in set(plan["scope_keys"])


# ---------------------------------------------------------------------------
# Plan shape
# ---------------------------------------------------------------------------
def test_transfer_strategy_plan_spellbook_id_is_source_spellbook_id() -> None:
    """
    Purpose:
        Verify the plan's spellbook_id is the source conduit's spellbook id.
    Contract:
        - plan["spellbook_id"] == metadata["source_spellbook_id"].
    Returns:
        None.
    Raises:
        AssertionError: If the spellbook_id is wrong.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(),
    )

    assert plan["spellbook_id"] == "spellbook-1"


def test_transfer_strategy_grants_transfer_capabilities() -> None:
    """
    Purpose:
        Verify the transfer capability set.
    Contract:
        - granted and required capabilities are
          (transfer_ownership, contract_mutation, cluster_link).
    Returns:
        None.
    Raises:
        AssertionError: If the capability tuples drift.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(),
    )

    expected = ("transfer_ownership", "contract_mutation", "cluster_link")
    assert plan["granted_capabilities"] == expected
    assert plan["required_capabilities"] == expected


def test_transfer_strategy_sorts_conduit_ids_and_stamps_transaction_identity() -> None:
    """
    Purpose:
        Verify the plan surfaces the sorted participant set and stamps the submitter
        identity into the normalized metadata.
    Contract:
        - plan["conduit_ids"] is the sorted participant set.
        - plan["metadata"]["transaction_identity"] is present.
    Returns:
        None.
    Raises:
        AssertionError: If ordering or identity stamping is wrong.
    """
    transaction_manager, registry, source_identity = _manager_registry_source()

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata=_footprint_metadata(
            participant_conduit_ids=("conduit-2", "conduit-1"),
        ),
    )

    assert plan["conduit_ids"] == ("conduit-1", "conduit-2")
    assert "transaction_identity" in plan["metadata"]
    assert plan["initiator_conduit_id"] == "conduit-1"
