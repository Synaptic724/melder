from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.spellbook.configuration.system_state import SystemState


def _build_payload() -> FrameDescriptorPayload:
    """
    Build one descriptor-safe frame payload for record tests.

    Returns:
        FrameDescriptorPayload: Fresh payload object.
    """
    return FrameDescriptorPayload(
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=True,
        root_conduit_count=1,
        root_conduit_ids=("conduit-1",),
        named_root_conduits=(("conduit-1", "root_1"),),
        conduit_cloud_entry_count=1,
        conduit_cloud_names=("root_1",),
        cluster_count=0,
        cluster_names=tuple(),
    )


def test_frame_record_exposes_stable_public_fields() -> None:
    """
    Verify the record stores the expected publication metadata and payload.

    Returns:
        None.
    """
    payload = _build_payload()
    record = FrameRecord(
        frame_name="ops",
        frame_id="frame-1",
        config_origin_spellbook_id="spellbook-1",
        payload=payload,
    )

    assert record.nexus_label == "default"
    assert record.nexus_version == "0.0.1"
    assert record.frame_name == "ops"
    assert record.frame_id == "frame-1"
    assert record.config_origin_spellbook_id == "spellbook-1"
    assert record.payload is payload


def test_frame_record_rejects_invalid_constructor_inputs() -> None:
    """
    Verify constructor validation rejects missing labels, versions, and payloads.

    Returns:
        None.
    """
    try:
        FrameRecord(
            nexus_label="",
            frame_name="ops",
            frame_id="frame-1",
            config_origin_spellbook_id=None,
            payload=_build_payload(),
        )
        raise AssertionError("Expected empty nexus_label to fail.")
    except ValueError as exc:
        assert "nexus_label cannot be empty" in str(exc)

    try:
        FrameRecord(
            nexus_version="",
            frame_name="ops",
            frame_id="frame-1",
            config_origin_spellbook_id=None,
            payload=_build_payload(),
        )
        raise AssertionError("Expected empty nexus_version to fail.")
    except ValueError as exc:
        assert "nexus_version cannot be empty" in str(exc)

    try:
        FrameRecord(
            frame_name="ops",
            frame_id="frame-1",
            config_origin_spellbook_id=None,
            payload=None,
        )
        raise AssertionError("Expected missing payload to fail.")
    except ValueError as exc:
        assert "payload cannot be None" in str(exc)

    try:
        FrameRecord(
            frame_name="ops",
            frame_id="frame-1",
            config_origin_spellbook_id=None,
            payload=object(),
        )
        raise AssertionError("Expected invalid payload type to fail.")
    except TypeError as exc:
        assert "payload must satisfy IFrameDescriptorPayload" in str(exc)


def test_frame_record_cleanup_is_idempotent_and_cleans_owned_payload() -> None:
    """
    Verify cleanup clears the record and cascades into the owned payload.

    Returns:
        None.
    """
    payload = _build_payload()
    record = FrameRecord(
        frame_name="ops",
        frame_id="frame-1",
        config_origin_spellbook_id="spellbook-1",
        payload=payload,
    )

    record.cleanup()
    record.cleanup()

    assert record.cleaned is True
    assert payload.cleaned is True
