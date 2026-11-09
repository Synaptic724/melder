"""System diagnostic severity string and historical numeric compatibility."""

import json
import pickle
from enum import StrEnum

import pytest

from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)


@pytest.mark.parametrize(
    ("member", "legacy_number"),
    [(SystemDiagnosticSeverity.ERROR, 1), (SystemDiagnosticSeverity.WARNING, 2)],
)
def test_diagnostic_severity_preserves_old_numeric_inputs(
    member: SystemDiagnosticSeverity, legacy_number: int,
) -> None:
    """Exact string values coexist with the captured historical numeric pickle."""
    old_pickle_prefix = bytes.fromhex(
        "80049566000000000000008c3f6d656c6465722e6165746865722e7370656c6c626f6f6b2e"
        "7370656c6c5f636f6d70696c65722e73797374656d2e73797374656d5f646961676e6f73746963"
        "948c1853797374656d446961676e6f7374696353657665726974799493944b"
    )
    old_pickle = old_pickle_prefix + bytes([legacy_number]) + bytes.fromhex("859452942e")
    assert isinstance(member, StrEnum)
    assert member.value == member.name
    assert str(member) == member.name
    assert json.loads(json.dumps(member)) == member.name
    assert SystemDiagnosticSeverity(legacy_number) is member
    assert SystemDiagnosticSeverity(float(legacy_number)) is member
    assert pickle.loads(old_pickle) is member
    diagnostic = SystemDiagnostic("severity-test", "message", severity=member)
    try:
        assert diagnostic.severity is member
    finally:
        diagnostic.cleanup()


@pytest.mark.parametrize("invalid", [0, 3, "error", "unknown", None, []])
def test_diagnostic_severity_rejects_unknown_values(invalid: object) -> None:
    """Unknown numeric and noncanonical string inputs retain ValueError."""
    with pytest.raises(ValueError):
        SystemDiagnosticSeverity(invalid)