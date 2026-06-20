from typing import List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure each cluster membership-transaction integration test starts clean.
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


def _make_configuration(*, aether_frame: str) -> SpellbookConfiguration:
    """Build a dynamic spellbook configuration with a single scheduler worker."""
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _make_book(frame_name: str) -> Spellbook:
    """Build a Spellbook bound to one frame for integration tests."""
    return Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )


def _cluster_conduit(
    frame_name: str,
    *,
    name: str,
    existence: Existence = Existence.unique_per_conduit_cluster,
    spell: type = BasicService,
    binding_name: Optional[str] = None,
) -> Tuple[Spellbook, Conduit]:
    """
    Bind one spell at the given existence and conjure a root conduit.

    The spell_id is fingerprinted from the structural profile + binding_name +
    existence (NOT the spellbook), so multiple conduits in ONE frame must each bind
    a distinct binding_name to avoid a spell_id collision. The binding_name defaults
    to the (unique) conduit name.

    Returns the (spellbook, conduit) pair so the caller can clean both up.
    """
    book = _make_book(frame_name)
    book.bind(
        spell=spell,
        existence=existence,
        permissions="create",
        binding_name=binding_name or name,
    )
    conduit = book.conjure(name=name)
    return book, conduit


def _cleanup(books: List[Spellbook], conduits: List[Conduit]) -> None:
    """Tear down conduits then spellbooks (children before owners)."""
    for conduit in conduits:
        conduit.permanent_cleanup()
    for book in books:
        book.cleanup()


# ---------------------------------------------------------------------------
# CLUSTER_JOIN end-to-end (add_conduit_to_cluster drives handle_join)
# ---------------------------------------------------------------------------
def test_add_conduit_to_cluster_tracks_single_membership() -> None:
    """
    Purpose:
        Verify a CLUSTER_JOIN (via add_conduit_to_cluster) tracks the new member.
    Contract:
        - After add, the cluster lists the conduit and the conduit lists the cluster.
    Returns:
        None.
    Raises:
        AssertionError: If membership is not tracked.
    """
    aether = Aether()
    frame_name = "frame-join-single"
    book, conduit = _cluster_conduit(frame_name, name="root-a")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        assert set(cloud._get_cluster("cluster-a").get_members()) == {conduit.id}
        assert set(cloud.get_clusters_for_conduit(conduit.id)) == {"cluster-a"}
    finally:
        _cleanup([book], [conduit])


def test_add_two_conduits_tracks_both_members() -> None:
    """
    Purpose:
        Verify two CLUSTER_JOINs into one cluster track both members.
    Contract:
        - Both conduit ids appear in the cluster membership.
    Returns:
        None.
    Raises:
        AssertionError: If either member is missing.
    """
    aether = Aether()
    frame_name = "frame-join-two"
    book_a, conduit_a = _cluster_conduit(frame_name, name="root-a")
    book_b, conduit_b = _cluster_conduit(frame_name, name="root-b", spell=BasicConfig)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit_a, "cluster-a")
        cloud.add_conduit_to_cluster(conduit_b, "cluster-a")

        assert set(cloud._get_cluster("cluster-a").get_members()) == {conduit_a.id, conduit_b.id}
    finally:
        _cleanup([book_a, book_b], [conduit_a, conduit_b])


def test_add_three_conduits_tracks_all_members() -> None:
    """
    Purpose:
        Verify a third CLUSTER_JOIN extends the existing membership (link over all).
    Contract:
        - All three conduit ids appear in the membership.
    Returns:
        None.
    Raises:
        AssertionError: If any member is missing.
    """
    aether = Aether()
    frame_name = "frame-join-three"
    book_a, conduit_a = _cluster_conduit(frame_name, name="root-a")
    book_b, conduit_b = _cluster_conduit(frame_name, name="root-b", spell=BasicConfig)
    book_c, conduit_c = _cluster_conduit(frame_name, name="root-c")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        for conduit in (conduit_a, conduit_b, conduit_c):
            cloud.add_conduit_to_cluster(conduit, "cluster-a")

        assert set(cloud._get_cluster("cluster-a").get_members()) == {
            conduit_a.id, conduit_b.id, conduit_c.id,
        }
    finally:
        _cleanup([book_a, book_b, book_c], [conduit_a, conduit_b, conduit_c])


