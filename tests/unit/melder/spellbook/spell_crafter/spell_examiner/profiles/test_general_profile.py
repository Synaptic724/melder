from typing import Any

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles import general_profile as general_module
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable


class _StubSpellbook:
    _spell_system_states = object()


class _CleanableStub(Cleanable):
    __slots__ = Cleanable.__slots__ + ["cleaned_calls"]

    def __init__(self) -> None:
        super().__init__()
        self.cleaned_calls = 0

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self.cleaned_calls += 1
        self._cleaned = True


class _BoomCleanable(Cleanable):
    __slots__ = Cleanable.__slots__

    def cleanup(self) -> None:
        raise RuntimeError("boom")


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


def test_create_from_target_raw_candidate_builds_uncompleted_profile(monkeypatch) -> None:
    binding_profile = object()
    calls: dict[str, Any] = {}

    class DummyBindingStrategy:
        def __init__(self, *, show_dunders: bool = False, max_repr: int = 120) -> None:
            calls["show_dunders"] = show_dunders
            calls["max_repr"] = max_repr

        def build_profile(self, candidate: Any) -> Any:
            calls["candidate"] = candidate
            return binding_profile

    monkeypatch.setattr(
        general_module,
        "BindingProfileStrategy",
        DummyBindingStrategy,
    )

    target = object()
    profile = SpellGeneralProfile.create_from_target(
        target,
        show_dunders=True,
        max_repr=33,
    )

    assert calls == {
        "show_dunders": True,
        "max_repr": 33,
        "candidate": target,
    }
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is None
    assert profile.profile_name == "general"
    assert profile.profile_version == "0.0.1"


def test_create_from_target_spell_uses_raw_spell_object_and_completes(monkeypatch) -> None:
    binding_profile = object()
    resolution_profile = object()
    calls: dict[str, Any] = {}

    class DummyBindingStrategy:
        def __init__(self, *, show_dunders: bool = False, max_repr: int = 120) -> None:
            calls["show_dunders"] = show_dunders
            calls["max_repr"] = max_repr

        def build_profile(self, candidate: Any) -> Any:
            calls["candidate"] = candidate
            return binding_profile

    class DummyResolutionStrategy:
        def build_profile(self, spell: Spell) -> Any:
            calls["spell"] = spell
            return resolution_profile

    monkeypatch.setattr(
        general_module,
        "BindingProfileStrategy",
        DummyBindingStrategy,
    )
    monkeypatch.setattr(
        general_module,
        "ResolutionProfileStrategy",
        DummyResolutionStrategy,
    )

    spell_object = object()
    spell = _make_spell(spell_object=spell_object)
    profile = SpellGeneralProfile.create_from_target(spell, max_repr=17)

    assert calls["candidate"] is spell_object
    assert calls["spell"] is spell
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile


def test_complete_with_spell_is_idempotent(monkeypatch) -> None:
    resolution_profile = object()
    calls = {"count": 0}

    class DummyResolutionStrategy:
        def build_profile(self, spell: Spell) -> Any:
            calls["count"] += 1
            return resolution_profile

    monkeypatch.setattr(
        general_module,
        "ResolutionProfileStrategy",
        DummyResolutionStrategy,
    )

    profile = SpellGeneralProfile(binding_profile=object())
    spell = _make_spell()

    profile.complete_with_spell(spell)
    profile.complete_with_spell(spell)

    assert calls["count"] == 1
    assert profile.resolution_profile is resolution_profile


def test_to_descriptor_payload_delegates_current_profile_state(monkeypatch) -> None:
    binding_profile = object()
    resolution_profile = object()
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
        general_module.SpellDescriptorPayload,
        "from_spell_profile",
        staticmethod(fake_from_spell_profile),
    )

    profile = SpellGeneralProfile(
        binding_profile=binding_profile,
        resolution_profile=resolution_profile,
    )

    assert profile.to_descriptor_payload() is sentinel
    assert captured["profile_name"] == "general"
    assert captured["profile_version"] == "0.0.1"
    assert captured["binding_profile"] is binding_profile
    assert captured["kwargs"] == {
        "resolution_payload": resolution_profile,
        "class_profile": None,
        "callable_profile": None,
        "metadata": {},
        "instance_members": {},
        "dynamic_access": {},
    }


def test_cleanup_cascades_and_nulls_references() -> None:
    binding_profile = _CleanableStub()
    resolution_profile = _CleanableStub()
    profile = SpellGeneralProfile(
        binding_profile=binding_profile,
        resolution_profile=resolution_profile,
    )

    profile.cleanup()

    assert binding_profile.cleaned_calls == 1
    assert resolution_profile.cleaned_calls == 1
    assert not hasattr(profile, 'profile_name')
    assert not hasattr(profile, 'profile_version')
    assert not hasattr(profile, 'binding_profile')
    assert not hasattr(profile, 'resolution_profile')
    assert profile.cleaned is True
    profile.cleanup()


def test_cleanup_swallows_child_errors() -> None:
    profile = SpellGeneralProfile(
        binding_profile=_BoomCleanable(),
        resolution_profile=_BoomCleanable(),
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert not hasattr(profile, 'binding_profile')
    assert not hasattr(profile, 'resolution_profile')
