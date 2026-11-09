"""Override target kind exact strings and legacy numeric compatibility."""

import hashlib
import json
import pickle
from enum import StrEnum

import pytest

from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec, TargetSpecKind


def test_target_kinds_keep_historical_numeric_pickle_inputs() -> None:
    """The three captured old numeric values reconstruct the same named members."""
    prefix = bytes.fromhex(
        "80049553000000000000008c366d656c6465722e6165746865722e7370656c6c626f6f6b2e"
        "7370656c6c5f636f6d70696c65722e6461672e7461726765745f73706563948c0e546172676574"
        "537065634b696e649493944b"
    )
    payloads = [prefix + bytes([number]) + bytes.fromhex("859452942e") for number in range(1, 4)]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == (
        "7263857f8ca84daddc60be48885df0f9fb6804c8b170f858c95b02cf9ebc3384"
    )
    for number, member in enumerate(TargetSpecKind, start=1):
        assert isinstance(member, StrEnum)
        assert member.value == member.name
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert TargetSpecKind(number) is member
        assert TargetSpecKind(float(number)) is member
        assert pickle.loads(payloads[number - 1]) is member


@pytest.mark.parametrize("invalid", [0, 4, "unknown", None, []])
def test_target_kind_rejects_unknown_values(invalid: object) -> None:
    """Invalid numeric and string inputs retain normal enum refusal."""
    with pytest.raises(ValueError):
        TargetSpecKind(invalid)


def test_override_parser_keeps_distinct_target_kinds() -> None:
    """Real parsing preserves path, unique and broadcast member identity."""
    path = TargetSpec.parse("service>repo")
    unique = TargetSpec.parse("*repo")
    broadcast = TargetSpec.parse("**repo")
    assert path.kind is TargetSpecKind.PATH and path.path == ("service", "repo")
    assert unique.kind is TargetSpecKind.UNIQUE and unique.param_name == "repo"
    assert broadcast.kind is TargetSpecKind.BROADCAST and broadcast.param_name == "repo"