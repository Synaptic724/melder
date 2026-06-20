import threading
from typing import Callable, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure each concurrency test starts on a clean Aether singleton.
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


def _make_cluster_conduit(frame_name: str, *, name: str) -> Tuple[Spellbook, Conduit]:
    """
    Bind one unique_per_conduit_cluster spell (distinct via binding_name) + conjure.

    The binding_name is the unique conduit name so every conduit in the frame gets a
    distinct spell_id (the fingerprint includes binding_name, not the spellbook).
    """
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
        binding_name=name,
    )
    conduit = book.conjure(name=name)
    return book, conduit


def _build_conduits(frame_name: str, count: int) -> Tuple[List[Spellbook], List[Conduit]]:
    """Build `count` distinct cluster conduits in one frame; return parallel lists."""
    books: List[Spellbook] = []
    conduits: List[Conduit] = []
    for index in range(count):
        book, conduit = _make_cluster_conduit(frame_name, name=f"root-{index}")
        books.append(book)
        conduits.append(conduit)
    return books, conduits


def _cleanup(books: List[Spellbook], conduits: List[Conduit]) -> None:
    """Tear down conduits then spellbooks (children before owners)."""
    for conduit in conduits:
        conduit.permanent_cleanup()
    for book in books:
        book.cleanup()


