from typing import Any, Dict, Iterable, Optional, Set, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.bind_transaction_strategy import (
    BindTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.conjure_transaction_strategy import (
    ConjureTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_link_transaction_strategy import (
    ClusterLinkTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.link_transaction_strategy import (
    LinkTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy import (
    TransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy_builder import (
    TransactionStrategyBuilder,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transfer_ownership_transaction_strategy import (
    TransferOwnershipTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unlink_transaction_strategy import (
    UnlinkTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.notch_transaction_strategy import (
    NotchTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_to_index_transaction_strategy import (
    AddToIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_from_index_transaction_strategy import (
    RemoveFromIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.elect_conduit_cluster_leader_transaction_strategy import (
    ElectConduitClusterLeaderTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unelect_conduit_cluster_leader_transaction_strategy import (
    UnelectConduitClusterLeaderTransactionStrategy,
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


class _DummyStrategy(TransactionStrategy):
    """
    Minimal strategy double for builder delegation tests.
    """

    @staticmethod
    def build_start_plan(
            *,
            transaction_manager: ChangeControlTransactionManager,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Return a stable marker payload for builder delegation tests.
        """
        del transaction_manager
        del devops_information_registry
        return {
            "owner_id": identity.owner_id,
            "metadata": dict(metadata),
        }

    @staticmethod
    def on_start(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        No-op start hook for builder tests.
        """
        del devops_information_registry
        metadata["started"] = identity.owner_id

    @staticmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        No-op end hook for builder tests.
        """
        del devops_information_registry
        metadata["ended"] = identity.owner_id


def _make_registry_and_identity(
        *,
        owner_kind: str = "spellbook",
        owner_id: str = "spellbook-1",
        metadata: Optional[Dict[str, Any]] = None,
        available_transactions: Optional[Tuple[str, ...]] = None,
) -> Tuple[ChangeControlTransactionManager, DevopsInformationRegistry, DevopsIdentity]:
    """
    Build a transaction manager, registry, and attached identity for tests.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    identity = DevopsIdentity(
        owner_kind=owner_kind,
        owner_id=owner_id,
        aetheric_frame_name="frame-1",
        metadata=metadata,
        available_transactions=available_transactions,
    )
    registry.register_identity(identity)
    return transaction_manager, registry, identity


def test_transaction_strategy_builder_resolves_enum_and_string_transaction_names() -> None:
    """
    Purpose:
        Verify the builder resolves strategies from both enum and string inputs.
    Contract:
        - Built-in registrations accept both enum members and normalized strings.
    Returns:
        None.
    Raises:
        AssertionError: If enum and string resolution diverge.
    """
    transaction_manager, registry, _identity = _make_registry_and_identity()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    assert builder.resolve(ChangeTransactionType.BIND) is BindTransactionStrategy
    assert builder.resolve(ChangeTransactionType.CONJURE) is ConjureTransactionStrategy
    assert builder.resolve("conjure") is ConjureTransactionStrategy
    assert builder.resolve("link") is LinkTransactionStrategy
    assert builder.resolve("cluster_link") is ClusterLinkTransactionStrategy
    assert builder.resolve("transfer_ownership") is TransferOwnershipTransactionStrategy
    assert builder.resolve("unlink") is UnlinkTransactionStrategy
    assert builder.resolve("notch") is NotchTransactionStrategy
    assert builder.resolve("add_to_index") is AddToIndexTransactionStrategy
    assert builder.resolve("remove_from_index") is RemoveFromIndexTransactionStrategy
    assert (
        builder.resolve("elect_conduit_cluster_leader")
        is ElectConduitClusterLeaderTransactionStrategy
    )
    assert (
        builder.resolve("unelect_conduit_cluster_leader")
        is UnelectConduitClusterLeaderTransactionStrategy
    )


def test_transaction_strategy_builder_register_strategy_replaces_existing_mapping() -> None:
    """
    Purpose:
        Verify explicit registration replaces the current strategy mapping.
    Contract:
        - register_strategy is last-write-wins for the normalized name.
    Returns:
        None.
    Raises:
        AssertionError: If replacement does not take effect.
    """
    transaction_manager, registry, identity = _make_registry_and_identity()
    builder = TransactionStrategyBuilder(transaction_manager, registry)
    builder.register_strategy("bind", _DummyStrategy)

    resolved = builder.resolve("bind")
    plan = builder.build_start_plan(
        transaction_type="bind",
        identity=identity,
        metadata={"origin_surface": "test"},
    )

    assert resolved is _DummyStrategy
    assert plan["owner_id"] == "spellbook-1"


def test_transaction_strategy_builder_rejects_unknown_transaction_name() -> None:
    """
    Purpose:
        Verify unknown transaction kinds fail clearly.
    Contract:
        - resolve raises NotImplementedError for unregistered names.
    Returns:
        None.
    Raises:
        AssertionError: If unknown transaction names are accepted.
    """
    transaction_manager, registry, _identity = _make_registry_and_identity()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    with pytest.raises(NotImplementedError, match="not implemented"):
        builder.resolve("unknown")


@pytest.mark.parametrize(
    ("transaction_type", "expected_exception", "expected_message"),
    [
        (None, TypeError, "transaction_type must be a ChangeTransactionType or string."),
        (" ", ValueError, "transaction_type must not be empty."),
    ],
)
def test_transaction_strategy_builder_register_strategy_validates_transaction_name(
        transaction_type: Any,
        expected_exception: type[BaseException],
        expected_message: str,
) -> None:
    """
    Purpose:
        Verify builder registration validates transaction-type input.
    Contract:
        - Invalid transaction names raise immediately.
    Returns:
        None.
    Raises:
        AssertionError: If invalid names are accepted.
    """
    transaction_manager, registry, _identity = _make_registry_and_identity()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    with pytest.raises(expected_exception, match=expected_message):
        builder.register_strategy(transaction_type, _DummyStrategy)


def test_bind_transaction_strategy_builds_pre_conjure_plan() -> None:
    """
    Purpose:
        Verify pre-conjure bind planning stays spellbook-local.
    Contract:
        - No conduit ids are claimed pre-conjure.
        - Spellbook and transaction-owner scopes are included.
    Returns:
        None.
    Raises:
        AssertionError: If pre-conjure planning widens incorrectly.
    """
    transaction_manager, registry, identity = _make_registry_and_identity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        metadata={"conjured": False, "conduit_id": None},
        available_transactions=("bind", "scan"),
    )

    plan = BindTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    )

    assert plan["initiator_conduit_id"] == "spellbook:spellbook-1"
    assert plan["conduit_ids"] == ()
    assert "scope:spellbook:spellbook-1" in plan["scope_keys"]
    assert (
        "scope:transaction:spellbook:spellbook-1:bind"
        in plan["scope_keys"]
    )
    assert plan["metadata"]["bind_mode"] == "pre_conjure"


def test_bind_transaction_strategy_builds_post_conjure_plan_with_cluster_scope() -> None:
    """
    Purpose:
        Verify post-conjure bind planning includes conduit, ward, and cluster scope.
    Contract:
        - Paired root conduit id is resolved from the registry.
        - Cluster membership contributes cluster scope and affected identities.
    Returns:
        None.
    Raises:
        AssertionError: If post-conjure planning omits required scope.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    spellbook_identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={"conjured": True, "conduit_id": "conduit-1"},
        available_transactions=("bind",),
    )
    conduit_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-1"},
        available_transactions=("link", "cluster_link"),
    )
    cluster_identity = DevopsIdentity(
        owner_kind="conduit_cluster",
        owner_id="cluster-1",
        aetheric_frame_name="frame-1",
        metadata={"cluster_name": "alpha"},
        available_transactions=("cluster_link",),
    )
    registry.register_identity(spellbook_identity)
    registry.register_identity(conduit_identity)
    registry.register_identity(cluster_identity)
    registry.register_cluster_membership(cluster_id="cluster-1", conduit_id="conduit-1")

    plan = BindTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=spellbook_identity,
        metadata={"conduit_id": "conduit-1"},
    )

    assert plan["initiator_conduit_id"] == "conduit-1"
    assert plan["conduit_ids"] == ("conduit-1",)
    assert "scope:conduit:conduit-1" in plan["scope_keys"]
    assert "scope:conduit_ward:conduit-1" in plan["scope_keys"]
    assert "scope:cluster:cluster-1" in plan["scope_keys"]
    assert plan["metadata"]["bind_mode"] == "post_conjure"
    assert plan["metadata"]["affected_cluster_ids"] == ("cluster-1",)
    # Claim modes: spellbook + clusters are INTENT (parallel member binds),
    # conduit/ward stay EXCLUSIVE (absent from scope_claims).
    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:cluster:cluster-1"] == ClaimMode.INTENT.value
    assert "scope:conduit:conduit-1" not in scope_claims
    assert "scope:conduit_ward:conduit-1" not in scope_claims


def test_bind_transaction_strategy_hooks_do_not_touch_spellbook() -> None:
    """
    Purpose:
        Verify the bind strategy's lifecycle hooks are DevOps-only no-ops. The
        Spellbook-local bind state is prepared/cleared by the Spellbook itself
        (begin_transaction / end_transaction), NOT by this DevOps strategy, so
        the strategy must never reach into the live Spellbook object.
    Contract:
        - on_start does not resolve or mutate the Spellbook object.
        - on_end does not resolve or mutate the Spellbook object.
    Returns:
        None.
    Raises:
        AssertionError: If a strategy hook reaches into the Spellbook runtime.
    """
    _transaction_manager, registry, identity = _make_registry_and_identity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        metadata={"conjured": False},
        available_transactions=("bind",),
    )
    spellbook = MagicMock()
    registry.refresh_identity(identity, object_ref=spellbook)

    BindTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    )
    BindTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    )

    spellbook._prepare_bind_transaction_state.assert_not_called()
    spellbook._clear_bind_transaction_state.assert_not_called()


def test_link_transaction_strategy_requires_local_and_peer_participants() -> None:
    """
    Purpose:
        Verify link planning rejects one-sided participant sets.
    Contract:
        - At least the local conduit and one peer conduit are required.
    Returns:
        None.
    Raises:
        AssertionError: If incomplete participant sets are accepted.
    """
    transaction_manager, registry, identity = _make_registry_and_identity(
        owner_kind="conduit",
        owner_id="conduit-1",
        metadata={"spellbook_id": "spellbook-1"},
        available_transactions=("link",),
    )

    with pytest.raises(RuntimeError, match="at least one peer conduit"):
        LinkTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=identity,
            metadata={"conduit_ids": ("conduit-1",)},
        )


def test_link_transaction_strategy_builds_spellbook_conduit_and_ward_scopes() -> None:
    """
    Purpose:
        Verify link planning includes the transaction-facing runtime scopes.
    Contract:
        - Each conduit contributes conduit and ward scope.
        - Resolved spellbooks contribute spellbook scope.
    Returns:
        None.
    Raises:
        AssertionError: If link planning omits required scope.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    source_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-1"},
        available_transactions=("link",),
    )
    peer_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-2",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-2"},
        available_transactions=("link",),
    )
    spellbook_a = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-1"},
        available_transactions=("bind",),
    )
    spellbook_b = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-2",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-2"},
        available_transactions=("bind",),
    )
    for identity in (source_identity, peer_identity, spellbook_a, spellbook_b):
        registry.register_identity(identity)
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-1",
        conduit_id="conduit-1",
    )
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-2",
        conduit_id="conduit-2",
    )

    plan = LinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata={"conduit_ids": ("conduit-2",)},
    )

    assert set(plan["conduit_ids"]) == {"conduit-1", "conduit-2"}
    assert "scope:conduit:conduit-1" in plan["scope_keys"]
    assert "scope:conduit:conduit-2" in plan["scope_keys"]
    assert "scope:spellbook:spellbook-1" in plan["scope_keys"]
    assert "scope:spellbook:spellbook-2" in plan["scope_keys"]
    assert plan["metadata"]["link_mode"] == "conduit_link"


def test_link_transaction_strategy_claims_spellbooks_intent_and_conduits_exclusive() -> None:
    """
    Purpose:
        Verify link planning claims owning spellbooks as INTENT (IX) while
        leaving participant conduits and wards to default EXCLUSIVE.
    Contract:
        - `scope_claims` contains exactly the resolved owning-spellbook scopes.
        - Each claimed spellbook scope carries the INTENT mode value.
        - Conduit and ward scopes are absent from `scope_claims`, so admission
          treats them as EXCLUSIVE.
    Returns:
        None.
    Raises:
        AssertionError: If link planning emits the wrong claim modes.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    source_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-1"},
        available_transactions=("link",),
    )
    peer_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-2",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-2"},
        available_transactions=("link",),
    )
    spellbook_a = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-1"},
        available_transactions=("bind",),
    )
    spellbook_b = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-2",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-2"},
        available_transactions=("bind",),
    )
    for identity in (source_identity, peer_identity, spellbook_a, spellbook_b):
        registry.register_identity(identity)
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-1",
        conduit_id="conduit-1",
    )
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-2",
        conduit_id="conduit-2",
    )

    plan = LinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata={"conduit_ids": ("conduit-2",)},
    )

    scope_claims = dict(plan["scope_claims"])
    assert set(scope_claims) == {
        "scope:spellbook:spellbook-1",
        "scope:spellbook:spellbook-2",
    }
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.INTENT.value


def test_unlink_transaction_strategy_claims_spellbooks_intent_and_conduits_exclusive() -> None:
    """
    Purpose:
        Verify unlink planning claims owning spellbooks as INTENT (IX) while
        leaving participant conduits and wards to default EXCLUSIVE, mirroring
        the link strategy because a sever mutates the same surfaces.
    Contract:
        - `scope_claims` contains exactly the resolved owning-spellbook scopes.
        - Each claimed spellbook scope carries the INTENT mode value.
        - Conduit and ward scopes are absent from `scope_claims`, so admission
          treats them as EXCLUSIVE.
        - `unlink_mode` metadata marks the conduit-unlink shape.
    Returns:
        None.
    Raises:
        AssertionError: If unlink planning emits the wrong claim modes.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    source_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-1"},
        available_transactions=("unlink",),
    )
    peer_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-2",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-2"},
        available_transactions=("unlink",),
    )
    spellbook_a = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-1"},
        available_transactions=("bind",),
    )
    spellbook_b = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-2",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-2"},
        available_transactions=("bind",),
    )
    for identity in (source_identity, peer_identity, spellbook_a, spellbook_b):
        registry.register_identity(identity)
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-1",
        conduit_id="conduit-1",
    )
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-2",
        conduit_id="conduit-2",
    )

    plan = UnlinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata={"conduit_ids": ("conduit-2",)},
    )

    scope_claims = dict(plan["scope_claims"])
    assert set(scope_claims) == {
        "scope:spellbook:spellbook-1",
        "scope:spellbook:spellbook-2",
    }
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.INTENT.value
    assert "scope:conduit:conduit-1" not in scope_claims
    assert "scope:conduit_ward:conduit-1" not in scope_claims
    assert plan["metadata"]["unlink_mode"] == "conduit_unlink"


