from typing import Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.bind_transaction_strategy import (
    BindTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.link_transaction_strategy import (
    LinkTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unlink_transaction_strategy import (
    UnlinkTransactionStrategy,
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
# Helpers
# ---------------------------------------------------------------------------
def _manager_and_registry() -> Tuple[ChangeControlTransactionManager, DevopsInformationRegistry]:
    """Return a fresh transaction manager + registry for one frame."""
    return ChangeControlTransactionManager(), DevopsInformationRegistry("frame-1")


def _register_conduit_pair(
        registry: DevopsInformationRegistry,
        *,
        conduit_id: str,
        spellbook_id: str,
        conduit_tx: Tuple[str, ...] = ("link",),
) -> DevopsIdentity:
    """
    Register a conduit + its owning spellbook + the ownership link.

    Returns the conduit identity so callers can use it as the submitter.
    """
    conduit_identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id=conduit_id,
        aetheric_frame_name="frame-1",
        metadata={"spellbook_id": spellbook_id},
        available_transactions=conduit_tx,
    )
    spellbook_identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id=spellbook_id,
        aetheric_frame_name="frame-1",
        metadata={"conduit_id": conduit_id},
        available_transactions=("bind",),
    )
    registry.register_identity(conduit_identity)
    registry.register_identity(spellbook_identity)
    registry.register_spellbook_conduit_ownership(
        spellbook_id=spellbook_id,
        conduit_id=conduit_id,
    )
    return conduit_identity


# ---------------------------------------------------------------------------
# Builder cross-cutting (all built transactions)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "name",
    [
        "link",
        "bind",
        "cluster_link",
        "unlink",
        "notch",
        "add_to_index",
        "remove_from_index",
        "elect_conduit_cluster_leader",
        "unelect_conduit_cluster_leader",
        "cluster_join",
        "cluster_leave",
    ],
)
def test_builder_resolves_every_built_transaction_name(name: str) -> None:
    """
    Purpose:
        Verify the builder resolves each transaction name authored in this program.
    Contract:
        - resolve(name) returns a strategy class (never None, never raises).
    Returns:
        None.
    Raises:
        AssertionError: If a built transaction name fails to resolve.
    """
    transaction_manager, registry = _manager_and_registry()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    resolved = builder.resolve(name)
    assert resolved is not None
    assert hasattr(resolved, "build_start_plan")


@pytest.mark.parametrize(
    "member",
    [
        ChangeTransactionType.LINK,
        ChangeTransactionType.BIND,
        ChangeTransactionType.CLUSTER_LINK,
        ChangeTransactionType.UNLINK,
        ChangeTransactionType.NOTCH,
        ChangeTransactionType.ADD_TO_INDEX,
        ChangeTransactionType.REMOVE_FROM_INDEX,
        ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER,
        ChangeTransactionType.UNELECT_CONDUIT_CLUSTER_LEADER,
        ChangeTransactionType.CLUSTER_JOIN,
        ChangeTransactionType.CLUSTER_LEAVE,
    ],
)
def test_builder_resolves_each_enum_member(member: ChangeTransactionType) -> None:
    """
    Purpose:
        Verify enum members resolve identically to their string payloads.
    Contract:
        - resolve(member) is resolve(str(member)) for every built type.
    Returns:
        None.
    Raises:
        AssertionError: If enum and string resolution diverge.
    """
    transaction_manager, registry = _manager_and_registry()
    builder = TransactionStrategyBuilder(transaction_manager, registry)

    assert builder.resolve(member) is builder.resolve(member.value)


