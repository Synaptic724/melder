"""
Regression tests: a cluster's membership and its `unique_per_conduit_cluster` instances follow the owner's rule.

EPIC-2026-10-14-slotted_lifetime_ownership_fixes, D1 and D2 (proven by the lifetime audit on 0.2.8235):
    D1 - A root's teardown never left its cluster: the dead root stayed in `members` (and as the elected leader), so
         unelect raised part-way, elect refused, and `delete_cluster` failed after removing the cluster from the
         cloud. An explicit leave dropped the leaver's share record before the unshare read it, so the leaver's
         roots stayed contracted to every remaining member.
    D2 - The cluster's instance lived in the elected leader conduit's own store: a leader change stranded it (a later
         election built a second one), the departed leader's teardown disposed it while members' holders still used
         it, and deleting the cluster disposed nothing.

Corrected behaviour asserted here: a root's teardown leaves its cluster (dissolving the team store first when it
leads), so the cluster stays electable and deletable; an explicit leave unshares the leaver's roots; the cluster owns
its team store, so its instance survives leader changes and is served again by the next leader, is purged only by
the elected leader, and is disposed exactly once - when the cluster is deleted or its frame is torn down, with a
failing disposal raised after the deletion finished.
"""

from collections.abc import Iterator
from typing import Any, List

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

pytestmark = pytest.mark.integration


class Leaf:
    """
    The cluster's `unique_per_conduit_cluster` instance.

    Contract:
        `close` is the disposal method declared at bind; `closes` counts how many times Melder ran it.
    """

    def __init__(self) -> None:
        """Start undisposed."""
        self.closes: int = 0

    def close(self) -> None:
        """Record one disposal."""
        self.closes += 1


class FailingLeaf(Leaf):
    """A cluster instance whose disposal method records the call and then raises."""

    def close(self) -> None:
        """Record one disposal, then fail."""
        super().close()
        raise RuntimeError("leaf close failed")


class Holder:
    """`unique_per_conduit` holder on a member root, over the cluster instance it reaches through the cluster."""

    def __init__(self, leaf: Any = SpellContract(spell=Leaf)) -> None:
        """Keep the cluster instance."""
        self.leaf = leaf


class ClusterWorld:
    """
    Three dynamic roots of one frame in one cluster named "team".

    Contract:
        `owner` binds the cluster spell (a `Leaf` class) and is linked to the other two; `leader` binds nothing;
        `member` binds `Holder` (`unique_per_conduit`); every root has joined the cluster and shared its roots. No
        leader is elected yet.
    """

    def __init__(self, frame: str, leaf_class: type = Leaf, with_holder: bool = True) -> None:
        """
        Build the world.

        Args:
            frame: Aetheric frame for the three roots.
            leaf_class: The cluster spell's class.
            with_holder: Whether `member` binds `Holder` (its contract names `Leaf`).
        """
        self.frame = frame
        owner_book = Spellbook(aetheric_frame=frame, configuration=_dynamic_configuration(frame))
        self.leaf_id: str = owner_book.bind(
            spell=leaf_class,
            existence=Existence.unique_per_conduit_cluster,
            permissions="create",
            disposal_method_names=["close"],
        )
        self.owner: Conduit = owner_book.conjure(dynamic=True, name=f"{frame}-owner")
        self.leader: Conduit = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name=f"{frame}-leader")
        member_book = Spellbook(aetheric_frame=frame)
        self.holder_id: str = ""
        if with_holder:
            self.holder_id = member_book.bind(spell=Holder, existence=Existence.unique_per_conduit, permissions="create")
        self.member: Conduit = member_book.conjure(dynamic=True, name=f"{frame}-member")
        self.owner.link(self.leader)
        self.owner.link(self.member)
        self.cloud: ConduitCloud = Spellbook._aether.get_conduit_cloud(frame)
        self.cloud.create_cluster("team")
        for root in (self.owner, self.leader, self.member):
            self.cloud.add_conduit_to_cluster(root, "team")
        for root in (self.owner, self.leader, self.member):
            self.cloud.refresh_cluster_shares_for_conduit(root)
        self.cluster: ConduitCluster = self.cloud.get_cluster("team")


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give each test a fresh Aether and reset it again afterwards."""
    _reset_aether()
    yield
    _reset_aether()


def _dynamic_configuration(frame: str) -> SpellbookConfiguration:
    """
    Return a dynamic configuration for one frame with one phase worker.

    Args:
        frame: The aetheric frame the configuration belongs to.

    Returns:
        SpellbookConfiguration: The configuration.
    """
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _leaf_errors(group: BaseException) -> List[BaseException]:
    """
    Return the non-group exceptions inside an exception group, depth first.

    Args:
        group: An exception, usually an ExceptionGroup.

    Returns:
        List[BaseException]: Every leaf exception (the argument itself when it is not a group).
    """
    if isinstance(group, BaseExceptionGroup):
        leaves: List[BaseException] = []
        for inner in group.exceptions:
            leaves.extend(_leaf_errors(inner))
        return leaves
    return [group]


def test_member_teardown_leaves_the_cluster_and_the_cluster_can_unelect_and_elect() -> None:
    """
    Tearing a non-leader member down must take it out of the cluster.

    Symptom (0.2.8235): the torn-down member stayed in `members`; `unelect_leader` raised AttributeError part-way and
    `elect_leader` then refused because the old leader was still recorded. Corrected: the member is gone from the
    cluster and from the cloud's lookup, and the cluster unelects and elects normally.
    """
    world = ClusterWorld("d1-member")
    world.cluster.elect_leader(world.leader.id)
    member_id = world.member.id
    world.member.cleanup()
    assert member_id not in world.cluster.get_members(), "a torn-down root must not stay a cluster member"
    assert world.cloud.get_clusters_for_conduit(member_id) == [], "the cloud must not report a torn-down member"
    world.cluster.unelect_leader()
    assert world.cluster.master_conduit_id is None
    world.cluster.elect_leader(world.owner.id)
    assert world.cluster.master_conduit_id == world.owner.id


def test_a_failed_leave_at_teardown_still_drops_the_root_from_the_cluster(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A root whose transactional exit fails during its teardown is still dropped from the cluster.

    The teardown logs the failed exit and falls back to the effect-only drop (`ConduitCluster.drop_member`), because
    the root is going away and cannot retry: the leader leaves `members`, the cluster is inert, and it can elect again.
    """
    world = ClusterWorld("d1-fallback")
    world.cluster.elect_leader(world.leader.id)

    def refuse_exit(self: ConduitCluster, conduit: Conduit) -> None:
        raise RuntimeError("cluster exit refused")

    monkeypatch.setattr(ConduitCluster, "release_member", refuse_exit)
    leader_id = world.leader.id
    world.leader.cleanup()
    monkeypatch.undo()
    assert leader_id not in world.cluster.get_members(), "a failed exit must still drop the torn-down root"
    assert world.cluster.master_conduit_id is None
    world.cluster.elect_leader(world.member.id)
    assert world.cluster.master_conduit_id == world.member.id


