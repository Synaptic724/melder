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
from melder.utilities.general_base.cleanable import Cleanable


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


def test_create_from_target_spell_runs_detail_completion(monkeypatch) -> None:
    binding_profile = object()
    spell = _make_spell()
    calls: dict[str, Any] = {}

    monkeypatch.setattr(
        detailed_module.SpellGeneralProfile,
        "create_from_target",
        classmethod(
            lambda cls, target, show_dunders=False, max_repr=120: SimpleNamespace(
                binding_profile=binding_profile,
                resolution_profile="resolution",
            )
        ),
        raising=True,
    )

    def fake_complete_with_spell(self: SpellDetailedProfile, target: Spell) -> None:
        calls["spell"] = target
        self.resolution_profile = "resolution"

    monkeypatch.setattr(
        detailed_module.SpellDetailedProfile,
        "complete_with_spell",
        fake_complete_with_spell,
        raising=True,
    )

    profile = SpellDetailedProfile.create_from_target(spell)

    assert isinstance(profile, SpellDetailedProfile)
    assert profile.binding_profile is binding_profile
    assert calls["spell"] is spell


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


def test_complete_with_spell_uses_method_path(monkeypatch) -> None:
    calls = {"complete": 0, "inspect_callable": 0}

    def fake_complete_with_spell(self: SpellDetailedProfile, spell: Spell) -> None:
        calls["complete"] += 1
        self.resolution_profile = "resolution"

    def fake_inspect_callable(self: SpellDetailedProfile, spell: Spell) -> Any:
        calls["inspect_callable"] += 1
        return "method-profile"

    monkeypatch.setattr(
        detailed_module.SpellGeneralProfile,
        "complete_with_spell",
        fake_complete_with_spell,
        raising=True,
    )
    monkeypatch.setattr(
        detailed_module.SpellDetailedProfile,
        "_inspect_callable",
        fake_inspect_callable,
        raising=True,
    )

    profile = SpellDetailedProfile(binding_profile=object())
    spell = _make_spell(spell_object=lambda value: value, spell_type=SpellType.METHOD)

    profile.complete_with_spell(spell)

    assert calls == {"complete": 1, "inspect_callable": 1}
    assert profile.class_profile is None
    assert profile.callable_profile == "method-profile"


def test_complete_with_spell_collects_callable_instance_members(monkeypatch) -> None:
    calls = {"complete": 0, "inspect_callable": 0}

    def fake_complete_with_spell(self: SpellDetailedProfile, spell: Spell) -> None:
        calls["complete"] += 1
        self.resolution_profile = "resolution"

    def fake_inspect_callable(self: SpellDetailedProfile, spell: Spell) -> Any:
        calls["inspect_callable"] += 1
        return "callable-instance-profile"

    monkeypatch.setattr(
        detailed_module.SpellGeneralProfile,
        "complete_with_spell",
        fake_complete_with_spell,
        raising=True,
    )
    monkeypatch.setattr(
        detailed_module.SpellDetailedProfile,
        "_inspect_callable",
        fake_inspect_callable,
        raising=True,
    )

    class CallableObject:
        def __init__(self) -> None:
            self.value = 7

        def __call__(self, arg: int) -> int:
            return arg + self.value

    instance = CallableObject()
    profile = SpellDetailedProfile(binding_profile=object())
    spell = _make_spell(
        spell_object=instance,
        spell_type=SpellType.EXISTING_CREATION,
    )

    profile.complete_with_spell(spell)

    assert calls == {"complete": 1, "inspect_callable": 1}
    assert profile.callable_profile == "callable-instance-profile"
    assert "value" in profile.instance_members
    assert profile.dynamic_access["has_getattribute"] is True