def test_join_registers_cluster_scoped_shared_root() -> None:
    """
    Purpose:
        Verify joining with a unique_per_conduit_cluster spell registers the conduit's
        shared root (the CLUSTER_JOIN sharing effect ran end-to-end without deadlock).
    Contract:
        - After join, the conduit's shareable root appears in the cluster registry.
    Returns:
        None.
    Raises:
        AssertionError: If the shared root is not registered.
    """
    aether = Aether()
    frame_name = "frame-join-share"
    book, conduit = _cluster_conduit(frame_name, name="root-a")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        cluster = cloud._get_cluster("cluster-a")
        assert cluster.get_shared_spells().get(conduit.id, set()) != set()
    finally:
        _cleanup([book], [conduit])


def test_non_cluster_spell_is_not_registered_as_shared_on_join() -> None:
    """
    Purpose:
        Verify a non-cluster (unique) spell is NOT registered as a shareable root.
    Contract:
        - After join, a unique-existence conduit has no shared-root entry.
    Returns:
        None.
    Raises:
        AssertionError: If a non-cluster spell leaks into the shared registry.
    """
    aether = Aether()
    frame_name = "frame-join-noshare"
    book, conduit = _cluster_conduit(frame_name, name="root-a", existence=Existence.unique)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        cluster = cloud._get_cluster("cluster-a")
        assert cluster.get_shared_spells().get(conduit.id, set()) == set()
    finally:
        _cleanup([book], [conduit])


def test_two_cluster_spell_conduits_each_register_a_shared_root() -> None:
    """
    Purpose:
        Verify two cluster-spell conduits both register shared roots after joining,
        proving the bidirectional CLUSTER_JOIN fan-out ran for both.
    Contract:
        - Each conduit has a non-empty shared-root entry.
    Returns:
        None.
    Raises:
        AssertionError: If either conduit's shared root is missing.
    """
    aether = Aether()
    frame_name = "frame-join-share-two"
    book_a, conduit_a = _cluster_conduit(frame_name, name="root-a")
    book_b, conduit_b = _cluster_conduit(frame_name, name="root-b")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit_a, "cluster-a")
        cloud.add_conduit_to_cluster(conduit_b, "cluster-a")

        cluster = cloud._get_cluster("cluster-a")
        shared = cluster.get_shared_spells()
        assert shared.get(conduit_a.id, set()) != set()
        assert shared.get(conduit_b.id, set()) != set()
    finally:
        _cleanup([book_a, book_b], [conduit_a, conduit_b])


def test_join_into_two_distinct_clusters_is_tracked_per_conduit() -> None:
    """
    Purpose:
        Verify cluster membership is tracked per conduit across two clusters.
    Contract:
        - conduit_a is in cluster-a; conduit_b is in cluster-b; neither bleeds over.
    Returns:
        None.
    Raises:
        AssertionError: If membership tracking crosses clusters.
    """
    aether = Aether()
    frame_name = "frame-join-two-clusters"
    book_a, conduit_a = _cluster_conduit(frame_name, name="root-a")
    book_b, conduit_b = _cluster_conduit(frame_name, name="root-b", spell=BasicConfig)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.create_cluster("cluster-b")
        cloud.add_conduit_to_cluster(conduit_a, "cluster-a")
        cloud.add_conduit_to_cluster(conduit_b, "cluster-b")

        assert set(cloud.get_clusters_for_conduit(conduit_a.id)) == {"cluster-a"}
        assert set(cloud.get_clusters_for_conduit(conduit_b.id)) == {"cluster-b"}
    finally:
        _cleanup([book_a, book_b], [conduit_a, conduit_b])