def test_member_teardown_leaves_the_cluster_deletable() -> None:
    """
    A cluster whose member was torn down must still delete cleanly.

    Symptom (0.2.8235): `delete_cluster` removed the cluster from the cloud, then its unelect raised on the dead
    member and the cluster was never cleaned. Corrected: deletion succeeds.
    """
    world = ClusterWorld("d1-delete")
    world.cluster.elect_leader(world.leader.id)
    world.member.cleanup()
    world.cloud.delete_cluster("team")
    assert not world.cloud.has_cluster_name("team")
    assert world.cluster.cleaned, "the deleted cluster must be cleaned"


def test_leader_teardown_leaves_the_cluster_inert_and_electable() -> None:
    """
    Tearing the elected leader down must dissolve the team store and take it out of the cluster.

    Symptom (0.2.8235): the cluster kept the dead root as `master_conduit_id` and as a member, so no other member
    could be elected. Corrected: the cluster is inert, the leader is gone, and another member can be elected.
    """
    world = ClusterWorld("d1-leader")
    world.cluster.elect_leader(world.leader.id)
    leader_id = world.leader.id
    world.leader.cleanup()
    assert world.cluster.master_conduit_id is None, "a torn-down leader must not stay elected"
    assert leader_id not in world.cluster.get_members(), "a torn-down leader must not stay a member"
    world.cluster.elect_leader(world.member.id)
    assert world.cluster.master_conduit_id == world.member.id


def test_explicit_leave_unshares_the_leavers_roots_from_every_member() -> None:
    """
    Leaving a cluster must remove the leaver's shared roots from the remaining members.

    Symptom (0.2.8235): `remove_conduit_from_cluster` dropped the leaver's share record before the leave read it, so
    every remaining member kept the leaver's roots in its contracts. Corrected: none does.
    """
    world = ClusterWorld("d1-leave", with_holder=False)
    assert world.member.get_spell_in_contracts(world.leaf_id) is not None, "precondition: the root is shared"
    assert world.leader.get_spell_in_contracts(world.leaf_id) is not None, "precondition: the root is shared"
    world.cloud.remove_conduit_from_cluster(world.owner, "team")
    assert world.owner.id not in world.cluster.get_members()
    assert world.member.get_spell_in_contracts(world.leaf_id) is None, "the leaver's root must be unshared"
    assert world.leader.get_spell_in_contracts(world.leaf_id) is None, "the leaver's root must be unshared"


