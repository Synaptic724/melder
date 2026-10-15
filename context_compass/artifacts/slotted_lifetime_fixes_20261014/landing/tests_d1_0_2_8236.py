"""D1 tests (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, notch 0.2.8236).

Updates the two cloud unit tests that pinned the old leave order and the member-set scan, and adds unit tests for the
ordered exit, the effect-only drop and the index lookup, plus an integration test for the teardown fallback.
Run from a tree root: python <this file> [<tree root>]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
CLOUD_UNIT = str(ROOT / "tests/unit/melder/aether/test_conduit_cloud.py")
CLUSTER_UNIT = str(ROOT / "tests/unit/melder/aether/conduit/test_conduit_cluster.py")
LIFETIME = str(ROOT / "tests/integration/melder/conduit/test_conduit_integration_cluster_member_lifetime.py")

cloud_edits = [
    (
        '''def test_remove_conduit_from_cluster_delegates_to_cluster(conduit_cloud, mock_conduit) -> None:
    """
    Verify remove_conduit_from_cluster delegates membership removal and leave handling.
    """
    cloud, _, _ = conduit_cloud
    cluster = MagicMock()
    cloud._conduit_clusters["cluster-1"] = cluster

    cloud.remove_conduit_from_cluster(mock_conduit, "cluster-1")

    cluster.remove_member.assert_called_once_with("conduit-1")
    cluster.handle_leave.assert_called_once_with(mock_conduit)
''',
        '''def test_remove_conduit_from_cluster_delegates_to_cluster(conduit_cloud, mock_conduit) -> None:
    """
    Verify remove_conduit_from_cluster runs the cluster's ordered exit.

    Updated with 0.2.8236: the cloud used to call `remove_member` and then `handle_leave`, which popped the leaver's
    share record before the leave read it, so the leaver's roots stayed contracted to every peer. The cloud now hands
    the whole exit to `ConduitCluster.release_member` (leave first, membership record after) and calls neither step
    itself.
    """
    cloud, _, _ = conduit_cloud
    cluster = MagicMock()
    cloud._conduit_clusters["cluster-1"] = cluster

    cloud.remove_conduit_from_cluster(mock_conduit, "cluster-1")

    cluster.release_member.assert_called_once_with(mock_conduit)
    cluster.remove_member.assert_not_called()
    cluster.handle_leave.assert_not_called()
''',
    ),
    (
        '''    """
    Verify refresh_cluster_shares_for_conduit calls refresh only on matching clusters.
    """
    cloud, _, _ = conduit_cloud
    matching_cluster = MagicMock()
    matching_cluster.get_members.return_value = {"conduit-1"}
    other_cluster = MagicMock()
    other_cluster.get_members.return_value = {"other"}
    cloud._conduit_clusters["cluster-1"] = matching_cluster
    cloud._conduit_clusters["cluster-2"] = other_cluster

    cloud.refresh_cluster_shares_for_conduit(mock_conduit)
''',
        '''    """
    Verify refresh_cluster_shares_for_conduit calls refresh only on matching clusters.

    Updated with 0.2.8236: membership is read from the frame's DevOps conduit->cluster index (the cloud names a cluster
    by its id), not from each cluster's member set, so the doubles are registered in the index instead of answering
    `get_members`.
    """
    cloud, _, _ = conduit_cloud
    matching_cluster = MagicMock()
    other_cluster = MagicMock()
    cloud._conduit_clusters["cluster-1"] = matching_cluster
    cloud._conduit_clusters["cluster-2"] = other_cluster
    cloud._cluster_names_by_id["cluster-id-1"] = "cluster-1"
    cloud._cluster_names_by_id["cluster-id-2"] = "cluster-2"
    registry.register_cluster_membership(cluster_id="cluster-id-1", conduit_id="conduit-1")
    registry.register_cluster_membership(cluster_id="cluster-id-2", conduit_id="other")

    cloud.refresh_cluster_shares_for_conduit(mock_conduit)
''',
    ),
    (
        '''def test_refresh_cluster_shares_for_conduit_only_hits_matching_clusters(
        conduit_cloud,
        mock_conduit,
) -> None:
''',
        '''def test_refresh_cluster_shares_for_conduit_only_hits_matching_clusters(
        conduit_cloud,
        mock_conduit,
        registry,
) -> None:
''',
    ),
    (
        '''def test_get_clusters_for_conduit_returns_empty_when_missing(conduit_cloud) -> None:
    """
    Verify get_clusters_for_conduit returns an empty list for unknown conduits.
    """
    cloud, _, _ = conduit_cloud

    assert cloud.get_clusters_for_conduit("missing") == []
''',
        '''def test_get_clusters_for_conduit_returns_empty_when_missing(conduit_cloud) -> None:
    """
    Verify get_clusters_for_conduit returns an empty list for unknown conduits.
    """
    cloud, _, _ = conduit_cloud

    assert cloud.get_clusters_for_conduit("missing") == []


def test_get_clusters_for_conduit_answers_from_the_membership_index(conduit_cloud, registry) -> None:
    """
    get_clusters_for_conduit names clusters from the frame's DevOps conduit->cluster index (0.2.8236).

    The index edge alone decides the answer - no member set is walked, so an edge for a conduit the cluster's member
    set lacks still names the cluster - and an edge naming a cluster this cloud does not map (deleted, or another
    cloud's) names nothing.
    """
    cloud, _, _ = conduit_cloud
    cloud.create_cluster("cluster-1")
    cluster = cloud.get_cluster("cluster-1")
    registry.register_cluster_membership(cluster_id=cluster.id, conduit_id="conduit-7")
    registry.register_cluster_membership(cluster_id="unmapped-cluster", conduit_id="conduit-8")

    assert cloud.get_clusters_for_conduit("conduit-7") == ["cluster-1"]
    assert "conduit-7" not in cluster.get_members()
    assert cloud.get_clusters_for_conduit("conduit-8") == []


def test_delete_cluster_forgets_the_cluster_for_membership_lookups(conduit_cloud, mock_conduit) -> None:
    """
    A deleted cluster is named for no conduit, and its name is free for a new cluster that holds nobody.
    """
    cloud, _, _ = conduit_cloud
    cloud.create_cluster("cluster-1")
    cloud.add_conduit_to_cluster(mock_conduit, "cluster-1")
    assert cloud.get_clusters_for_conduit("conduit-1") == ["cluster-1"]

    cloud.delete_cluster("cluster-1")
    assert cloud.get_clusters_for_conduit("conduit-1") == []

    cloud.create_cluster("cluster-1")
    assert cloud.get_clusters_for_conduit("conduit-1") == []
''',
    ),
]

cluster_edits = [
    (
        '''    """unbind_member drops a still-bound facade even after the cluster dissolved.

    Mirrors the leader-leave path: `unelect_leader` already cleared
    master_conduit_id and the cloud removed the leader from `members`, so the
    departed leader's own facade must still be dropped unconditionally.
    """
''',
        '''    """unbind_member drops a still-bound facade even after the cluster dissolved.

    Mirrors a late or repeated exit: the cluster was already unelected
    (master_conduit_id cleared), and the departed member's own facade must still
    be dropped unconditionally.
    """
''',
    ),
    (
        '''def test_unbind_member_raises_after_cleanup() -> None:
    """unbind_member is guarded by check_cleaned after the cluster is cleaned."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.cleanup()

    with pytest.raises(RuntimeError):
        cluster.unbind_member(leaver)
''',
        '''def test_unbind_member_raises_after_cleanup() -> None:
    """unbind_member is guarded by check_cleaned after the cluster is cleaned."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.cleanup()

    with pytest.raises(RuntimeError):
        cluster.unbind_member(leaver)


# ----------------------------------------------------------------------
# Ordered exit (release_member) and the effect-only drop (drop_member), 0.2.8236
# ----------------------------------------------------------------------
def test_release_member_leaves_while_the_share_record_exists_then_drops_the_membership(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """release_member runs handle_leave first, while the leaver's share record exists, then remove_member.

    Regression (0.2.8236): the cloud removed the membership first, which popped the share record the leave's unshare
    reads, so the leaver's roots stayed contracted to every remaining member.
    """
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.add_member(leaver._id)
    cluster.add_shared_spell(leaver._id, SpellIndex("spell-1"))
    seen: list[tuple[str, bool]] = []

    def record_leave(self: ConduitCluster, conduit: Any) -> None:
        seen.append((conduit._id, conduit._id in self.shared_spells))

    monkeypatch.setattr(ConduitCluster, "handle_leave", record_leave)

    cluster.release_member(leaver)

    assert seen == [("leaver", True)]
    assert leaver._id not in cluster.get_members()
    assert leaver._id not in cluster.get_shared_spells()
    assert cluster._devops_information_registry.get_clusters_for_conduit(leaver._id) == ()


def test_drop_member_of_the_elected_leader_leaves_the_cluster_inert() -> None:
    """Dropping the elected leader unbinds every member facade, clears the leader and removes its membership."""
    leader = _FacadeConduit("leader")
    member = _FacadeConduit("member")
    cluster = _make_facade_cluster(leader, member)
    cluster.add_member(leader._id)
    cluster.add_member(member._id)
    cluster.bind_elected_leader(leader._id)

    cluster.drop_member(leader)

    assert cluster.master_conduit_id is None
    assert cluster.get_members() == {member._id}
    assert leader._cluster_creations.is_active() is False
    assert member._cluster_creations.is_active() is False
    assert cluster._devops_information_registry.get_clusters_for_conduit(leader._id) == ()


def test_drop_member_of_a_member_keeps_the_leader_elected() -> None:
    """Dropping a non-leader removes only that member and its facade; the leader stays elected."""
    leader = _FacadeConduit("leader")
    member = _FacadeConduit("member")
    cluster = _make_facade_cluster(leader, member)
    cluster.add_member(leader._id)
    cluster.add_member(member._id)
    cluster.bind_elected_leader(leader._id)

    cluster.drop_member(member)

    assert cluster.master_conduit_id == leader._id
    assert cluster.get_members() == {leader._id}
    assert leader._cluster_creations.is_active() is True
    assert member._cluster_creations.is_active() is False


def test_drop_member_is_idempotent_for_a_conduit_that_is_not_a_member() -> None:
    """drop_member of a non-member, or a second drop, changes nothing and does not raise."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.add_member(leaver._id)

    cluster.drop_member(leaver)
    cluster.drop_member(leaver)

    assert cluster.get_members() == set()
    assert leaver._cluster_creations.is_active() is False


def test_drop_member_raises_after_cleanup() -> None:
    """drop_member is guarded by check_cleaned after the cluster is cleaned."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.cleanup()

    with pytest.raises(RuntimeError):
        cluster.drop_member(leaver)
''',
    ),
]

lifetime_edits = [
    (
        '''def test_member_teardown_leaves_the_cluster_deletable() -> None:
''',
        '''def test_a_failed_leave_at_teardown_still_drops_the_root_from_the_cluster(monkeypatch: pytest.MonkeyPatch) -> None:
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
''',
    ),
]

print("cloud unit", edit_tool.apply(CLOUD_UNIT, cloud_edits))
print("cluster unit", edit_tool.apply(CLUSTER_UNIT, cluster_edits))
print("lifetime", edit_tool.apply(LIFETIME, lifetime_edits))