# ---------------------------------------------------------------------------
# CLUSTER_LEAVE end-to-end (remove_conduit_from_cluster drives handle_leave)
# ---------------------------------------------------------------------------
def test_remove_conduit_updates_membership() -> None:
    """
    Purpose:
        Verify a CLUSTER_LEAVE (via remove_conduit_from_cluster) drops the member.
    Contract:
        - After remove, the cluster no longer lists the conduit and its cluster set is empty.
    Returns:
        None.
    Raises:
        AssertionError: If the member is not removed.
    """
    aether = Aether()
    frame_name = "frame-leave-one"
    book_a, conduit_a = _cluster_conduit(frame_name, name="root-a")
    book_b, conduit_b = _cluster_conduit(frame_name, name="root-b", spell=BasicConfig)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit_a, "cluster-a")
        cloud.add_conduit_to_cluster(conduit_b, "cluster-a")

        cloud.remove_conduit_from_cluster(conduit_b, "cluster-a")

        assert set(cloud._get_cluster("cluster-a").get_members()) == {conduit_a.id}
        assert set(cloud.get_clusters_for_conduit(conduit_b.id)) == set()
    finally:
        _cleanup([book_a, book_b], [conduit_a, conduit_b])


def test_remove_last_conduit_empties_cluster() -> None:
    """
    Purpose:
        Verify removing the only member leaves the cluster empty.
    Contract:
        - After removing the lone member, membership is empty.
    Returns:
        None.
    Raises:
        AssertionError: If membership is not empty.
    """
    aether = Aether()
    frame_name = "frame-leave-last"
    book, conduit = _cluster_conduit(frame_name, name="root-a")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit, "cluster-a")
        cloud.remove_conduit_from_cluster(conduit, "cluster-a")

        assert set(cloud._get_cluster("cluster-a").get_members()) == set()
    finally:
        _cleanup([book], [conduit])


def test_remove_conduit_drops_its_shared_root_entry() -> None:
    """
    Purpose:
        Verify CLUSTER_LEAVE drops the leaver's shared-root registry entry.
    Contract:
        - After remove, the conduit has no shared-root entry in the cluster.
    Returns:
        None.
    Raises:
        AssertionError: If the leaver's shared entry survives.
    """
    aether = Aether()
    frame_name = "frame-leave-share"
    book_a, conduit_a = _cluster_conduit(frame_name, name="root-a")
    book_b, conduit_b = _cluster_conduit(frame_name, name="root-b")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit_a, "cluster-a")
        cloud.add_conduit_to_cluster(conduit_b, "cluster-a")

        cloud.remove_conduit_from_cluster(conduit_b, "cluster-a")

        cluster = cloud._get_cluster("cluster-a")
        assert conduit_b.id not in cluster.get_shared_spells()
    finally:
        _cleanup([book_a, book_b], [conduit_a, conduit_b])


def test_add_remove_readd_tracks_membership_each_time() -> None:
    """
    Purpose:
        Verify repeated join/leave/join cycles track membership correctly each time.
    Contract:
        - After add the member is present; after remove absent; after re-add present.
    Returns:
        None.
    Raises:
        AssertionError: If any cycle step is mistracked.
    """
    aether = Aether()
    frame_name = "frame-cycle"
    book, conduit = _cluster_conduit(frame_name, name="root-a")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")

        cloud.add_conduit_to_cluster(conduit, "cluster-a")
        assert conduit.id in set(cloud._get_cluster("cluster-a").get_members())

        cloud.remove_conduit_from_cluster(conduit, "cluster-a")
        assert conduit.id not in set(cloud._get_cluster("cluster-a").get_members())

        cloud.add_conduit_to_cluster(conduit, "cluster-a")
        assert conduit.id in set(cloud._get_cluster("cluster-a").get_members())
    finally:
        _cleanup([book], [conduit])


