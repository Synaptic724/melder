"""Contract enum exact strings, old numeric values and strict detail families."""

import json
import pickle
from enum import Enum, StrEnum
from typing import cast

import pytest

from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.contract.details import Detail, IndexDetail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex


@pytest.mark.parametrize(
    ("enum_type", "pickle_prefix"),
    [
        (
            ContractTypes,
            "80049565000000000000008c496d656c6465722e6165746865722e636f6e647569742e636f6e647569745f"
            "776172642e636f6e74726163742e636f6e74726163745f74797065732e636f6e74726163745f7479706573"
            "948c0d436f6e747261637454797065739493944b",
        ),
        (
            DetailReason,
            "80049554000000000000008c396d656c6465722e6165746865722e636f6e647569742e636f6e647569745f"
            "776172642e636f6e74726163742e64657461696c5f726561736f6e948c0c44657461696c526561736f6e"
            "9493944b",
        ),
    ],
)
def test_contract_enums_keep_old_numeric_and_pickle_inputs(enum_type: type[Enum], pickle_prefix: str) -> None:
    """New string values equal names while captured old numeric values still resolve."""
    for number, member in enumerate(enum_type, start=1):
        old_pickle = bytes.fromhex(pickle_prefix) + bytes([number]) + bytes.fromhex("859452942e")
        assert isinstance(member, StrEnum)
        assert member.value == member.name
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert enum_type(number) is member
        assert enum_type(float(number)) is member
        assert pickle.loads(old_pickle) is member


@pytest.mark.parametrize("enum_type", [ContractTypes, DetailReason])
@pytest.mark.parametrize("invalid", [0, 5, "unknown", None, []])
def test_contract_enums_reject_unknown_values(enum_type: type[Enum], invalid: object) -> None:
    """Unknown numeric and string values retain normal ValueError."""
    with pytest.raises(ValueError):
        enum_type(invalid)

def test_contract_details_keep_strict_enum_family_boundaries() -> None:
    """Equal strings and foreign families cannot substitute for typed detail members."""
    class ForeignReason(StrEnum):
        manual = "manual"

    index = SpellIndex("spell-id")
    try:
        detail = Detail(index, "spell-id", Permissions.read, ContractTypes.received, DetailReason.manual)
        indexed = IndexDetail(index, "spell-id", Permissions.read, ContractTypes.received, DetailReason.manual)
        try:
            assert detail.contract_type is ContractTypes.received
            assert detail.reason is DetailReason.manual
            assert indexed.contract_type is ContractTypes.received
            assert indexed.reason is DetailReason.manual
        finally:
            detail.cleanup()
            indexed.cleanup()
        with pytest.raises(TypeError, match="contract_type must be ContractTypes"):
            Detail(index, "spell-id", Permissions.read, cast(ContractTypes, "received"), DetailReason.manual)
        with pytest.raises(TypeError, match="reason must be DetailReason"):
            IndexDetail(index, "spell-id", Permissions.read, ContractTypes.received, cast(DetailReason, ForeignReason.manual))
    finally:
        index.cleanup()