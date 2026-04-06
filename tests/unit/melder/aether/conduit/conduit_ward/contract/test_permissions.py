from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions


def test_permissions_members_are_stable() -> None:
    """
    Verify the public Permissions enum exposes the expected member names in order.
    """
    members = list(Permissions)

    assert members == [
        Permissions.read,
        Permissions.create,
        Permissions.block,
    ]


def test_permissions_values_are_unique() -> None:
    """
    Verify each Permissions member has a unique enum value.
    """
    values = {member.value for member in Permissions}

    assert len(values) == 3
