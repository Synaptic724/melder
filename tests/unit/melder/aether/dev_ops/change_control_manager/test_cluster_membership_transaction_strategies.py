from typing import Dict, Iterable, Optional, Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_join_transaction_strategy import (
    ClusterJoinTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_leave_transaction_strategy import (
    ClusterLeaveTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy_builder import (
    TransactionStrategyBuilder,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ClaimMode,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------
def _make_cluster_registry(
        conduit_to_spellbook: Iterable[Tuple[str, Optional[str]]],
) -> Tuple[ChangeControlTransactionManager, DevopsInformationRegistry, DevopsIdentity]:
    """
    Build a transaction manager + registry + cluster identity for membership tests.

    Purpose:
        Construct the minimal real DevOps wiring a cluster-membership strategy reads:
        a transaction manager (scope-key helpers), a registry populated with the
        cluster identity plus each involved conduit and (optionally) its owning
        spellbook, and the spellbook->conduit ownership links.
    Args:
        conduit_to_spellbook:
            Iterable of `(conduit_id, spellbook_id)` pairs. When `spellbook_id` is
            None the conduit is registered with no owning spellbook (to exercise the
            unresolved-spellbook branch).
    Returns:
        Tuple[ChangeControlTransactionManager, DevopsInformationRegistry, DevopsIdentity]:
            The manager, the populated registry, and the cluster identity to pass as
            the transaction `identity`.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    cluster_identity = DevopsIdentity(
        owner_kind="conduit_cluster",
        owner_id="cluster-1",
        aetheric_frame_name="frame-1",
        metadata={"cluster_name": "alpha"},
        available_transactions=("cluster_join", "cluster_leave", "cluster_link"),
    )
    registry.register_identity(cluster_identity)
    for conduit_id, spellbook_id in conduit_to_spellbook:
        conduit_identity = DevopsIdentity(
            owner_kind="conduit",
            owner_id=conduit_id,
            aetheric_frame_name="frame-1",
            metadata={"spellbook_id": spellbook_id} if spellbook_id else {},
            available_transactions=("link",),
        )
        registry.register_identity(conduit_identity)
        if spellbook_id is None:
            continue
        spellbook_identity = DevopsIdentity(
            owner_kind="spellbook",
            owner_id=spellbook_id,
            aetheric_frame_name="frame-1",
            metadata={"conduit_id": conduit_id},
            available_transactions=("bind",),
        )
        registry.register_identity(spellbook_identity)
        registry.register_spellbook_conduit_ownership(
            spellbook_id=spellbook_id,
            conduit_id=conduit_id,
        )
    return transaction_manager, registry, cluster_identity


def _two_member_registry() -> Tuple[
    ChangeControlTransactionManager, DevopsInformationRegistry, DevopsIdentity
]:
    """Return a registry with conduit-1/spellbook-1 and conduit-2/spellbook-2 registered."""
    return _make_cluster_registry(
        (("conduit-1", "spellbook-1"), ("conduit-2", "spellbook-2")),
    )


# ---------------------------------------------------------------------------
# Builder + enum cross-cutting
# ---------------------------------------------------------------------------
def test_change_transaction_type_has_cluster_membership_values() -> None:
    """
    Purpose:
        Verify the enum exposes the cluster-membership transaction values.
    Contract:
        - CLUSTER_JOIN/CLUSTER_LEAVE equal their stable string payloads.
    Returns:
        None.
    Raises:
        AssertionError: If the enum values drift.
    """
    assert ChangeTransactionType.CLUSTER_JOIN == "cluster_join"
    assert ChangeTransactionType.CLUSTER_LEAVE == "cluster_leave"


def test_builder_resolves_cluster_join_from_enum_and_string() -> None:
    """
    Purpose:
        Verify the builder maps cluster_join (enum + string) to its strategy.
    Contract:
        - Both ChangeTransactionType.CLUSTER_JOIN and "cluster_join" resolve to
          ClusterJoinTransactionStrategy.
    Returns:
        None.
    Raises:
        AssertionError: If resolution diverges.
    """
    transaction_manager, registry, _identity = _two_member_registry()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    assert builder.resolve(ChangeTransactionType.CLUSTER_JOIN) is ClusterJoinTransactionStrategy
    assert builder.resolve("cluster_join") is ClusterJoinTransactionStrategy


def test_builder_resolves_cluster_leave_from_enum_and_string() -> None:
    """
    Purpose:
        Verify the builder maps cluster_leave (enum + string) to its strategy.
    Contract:
        - Both ChangeTransactionType.CLUSTER_LEAVE and "cluster_leave" resolve to
          ClusterLeaveTransactionStrategy.
    Returns:
        None.
    Raises:
        AssertionError: If resolution diverges.
    """
    transaction_manager, registry, _identity = _two_member_registry()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    assert builder.resolve(ChangeTransactionType.CLUSTER_LEAVE) is ClusterLeaveTransactionStrategy
    assert builder.resolve("cluster_leave") is ClusterLeaveTransactionStrategy


def test_cluster_membership_strategies_use_distinct_mode_markers() -> None:
    """
    Purpose:
        Verify join and leave stamp distinct membership-mode markers.
    Contract:
        - cluster_join -> "cluster_join"; cluster_leave -> "cluster_leave".
    Returns:
        None.
    Raises:
        AssertionError: If the markers are missing or identical.
    """
    transaction_manager, registry, identity = _two_member_registry()
    metadata = {"conduit_ids": ("conduit-1", "conduit-2")}

    join_plan = ClusterJoinTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata=dict(metadata),
    )
    leave_plan = ClusterLeaveTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata=dict(metadata),
    )

    assert join_plan["metadata"]["cluster_membership_mode"] == "cluster_join"
    assert leave_plan["metadata"]["cluster_membership_mode"] == "cluster_leave"


# ---------------------------------------------------------------------------
# CLUSTER_JOIN strategy
# ---------------------------------------------------------------------------
def test_cluster_join_strategy_builds_conduit_ward_and_spellbook_scopes() -> None:
    """
    Purpose:
        Verify cluster-join planning seals every involved conduit, its ward, and its
        owning spellbook.
    Contract:
        - Each involved conduit contributes a conduit scope and a ward scope.
        - Each resolvable owning spellbook contributes a spellbook scope.
        - No cluster scope is sealed (join seals the conduits, not a cluster lock).
    Returns:
        None.
    Raises:
        AssertionError: If a required scope is missing or a cluster scope leaks in.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterJoinTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-1", "conduit-2")},
    )

    scope_keys = set(plan["scope_keys"])
    assert "scope:conduit:conduit-1" in scope_keys
    assert "scope:conduit:conduit-2" in scope_keys
    assert "scope:conduit_ward:conduit-1" in scope_keys
    assert "scope:conduit_ward:conduit-2" in scope_keys
    assert "scope:spellbook:spellbook-1" in scope_keys
    assert "scope:spellbook:spellbook-2" in scope_keys
    assert "scope:cluster:cluster-1" not in scope_keys


def test_cluster_join_strategy_claims_spellbooks_intent_conduits_exclusive() -> None:
    """
    Purpose:
        Verify cluster-join claim modes match the link pattern.
    Contract:
        - Owning spellbooks are claimed INTENT.
        - Conduits and wards are left to default EXCLUSIVE (absent from scope_claims).
    Returns:
        None.
    Raises:
        AssertionError: If a claim mode is wrong.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterJoinTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-1", "conduit-2")},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.INTENT.value
    assert "scope:conduit:conduit-1" not in scope_claims
    assert "scope:conduit_ward:conduit-1" not in scope_claims


def test_cluster_join_strategy_grants_membership_and_contract_capabilities() -> None:
    """
    Purpose:
        Verify cluster-join declares its capability set.
    Contract:
        - granted and required capabilities are
          (cluster_join, cluster_link, contract_mutation).
    Returns:
        None.
    Raises:
        AssertionError: If the capability tuples drift.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterJoinTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-1",)},
    )

    assert plan["granted_capabilities"] == ("cluster_join", "cluster_link", "contract_mutation")
    assert plan["required_capabilities"] == ("cluster_join", "cluster_link", "contract_mutation")


def test_cluster_join_strategy_passes_through_sorted_conduit_ids() -> None:
    """
    Purpose:
        Verify the involved conduit ids surface as a sorted tuple on the plan.
    Contract:
        - plan["conduit_ids"] is the sorted set of involved conduits.
    Returns:
        None.
    Raises:
        AssertionError: If ordering or membership is wrong.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterJoinTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-2", "conduit-1")},
    )

    assert plan["conduit_ids"] == ("conduit-1", "conduit-2")


def test_cluster_join_strategy_requires_at_least_one_conduit_id() -> None:
    """
    Purpose:
        Verify cluster-join rejects an empty involved-conduit set.
    Contract:
        - An empty conduit_ids metadata raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If empty membership is accepted.
    """
    transaction_manager, registry, identity = _two_member_registry()

    with pytest.raises(RuntimeError, match="at least one conduit id"):
        ClusterJoinTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=identity,
            metadata={"conduit_ids": ()},
        )


def test_cluster_join_involved_conduit_ids_strips_and_dedups() -> None:
    """
    Purpose:
        Verify the involved-conduit collector normalizes its input.
    Contract:
        - Whitespace is stripped, blanks dropped, and duplicates collapsed.
    Returns:
        None.
    Raises:
        AssertionError: If normalization is wrong.
    """
    result = ClusterJoinTransactionStrategy._involved_conduit_ids(
        {"conduit_ids": ("conduit-1", " conduit-1 ", "conduit-2", "", "   ")},
    )
    assert result == {"conduit-1", "conduit-2"}


def test_cluster_join_strategy_tolerates_unresolved_spellbook() -> None:
    """
    Purpose:
        Verify a conduit with no owning spellbook still seals its conduit + ward.
    Contract:
        - When the registry has no spellbook for a conduit, the conduit and ward
          scopes are still sealed and no spellbook scope/claim is added.
    Returns:
        None.
    Raises:
        AssertionError: If the unresolved-spellbook branch widens or narrows wrongly.
    """
    transaction_manager, registry, identity = _make_cluster_registry(
        (("conduit-x", None),),
    )

    plan = ClusterJoinTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-x",)},
    )

    scope_keys = set(plan["scope_keys"])
    assert "scope:conduit:conduit-x" in scope_keys
    assert "scope:conduit_ward:conduit-x" in scope_keys
    assert not any(key.startswith("scope:spellbook:") for key in scope_keys)
    assert plan["scope_claims"] == ()


def test_cluster_join_strategy_hooks_are_no_ops() -> None:
    """
    Purpose:
        Verify cluster-join coordination hooks do no DevOps work.
    Contract:
        - on_start and on_end return None and do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If a hook returns non-None or raises.
    """
    _transaction_manager, registry, identity = _two_member_registry()

    assert ClusterJoinTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    ) is None
    assert ClusterJoinTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    ) is None


def test_cluster_join_seals_a_single_involved_conduit() -> None:
    """
    Purpose:
        Verify a single-conduit join is admissible and seals that conduit.
    Contract:
        - One involved conduit yields exactly its conduit + ward + spellbook scope.
    Returns:
        None.
    Raises:
        AssertionError: If a single-member join is rejected or mis-sealed.
    """
    transaction_manager, registry, identity = _make_cluster_registry(
        (("conduit-1", "spellbook-1"),),
    )

    plan = ClusterJoinTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-1",)},
    )

    assert plan["conduit_ids"] == ("conduit-1",)
    scope_keys = set(plan["scope_keys"])
    assert "scope:conduit:conduit-1" in scope_keys
    assert "scope:spellbook:spellbook-1" in scope_keys


# ---------------------------------------------------------------------------
# CLUSTER_LEAVE strategy
# ---------------------------------------------------------------------------
def test_cluster_leave_strategy_builds_conduit_ward_and_spellbook_scopes() -> None:
    """
    Purpose:
        Verify cluster-leave planning seals every involved conduit, its ward, and its
        owning spellbook.
    Contract:
        - Each involved conduit contributes a conduit scope and a ward scope.
        - Each resolvable owning spellbook contributes a spellbook scope.
        - No cluster scope is sealed.
    Returns:
        None.
    Raises:
        AssertionError: If a required scope is missing or a cluster scope leaks in.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterLeaveTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-1", "conduit-2")},
    )

    scope_keys = set(plan["scope_keys"])
    assert "scope:conduit:conduit-1" in scope_keys
    assert "scope:conduit:conduit-2" in scope_keys
    assert "scope:conduit_ward:conduit-1" in scope_keys
    assert "scope:conduit_ward:conduit-2" in scope_keys
    assert "scope:spellbook:spellbook-1" in scope_keys
    assert "scope:spellbook:spellbook-2" in scope_keys
    assert "scope:cluster:cluster-1" not in scope_keys


