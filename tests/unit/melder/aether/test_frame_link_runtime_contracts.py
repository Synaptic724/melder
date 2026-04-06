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
    assert link._frame_name is None
    assert link._source_kind is None
    assert link._source_id is None
    assert link._display_name is None
    assert link._metadata is None
