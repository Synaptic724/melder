from melder.aether.nexus.rift.frame_link.frame_link import FrameLink


def test_frame_link_exposes_stable_public_fields() -> None:
    """
    Verify the link stores the expected stable identity and metadata.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="spell",
        source_id="ops-spellbook:spell-1",
        display_name="SpellOne",
        metadata={"payload_type": "general"},
    )

    assert link.link_id == "ops:spell:ops-spellbook:spell-1"
    assert link.frame_name == "ops"
    assert link.source_kind == "spell"
    assert link.source_id == "ops-spellbook:spell-1"
    assert link.display_name == "SpellOne"
    assert link.metadata == {"payload_type": "general"}


def test_frame_link_derives_display_name_and_detaches_metadata_snapshot() -> None:
    """
    Verify display name derivation and metadata snapshots are detached copies.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="frame",
        source_id="ops-frame",
        metadata={"visible": True},
    )

    metadata_snapshot = link.metadata
    metadata_snapshot.clear()

    assert link.display_name == "ops-frame"
    assert link.metadata == {"visible": True}


def test_frame_link_rejects_empty_identity_fields() -> None:
    """
    Verify constructor validation rejects empty required identity fields.

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


def test_frame_link_clone_and_cleanup_contracts() -> None:
    """
    Verify clone detaches state and cleanup is idempotent.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="conduit",
        source_id="ops-conduit-1",
        metadata={"policy": "default"},
    )

    cloned = link.clone()

    assert cloned is not link
    assert cloned.link_id == link.link_id
    assert cloned.metadata == {"policy": "default"}

    link.cleanup()
    link.cleanup()

    assert link.cleaned is True
