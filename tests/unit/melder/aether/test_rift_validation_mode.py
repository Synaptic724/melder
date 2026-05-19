from melder.nexus.configuration.rift_validation_mode import (
    RiftValidationMode,
)


def test_rift_validation_mode_members_are_stable() -> None:
    """
    Verify the public RiftValidationMode enum exposes the expected member order.
    """
    members = list(RiftValidationMode)

    assert members == [
        RiftValidationMode.strict,
        RiftValidationMode.relaxed,
        RiftValidationMode.unsafe,
    ]


def test_rift_validation_mode_values_are_stable_strings() -> None:
    """
    Verify each RiftValidationMode member keeps its expected wire value.
    """
    assert [member.value for member in RiftValidationMode] == [
        "strict",
        "relaxed",
        "unsafe",
    ]


def test_rift_validation_mode_internal_sentinel_is_not_public_member() -> None:
    """
    Verify the internal registration sentinel is not exposed as an enum member.
    """
    assert "__melder_internal__" not in RiftValidationMode.__members__