def test_cluster_leave_strategy_claims_spellbooks_intent_conduits_exclusive() -> None:
    """
    Purpose:
        Verify cluster-leave claim modes match the link pattern.
    Contract:
        - Owning spellbooks are claimed INTENT.
        - Conduits and wards are left to default EXCLUSIVE (absent from scope_claims).
    Returns:
        None.
    Raises:
        AssertionError: If a claim mode is wrong.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterLeaveTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-1", "conduit-2")},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.INTENT.value
    assert "scope:conduit:conduit-1" not in scope_claims
    assert "scope:conduit_ward:conduit-1" not in scope_claims


def test_cluster_leave_strategy_grants_membership_and_contract_capabilities() -> None:
    """
    Purpose:
        Verify cluster-leave declares its capability set.
    Contract:
        - granted and required capabilities are
          (cluster_leave, cluster_link, contract_mutation).
    Returns:
        None.
    Raises:
        AssertionError: If the capability tuples drift.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterLeaveTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-1",)},
    )

    assert plan["granted_capabilities"] == ("cluster_leave", "cluster_link", "contract_mutation")
    assert plan["required_capabilities"] == ("cluster_leave", "cluster_link", "contract_mutation")


def test_cluster_leave_strategy_passes_through_sorted_conduit_ids() -> None:
    """
    Purpose:
        Verify the involved conduit ids surface as a sorted tuple on the plan.
    Contract:
        - plan["conduit_ids"] is the sorted set of involved conduits.
    Returns:
        None.
    Raises:
        AssertionError: If ordering or membership is wrong.
    """
    transaction_manager, registry, identity = _two_member_registry()

    plan = ClusterLeaveTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"conduit_ids": ("conduit-2", "conduit-1")},
    )

    assert plan["conduit_ids"] == ("conduit-1", "conduit-2")


