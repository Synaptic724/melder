"""SpellType exact strings and historical numeric representation compatibility."""

import hashlib
import json
import pickle
from enum import StrEnum

import pytest

from melder.aether.spellbook.resolution_style_matrix import ResolutionStyleMatrix
from melder.aether.spellbook.spell_types.spell_types import SpellType


def test_spell_types_keep_captured_old_numeric_pickle_inputs() -> None:
    """Every ordered old numeric value reconstructs its same exact-name member."""
    prefix = bytes.fromhex(
        "80049547000000000000008c2f6d656c6465722e6165746865722e7370656c6c626f6f6b2e"
        "7370656c6c5f74797065732e7370656c6c5f7479706573948c095370656c6c547970659493944b"
    )
    payloads = [prefix + bytes([number]) + bytes.fromhex("859452942e") for number in range(1, 15)]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == (
        "23db74f3152f293700c21b733cb2e80d440735cddd5cede0351c6879633197bf"
    )
    assert len(SpellType) == 14
    for number, member in enumerate(SpellType, start=1):
        assert isinstance(member, StrEnum)
        assert member.value == member.name
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert SpellType(number) is member
        assert SpellType(float(number)) is member
        assert pickle.loads(payloads[number - 1]) is member


@pytest.mark.parametrize("invalid", [0, 15, "unknown", None, []])
def test_spell_type_rejects_unknown_values(invalid: object) -> None:
    """Invalid old or new values retain the ordinary enum refusal."""
    with pytest.raises(ValueError):
        SpellType(invalid)


def test_spell_types_keep_resolution_family_policy() -> None:
    """Real matrix classification still distinguishes the binding families."""
    assert ResolutionStyleMatrix.validate() == ()
    assert ResolutionStyleMatrix.get_family_for_spell_type(SpellType.SPELL) == "class_based"
    assert ResolutionStyleMatrix.get_family_for_spell_type(SpellType.METHOD) == "callable_based"
    assert ResolutionStyleMatrix.get_family_for_spell_type(SpellType.EXISTING_CREATION) == "existing_object_based"