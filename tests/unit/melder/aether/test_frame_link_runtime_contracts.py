import threading

from melder.aether.nexus.rift.frame_link.frame_link import FrameLink


def test_frame_link_defaults_display_name_to_source_id() -> None:
    """
    Verify frame links default the display name to the source id.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="spell",
        source_id="spell-1",
    )

    assert link.display_name == "spell-1"
    assert link.link_id == "ops:spell:spell-1"
    assert link.frame_name == "ops"
    assert link.source_kind == "spell"
    assert link.source_id == "spell-1"


def test_frame_link_preserves_explicit_display_name_and_metadata_copy() -> None:
    """
    Verify frame links preserve explicit display names and detach metadata input.

    Returns:
        None.
    """
    metadata = {"source": "compiled"}
    link = FrameLink(
        frame_name="ops",
        source_kind="conduit",
        source_id="conduit-1",
        display_name="default",
        metadata=metadata,
    )
    metadata["mutated"] = True

    assert link.display_name == "default"
    assert link.metadata == {"source": "compiled"}


def test_frame_link_from_view_subject_detaches_metadata_input() -> None:
    """
    Verify view-subject construction detaches metadata input.

    Returns:
        None.
    """
    metadata = {"payload_fields": ("system_state",)}
    link = FrameLink.from_view_subject(
        frame_name="ops",
        source_kind="frame",
        source_id="frame-1",
        display_name="ops",
        metadata=metadata,
    )
    metadata["mutated"] = True

    assert link.metadata == {"payload_fields": ("system_state",)}


def test_frame_link_cleanup_clears_owned_state() -> None:
    """
    Verify frame-link cleanup clears owned state.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="frame",
        source_id="ops",
    )

    link.cleanup()

    assert link.cleaned is True
    assert not hasattr(link, '_frame_name')
    assert not hasattr(link, '_source_kind')
    assert not hasattr(link, '_source_id')
    assert not hasattr(link, '_display_name')
    assert not hasattr(link, '_metadata')
    link.cleanup()


def test_frame_link_rejects_empty_identity_fields() -> None:
    """
    Verify frame links reject empty identity inputs.

    Returns:
        None.
    """
    try:
        FrameLink(frame_name="", source_kind="frame", source_id="ops-frame")
        raise AssertionError("Expected empty frame_name to fail.")
    except ValueError as exc:
        assert "frame_name cannot be empty" in str(exc)

    try:
        FrameLink(frame_name="ops", source_kind="", source_id="ops-frame")
        raise AssertionError("Expected empty source_kind to fail.")
    except ValueError as exc:
        assert "source_kind cannot be empty" in str(exc)

    try:
        FrameLink(frame_name="ops", source_kind="frame", source_id="")
        raise AssertionError("Expected empty source_id to fail.")
    except ValueError as exc:
        assert "source_id cannot be empty" in str(exc)


def test_frame_link_metadata_property_and_clone_detach_state() -> None:
    """
    Verify metadata snapshots and cloned links detach owned state.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="conduit",
        source_id="conduit-1",
        metadata={"policy": "default"},
    )

    metadata_snapshot = link.metadata
    cloned = link.clone()
    metadata_snapshot.clear()

    assert link.metadata == {"policy": "default"}
    assert cloned is not link
    assert cloned.link_id == link.link_id
    assert cloned.metadata == {"policy": "default"}


def test_frame_link_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _CoordinatedLock:
        def __init__(self, link: FrameLink) -> None:
            self._link = link
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
                self._link._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    link = FrameLink(
        frame_name="ops",
        source_kind="frame",
        source_id="ops",
    )
    link._lock = _CoordinatedLock(link)

    first = threading.Thread(target=link.cleanup)
    second = threading.Thread(target=link.cleanup)
    first.start()
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert link.cleaned is True