def test_cluster_link_transaction_strategy_requires_cluster_id_and_two_members() -> None:
    """
    Purpose:
        Verify cluster-link planning validates required metadata.
    Contract:
        - cluster_id is mandatory.
        - At least two conduit ids are required.
    Returns:
        None.
    Raises:
        AssertionError: If invalid cluster-link metadata is accepted.
    """
    transaction_manager, registry, identity = _make_registry_and_identity(
        owner_kind="conduit_cluster",
        owner_id="cluster-1",
        metadata={"cluster_name": "alpha"},
        available_transactions=("cluster_link",),
    )

    with pytest.raises(RuntimeError, match="requires cluster_id metadata"):
        ClusterLinkTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=identity,
            metadata={"conduit_ids": ("conduit-1", "conduit-2")},
        )

    with pytest.raises(RuntimeError, match="at least two conduit ids"):
        ClusterLinkTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=identity,
            metadata={"cluster_id": "cluster-1", "conduit_ids": ("conduit-1",)},
        )


def test_cluster_link_transaction_strategy_builds_cluster_and_spellbook_scopes() -> None:
    """
    Purpose:
        Verify cluster-link planning includes cluster, conduit, ward, and spellbook scopes.
    Contract:
        - The cluster id becomes a cluster scope.
        - Each member conduit contributes conduit and ward scope.
    Returns:
        None.
    Raises:
        AssertionError: If cluster-link planning omits required scope.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    cluster_identity = DevopsIdentity(
        owner_kind="conduit_cluster",
        owner_id="cluster-1",
        aetheric_frame_name="frame-1",
        metadata={"cluster_name": "alpha"},
        available_transactions=("cluster_link",),
    )
    conduit_a = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-1"},
        available_transactions=("link",),
    )
    conduit_b = DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-2",
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": "spellbook-2"},
        available_transactions=("link",),
    )
    spellbook_a = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-1"},
        available_transactions=("bind",),
    )
    spellbook_b = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-2",
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": "conduit-2"},
        available_transactions=("bind",),
    )
    for identity in (cluster_identity, conduit_a, conduit_b, spellbook_a, spellbook_b):
        registry.register_identity(identity)
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-1",
        conduit_id="conduit-1",
    )
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-2",
        conduit_id="conduit-2",
    )

    plan = ClusterLinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=cluster_identity,
        metadata={
            "cluster_id": "cluster-1",
            "conduit_ids": ("conduit-1", "conduit-2"),
        },
    )

    assert "scope:cluster:cluster-1" in plan["scope_keys"]
    assert "scope:conduit:conduit-1" in plan["scope_keys"]
    assert "scope:conduit:conduit-2" in plan["scope_keys"]
    assert "scope:spellbook:spellbook-1" in plan["scope_keys"]
    assert "scope:spellbook:spellbook-2" in plan["scope_keys"]
    assert plan["metadata"]["cluster_mode"] == "cluster_link"
    # Claim modes: member spellbooks are INTENT; cluster + conduits + wards
    # stay EXCLUSIVE (absent from scope_claims).
    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.INTENT.value
    assert "scope:cluster:cluster-1" not in scope_claims
    assert "scope:conduit:conduit-1" not in scope_claims
    assert "scope:conduit_ward:conduit-1" not in scope_claims


def test_transfer_ownership_transaction_strategy_requires_conduit_identity() -> None:
    """
    Purpose:
        Verify transfer planning rejects non-conduit submitter identities.
    Contract:
        - Only conduit identities may originate ownership-transfer planning.
    Returns:
        None.
    Raises:
        AssertionError: If non-conduit identities are accepted.
    """
    transaction_manager, registry, identity = _make_registry_and_identity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        available_transactions=("transfer_ownership",),
    )

    with pytest.raises(RuntimeError, match="must originate from a conduit identity"):
        TransferOwnershipTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=identity,
            metadata={},
        )


def test_transfer_ownership_strategy_builds_scopes_from_metadata_footprint() -> None:
    """
    Purpose:
        Verify transfer planning is envelope-only: it builds conduit/ward/spellbook/
        cluster/binding scopes purely from the affected footprint the conduit call site
        stamped into metadata, with no live-object reach.
    Contract:
        - conduit_ids equals participant_conduit_ids from metadata.
        - cluster scope comes from affected_cluster_ids.
        - spellbook scopes come from affected_identity_keys.
        - the plan spellbook_id is source_spellbook_id.
    Returns:
        None.
    Raises:
        AssertionError: If the plan does not reflect the metadata footprint.
    """
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

    plan = TransferOwnershipTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source_identity,
        metadata={
            "target_conduit_id": "conduit-2",
            "source_conduit_id": "conduit-1",
            "source_spellbook_id": "spellbook-1",
            "spell_id": "spell-1",
            "binding_keys": (("frame", "__default__"),),
            "participant_conduit_ids": (
                "borrower-1",
                "borrower-2",
                "conduit-1",
                "conduit-2",
            ),
            "affected_cluster_ids": ("cluster-1",),
            "affected_identity_keys": (
                ("conduit", "conduit-1"),
                ("conduit", "conduit-2"),
                ("conduit_ward", "conduit-1"),
                ("conduit_ward", "conduit-2"),
                ("spellbook", "spellbook-1"),
                ("spellbook", "spellbook-2"),
                ("conduit_cluster", "cluster-1"),
            ),
        },
    )

    assert set(plan["conduit_ids"]) == {"conduit-1", "conduit-2", "borrower-1", "borrower-2"}
    scope_keys = set(plan["scope_keys"])
    assert "scope:conduit:conduit-1" in scope_keys
    assert "scope:conduit_ward:conduit-2" in scope_keys
    assert "scope:spellbook:spellbook-1" in scope_keys
    assert "scope:spellbook:spellbook-2" in scope_keys
    assert "scope:cluster:cluster-1" in scope_keys
    assert transaction_manager.make_scope_key_binding("frame", "__default__") in scope_keys
    assert plan["spellbook_id"] == "spellbook-1"


def test_transfer_ownership_strategy_requires_participant_footprint_metadata() -> None:
    """
    Purpose:
        Verify the strategy fails fast when the conduit-built footprint is absent (the
        strategy no longer discovers it itself).
    Contract:
        - Missing participant_conduit_ids raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If a footprint-less transfer request is accepted.
    """
    transaction_manager, registry, source_identity = _make_registry_and_identity(
        owner_kind="conduit",
        owner_id="conduit-1",
        available_transactions=("transfer_ownership",),
    )

    with pytest.raises(RuntimeError, match="participant_conduit_ids"):
        TransferOwnershipTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=source_identity,
            metadata={"target_conduit_id": "conduit-2"},
        )


def test_notch_transaction_strategy_seals_spellbook_conduit_binding_exclusive() -> None:
    """
    Purpose:
        Verify a notch seals the owning spellbook, its conduit, and the targeted
        binding key all EXCLUSIVE (blocks bind/transfer/link/cluster on them).
    Contract:
        - spellbook, conduit, and binding scopes are all EXCLUSIVE.
        - metadata marks the notch mode.
    Returns:
        None.
    Raises:
        AssertionError: If notch planning does not seal exclusively.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=("notch",),
    )
    registry.register_identity(identity)

    plan = NotchTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "owner_conduit_id": "conduit-1",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_claims = dict(plan["scope_claims"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims[binding_scope] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["index_mode"] == "notch"


def test_add_to_index_transaction_strategy_seals_both_sides_exclusive() -> None:
    """
    Purpose:
        Verify add-to-index seals BOTH source and target spellbooks/conduits
        plus the moved binding key, all EXCLUSIVE.
    Contract:
        - Both spellbook scopes, both conduit scopes, and the binding scope are
          EXCLUSIVE.
        - metadata marks the add_to_index mode.
    Returns:
        None.
    Raises:
        AssertionError: If add planning does not seal both sides exclusively.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=("add_to_index",),
    )
    registry.register_identity(identity)

    plan = AddToIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "source_spellbook_id": "spellbook-1",
            "target_spellbook_id": "spellbook-2",
            "source_conduit_id": "conduit-1",
            "target_conduit_id": "conduit-2",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_claims = dict(plan["scope_claims"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-2"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims[binding_scope] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["index_mode"] == "add_to_index"


def test_remove_from_index_transaction_strategy_seals_spellbook_conduit_binding_exclusive() -> None:
    """
    Purpose:
        Verify remove-from-index seals the owning spellbook, conduit, and the
        moved binding key all EXCLUSIVE.
    Contract:
        - spellbook, conduit, and binding scopes are all EXCLUSIVE.
        - metadata marks the remove_from_index mode.
    Returns:
        None.
    Raises:
        AssertionError: If remove planning does not seal exclusively.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=("remove_from_index",),
    )
    registry.register_identity(identity)

    plan = RemoveFromIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "spellbook_id": "spellbook-1",
            "owner_conduit_id": "conduit-1",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_claims = dict(plan["scope_claims"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims[binding_scope] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["index_mode"] == "remove_from_index"


class _RecordingGateOps:
    """
    Records lineage drain/quiesce/reopen calls for cluster-leader
    coordination tests (park-mode freeze since patch
    notch_conduit_gate_freeze_2026_07_12).
    """

    def __init__(self) -> None:
        """Start with empty drain, quiesce, and reopen logs."""
        self.closed: list = []
        self.quiesced: list = []
        self.enabled: list = []

    def close_and_wait_conduit_lineage(self, root_id: str) -> None:
        """Record a terminal drain request for one root lineage."""
        self.closed.append(root_id)

    def quiesce_conduit_lineage(self, root_id: str) -> None:
        """Record a park-mode freeze+drain request for one root lineage."""
        self.quiesced.append(root_id)

    def enable_conduit_lineage(self, root_id: str) -> None:
        """Record a reopen request for one root lineage."""
        self.enabled.append(root_id)


def _make_cluster_leader_identity(transaction_name: str) -> DevopsIdentity:
    """
    Build an attached conduit identity that supports one cluster-leader transaction.
    """
    return DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=(transaction_name,),
    )


def test_transaction_strategy_builder_resolves_cluster_leader_election_names() -> None:
    """
    Purpose:
        Verify the builder resolves the elect/unelect cluster-leader strategies
        from both enum and string inputs.
    Contract:
        - elect/unelect register and resolve to their strategy classes.
    Returns:
        None.
    Raises:
        AssertionError: If cluster-leader-election resolution diverges.
    """
    transaction_manager, registry, _identity = _make_registry_and_identity()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    assert (
        builder.resolve(ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER)
        is ElectConduitClusterLeaderTransactionStrategy
    )
    assert (
        builder.resolve("elect_conduit_cluster_leader")
        is ElectConduitClusterLeaderTransactionStrategy
    )
    assert (
        builder.resolve(ChangeTransactionType.UNELECT_CONDUIT_CLUSTER_LEADER)
        is UnelectConduitClusterLeaderTransactionStrategy
    )
    assert (
        builder.resolve("unelect_conduit_cluster_leader")
        is UnelectConduitClusterLeaderTransactionStrategy
    )


def test_elect_cluster_leader_strategy_seals_member_conduits_exclusive() -> None:
    """
    Purpose:
        Verify electing a leader seals every cluster member conduit EXCLUSIVE,
        isolated to those conduits (no spellbook/binding scope), and marks the mode.
    Contract:
        - Each member conduit scope is EXCLUSIVE.
        - conduit_ids carries the sorted footprint; metadata marks the elect mode.
    Returns:
        None.
    Raises:
        AssertionError: If elect planning does not seal the members exclusively.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    identity = _make_cluster_leader_identity("elect_conduit_cluster_leader")
    registry.register_identity(identity)

    plan = ElectConduitClusterLeaderTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"member_conduit_ids": ("conduit-1", "conduit-2")},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-2"] == ClaimMode.EXCLUSIVE.value
    assert plan["conduit_ids"] == ("conduit-1", "conduit-2")
    assert plan["metadata"]["cluster_leader_mode"] == "elect"


def test_unelect_cluster_leader_strategy_seals_member_conduits_exclusive() -> None:
    """
    Purpose:
        Verify unelecting a leader seals every cluster member conduit EXCLUSIVE
        and marks the unelect mode.
    Contract:
        - Each member conduit scope is EXCLUSIVE.
        - metadata marks the unelect mode.
    Returns:
        None.
    Raises:
        AssertionError: If unelect planning does not seal the members exclusively.
    """
    transaction_manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame-1")
    identity = _make_cluster_leader_identity("unelect_conduit_cluster_leader")
    registry.register_identity(identity)

    plan = UnelectConduitClusterLeaderTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"member_conduit_ids": ("conduit-1", "conduit-2")},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-2"] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["cluster_leader_mode"] == "unelect"


def test_unelect_cluster_leader_drains_then_reopens_member_root_lineages() -> None:
    """
    Purpose:
        Verify unelect drains every member root lineage on_start and reopens every
        member root lineage on_end (the use-after-dispose guard, fail-closed).
    Contract:
        - on_start drains each member root once.
        - on_end reopens each member root once.
    Returns:
        None.
    Raises:
        AssertionError: If drain/reopen footprints do not match the member roots.
    """
    gate_ops = _RecordingGateOps()
    registry = DevopsInformationRegistry("frame-1")
    identity = _make_cluster_leader_identity("unelect_conduit_cluster_leader")
    registry.register_identity(identity)
    metadata = {
        "member_root_conduit_ids": ("root-1", "root-2"),
        "conduit_lineage_gate_ops": gate_ops,
    }

    UnelectConduitClusterLeaderTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata=metadata,
    )
    UnelectConduitClusterLeaderTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata=metadata,
    )

    assert gate_ops.closed == ["root-1", "root-2"]
    assert gate_ops.enabled == ["root-1", "root-2"]


def test_elect_cluster_leader_on_start_does_not_drain() -> None:
    """
    Purpose:
        Verify electing a leader performs no lineage drain (inert -> active needs
        no coordination); a gate facade in metadata is left untouched on_start.
    Contract:
        - on_start drains nothing even when a gate facade is supplied.
    Returns:
        None.
    Raises:
        AssertionError: If elect on_start drains any lineage.
    """
    gate_ops = _RecordingGateOps()
    registry = DevopsInformationRegistry("frame-1")
    identity = _make_cluster_leader_identity("elect_conduit_cluster_leader")
    registry.register_identity(identity)

    ElectConduitClusterLeaderTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "member_root_conduit_ids": ("root-1",),
            "conduit_lineage_gate_ops": gate_ops,
        },
    )

    assert gate_ops.closed == []
