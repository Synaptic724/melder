from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode


def test_nexus_frame_mode_members_are_stable() -> None:
    """
    Verify the public NexusFrameMode enum exposes the expected member order.
    """
    members = list(NexusFrameMode)

    assert members == [
        NexusFrameMode.single,
        NexusFrameMode.indexed,
        NexusFrameMode.one_per_workspace,
    ]


def test_nexus_frame_mode_values_are_stable_strings() -> None:
    """
    Verify each NexusFrameMode member keeps its expected wire value.
    """
    assert [member.value for member in NexusFrameMode] == [
        "single",
        "indexed",
        "one_per_workspace",
    ]


def test_nexus_frame_mode_internal_sentinel_is_not_public_member() -> None:
    """
    Verify the internal registration sentinel is not exposed as an enum member.
    """
    assert "__melder_internal__" not in NexusFrameMode.__members__
