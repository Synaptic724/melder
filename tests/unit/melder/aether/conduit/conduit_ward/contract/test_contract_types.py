from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import (
    ContractTypes,
)


def test_contract_types_members_are_stable() -> None:
    """
    Verify the public ContractTypes enum exposes the expected member names in order.
    """
    members = list(ContractTypes)

    assert members == [
        ContractTypes.initiated,
        ContractTypes.received,
    ]


def test_contract_types_values_are_unique() -> None:
    """
    Verify each ContractTypes member has a unique enum value.
    """
    values = {member.value for member in ContractTypes}

    assert len(values) == 2