def test_cluster_leave_strategy_requires_at_least_one_conduit_id() -> None:
    """
    Purpose:
        Verify cluster-leave rejects an empty involved-conduit set.
    Contract:
        - An empty conduit_ids metadata raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If empty membership is accepted.
    """
    transaction_manager, registry, identity = _two_member_registry()

    with pytest.raises(RuntimeError, match="at least one conduit id"):
        ClusterLeaveTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=identity,
            metadata={"conduit_ids": ()},
        )


def test_cluster_leave_involved_conduit_ids_strips_and_dedups() -> None:
    """
    Purpose:
        Verify the involved-conduit collector normalizes its input.
    Contract:
        - Whitespace is stripped, blanks dropped, and duplicates collapsed.
    Returns:
        None.
    Raises:
        AssertionError: If normalization is wrong.
    """
    result = ClusterLeaveTransactionStrategy._involved_conduit_ids(
        {"conduit_ids": ("conduit-9", "conduit-9", " conduit-7 ", "")},
    )
    assert result == {"conduit-9", "conduit-7"}


def test_cluster_leave_strategy_hooks_are_no_ops() -> None:
    """
    Purpose:
        Verify cluster-leave coordination hooks do no DevOps work.
    Contract:
        - on_start and on_end return None and do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If a hook returns non-None or raises.
    """
    _transaction_manager, registry, identity = _two_member_registry()

    assert ClusterLeaveTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    ) is None
    assert ClusterLeaveTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    ) is None
