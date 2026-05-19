from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.spellbook.configuration.system_state import SystemState


def test_frame_descriptor_payload_exposes_stable_public_fields() -> None:
    """
    Verify the payload stores the expected descriptor-facing frame metadata.

    Returns:
        None.
    """
    payload = FrameDescriptorPayload(
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=True,
        root_conduit_count=2,
        root_conduit_ids=("conduit-1", "conduit-2"),
        named_root_conduits=(("conduit-1", "root_1"), ("conduit-2", "root_2")),
        conduit_cloud_entry_count=1,
        conduit_cloud_names=("root_1",),
        cluster_count=1,
        cluster_names=("cluster-1",),
    )

    assert payload.payload_version == "0.0.1"
    assert payload.system_state is SystemState.dynamic
    assert payload.ai_native_enabled is True
    assert payload.rift_enabled is True
    assert payload.root_conduit_count == 2
    assert payload.root_conduit_ids == ("conduit-1", "conduit-2")
    assert payload.named_root_conduits == (
        ("conduit-1", "root_1"),
        ("conduit-2", "root_2"),
    )
    assert payload.conduit_cloud_entry_count == 1
    assert payload.conduit_cloud_names == ("root_1",)
    assert payload.cluster_count == 1
    assert payload.cluster_names == ("cluster-1",)


def test_frame_descriptor_payload_rejects_empty_payload_version() -> None:
    """
    Verify payload-version validation fails fast for an empty version string.

    Returns:
        None.
    """
    try:
        FrameDescriptorPayload(
            system_state=SystemState.dynamic,
            ai_native_enabled=True,
            rift_enabled=True,
            root_conduit_count=0,
            root_conduit_ids=tuple(),
            named_root_conduits=tuple(),
            conduit_cloud_entry_count=0,
            conduit_cloud_names=tuple(),
            cluster_count=0,
            cluster_names=tuple(),
            payload_version="",
        )
        raise AssertionError("Expected empty payload_version to fail.")
    except ValueError as exc:
        assert "payload_version cannot be empty" in str(exc)


def test_frame_descriptor_payload_cleanup_is_idempotent() -> None:
    """
    Verify cleanup clears the payload and can be called repeatedly.

    Returns:
        None.
    """
    payload = FrameDescriptorPayload(
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

    payload.cleanup()
    payload.cleanup()

    assert payload.cleaned is True