def _run_in_parallel(workers: List[Callable[[], None]]) -> List[BaseException]:
    """
    Run each callable on its own thread, released together via a barrier.

    Purpose:
        Maximize contention (all workers cross the barrier at once) and collect any
        exception each worker raises, so the caller can assert on a clean run.
    Returns:
        List[BaseException]: Exceptions raised by workers (empty on a clean run).
    """
    barrier = threading.Barrier(len(workers))
    errors: List[BaseException] = []
    errors_lock = threading.Lock()

    def _wrapped(work: Callable[[], None]) -> None:
        try:
            barrier.wait()
            work()
        except BaseException as exc:  # test harness: record, then assert empty
            with errors_lock:
                errors.append(exc)

    threads = [threading.Thread(target=_wrapped, args=(work,)) for work in workers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return errors


# ---------------------------------------------------------------------------
# Concurrent CLUSTER_JOIN
# ---------------------------------------------------------------------------
def test_concurrent_joins_to_one_cluster_track_every_member() -> None:
    """
    Purpose:
        Verify N concurrent CLUSTER_JOINs into one cluster all succeed and every member
        is tracked (the cluster lock + transaction embargo serialize, never deadlock).
    Contract:
        - No worker raises.
        - Final membership equals the full set of joined conduit ids.
    Returns:
        None.
    Raises:
        AssertionError: If any join fails or a member is lost.
    """
    aether = Aether()
    frame_name = "frame-cc-join"
    books, conduits = _build_conduits(frame_name, 8)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")

        errors = _run_in_parallel(
            [lambda c=c: cloud.add_conduit_to_cluster(c, "cluster-a") for c in conduits]
        )

        assert errors == []
        assert set(cloud._get_cluster("cluster-a").get_members()) == {c.id for c in conduits}
    finally:
        _cleanup(books, conduits)


def test_concurrent_joins_register_all_shared_roots_without_deadlock() -> None:
    """
    Purpose:
        Verify concurrent joins of cluster-spell conduits all register their shared roots,
        proving the in-window (transaction-free) share fan-out holds under contention.
    Contract:
        - No worker raises (no embargo self-conflict / deadlock).
        - Every conduit has a non-empty shared-root entry afterward.
    Returns:
        None.
    Raises:
        AssertionError: If a share is missing or a worker deadlocks/raises.
    """
    aether = Aether()
    frame_name = "frame-cc-share"
    books, conduits = _build_conduits(frame_name, 6)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")

        errors = _run_in_parallel(
            [lambda c=c: cloud.add_conduit_to_cluster(c, "cluster-a") for c in conduits]
        )

        assert errors == []
        cluster = cloud._get_cluster("cluster-a")
        shared = cluster.get_shared_spells()
        for conduit in conduits:
            assert shared.get(conduit.id, set()) != set()
    finally:
        _cleanup(books, conduits)


def test_concurrent_joins_are_serialized_with_no_lost_members() -> None:
    """
    Purpose:
        Verify the membership mutation is atomic under contention: N concurrent joins
        produce exactly N members (no lost updates from racing members.add).
    Contract:
        - Final membership count equals the number of joiners.
    Returns:
        None.
    Raises:
        AssertionError: If members are lost to a race.
    """
    aether = Aether()
    frame_name = "frame-cc-serialize"
    books, conduits = _build_conduits(frame_name, 10)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")

        errors = _run_in_parallel(
            [lambda c=c: cloud.add_conduit_to_cluster(c, "cluster-a") for c in conduits]
        )

        assert errors == []
        assert len(set(cloud._get_cluster("cluster-a").get_members())) == len(conduits)
    finally:
        _cleanup(books, conduits)


# ---------------------------------------------------------------------------
# Concurrent CLUSTER_LEAVE
# ---------------------------------------------------------------------------
def test_concurrent_leaves_empty_the_cluster() -> None:
    """
    Purpose:
        Verify N concurrent CLUSTER_LEAVEs all succeed and empty the cluster.
    Contract:
        - No worker raises; final membership is empty.
    Returns:
        None.
    Raises:
        AssertionError: If a leave fails or a member lingers.
    """
    aether = Aether()
    frame_name = "frame-cc-leave"
    books, conduits = _build_conduits(frame_name, 8)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        for conduit in conduits:
            cloud.add_conduit_to_cluster(conduit, "cluster-a")

        errors = _run_in_parallel(
            [lambda c=c: cloud.remove_conduit_from_cluster(c, "cluster-a") for c in conduits]
        )

        assert errors == []
        assert set(cloud._get_cluster("cluster-a").get_members()) == set()
    finally:
        _cleanup(books, conduits)


def test_concurrent_mixed_join_and_leave_reach_consistent_state() -> None:
    """
    Purpose:
        Verify a mix of concurrent joins (new) and leaves (pre-existing members) reaches a
        consistent final membership.
    Contract:
        - No worker raises.
        - Final members are exactly the joiners (the leavers all departed).
    Returns:
        None.
    Raises:
        AssertionError: If the final membership is inconsistent.
    """
    aether = Aether()
    frame_name = "frame-cc-mixed"
    books, conduits = _build_conduits(frame_name, 8)
    stayers = conduits[:4]
    leavers = conduits[4:]
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        for conduit in leavers:
            cloud.add_conduit_to_cluster(conduit, "cluster-a")

        workers: List[Callable[[], None]] = []
        for conduit in stayers:
            workers.append(lambda c=conduit: cloud.add_conduit_to_cluster(c, "cluster-a"))
        for conduit in leavers:
            workers.append(lambda c=conduit: cloud.remove_conduit_from_cluster(c, "cluster-a"))
        errors = _run_in_parallel(workers)

        assert errors == []
        assert set(cloud._get_cluster("cluster-a").get_members()) == {c.id for c in stayers}
    finally:
        _cleanup(books, conduits)


def test_concurrent_adds_of_same_conduit_admit_exactly_one() -> None:
    """
    Purpose:
        Verify the single-cluster exclusivity invariant holds atomically under contention:
        when many threads race to add the SAME conduit, the conduit ends up a member exactly
        once and every losing thread is rejected with the exclusivity error (no double-add,
        no corruption, no unexpected error).
    Contract:
        - Final membership is exactly {conduit.id} (one membership, never two).
        - At least one racing add is rejected, and every rejection is the exclusivity
          ValueError ("exclusive (one per conduit)").
    Returns:
        None.
    Raises:
        AssertionError: If exclusivity is not enforced atomically under contention.
    """
    aether = Aether()
    frame_name = "frame-cc-same"
    book, conduit = _make_cluster_conduit(frame_name, name="root-0")
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")

        errors = _run_in_parallel(
            [lambda: cloud.add_conduit_to_cluster(conduit, "cluster-a") for _ in range(8)]
        )

        assert set(cloud._get_cluster("cluster-a").get_members()) == {conduit.id}
        assert len(errors) >= 1
        assert all(isinstance(exc, ValueError) for exc in errors)
        assert all("exclusive" in str(exc) for exc in errors)
    finally:
        _cleanup([book], [conduit])


# ---------------------------------------------------------------------------
# Concurrency across distinct clusters
# ---------------------------------------------------------------------------
def test_concurrent_joins_across_two_clusters_are_isolated() -> None:
    """
    Purpose:
        Verify concurrent joins into two distinct clusters do not cross-contaminate.
    Contract:
        - No worker raises.
        - Each cluster ends with exactly its assigned members.
    Returns:
        None.
    Raises:
        AssertionError: If membership crosses clusters.
    """
    aether = Aether()
    frame_name = "frame-cc-two-clusters"
    books, conduits = _build_conduits(frame_name, 8)
    group_a = conduits[:4]
    group_b = conduits[4:]
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")
        cloud.create_cluster("cluster-b")

        workers: List[Callable[[], None]] = []
        for conduit in group_a:
            workers.append(lambda c=conduit: cloud.add_conduit_to_cluster(c, "cluster-a"))
        for conduit in group_b:
            workers.append(lambda c=conduit: cloud.add_conduit_to_cluster(c, "cluster-b"))
        errors = _run_in_parallel(workers)

        assert errors == []
        assert set(cloud._get_cluster("cluster-a").get_members()) == {c.id for c in group_a}
        assert set(cloud._get_cluster("cluster-b").get_members()) == {c.id for c in group_b}
    finally:
        _cleanup(books, conduits)


def test_concurrent_reads_during_membership_churn_never_crash() -> None:
    """
    Purpose:
        Verify membership reads (get_members / get_clusters_for_conduit) are safe to run
        concurrently with joins (readers never see a torn structure and never crash).
    Contract:
        - No worker (reader or writer) raises.
        - All writers' members are present at the end.
    Returns:
        None.
    Raises:
        AssertionError: If a concurrent reader or writer raises.
    """
    aether = Aether()
    frame_name = "frame-cc-readers"
    books, conduits = _build_conduits(frame_name, 6)
    try:
        cloud = aether._ensure_frame(frame_name)._conduit_cloud
        cloud.create_cluster("cluster-a")

        def _reader() -> None:
            for _ in range(20):
                set(cloud._get_cluster("cluster-a").get_members())

        workers: List[Callable[[], None]] = [
            lambda c=c: cloud.add_conduit_to_cluster(c, "cluster-a") for c in conduits
        ]
        workers.extend(_reader for _ in range(3))
        errors = _run_in_parallel(workers)

        assert errors == []
        assert set(cloud._get_cluster("cluster-a").get_members()) == {c.id for c in conduits}
    finally:
        _cleanup(books, conduits)
