from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType


def test_rift_space_type_members_are_stable() -> None:
    """
    Verify the public RiftSpaceType enum exposes the expected member order.
    """
    members = list(RiftSpaceType)

    assert members == [
        RiftSpaceType.static,
        RiftSpaceType.capability,
        RiftSpaceType.dynamic,
    ]


def test_rift_space_type_values_are_stable_strings() -> None:
    """
    Verify each RiftSpaceType member keeps its expected wire value.
    """
    assert [member.value for member in RiftSpaceType] == [
        "static",
        "capability",
        "dynamic",
    ]


def test_rift_space_type_internal_sentinel_is_not_public_member() -> None:
    """
    Verify the internal registration sentinel is not exposed as an enum member.
    """
    assert "__melder_internal__" not in RiftSpaceType.__members__
