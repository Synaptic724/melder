"""Exact CLEANED enum values with #656 numeric and recorded-state compatibility."""

import hashlib
import json
import pickle
from enum import Enum, StrEnum

import pytest

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.utilities.helpers.general_helpers import EnumHelpers


@pytest.mark.parametrize(
    ("enum_type", "prefix", "count", "digest"),
    [
        (
            SpellValidity,
            "80049563000000000000008c476d656c6465722e6165746865722e61657468657269635f6672616d652e"
            "6465765f6f70732e7370656c6c5f73797374656d5f7374617465732e7370656c6c5f76616c6964697479"
            "948c0d5370656c6c56616c69646974799493944b",
            6,
            "db9502d8ffe4c2d83c06d7ffb6f1aea6f4e3eaa43e0a380abe331cca938b38d4",
        ),
        (
            ConduitState,
            "8004954c000000000000008c316d656c6465722e6165746865722e636f6e647569742e636f6e647569745f"
            "73746174652e636f6e647569745f7374617465948c0c436f6e6475697453746174659493944b",
            4,
            "2dc17118cb3028957c0bc1e72be76c4cb4ee4f467b95aacb52e48dcd401e96f9",
        ),
    ],
)
def test_terminal_numeric_enums_keep_old_inputs(
    enum_type: type[Enum], prefix: str, count: int, digest: str,
) -> None:
    """All old numeric values and captured pickles still reconstruct their members."""
    payloads = [bytes.fromhex(prefix) + bytes([n]) + bytes.fromhex("859452942e") for n in range(1, count + 1)]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == digest
    assert len(enum_type) == count
    for number, member in enumerate(enum_type, start=1):
        assert isinstance(member, StrEnum)
        assert member.value == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert enum_type(number) is member
        assert enum_type(float(number)) is member
        assert pickle.loads(payloads[number - 1]) is member


def test_recorded_unit_state_keeps_old_cleaned_value_and_pickle() -> None:
    """Old lowercase terminal data remains readable while new value matches CLEANED."""
    payload = bytes.fromhex(
        "80049558000000000000008c306d656c6465722e6372797374616c6c697a65722e6372797374616c732e"
        "7265636f726465645f756e69745f7374617465948c115265636f72646564556e69745374617465949394"
        "8c07636c65616e656494859452942e"
    )
    assert isinstance(RecordedUnitState.CLEANED, StrEnum)
    assert RecordedUnitState.CLEANED.value == "CLEANED"
    assert RecordedUnitState("cleaned") is RecordedUnitState.CLEANED
    assert pickle.loads(payload) is RecordedUnitState.CLEANED
    assert RecordedUnitState.enabled.value == "enabled"
    assert RecordedUnitState.disabled.value == "disabled"


@pytest.mark.parametrize("raw_first", [True, False])
def test_terminal_name_lookup_rejects_equal_foreign_family_in_both_cache_orders(raw_first: bool) -> None:
    """The type-sensitive helper must not conflate equal CLEANED enum families."""
    EnumHelpers.convert_enum_and_check.cache_clear()
    if raw_first:
        assert EnumHelpers.convert_enum_and_check("CLEANED", ConduitState) is ConduitState.CLEANED
    with pytest.raises(ValueError):
        EnumHelpers.convert_enum_and_check(RecordedUnitState.CLEANED, ConduitState)
    assert EnumHelpers.convert_enum_and_check("CLEANED", ConduitState) is ConduitState.CLEANED
    assert ConduitState.resolve("cleaned") is ConduitState.CLEANED
    assert str(ConduitState.CLEANED) == "cleaned"
    EnumHelpers.convert_enum_and_check.cache_clear()