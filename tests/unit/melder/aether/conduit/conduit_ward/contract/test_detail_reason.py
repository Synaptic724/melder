from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason


def test_detail_reason_members_are_stable() -> None:
    """
    Verify the public DetailReason enum exposes the expected member names in order.
    """
    members = list(DetailReason)

    assert members == [
        DetailReason.root,
        DetailReason.dependency,
        DetailReason.manual,
        DetailReason.other,
    ]


def test_detail_reason_values_are_unique() -> None:
    """
    Verify each DetailReason member has a unique enum value.
    """
    values = {member.value for member in DetailReason}

    assert len(values) == 4
