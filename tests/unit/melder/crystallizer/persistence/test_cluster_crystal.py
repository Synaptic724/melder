"""
Unit contract tests for ClusterCrystal: the record's cluster map
(dispatch, replace-on-emit, eviction + tombstone capture, frame sweep).
"""
import pytest

from melder.crystallizer.crystals.cluster_crystal import ClusterCrystal
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile


def _cluster(cluster_id="cl-1", name="workers", frame="frame-a",
             members=("conduit-a",), leader=None, shared=None):
    """Build one cluster twin."""
    return ClusterCrystal(
        cluster_id=cluster_id,
        cluster_name=name,
        frame_name=frame,
        member_conduit_ids=list(members),
        leader_conduit_id=leader,
        shared_spells=list(shared or []),
    )


def test_dispatch_describe_and_detachment():
    """
    Purpose:
        Verify record() routes cluster twins and describe() detaches.
    Contract:
        The twin lands in its level map (cluster_count), journals kind
        "cluster", and mutating described lists never touches the twin.
    Returns:
        None.
    Raises:
        AssertionError: If dispatch or detachment drifts.
    """
    profile = PersistenceProfile("p")
    twin = _cluster(members=("conduit-a", "conduit-b"), leader="conduit-a",
                    shared=[{"owner_conduit_id": "conduit-a", "index_id": "idx-1"}])
    profile.record(twin)
    assert profile.describe()["cluster_count"] == 1
    described = twin.describe()
    described["member_conduit_ids"].append("conduit-x")
    described["shared_spells"].clear()
    fresh = twin.describe()
    assert fresh["member_conduit_ids"] == ["conduit-a", "conduit-b"]
    assert fresh["leader_conduit_id"] == "conduit-a"
    assert fresh["shared_spells"] == [
        {"owner_conduit_id": "conduit-a", "index_id": "idx-1"}
    ]
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert entries == [(1, "cluster", "cl-1")]


def test_replace_on_emit_and_removal_tombstone():
    """
    Purpose:
        Verify snapshot replacement and eviction semantics.
    Contract:
        Re-emitting a cluster_id displaces + cleans the old snapshot;
        remove_cluster_crystal evicts + journals the tombstone and
        tolerates unrecorded ids.
    Returns:
        None.
    Raises:
        AssertionError: If replacement or eviction drifts.
    """
    profile = PersistenceProfile("p")
    first = _cluster()
    profile.record(first)
    profile.record(_cluster(members=("conduit-a", "conduit-b")))
    assert first.cleaned is True
    assert profile.describe()["cluster_count"] == 1
    profile.remove_cluster_crystal("cl-1")
    profile.remove_cluster_crystal("ghost-cl")
    assert profile.describe()["cluster_count"] == 0
    payloads, _entries, _rng = profile.capture_segment_since(0)
    assert payloads["cluster_removed"]["cl-1"] == {
        "cluster_id": "cl-1", "removed": True,
    }
    assert payloads["cluster_removed"]["ghost-cl"] == {
        "cluster_id": "ghost-cl", "removed": True,
    }


def test_frame_sweep_takes_the_frames_clusters():
    """
    Purpose:
        Verify frame death sweeps its clusters.
    Contract:
        remove_frame_crystal evicts cluster twins whose frame_name
        matches; a sibling frame's cluster survives.
    Returns:
        None.
    Raises:
        AssertionError: If the sweep misses or over-reaches.
    """
    profile = PersistenceProfile("p")
    doomed = _cluster(cluster_id="cl-1", frame="frame-a")
    survivor = _cluster(cluster_id="cl-2", frame="frame-b")
    profile.record(doomed)
    profile.record(survivor)
    profile.remove_frame_crystal("frame-a")
    assert doomed.cleaned is True
    assert survivor.cleaned is False
    assert profile.describe()["cluster_count"] == 1
