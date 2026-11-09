"""Lifetime enum exact strings, historic values and managed-mode family checks."""

import json
import pickle
from enum import Enum, StrEnum

import pytest

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode


@pytest.mark.parametrize(
    ("enum_type", "pickle_prefix"),
    [
        (
            Existence,
            "80049543000000000000008c2b6d656c6465722e6165746865722e7370656c6c626f6f6b2e6578697374656e"
            "63652e6578697374656e6365948c094578697374656e63659493944b",
        ),
        (
            ManagedSpellMode,
            "80049553000000000000008c346d656c6465722e6165746865722e7370656c6c626f6f6b2e6578697374656e"
            "63652e6d616e616765645f7370656c6c5f6d6f6465948c104d616e616765645370656c6c4d6f64659493944b",
        ),
    ],
)
def test_lifetime_enums_keep_historical_numeric_and_pickle_inputs(
    enum_type: type[Enum], pickle_prefix: str,
) -> None:
    """Exact names coexist with the captured old numeric constructor payloads."""
    for number, member in enumerate(enum_type, start=1):
        old_pickle = bytes.fromhex(pickle_prefix) + bytes([number]) + bytes.fromhex("859452942e")
        assert isinstance(member, StrEnum)
        assert member.value == member.name
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert enum_type(number) is member
        assert enum_type(float(number)) is member
        assert pickle.loads(old_pickle) is member


@pytest.mark.parametrize("enum_type", [Existence, ManagedSpellMode])
@pytest.mark.parametrize("invalid", [0, 8, "unknown", None, []])
def test_lifetime_enums_reject_unknown_values(enum_type: type[Enum], invalid: object) -> None:
    """Unknown values retain normal enum refusal."""
    with pytest.raises(ValueError):
        enum_type(invalid)


def test_managed_mode_keeps_foreign_enums_out_of_the_string_branch() -> None:
    """A mode-shaped foreign string enum is not a managed-mode member or plain name."""
    class ForeignMode(StrEnum):
        queue = "queue"

    assert Bind._normalize_managed_mode(ManagedSpellMode.queue) is ManagedSpellMode.queue
    assert Bind._normalize_managed_mode("QUEUE") is ManagedSpellMode.queue
    with pytest.raises(TypeError):
        Bind._normalize_managed_mode(Existence.unique)
    with pytest.raises(TypeError):
        Bind._normalize_managed_mode(ForeignMode.queue)