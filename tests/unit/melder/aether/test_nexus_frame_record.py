import threading
import types

from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.aether.nexus.nexus_frame_record import NexusFrameRecord


def _build_record(*, owner_rift_id: str | None = "rift-1") -> NexusFrameRecord:
    """
    Build one Nexus frame record with a lightweight frame stub.

    Returns:
        NexusFrameRecord: Fresh record for unit tests.
    """
    return NexusFrameRecord(
        frame_name="ops",
        frame=types.SimpleNamespace(name="ops"),
        nexus_frame_mode=NexusFrameMode.single,
        creator_rift_id="rift-1",
        owner_rift_id=owner_rift_id,
        immutable=False,
    )


def test_nexus_frame_record_exposes_identity_and_metadata() -> None:
    """
    Verify the record exposes its stable identity and metadata fields.

    Returns:
        None.
    """
    record = _build_record()

    assert record.id is not None
    assert record.frame_name == "ops"
    assert record.frame.name == "ops"
    assert record.nexus_frame_mode is NexusFrameMode.single
    assert record.creator_rift_id == "rift-1"
    assert record.owner_rift_id == "rift-1"
    assert record.immutable is False


def test_nexus_frame_record_attachment_snapshot_and_count_are_stable() -> None:
    """
    Verify attachment snapshots are detached and counts are deduplicated.

    Returns:
        None.
    """
    record = _build_record()

    record.attach_rift_id("rift-1")
    record.attach_rift_id("rift-1")
    record.attach_rift_id("rift-2")
    snapshot = record.attached_rift_ids
    snapshot.clear()

    assert record.attached_rift_ids == {"rift-1", "rift-2"}
    assert record.attached_rift_count == 2
    assert record.has_attached_rifts() is True


def test_nexus_frame_record_attach_can_promote_owner_when_owner_missing() -> None:
    """
    Verify the first attached Rift becomes owner when no owner is set.

    Returns:
        None.
    """
    record = _build_record(owner_rift_id=None)

    record.attach_rift_id("rift-2")

    assert record.owner_rift_id == "rift-2"


def test_nexus_frame_record_detach_transfers_owner_deterministically() -> None:
    """
    Verify owner transfer uses the sorted remaining attachment set.

    Returns:
        None.
    """
    record = _build_record(owner_rift_id="rift-2")
    record.attach_rift_id("rift-3")
    record.attach_rift_id("rift-1")
    record.attach_rift_id("rift-2")

    record.detach_rift_id("rift-2")

    assert record.owner_rift_id == "rift-1"
    assert record.attached_rift_ids == {"rift-1", "rift-3"}


def test_nexus_frame_record_detach_clears_owner_when_no_attachments_remain() -> None:
    """
    Verify owner becomes None when the last attached Rift detaches.

    Returns:
        None.
    """
    record = _build_record(owner_rift_id="rift-1")
    record.attach_rift_id("rift-1")

    record.detach_rift_id("rift-1")

    assert record.owner_rift_id is None
    assert record.attached_rift_ids == set()
    assert record.has_attached_rifts() is False


def test_nexus_frame_record_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    record = _build_record()
    record.attach_rift_id("rift-1")

    record.cleanup()
    record.cleanup()

    assert record.cleaned is True


def test_nexus_frame_record_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the record.

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    record = _build_record()
    record.attach_rift_id("rift-1")
    coordinated_lock = _CoordinatedLock()
    record._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        record.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert record.cleaned is True
    assert record._lock is None
