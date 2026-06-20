from contextlib import contextmanager
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_cluster_transactions() -> None:
    """
    Purpose:
        Ensure each cluster-transaction component test starts on a clean Aether.
    Contract:
        - Resets the Aether singleton + rebinds Spellbook/Conduit._aether before and
          after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class _RecordingMediator:
    """
    Frame mediator double that records start/end transaction calls.

    Purpose:
        Capture exactly which change-control transaction a cluster call site opens
        (type + metadata) and how it is closed (expected_type + success), without
        standing up the real admission machinery.
    """

    def __init__(self) -> None:
        """Start with empty start/end logs."""
        self.start_calls: List[Dict[str, Any]] = []
        self.end_calls: List[Dict[str, Any]] = []

    def start_transaction(
        self,
        *,
        identity: Any,
        transaction_type: ChangeTransactionType,
        metadata: Dict[str, Any],
    ) -> None:
        """Record one start_transaction request."""
        self.start_calls.append(
            {
                "identity": identity,
                "transaction_type": transaction_type,
                "metadata": dict(metadata),
            }
        )

    def end_transaction(
        self,
        *,
        expected_type: ChangeTransactionType,
        success: bool,
    ) -> None:
        """Record one end_transaction request."""
        self.end_calls.append({"expected_type": expected_type, "success": success})


class _MembershipConduitStub:
    """
    Conduit double for cluster membership-transaction component tests.

    Purpose:
        Satisfy everything `ConduitCluster.handle_join` / `handle_leave` and the
        share helpers touch: identity + state, a shared recording mediator, a
        recording `transaction()` context manager, and recording contract calls.
    """

    def __init__(
        self,
        *,
        conduit_id: str,
        spellbook: Spellbook,
        mediator: _RecordingMediator,
        aetheric_frame: str = "default",
    ) -> None:
        """Store identity, spellbook, the shared mediator, and call logs."""
        self._id = conduit_id
        self._spellbook = spellbook
        self._aetheric_frame_name = aetheric_frame
        self._conduit_state = ConduitState.normal
        self._mediator = mediator
        self.transaction_calls: List[Union[ChangeTransactionType, str]] = []
        self.contract_calls: List[Dict[str, object]] = []
        self.remove_root_calls: List[Dict[str, object]] = []
        self._cluster_creations = ClusterCreations()

    def _get_required_transaction_mediator(self) -> _RecordingMediator:
        """Return the shared recording mediator (the cluster opens its tx through this)."""
        return self._mediator

    @contextmanager
    def transaction(
        self,
        transaction_type: Union[ChangeTransactionType, str],
        *,
        conduits: Optional[Iterable[object]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Iterator["_MembershipConduitStub"]:
        """Record the inner per-pair transaction type, then yield self (no-op window)."""
        self.transaction_calls.append(transaction_type)
        yield self

    def add_spell_to_contract(
        self,
        *,
        spell: object,
        conduit: object,
        permissions: str,
        aetheric_frame: str,
        reason: DetailReason,
        root_spell_id: str,
        link_dependencies: bool,
    ) -> None:
        """Record a contract (share) call."""
        self.contract_calls.append(
            {"spell": spell, "conduit": conduit, "root_spell_id": root_spell_id}
        )

    def remove_root_from_contracts(
        self,
        *,
        root_spell_id: str,
        conduit: object,
        aetheric_frame: str,
    ) -> None:
        """Record a removal (unshare) call."""
        self.remove_root_calls.append({"root_spell_id": root_spell_id, "conduit": conduit})


def _make_spellbook() -> Spellbook:
    """Return a Spellbook configured with one scheduler worker for component tests."""
    spellbook = Spellbook()
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _cluster_with(
    stubs: Iterable[_MembershipConduitStub],
    *,
    aetheric_frame_name: str = "default",
) -> ConduitCluster:
    """Build a ConduitCluster whose registry resolves the supplied stubs by id."""
    registry: Dict[str, _MembershipConduitStub] = {stub._id: stub for stub in stubs}
    return ConduitCluster(
        "cluster-a",
        registry,
        aetheric_frame_name,
        DevopsInformationRegistry(aetheric_frame_name),
        True,
    )


def _spell_index_for(spellbook: Spellbook, spell_id: str) -> object:
    """Resolve the SpellIndex whose selected spell id matches, for share seeding."""
    for spell_index, spell in spellbook.spells.items():
        if spell_index.selected_spell_id == spell_id:
            return spell.spell_index
    raise AssertionError("expected a bound cluster spell index")


# ---------------------------------------------------------------------------
# Identity declaration
# ---------------------------------------------------------------------------
def test_cluster_identity_declares_membership_and_leader_transactions() -> None:
    """
    Purpose:
        Verify the cluster's DevOps identity declares every membership/leader
        transaction the mediator must admit on it.
    Contract:
        - available_transactions includes cluster_join, cluster_leave, elect, unelect.
    Returns:
        None.
    Raises:
        AssertionError: If a declared transaction is missing.
    """
    cluster = _cluster_with(())

    declared = set(cluster._devops_identity.available_transactions)
    assert {
        "cluster_join",
        "cluster_leave",
        "elect_conduit_cluster_leader",
        "unelect_conduit_cluster_leader",
    } <= declared


# ---------------------------------------------------------------------------
# CLUSTER_JOIN wrap
# ---------------------------------------------------------------------------
def test_handle_join_opens_cluster_join_over_all_involved_conduits() -> None:
    """
    Purpose:
        Verify handle_join opens a single CLUSTER_JOIN transaction sealing the joiner
        plus every existing member (the link-pattern footprint).
    Contract:
        - Exactly one start_transaction of type CLUSTER_JOIN is opened.
        - Its metadata conduit_ids equal the sorted joiner + existing members.
    Returns:
        None.
    Raises:
        AssertionError: If the transaction type or footprint is wrong.
    """
    mediator = _RecordingMediator()
    member_a = _MembershipConduitStub(conduit_id="m-a", spellbook=_make_spellbook(), mediator=mediator)
    member_b = _MembershipConduitStub(conduit_id="m-b", spellbook=_make_spellbook(), mediator=mediator)
    joiner = _MembershipConduitStub(conduit_id="j-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((member_a, member_b, joiner))
    cluster.members.update({"m-a", "m-b"})

    cluster.handle_join(joiner)

    assert len(mediator.start_calls) == 1
    start = mediator.start_calls[0]
    assert start["transaction_type"] == ChangeTransactionType.CLUSTER_JOIN
    assert start["metadata"]["conduit_ids"] == ("j-1", "m-a", "m-b")


def test_handle_join_commits_success_true_and_adds_member() -> None:
    """
    Purpose:
        Verify a clean handle_join commits (success=True) and adds the joiner to members.
    Contract:
        - end_transaction is called once with CLUSTER_JOIN and success=True.
        - The joiner id is present in cluster membership afterward.
    Returns:
        None.
    Raises:
        AssertionError: If commit/membership state is wrong.
    """
    mediator = _RecordingMediator()
    member_a = _MembershipConduitStub(conduit_id="m-a", spellbook=_make_spellbook(), mediator=mediator)
    joiner = _MembershipConduitStub(conduit_id="j-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((member_a, joiner))
    cluster.members.add("m-a")

    cluster.handle_join(joiner)

    assert mediator.end_calls == [
        {"expected_type": ChangeTransactionType.CLUSTER_JOIN, "success": True}
    ]
    assert "j-1" in cluster.get_members()


def test_handle_join_metadata_carries_cluster_id_and_origin_surface() -> None:
    """
    Purpose:
        Verify the CLUSTER_JOIN metadata identifies the cluster and the call site.
    Contract:
        - metadata carries the cluster id and an origin_surface marker.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostic metadata is missing.
    """
    mediator = _RecordingMediator()
    joiner = _MembershipConduitStub(conduit_id="j-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((joiner,))

    cluster.handle_join(joiner)

    metadata = mediator.start_calls[0]["metadata"]
    assert metadata["cluster_id"] == cluster._id
    assert metadata["origin_surface"] == "conduit_cluster.handle_join"


def test_handle_join_single_first_member_seals_only_itself() -> None:
    """
    Purpose:
        Verify the first conduit to join an empty cluster seals just itself.
    Contract:
        - conduit_ids equals the lone joiner.
    Returns:
        None.
    Raises:
        AssertionError: If an empty cluster's first join widens the footprint.
    """
    mediator = _RecordingMediator()
    joiner = _MembershipConduitStub(conduit_id="j-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((joiner,))

    cluster.handle_join(joiner)

    assert mediator.start_calls[0]["metadata"]["conduit_ids"] == ("j-1",)


# ---------------------------------------------------------------------------
# CLUSTER_LEAVE wrap
# ---------------------------------------------------------------------------
def test_handle_leave_opens_cluster_leave_over_involved_conduits() -> None:
    """
    Purpose:
        Verify handle_leave opens a single CLUSTER_LEAVE transaction over the leaver
        and the remaining members.
    Contract:
        - Exactly one start_transaction of type CLUSTER_LEAVE is opened.
        - Its metadata conduit_ids include the leaver and the remaining members.
    Returns:
        None.
    Raises:
        AssertionError: If the transaction type or footprint is wrong.
    """
    mediator = _RecordingMediator()
    member_a = _MembershipConduitStub(conduit_id="m-a", spellbook=_make_spellbook(), mediator=mediator)
    leaver = _MembershipConduitStub(conduit_id="l-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((member_a, leaver))
    cluster.members.update({"m-a", "l-1"})

    cluster.handle_leave(leaver)

    assert len(mediator.start_calls) == 1
    start = mediator.start_calls[0]
    assert start["transaction_type"] == ChangeTransactionType.CLUSTER_LEAVE
    assert start["metadata"]["conduit_ids"] == ("l-1", "m-a")


def test_handle_leave_commits_success_true_and_removes_member() -> None:
    """
    Purpose:
        Verify a clean handle_leave commits (success=True) and removes the leaver.
    Contract:
        - end_transaction is called once with CLUSTER_LEAVE and success=True.
        - The leaver id is absent from cluster membership afterward.
    Returns:
        None.
    Raises:
        AssertionError: If commit/membership state is wrong.
    """
    mediator = _RecordingMediator()
    member_a = _MembershipConduitStub(conduit_id="m-a", spellbook=_make_spellbook(), mediator=mediator)
    leaver = _MembershipConduitStub(conduit_id="l-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((member_a, leaver))
    cluster.members.update({"m-a", "l-1"})

    cluster.handle_leave(leaver)

    assert mediator.end_calls == [
        {"expected_type": ChangeTransactionType.CLUSTER_LEAVE, "success": True}
    ]
    assert "l-1" not in cluster.get_members()


def test_handle_leave_drops_leaver_shared_spells_entry() -> None:
    """
    Purpose:
        Verify handle_leave drops the leaver's shared-root registry entry.
    Contract:
        - After leave, the leaver has no entry in the shared-spells registry.
    Returns:
        None.
    Raises:
        AssertionError: If the leaver's shared entry survives the leave.
    """
    mediator = _RecordingMediator()
    leaver = _MembershipConduitStub(conduit_id="l-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((leaver,))
    cluster.members.add("l-1")
    cluster.add_shared_spell("l-1", 7)

    cluster.handle_leave(leaver)

    assert "l-1" not in cluster.get_shared_spells()


# ---------------------------------------------------------------------------
# In-window share / unshare transaction-free flag
# ---------------------------------------------------------------------------
def _seed_owner_with_cluster_spell() -> Tuple[_MembershipConduitStub, _MembershipConduitStub, ConduitCluster]:
    """Build owner (with a bound cluster spell + shared index), borrower, and cluster."""
    mediator = _RecordingMediator()
    owner_spellbook = _make_spellbook()
    spell_id = owner_spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _MembershipConduitStub(
        conduit_id="owner-1", spellbook=owner_spellbook, mediator=mediator, aetheric_frame="default",
    )
    borrower = _MembershipConduitStub(conduit_id="borrower-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((owner, borrower))
    cluster.add_shared_spell("owner-1", _spell_index_for(owner_spellbook, spell_id))
    return owner, borrower, cluster


def test_share_to_borrower_open_transaction_false_skips_inner_cluster_link() -> None:
    """
    Purpose:
        Verify the in-window share path runs the contract directly under the held
        CLUSTER_JOIN seal, opening NO nested cluster_link transaction.
    Contract:
        - With open_transaction=False the borrower's transaction() is never entered.
        - The share contract is still applied.
    Returns:
        None.
    Raises:
        AssertionError: If a nested transaction is opened or the share is skipped.
    """
    owner, borrower, cluster = _seed_owner_with_cluster_spell()

    cluster.share_to_borrower(owner, borrower, open_transaction=False)

    assert borrower.transaction_calls == []
    assert len(borrower.contract_calls) == 1


def test_share_to_borrower_open_transaction_true_opens_cluster_link() -> None:
    """
    Purpose:
        Verify the standalone share path still opens its own cluster_link transaction.
    Contract:
        - With open_transaction=True the borrower's transaction() is entered with
          CLUSTER_LINK, and the share contract is applied.
    Returns:
        None.
    Raises:
        AssertionError: If no cluster_link transaction is opened.
    """
    owner, borrower, cluster = _seed_owner_with_cluster_spell()

    cluster.share_to_borrower(owner, borrower, open_transaction=True)

    assert borrower.transaction_calls == [ChangeTransactionType.CLUSTER_LINK]
    assert len(borrower.contract_calls) == 1


def test_remove_shared_from_borrower_open_transaction_false_skips_inner_cluster_link() -> None:
    """
    Purpose:
        Verify the in-window unshare path runs the removal directly under the held
        CLUSTER_LEAVE seal, opening NO nested cluster_link transaction.
    Contract:
        - With open_transaction=False the borrower's transaction() is never entered.
        - The removal is still applied.
    Returns:
        None.
    Raises:
        AssertionError: If a nested transaction is opened or the removal is skipped.
    """
    owner, borrower, cluster = _seed_owner_with_cluster_spell()

    cluster.remove_shared_from_borrower(owner, borrower, "default", open_transaction=False)

    assert borrower.transaction_calls == []
    assert len(borrower.remove_root_calls) == 1


def test_remove_shared_from_borrower_default_opens_cluster_link() -> None:
    """
    Purpose:
        Verify the standalone unshare path still opens its own cluster_link transaction.
    Contract:
        - The default (open_transaction=True) enters transaction() with CLUSTER_LINK.
    Returns:
        None.
    Raises:
        AssertionError: If no cluster_link transaction is opened.
    """
    owner, borrower, cluster = _seed_owner_with_cluster_spell()

    cluster.remove_shared_from_borrower(owner, borrower, "default")

    assert borrower.transaction_calls == [ChangeTransactionType.CLUSTER_LINK]
    assert len(borrower.remove_root_calls) == 1


# ---------------------------------------------------------------------------
# Leader election wrap + re-election guard
# ---------------------------------------------------------------------------
def test_bind_elected_leader_refuses_when_a_leader_is_already_elected() -> None:
    """
    Purpose:
        Verify the re-election guard: binding a new leader while one is elected raises.
    Contract:
        - bind_elected_leader raises RuntimeError when master_conduit_id is set.
    Returns:
        None.
    Raises:
        AssertionError: If re-election is allowed.
    """
    cluster = _cluster_with(())
    cluster.master_conduit_id = "leader-existing"

    with pytest.raises(RuntimeError, match="already elected"):
        cluster.bind_elected_leader("leader-new")


def test_elect_leader_opens_elect_and_aborts_when_already_elected() -> None:
    """
    Purpose:
        Verify elect_leader opens an ELECT transaction and aborts (success=False) when
        the in-window bind hits the re-election guard, propagating the error.
    Contract:
        - start_transaction opens ELECT_CONDUIT_CLUSTER_LEADER.
        - The guard raises; end_transaction is called with success=False (fail-closed).
    Returns:
        None.
    Raises:
        AssertionError: If the transaction is not opened or not aborted.
    """
    mediator = _RecordingMediator()
    leader = _MembershipConduitStub(conduit_id="leader-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((leader,))
    cluster.master_conduit_id = "leader-existing"

    with pytest.raises(RuntimeError, match="already elected"):
        cluster.elect_leader("leader-1")

    assert mediator.start_calls[0]["transaction_type"] == (
        ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER
    )
    assert mediator.end_calls == [
        {"expected_type": ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER, "success": False}
    ]


def test_elect_leader_raises_when_leader_conduit_cannot_be_resolved() -> None:
    """
    Purpose:
        Verify elect_leader fails fast when the named leader is not resolvable.
    Contract:
        - An unresolved leader id raises RuntimeError before any transaction opens.
    Returns:
        None.
    Raises:
        AssertionError: If an unresolved leader is silently accepted.
    """
    cluster = _cluster_with(())

    with pytest.raises(RuntimeError):
        cluster.elect_leader("missing-leader")


# ---------------------------------------------------------------------------
# Fan-out under the seal (the core "subsumes cluster_link" invariant)
# ---------------------------------------------------------------------------
def _stub_with_cluster_spell(conduit_id: str, mediator: _RecordingMediator) -> _MembershipConduitStub:
    """Build a membership stub whose spellbook has one unique_per_conduit_cluster spell bound."""
    spellbook = _make_spellbook()
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    return _MembershipConduitStub(conduit_id=conduit_id, spellbook=spellbook, mediator=mediator)


def test_handle_join_fans_out_shares_in_both_directions_without_nested_transactions() -> None:
    """
    Purpose:
        Verify a join shares each member's cluster spell to the joiner and the joiner's
        to each member, all under the held CLUSTER_JOIN seal with NO nested cluster_link.
    Contract:
        - Both the joiner and the existing member receive a share contract.
        - Neither conduit opens its own cluster_link transaction.
    Returns:
        None.
    Raises:
        AssertionError: If a share is missing or a nested transaction is opened.
    """
    mediator = _RecordingMediator()
    member = _stub_with_cluster_spell("m-a", mediator)
    joiner = _stub_with_cluster_spell("j-1", mediator)
    cluster = _cluster_with((member, joiner))
    cluster.members.add("m-a")

    cluster.handle_join(joiner)

    assert len(member.contract_calls) == 1
    assert len(joiner.contract_calls) == 1
    assert member.transaction_calls == []
    assert joiner.transaction_calls == []


def test_handle_leave_tears_down_shares_in_both_directions_without_nested_transactions() -> None:
    """
    Purpose:
        Verify a leave removes the leaver's shared roots from the remaining member and
        the member's from the leaver, all under the held CLUSTER_LEAVE seal with NO
        nested cluster_link.
    Contract:
        - Both the leaver and the remaining member receive a removal call.
        - Neither conduit opens its own cluster_link transaction.
    Returns:
        None.
    Raises:
        AssertionError: If a teardown is missing or a nested transaction is opened.
    """
    mediator = _RecordingMediator()
    member = _stub_with_cluster_spell("m-a", mediator)
    leaver = _stub_with_cluster_spell("l-1", mediator)
    cluster = _cluster_with((member, leaver))
    cluster.members.update({"m-a", "l-1"})
    cluster.refresh_shareable_roots(member)
    cluster.refresh_shareable_roots(leaver)

    cluster.handle_leave(leaver)

    assert len(member.remove_root_calls) == 1
    assert len(leaver.remove_root_calls) == 1
    assert member.transaction_calls == []
    assert leaver.transaction_calls == []


def test_handle_join_is_leaderless_and_does_not_require_an_elected_leader() -> None:
    """
    Purpose:
        Verify membership + sharing work with no elected leader (Layer 1 is always on).
    Contract:
        - With master_conduit_id None, handle_join still commits CLUSTER_JOIN success.
    Returns:
        None.
    Raises:
        AssertionError: If a leaderless join fails to commit.
    """
    mediator = _RecordingMediator()
    joiner = _stub_with_cluster_spell("j-1", mediator)
    cluster = _cluster_with((joiner,))

    assert cluster.master_conduit_id is None
    cluster.handle_join(joiner)

    assert mediator.end_calls == [
        {"expected_type": ChangeTransactionType.CLUSTER_JOIN, "success": True}
    ]


def test_handle_leave_metadata_carries_cluster_id_and_origin_surface() -> None:
    """
    Purpose:
        Verify the CLUSTER_LEAVE metadata identifies the cluster and the call site.
    Contract:
        - metadata carries the cluster id and the handle_leave origin_surface marker.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostic metadata is missing.
    """
    mediator = _RecordingMediator()
    leaver = _MembershipConduitStub(conduit_id="l-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((leaver,))
    cluster.members.add("l-1")

    cluster.handle_leave(leaver)

    metadata = mediator.start_calls[0]["metadata"]
    assert metadata["cluster_id"] == cluster._id
    assert metadata["origin_surface"] == "conduit_cluster.handle_leave"


def test_handle_join_closes_the_same_transaction_type_it_opened() -> None:
    """
    Purpose:
        Verify the wrap closes CLUSTER_JOIN with the matching expected_type (the
        try/finally never crosses transaction types).
    Contract:
        - The opened transaction_type equals the closed expected_type.
    Returns:
        None.
    Raises:
        AssertionError: If the open/close types diverge.
    """
    mediator = _RecordingMediator()
    joiner = _MembershipConduitStub(conduit_id="j-1", spellbook=_make_spellbook(), mediator=mediator)
    cluster = _cluster_with((joiner,))

    cluster.handle_join(joiner)

    assert mediator.start_calls[0]["transaction_type"] == mediator.end_calls[0]["expected_type"]