def test_remove_one_of_three_keeps_the_rest() -> None:
    """
    Purpose:
        Verify removing one member of three leaves the remaining two intact.
    Contract:
        - After removing one, the other two remain members.
    Returns:
        None.
    Raises:
        AssertionError: If the remaining members are disturbed.
    """
    aether = Aether()
    frame_name = "frame-leave-of-three"
    book_a, conduit_a = _cluster_conduit(frame_name, name="root-a")
    book_b, conduit_b = _cluster_conduit(frame_name, name="root-b", spell=BasicConfig)
    book_c, conduit_c = _cluster_conduit(frame_name, name="root-c")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        for conduit in (conduit_a, conduit_b, conduit_c):
            cloud.add_conduit_to_cluster(conduit, "cluster-a")

        cloud.remove_conduit_from_cluster(conduit_b, "cluster-a")

        assert set(cloud._get_cluster("cluster-a").get_members()) == {conduit_a.id, conduit_c.id}
    finally:
        _cleanup([book_a, book_b, book_c], [conduit_a, conduit_b, conduit_c])


# ---------------------------------------------------------------------------
# Guards / edges
# ---------------------------------------------------------------------------
def test_remove_from_missing_cluster_raises() -> None:
    """
    Purpose:
        Verify removing from a non-existent cluster raises before any transaction.
    Contract:
        - A missing cluster name raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If a missing-cluster remove is silently accepted.
    """
    aether = Aether()
    frame_name = "frame-missing-remove"
    book, conduit = _cluster_conduit(frame_name, name="root-a")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        with pytest.raises(ValueError, match="does not exist"):
            cloud.remove_conduit_from_cluster(conduit=conduit, cluster_name="missing")
    finally:
        _cleanup([book], [conduit])


def test_get_missing_cluster_raises() -> None:
    """
    Purpose:
        Verify looking up a non-existent cluster raises.
    Contract:
        - A missing cluster name raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If a missing-cluster lookup is silently accepted.
    """
    aether = Aether()
    frame_name = "frame-missing-get"
    cloud = aether._ensure_frame(frame_name)._conduit_cloud
    with pytest.raises(ValueError, match="does not exist"):
        cloud._get_cluster("missing")


def test_clusters_for_unknown_conduit_is_empty() -> None:
    """
    Purpose:
        Verify an unknown conduit id maps to no clusters.
    Contract:
        - get_clusters_for_conduit returns an empty list for unknown ids.
    Returns:
        None.
    Raises:
        AssertionError: If a non-empty result is returned.
    """
    aether = Aether()
    frame_name = "frame-unknown-conduit"
    cloud = aether._ensure_frame(frame_name)._conduit_cloud
    assert cloud.get_clusters_for_conduit("unknown-id") == []


def test_join_then_membership_is_discoverable_both_directions() -> None:
    """
    Purpose:
        Verify membership is symmetric: the cluster lists the conduit and the conduit
        lists the cluster after a CLUSTER_JOIN.
    Contract:
        - cluster.get_members() contains the conduit id AND
          get_clusters_for_conduit(conduit.id) contains the cluster.
    Returns:
        None.
    Raises:
        AssertionError: If either direction is missing.
    """
    aether = Aether()
    frame_name = "frame-symmetric"
    book, conduit = _cluster_conduit(frame_name, name="root-a")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        assert conduit.id in set(cloud._get_cluster("cluster-a").get_members())
        assert "cluster-a" in set(cloud.get_clusters_for_conduit(conduit.id))
    finally:
        _cleanup([book], [conduit])


def test_conduit_cannot_join_a_second_cluster() -> None:
    """
    Purpose:
        Verify the single-cluster exclusivity blocker: a conduit already in one cluster
        cannot be added to another (cluster membership is one-per-conduit).
    Contract:
        - Adding an already-clustered conduit to a second cluster raises ValueError.
        - The conduit remains a member of only its original cluster.
    Returns:
        None.
    Raises:
        AssertionError: If a conduit is allowed into two clusters.
    """
    aether = Aether()
    frame_name = "frame-exclusive"
    book, conduit = _cluster_conduit(frame_name, name="root-a")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.create_cluster("cluster-b")
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        with pytest.raises(ValueError, match="exclusive"):
            cloud.add_conduit_to_cluster(conduit, "cluster-b")

        assert set(cloud.get_clusters_for_conduit(conduit.id)) == {"cluster-a"}
    finally:
        _cleanup([book], [conduit])
