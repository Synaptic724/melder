from melder.aether.nexus.configuration.rift_creation_mode import RiftCreationMode


def test_rift_creation_mode_members_are_stable() -> None:
    """
    Verify the public RiftCreationMode enum exposes the expected member order.
    """
    members = list(RiftCreationMode)

    assert members == [
        RiftCreationMode.open,
        RiftCreationMode.token_required,
        RiftCreationMode.prebuilt_only,
    ]


def test_rift_creation_mode_values_are_stable_strings() -> None:
    """
    Verify each RiftCreationMode member keeps its expected wire value.
    """
    assert [member.value for member in RiftCreationMode] == [
        "open",
        "token_required",
        "prebuilt_only",
    ]


def test_rift_creation_mode_internal_sentinel_is_not_public_member() -> None:
    """
    Verify the internal registration sentinel is not exposed as an enum member.
    """
    assert "__melder_internal__" not in RiftCreationMode.__members__
