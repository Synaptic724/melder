from melder.aether.conduit.conduit_ward.policies.policies import Policies


def test_policies_members_are_stable() -> None:
    """
    Verify the public Policies enum exposes the expected member names in order.
    """
    members = list(Policies)

    assert members == [
        Policies.default,
        Policies.whitelist_all,
        Policies.block_all,
        Policies.inbound_only,
        Policies.outbound_only,
    ]


def test_policies_values_are_unique() -> None:
    """
    Verify each Policies member has a unique enum value.
    """
    values = {member.value for member in Policies}

    assert len(values) == 5
