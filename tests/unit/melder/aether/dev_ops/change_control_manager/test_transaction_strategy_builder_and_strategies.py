from typing import Any, Dict, Iterable, Optional, Set, Tuple
from unittest.mock import MagicMock, patch

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.bind_transaction_strategy import (
    BindTransactionStrategy,
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
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
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


class _FakeCluster:
    """
    Minimal cluster object exposing member ids.
    """

    def __init__(self, members: Iterable[str]) -> None:
        """Store detached cluster membership."""
        self._members = set(members)

    def get_members(self) -> Set[str]:
        """
        Return a detached membership snapshot.
        """
        return set(self._members)


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
    assert builder.resolve("link") is LinkTransactionStrategy
    assert builder.resolve("cluster_link") is ClusterLinkTransactionStrategy
    assert builder.resolve("transfer_ownership") is TransferOwnershipTransactionStrategy


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
        metadata={},
    )

    assert plan["initiator_conduit_id"] == "conduit-1"
    assert plan["conduit_ids"] == ("conduit-1",)
    assert "scope:conduit:conduit-1" in plan["scope_keys"]
    assert "scope:conduit_ward:conduit-1" in plan["scope_keys"]
    assert "scope:cluster:cluster-1" in plan["scope_keys"]
    assert plan["metadata"]["bind_mode"] == "post_conjure"
    assert plan["metadata"]["affected_cluster_ids"] == ("cluster-1",)


def test_bind_transaction_strategy_on_start_and_on_end_call_spellbook_local_hooks() -> None:
    """
    Purpose:
        Verify bind strategy start and end hooks resolve the live Spellbook object.
    Contract:
        - on_start calls _prepare_bind_transaction_state.
        - on_end calls _clear_bind_transaction_state.
    Returns:
        None.
    Raises:
        AssertionError: If spellbook-local bind hooks are not invoked.
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

    spellbook._prepare_bind_transaction_state.assert_called_once_with()
    spellbook._clear_bind_transaction_state.assert_called_once_with()


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


def test_transfer_ownership_transaction_strategy_builds_participant_scope_from_preflight() -> None:
    """
    Purpose:
        Verify transfer planning incorporates borrowers and cluster memberships.
    Contract:
        - Source and target conduits are always included.
        - Borrowers and cluster ids discovered during preflight are folded in.
    Returns:
        None.
    Raises:
        AssertionError: If preflight participants are omitted.
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
    registry.register_identity(
        DevopsIdentity(
            owner_kind="spellbook",
            owner_id="spellbook-1",
            aetheric_frame_name="frame-1",
            metadata={"conduit_id": "conduit-1"},
            available_transactions=("bind",),
        )
    )
    registry.register_identity(
        DevopsIdentity(
            owner_kind="spellbook",
            owner_id="spellbook-2",
            aetheric_frame_name="frame-1",
            metadata={"conduit_id": "conduit-2"},
            available_transactions=("bind",),
        )
    )
    registry.register_identity(
        DevopsIdentity(
            owner_kind="conduit_cluster",
            owner_id="cluster-1",
            aetheric_frame_name="frame-1",
            metadata={"cluster_name": "alpha"},
            available_transactions=("cluster_link",),
        )
    )
    registry.register_cluster_membership(cluster_id="cluster-1", conduit_id="conduit-1")
    registry.register_cluster_membership(cluster_id="cluster-1", conduit_id="borrower-2")

    source_spellbook = MagicMock()
    source_spellbook._id = "spellbook-1"
    target_spellbook = MagicMock()
    target_spellbook._id = "spellbook-2"
    spell = MagicMock()
    spell.spell_id = "spell-1"
    spell.key = ("frame", "__default__")
    spell.spell_index.id = "index-1"
    source_conduit = MagicMock()
    source_conduit._id = "conduit-1"
    source_conduit._spellbook = source_spellbook
    source_conduit.get_spell_by_id.return_value = spell
    source_conduit.get_spell_by_index_id.return_value = spell
    target_conduit = MagicMock()
    target_conduit._id = "conduit-2"
    target_conduit._spellbook = target_spellbook
    cluster_object = _FakeCluster(("conduit-1", "borrower-2"))

    registry.register_identity(
        DevopsIdentity(
            owner_kind="conduit",
            owner_id="conduit-2",
            aetheric_frame_name="frame-1",
            metadata={"spellbook_id": "spellbook-2"},
            available_transactions=("transfer_ownership",),
        )
    )
    registry.register_identity(
        DevopsIdentity(
            owner_kind="conduit",
            owner_id="borrower-2",
            aetheric_frame_name="frame-1",
            metadata={"spellbook_id": "spellbook-2"},
            available_transactions=("link",),
        )
    )
    registry.refresh_identity(source_identity, object_ref=source_conduit)
    registry.refresh_identity(
        registry.get_identity(owner_kind="conduit", owner_id="conduit-2"),
        object_ref=target_conduit,
    )
    registry.refresh_identity(
        registry.get_identity(owner_kind="conduit_cluster", owner_id="cluster-1"),
        object_ref=cluster_object,
    )

    with patch(
        "melder.aether.aetheric_frame.dev_ops.change_control_manager."
        "transaction_manager.strategies.transfer_ownership_transaction_strategy."
        "TransferOfOwnership._build_preflight_summary",
        return_value={
            "borrowers": (
                {
                    "type": "contract",
                    "borrower_conduit_id": "borrower-1",
                },
                {
                    "type": "cluster",
                    "cluster_id": "cluster-1",
                    "member_conduit_ids": ("conduit-1", "borrower-2"),
                },
            ),
            "dependencies": ("dep-1",),
        },
    ):
        plan = TransferOwnershipTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=source_identity,
            metadata={
                "target_conduit_id": "conduit-2",
                "spell_id": "spell-1",
                "move_creations": True,
            },
        )

    assert set(plan["conduit_ids"]) == {"conduit-1", "conduit-2", "borrower-1", "borrower-2"}
    assert "scope:cluster:cluster-1" in plan["scope_keys"]
    assert plan["metadata"]["source_conduit_id"] == "conduit-1"
    assert plan["metadata"]["target_conduit_id"] == "conduit-2"
    assert plan["metadata"]["preflight_dependencies"] == ("dep-1",)
