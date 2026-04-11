from types import SimpleNamespace
from typing import Any

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.profiles import (
    detailed_profile as detailed_module,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.spellbook.spell_types.spell_types import SpellType


class _StubSpellbook:
    _spell_system_states = object()


def _make_spell(spell_object: Any = None, spell_type: SpellType = SpellType.SPELL) -> Spell:
    if spell_object is None:
        spell_object = object()
    return Spell(
        spell=spell_object,
        spell_index=SpellIndex("v1"),
        spellframe=None,
        binding_name=None,
        spell_name="name",
        existence=Existence.unique,
        spell_type=spell_type,
        spell_id="id",
        permissions=Permissions.read,
        aetheric_frame="frame",
        spellbook=_StubSpellbook(),
    )


def test_create_from_target_raw_target_rewraps_general_profile(monkeypatch) -> None:
    binding_profile = object()

    monkeypatch.setattr(
        detailed_module.SpellGeneralProfile,
        "create_from_target",
        classmethod(
            lambda cls, target, show_dunders=False, max_repr=120: SimpleNamespace(
                binding_profile=binding_profile,
                resolution_profile=None,
            )
        ),
        raising=True,
    )

    profile = SpellDetailedProfile.create_from_target(
        object(),
        show_dunders=True,
        max_repr=21,
    )

    assert isinstance(profile, SpellDetailedProfile)
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is None
    assert profile.class_profile is None
    assert profile.callable_profile is None
    assert profile.metadata == {}
    assert profile.instance_members == {}
    assert profile.dynamic_access == {}


def test_complete_with_spell_rejects_non_spell_instance() -> None:
    profile = SpellDetailedProfile(binding_profile=object())

    with pytest.raises(TypeError, match="requires a Spell instance"):
        profile.complete_with_spell(object())


def test_complete_with_spell_is_idempotent_after_detail_completion(monkeypatch) -> None:
    calls = {"complete": 0, "inspect_class": 0, "inspect_callable": 0}

    def fake_complete_with_spell(self: SpellDetailedProfile, spell: Spell) -> None:
        calls["complete"] += 1
        self.resolution_profile = "resolution"

    def fake_inspect_class(self: SpellDetailedProfile, spell: Spell) -> Any:
        calls["inspect_class"] += 1
        return SimpleNamespace(dynamic_access={"has_getattr": True})

    def fake_inspect_callable(self: SpellDetailedProfile, spell: Spell) -> Any:
        calls["inspect_callable"] += 1
        return "callable-profile"

    monkeypatch.setattr(
        detailed_module.SpellGeneralProfile,
        "complete_with_spell",
        fake_complete_with_spell,
        raising=True,
    )
    monkeypatch.setattr(
        detailed_module.SpellDetailedProfile,
        "_inspect_class",
        fake_inspect_class,
        raising=True,
    )
    monkeypatch.setattr(
        detailed_module.SpellDetailedProfile,
        "_inspect_callable",
        fake_inspect_callable,
        raising=True,
    )

    class Service:
        def run(self) -> str:
            return "ok"

    profile = SpellDetailedProfile(binding_profile=object())
    spell = _make_spell(spell_object=Service, spell_type=SpellType.SPELL)

    profile.complete_with_spell(spell)
    profile.complete_with_spell(spell)

    assert calls == {
        "complete": 2,
        "inspect_class": 1,
        "inspect_callable": 1,
    }
    assert profile.resolution_profile == "resolution"
    assert profile.class_profile.dynamic_access == {"has_getattr": True}
    assert profile.callable_profile == "callable-profile"
    assert profile.dynamic_access == {"has_getattr": True}


def test_to_descriptor_payload_delegates_current_profile_state(monkeypatch) -> None:
    binding_profile = object()
    resolution_profile = object()
    class_profile = object()
    callable_profile = object()
    captured: dict[str, Any] = {}
    sentinel = object()

    def fake_from_spell_profile(
        profile_name: str,
        profile_version: str,
        binding_arg: Any,
        **kwargs: Any,
    ) -> Any:
        captured["profile_name"] = profile_name
        captured["profile_version"] = profile_version
        captured["binding_profile"] = binding_arg
        captured["kwargs"] = kwargs
        return sentinel

    monkeypatch.setattr(
        detailed_module.SpellDescriptorPayload,
        "from_spell_profile",
        staticmethod(fake_from_spell_profile),
    )

    profile = SpellDetailedProfile(
        binding_profile=binding_profile,
        resolution_profile=resolution_profile,
        class_profile=class_profile,
        callable_profile=callable_profile,
        metadata={"meta": 1},
        instance_members={"value": {"type": "int"}},
        dynamic_access={"has_getattr": True},
    )

    assert profile.to_descriptor_payload() is sentinel
    assert captured["profile_name"] == "detailed"
    assert captured["profile_version"] == "0.0.1"
    assert captured["binding_profile"] is binding_profile
    assert captured["kwargs"] == {
        "resolution_payload": resolution_profile,
        "class_profile": class_profile,
        "callable_profile": callable_profile,
        "metadata": {"meta": 1},
        "instance_members": {"value": {"type": "int"}},
        "dynamic_access": {"has_getattr": True},
    }


def test_instance_member_helpers_filter_and_capture_runtime_surface() -> None:
    profile = SpellDetailedProfile(binding_profile=object())

    class DynamicInstance:
        __slots__ = ("value",)

        def __init__(self) -> None:
            self.value = 7

        def __getattr__(self, name: str) -> Any:
            raise AttributeError(name)

    instance = DynamicInstance()
    members = profile._inspect_instance_members(instance)
    flags = profile._dynamic_access_flags(instance)

    assert profile._should_collect_instance_members(DynamicInstance) is False
    assert profile._should_collect_instance_members(len) is False
    assert profile._should_collect_instance_members(lambda value: value) is False
    assert profile._should_collect_instance_members(instance) is True
    assert "value" in members
    assert members["value"]["type"] == "int"
    assert members["value"]["callable"] is False
    assert flags == {
        "has_getattr": True,
        "has_getattribute": True,
        "has_setattr": True,
    }