# ---------------------------------------------------------------------------
# BIND
# ---------------------------------------------------------------------------
def test_bind_pre_conjure_stays_spellbook_local() -> None:
    """
    Purpose:
        Verify pre-conjure bind claims no conduit and seals only the spellbook.
    Contract:
        - conduit_ids is empty.
        - the spellbook scope and the bind transaction-owner scope are present.
        - bind_mode is pre_conjure.
    Returns:
        None.
    Raises:
        AssertionError: If pre-conjure bind widens beyond the spellbook.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={"conjured": False, "conduit_id": None},
        available_transactions=("bind", "scan"),
    )
    registry.register_identity(identity)

    plan = BindTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={},
    )

    assert plan["conduit_ids"] == ()
    assert plan["initiator_conduit_id"] == "spellbook:spellbook-1"
    assert "scope:spellbook:spellbook-1" in plan["scope_keys"]
    assert "scope:transaction:spellbook:spellbook-1:bind" in plan["scope_keys"]
    assert plan["metadata"]["bind_mode"] == "pre_conjure"


def test_bind_post_conjure_seals_conduit_ward_and_cluster() -> None:
    """
    Purpose:
        Verify post-conjure bind resolves the paired conduit and includes cluster scope.
    Contract:
        - conduit, ward, and cluster scopes are present.
        - bind_mode is post_conjure and affected_cluster_ids carries the cluster.
    Returns:
        None.
    Raises:
        AssertionError: If post-conjure bind omits the conduit/cluster footprint.
    """
    transaction_manager, registry = _manager_and_registry()
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
    for to_register in (spellbook_identity, conduit_identity, cluster_identity):
        registry.register_identity(to_register)
    registry.register_cluster_membership(cluster_id="cluster-1", conduit_id="conduit-1")

    plan = BindTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=spellbook_identity,
        metadata={"conduit_id": "conduit-1"},
    )

    assert plan["conduit_ids"] == ("conduit-1",)
    assert "scope:conduit:conduit-1" in plan["scope_keys"]
    assert "scope:conduit_ward:conduit-1" in plan["scope_keys"]
    assert "scope:cluster:cluster-1" in plan["scope_keys"]
    assert plan["metadata"]["bind_mode"] == "post_conjure"
    assert plan["metadata"]["affected_cluster_ids"] == ("cluster-1",)


def test_bind_post_conjure_claims_spellbook_and_cluster_intent() -> None:
    """
    Purpose:
        Verify post-conjure bind claims the spellbook and cluster INTENT, conduit
        EXCLUSIVE, so parallel member binds across one cluster do not serialize.
    Contract:
        - spellbook and cluster scopes carry INTENT.
        - conduit and ward scopes are absent from scope_claims (EXCLUSIVE).
    Returns:
        None.
    Raises:
        AssertionError: If the bind claim modes are wrong.
    """
    transaction_manager, registry = _manager_and_registry()
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
        available_transactions=("cluster_link",),
    )
    cluster_identity = DevopsIdentity(
        owner_kind="conduit_cluster",
        owner_id="cluster-1",
        aetheric_frame_name="frame-1",
        metadata={"cluster_name": "alpha"},
        available_transactions=("cluster_link",),
    )
    for to_register in (spellbook_identity, conduit_identity, cluster_identity):
        registry.register_identity(to_register)
    registry.register_cluster_membership(cluster_id="cluster-1", conduit_id="conduit-1")

    plan = BindTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=spellbook_identity,
        metadata={"conduit_id": "conduit-1"},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:cluster:cluster-1"] == ClaimMode.INTENT.value
    assert "scope:conduit:conduit-1" not in scope_claims
    assert "scope:conduit_ward:conduit-1" not in scope_claims


def test_bind_hooks_never_reach_into_spellbook_runtime() -> None:
    """
    Purpose:
        Verify the bind strategy hooks are DevOps-only and never call the live
        Spellbook's bind-state methods (the Spellbook owns that, not the strategy).
    Contract:
        - on_start and on_end leave _prepare_bind_transaction_state /
          _clear_bind_transaction_state uncalled.
    Returns:
        None.
    Raises:
        AssertionError: If a hook reaches into the Spellbook object.
    """
    _transaction_manager, registry = _manager_and_registry()
    identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id="spellbook-1",
        aetheric_frame_name="frame-1",
        metadata={"conjured": False},
        available_transactions=("bind",),
    )
    registry.register_identity(identity)
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


# ---------------------------------------------------------------------------
# LINK
# ---------------------------------------------------------------------------
def test_link_requires_at_least_one_peer() -> None:
    """
    Purpose:
        Verify link planning rejects a participant set with no peer.
    Contract:
        - A submitter-only participant set raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If a one-sided link is accepted.
    """
    transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1",
    )

    with pytest.raises(RuntimeError, match="at least one peer conduit"):
        LinkTransactionStrategy.build_start_plan(
            transaction_manager=transaction_manager,
            devops_information_registry=registry,
            identity=source,
            metadata={"conduit_ids": ("conduit-1",)},
        )


def test_link_builds_conduit_ward_and_spellbook_scopes() -> None:
    """
    Purpose:
        Verify link planning seals both participants' conduit, ward, and spellbook.
    Contract:
        - Both conduit scopes and both owning-spellbook scopes are present.
        - link_mode is conduit_link.
    Returns:
        None.
    Raises:
        AssertionError: If link planning omits a participant scope.
    """
    transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1",
    )
    _register_conduit_pair(registry, conduit_id="conduit-2", spellbook_id="spellbook-2")

    plan = LinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source,
        metadata={"conduit_ids": ("conduit-2",)},
    )

    assert set(plan["conduit_ids"]) == {"conduit-1", "conduit-2"}
    assert "scope:conduit:conduit-1" in plan["scope_keys"]
    assert "scope:conduit:conduit-2" in plan["scope_keys"]
    assert "scope:spellbook:spellbook-1" in plan["scope_keys"]
    assert "scope:spellbook:spellbook-2" in plan["scope_keys"]
    assert plan["metadata"]["link_mode"] == "conduit_link"


def test_link_claims_only_owning_spellbooks_intent() -> None:
    """
    Purpose:
        Verify link claims exactly the two owning spellbooks INTENT and nothing else.
    Contract:
        - scope_claims keys equal the two owning-spellbook scopes.
        - Each is INTENT.
    Returns:
        None.
    Raises:
        AssertionError: If the claim set is wrong.
    """
    transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1",
    )
    _register_conduit_pair(registry, conduit_id="conduit-2", spellbook_id="spellbook-2")

    plan = LinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source,
        metadata={"conduit_ids": ("conduit-2",)},
    )

    scope_claims = dict(plan["scope_claims"])
    assert set(scope_claims) == {"scope:spellbook:spellbook-1", "scope:spellbook:spellbook-2"}
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.INTENT.value


def test_link_includes_all_named_peers() -> None:
    """
    Purpose:
        Verify link planning seals every named peer plus the submitter.
    Contract:
        - conduit_ids is the union of the submitter and all named peers.
    Returns:
        None.
    Raises:
        AssertionError: If a named peer is dropped.
    """
    transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1",
    )
    _register_conduit_pair(registry, conduit_id="conduit-2", spellbook_id="spellbook-2")
    _register_conduit_pair(registry, conduit_id="conduit-3", spellbook_id="spellbook-3")

    plan = LinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source,
        metadata={"conduit_ids": ("conduit-2", "conduit-3")},
    )

    assert set(plan["conduit_ids"]) == {"conduit-1", "conduit-2", "conduit-3"}


def test_link_hooks_are_no_ops() -> None:
    """
    Purpose:
        Verify the link strategy lifecycle hooks are no-ops.
    Contract:
        - on_start and on_end return None and do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If a hook returns non-None or raises.
    """
    _transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1",
    )

    assert LinkTransactionStrategy.on_start(
        devops_information_registry=registry, identity=source, metadata={},
    ) is None
    assert LinkTransactionStrategy.on_end(
        devops_information_registry=registry, identity=source, metadata={},
    ) is None


# ---------------------------------------------------------------------------
# UNLINK
# ---------------------------------------------------------------------------
def test_unlink_claims_owning_spellbooks_intent_conduits_exclusive() -> None:
    """
    Purpose:
        Verify unlink mirrors link claim modes (a sever mutates the same surfaces).
    Contract:
        - Owning spellbooks are INTENT; conduits/wards EXCLUSIVE (absent).
        - unlink_mode is conduit_unlink.
    Returns:
        None.
    Raises:
        AssertionError: If unlink claim modes diverge from the link pattern.
    """
    transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1", conduit_tx=("unlink",),
    )
    _register_conduit_pair(
        registry, conduit_id="conduit-2", spellbook_id="spellbook-2", conduit_tx=("unlink",),
    )

    plan = UnlinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source,
        metadata={"conduit_ids": ("conduit-2",)},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.INTENT.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.INTENT.value
    assert "scope:conduit:conduit-1" not in scope_claims
    assert "scope:conduit_ward:conduit-1" not in scope_claims
    assert plan["metadata"]["unlink_mode"] == "conduit_unlink"


def test_unlink_builds_both_participant_conduit_scopes() -> None:
    """
    Purpose:
        Verify unlink seals both participants' conduit scopes.
    Contract:
        - Both conduit scopes are present; conduit_ids is the participant union.
    Returns:
        None.
    Raises:
        AssertionError: If a participant scope is missing.
    """
    transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1", conduit_tx=("unlink",),
    )
    _register_conduit_pair(
        registry, conduit_id="conduit-2", spellbook_id="spellbook-2", conduit_tx=("unlink",),
    )

    plan = UnlinkTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=source,
        metadata={"conduit_ids": ("conduit-2",)},
    )

    assert set(plan["conduit_ids"]) == {"conduit-1", "conduit-2"}
    assert "scope:conduit:conduit-1" in plan["scope_keys"]
    assert "scope:conduit:conduit-2" in plan["scope_keys"]


def test_unlink_hooks_are_no_ops() -> None:
    """
    Purpose:
        Verify the unlink strategy lifecycle hooks are no-ops.
    Contract:
        - on_start and on_end return None and do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If a hook returns non-None or raises.
    """
    _transaction_manager, registry = _manager_and_registry()
    source = _register_conduit_pair(
        registry, conduit_id="conduit-1", spellbook_id="spellbook-1", conduit_tx=("unlink",),
    )

    assert UnlinkTransactionStrategy.on_start(
        devops_information_registry=registry, identity=source, metadata={},
    ) is None
    assert UnlinkTransactionStrategy.on_end(
        devops_information_registry=registry, identity=source, metadata={},
    ) is None