def test_cluster_instance_survives_a_leader_change_and_is_served_by_the_next_leader() -> None:
    """
    The cluster, not its current leader, owns the cluster instance.

    Symptom (0.2.8235): after the leader left and a member was elected, the cluster built a second instance; the
    first stayed in the departed leader's store and that conduit's teardown disposed it while the member's holder
    still used it. Corrected: the next leader serves the same instance and the departed leader's teardown leaves
    it alone.
    """
    world = ClusterWorld("d2-change")
    world.cluster.elect_leader(world.leader.id)
    holder = world.member.meld(spell_id=world.holder_id)
    leaf = holder.leaf
    assert world.member.meld(spell_id=world.leaf_id) is leaf, "precondition: the holder holds the cluster instance"
    world.cloud.remove_conduit_from_cluster(world.leader, "team")
    world.cluster.elect_leader(world.member.id)
    assert world.member.meld(spell_id=world.leaf_id) is leaf, "a leader change must not build a second instance"
    world.leader.cleanup()
    assert leaf.closes == 0, "the departed leader's teardown disposed the cluster's instance"
    assert world.member.meld(spell_id=world.holder_id) is holder


def test_leader_teardown_keeps_the_cluster_instance_for_the_next_leader() -> None:
    """
    Tearing the elected leader down must not dispose the cluster's instance.

    Symptom (0.2.8235): the leader's own store held the instance, so its teardown disposed it while the member's
    holder kept it. Corrected: the instance stays open and the next leader serves it.
    """
    world = ClusterWorld("d2-teardown")
    world.cluster.elect_leader(world.leader.id)
    holder = world.member.meld(spell_id=world.holder_id)
    leaf = holder.leaf
    world.leader.cleanup()
    assert leaf.closes == 0, "the leader's teardown disposed the cluster's instance"
    world.cluster.elect_leader(world.member.id)
    assert world.member.meld(spell_id=world.leaf_id) is leaf


def test_delete_cluster_disposes_its_instance_once() -> None:
    """
    Deleting a cluster disposes the instances it owns, exactly once.

    Symptom (0.2.8235): deletion disposed nothing; the instance was disposed later, with the leader conduit.
    Corrected: deletion disposes it, and tearing the roots down afterwards does not dispose it again.
    """
    world = ClusterWorld("d2-delete", with_holder=False)
    world.cluster.elect_leader(world.leader.id)
    leaf = world.member.meld(spell_id=world.leaf_id)
    world.cloud.delete_cluster("team")
    assert leaf.closes == 1, "deleting the cluster must dispose its instance"
    for root in (world.member, world.leader, world.owner):
        root.cleanup()
    assert leaf.closes == 1, "the instance must be disposed exactly once"


def test_delete_cluster_raises_a_failing_disposal_after_the_deletion_finished() -> None:
    """
    A failing disposal method of a cluster instance is raised by `delete_cluster`, after the cluster is gone.
    """
    world = ClusterWorld("d2-delete-fails", leaf_class=FailingLeaf, with_holder=False)
    world.cluster.elect_leader(world.leader.id)
    leaf = world.member.meld(spell_id=world.leaf_id)
    with pytest.raises(ExceptionGroup) as raised:
        world.cloud.delete_cluster("team")
    assert not world.cloud.has_cluster_name("team"), "the cluster must be deleted before the failure is raised"
    assert world.cluster.cleaned
    assert leaf.closes == 1
    causes = [leaf_error.__cause__ for leaf_error in _leaf_errors(raised.value)]
    assert any(isinstance(cause, RuntimeError) and str(cause) == "leaf close failed" for cause in causes)


def test_frame_teardown_disposes_the_cluster_instance_once() -> None:
    """
    Control (green on 0.2.8235 too): tearing the whole frame down disposes the cluster's instance exactly once.
    """
    world = ClusterWorld("d2-frame", with_holder=False)
    world.cluster.elect_leader(world.leader.id)
    leaf = world.member.meld(spell_id=world.leaf_id)
    _reset_aether()
    assert leaf.closes == 1


def test_only_the_elected_leader_purges_the_cluster_instance() -> None:
    """
    Control (green on 0.2.8235 too): purge authority over a cluster instance stays with the elected leader.
    """
    world = ClusterWorld("d2-purge", with_holder=False)
    world.cluster.elect_leader(world.leader.id)
    leaf = world.member.meld(spell_id=world.leaf_id)
    with pytest.raises(RuntimeError, match="elected cluster leader"):
        world.member.purge(spell_id=world.leaf_id)
    assert leaf.closes == 0
    assert world.leader.purge(spell_id=world.leaf_id) == 1
    assert leaf.closes == 1