def test_complete_with_spell_collects_non_callable_instance_members(monkeypatch) -> None:
    def fake_complete_with_spell(self: SpellDetailedProfile, spell: Spell) -> None:
        self.resolution_profile = "resolution"

    monkeypatch.setattr(
        detailed_module.SpellGeneralProfile,
        "complete_with_spell",
        fake_complete_with_spell,
        raising=True,
    )

    class PlainObject:
        def __init__(self) -> None:
            self.value = 9

    instance = PlainObject()
    profile = SpellDetailedProfile(binding_profile=object())
    spell = _make_spell(
        spell_object=instance,
        spell_type=SpellType.EXISTING_CREATION,
    )

    profile.complete_with_spell(spell)

    assert profile.callable_profile is None
    assert "value" in profile.instance_members
    assert profile.dynamic_access["has_getattribute"] is True


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


def test_cleanup_swallows_detail_child_errors() -> None:
    class BoomProfile(Cleanable):
        __slots__ = Cleanable.__slots__

        def cleanup(self) -> None:
            raise RuntimeError("boom")

    profile = SpellDetailedProfile(
        binding_profile=object(),
        resolution_profile=object(),
        class_profile=BoomProfile(),
        callable_profile=BoomProfile(),
        metadata={"meta": 1},
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert not hasattr(profile, "metadata")
    profile.cleanup()


def test_inspect_class_skips_members_that_fail_lookup(monkeypatch) -> None:
    class DummyClassInspector:
        def __init__(self, target: Any, show_dunders: bool, max_repr: int) -> None:
            self.target = target
            self.show_dunders = show_dunders
            self.max_repr = max_repr

        def inspect(self) -> dict[str, Any]:
            return {
                "name": "BrokenClass",
                "qualname": "BrokenClass",
                "module": "tests",
                "mro": ["BrokenClass", "object"],
                "bases": ["object"],
                "annotations": {},
                "protocols": [],
                "slots": [],
                "file": None,
                "source_line_offset": None,
                "source_end_line": None,
                "source_preview": None,
                "source_text": None,
                "members": {"ghost": {"callable": True}},
                "is_dataclass": False,
                "decorated": False,
                "docstring_raw": None,
                "docstring_summary": "",
                "behavior_summary": "",
                "tags": [],
                "dynamic_access": {},
            }

    monkeypatch.setattr(
        detailed_module,
        "ClassInspector",
        DummyClassInspector,
    )

    class Sample:
        pass

    spell = _make_spell(spell_object=Sample, spell_type=SpellType.SPELL)
    profile = SpellDetailedProfile(binding_profile=object())
    class_profile = profile._inspect_class(spell)

    assert class_profile.name == "BrokenClass"
    assert class_profile.methods == {}


def test_inspect_class_builds_method_profiles_for_callable_members(monkeypatch) -> None:
    class DummyClassInspector:
        def __init__(self, target: Any, show_dunders: bool, max_repr: int) -> None:
            self.target = target
            self.show_dunders = show_dunders
            self.max_repr = max_repr

        def inspect(self) -> dict[str, Any]:
            return {
                "name": "Service",
                "qualname": "Service",
                "module": "tests",
                "mro": ["Service", "object"],
                "bases": ["object"],
                "annotations": {},
                "protocols": {},
                "slots": [],
                "file": None,
                "source_line_offset": None,
                "source_end_line": None,
                "source_preview": None,
                "source_text": None,
                "members": {"run": {"callable": True}},
                "is_dataclass": False,
                "decorated": False,
                "docstring_raw": None,
                "docstring_summary": "",
                "behavior_summary": "",
                "tags": [],
                "dynamic_access": {"has_getattr": True},
            }

    class DummyMethodInspector:
        def __init__(self, target: Any, max_repr: int) -> None:
            self.target = target
            self.max_repr = max_repr

        def inspect(self) -> dict[str, Any]:
            return {
                "name": "run",
                "qualname": "Service.run",
                "module": "tests",
                "id": 7,
                "type": "function",
                "repr": "<function Service.run>",
                "builtin_mod": False,
                "extension_mod": False,
                "file": "service.py",
                "preview": "def run(self): ...",
                "src_offset": 11,
                "start_line": 11,
                "end_line": 12,
                "source_text": "def run(self): return 'ok'",
                "signature": "(self)",
                "parameters": [],
                "uninspectable": False,
                "func": True,
                "method": True,
                "builtin": False,
                "classmethod": False,
                "staticmethod": False,
                "generator": False,
                "async_gen": False,
                "coroutine": False,
                "lambda_fn": False,
                "abstract": False,
                "closure": None,
                "decorated": False,
                "wrapped_repr": None,
                "docstring_raw": None,
                "docstring_summary": "",
                "behavior_summary": "",
                "tags": [],
            }

    monkeypatch.setattr(detailed_module, "ClassInspector", DummyClassInspector)
    monkeypatch.setattr(detailed_module, "MethodInspector", DummyMethodInspector)

    class Service:
        def run(self) -> str:
            return "ok"

    spell = _make_spell(spell_object=Service, spell_type=SpellType.SPELL)
    profile = SpellDetailedProfile(binding_profile=object())
    class_profile = profile._inspect_class(spell)

    assert "run" in class_profile.methods
    assert class_profile.methods["run"].qualname == "Service.run"
    assert class_profile.dynamic_access == {"has_getattr": True}


def test_inspect_callable_builds_method_profile(monkeypatch) -> None:
    class DummyMethodInspector:
        def __init__(self, target: Any, max_repr: int) -> None:
            self.target = target
            self.max_repr = max_repr

        def inspect(self) -> dict[str, Any]:
            return {
                "name": "spell_fn",
                "qualname": "spell_fn",
                "module": "tests",
                "id": 9,
                "type": "function",
                "repr": "<function spell_fn>",
                "builtin_mod": False,
                "extension_mod": False,
                "file": "spell.py",
                "preview": "def spell_fn(): ...",
                "src_offset": 21,
                "start_line": 21,
                "end_line": 22,
                "source_text": "def spell_fn(): return 1",
                "signature": "()",
                "parameters": [],
                "uninspectable": False,
                "func": True,
                "method": False,
                "builtin": False,
                "classmethod": False,
                "staticmethod": False,
                "generator": False,
                "async_gen": False,
                "coroutine": False,
                "lambda_fn": False,
                "abstract": False,
                "closure": None,
                "decorated": False,
                "wrapped_repr": None,
                "docstring_raw": None,
                "docstring_summary": "",
                "behavior_summary": "",
                "tags": [],
            }

    monkeypatch.setattr(detailed_module, "MethodInspector", DummyMethodInspector)

    def spell_fn() -> int:
        return 1

    spell = _make_spell(spell_object=spell_fn, spell_type=SpellType.METHOD)
    profile = SpellDetailedProfile(binding_profile=object())
    method_profile = profile._inspect_callable(spell)

    assert method_profile.name == "spell_fn"
    assert method_profile.signature == "()"
    assert method_profile.file == "spell.py"


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


def test_inspect_instance_members_handles_vars_slots_and_getattr_failures() -> None:
    profile = SpellDetailedProfile(binding_profile=object())

    class MixedInstance:
        __slots__ = ("broken", "__dict__")

        def __init__(self) -> None:
            self.__dict__["value"] = 3

        def __getattribute__(self, name: str) -> Any:
            if name == "broken":
                raise RuntimeError("boom")
            return object.__getattribute__(self, name)

    members = profile._inspect_instance_members(MixedInstance())

    assert members["value"]["type"] == "int"
    assert members["broken"]["type"] == "NoneType"
    assert members["broken"]["repr"] == "None"


def test_inspect_instance_members_handles_string_slots() -> None:
    profile = SpellDetailedProfile(binding_profile=object())

    class SingleSlotInstance:
        __slots__ = "value"

        def __init__(self) -> None:
            self.value = 5

    members = profile._inspect_instance_members(SingleSlotInstance())

    assert members["value"]["type"] == "int"


def test_has_attribute_in_mro_returns_false_when_missing() -> None:
    profile = SpellDetailedProfile(binding_profile=object())

    class PlainObject:
        pass

    assert profile._has_attribute_in_mro(PlainObject, "__missing__") is False
