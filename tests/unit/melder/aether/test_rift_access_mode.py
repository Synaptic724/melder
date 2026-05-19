from melder.nexus.configuration.rift_access_mode import RiftAccessMode


def test_rift_access_mode_members_are_stable() -> None:
    """
    Verify the public RiftAccessMode enum exposes the expected member order.
    """
    members = list(RiftAccessMode)

    assert members == [
        RiftAccessMode.open,
        RiftAccessMode.token_required,
        RiftAccessMode.system_only,
    ]


def test_rift_access_mode_values_are_stable_strings() -> None:
    """
    Verify each RiftAccessMode member keeps its expected wire value.
    """
    assert [member.value for member in RiftAccessMode] == [
        "open",
        "token_required",
        "system_only",
    ]


def test_rift_access_mode_internal_sentinel_is_not_public_member() -> None:
    """
    Verify the internal registration sentinel is not exposed as an enum member.
    """
    assert "__melder_internal__" not in RiftAccessMode.__members__
