"""Compatibility checks for the binding-kind enum and its published descriptor."""

import json
import pickle
from enum import StrEnum

import pytest

from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    SpellBindingKind,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.nexus.frame_descriptor.spell_descriptor_payload import SpellDescriptorPayload


@pytest.mark.parametrize(
    ("member", "legacy_number"),
    [
        (SpellBindingKind.CLASS, 1),
        (SpellBindingKind.CALLABLE, 2),
        (SpellBindingKind.INSTANCE, 3),
        (SpellBindingKind.OTHER, 4),
    ],
)
def test_binding_kind_keeps_legacy_numeric_inputs_and_pickles(member: SpellBindingKind, legacy_number: int) -> None:
    """Keep captured numeric inputs readable while publishing the selected string value."""
    old_pickle_prefix = bytes.fromhex(
        "8004956d000000000000008c4e6d656c6465722e6165746865722e7370656c6c626f6f6b2e"
        "7370656c6c5f636f6d70696c65722e7370656c6c5f6578616d696e65722e70726f66696c6573"
        "2e62696e64696e675f70726f66696c65948c105370656c6c42696e64696e674b696e649493944b"
    )
    old_pickle = old_pickle_prefix + bytes([legacy_number]) + bytes.fromhex("859452942e")

    assert isinstance(member, StrEnum)
    assert member.value == member.name
    assert str(member) == member.name
    assert json.loads(json.dumps(member)) == member.name
    assert SpellBindingKind(legacy_number) is member
    assert SpellBindingKind(float(legacy_number)) is member
    assert pickle.loads(old_pickle) is member


@pytest.mark.parametrize("invalid", [0, 5, "class", "unknown", None, []])
def test_binding_kind_rejects_unknown_values(invalid: object) -> None:
    """Do not broaden the accepted historical input set to unrelated values."""
    with pytest.raises(ValueError):
        SpellBindingKind(invalid)


def test_binding_profile_descriptor_keeps_the_published_kind_name() -> None:
    """A real class profile still publishes the same detached kind token."""
    class Candidate:
        pass

    profile = BindingProfileStrategy().build_profile(Candidate)
    payload = SpellDescriptorPayload.from_spell_profile(
        "general", "0.0.1", profile, resolution_payload={}
    )
    try:
        assert profile.kind is SpellBindingKind.CLASS
        assert payload.binding_payload["kind"] == "CLASS"
        assert type(payload.binding_payload["kind"]) is str
        assert "original_object" not in payload.binding_payload
    finally:
        payload.cleanup()
        profile.cleanup()