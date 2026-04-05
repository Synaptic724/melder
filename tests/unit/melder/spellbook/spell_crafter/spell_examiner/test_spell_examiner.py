import types

import pytest

from melder.spellbook.spell import Spell
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.spell_crafter.spell_examiner.spell_examiner import (
    SpellExaminer,
    SpellExaminationKind,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import (
    ResolutionProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.ai_profile_strategy import (
    AIProfileStrategy,
)
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_types.spell_types import SpellType
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions


class _StubSpellbook:
    def __init__(self):
        self._spell_system_states = object()


def _spell():
    return Spell(
        spell=object(),
        spell_index=SpellIndex("v1"),
        spellframe=None,
        binding_name=None,
        spell_name="name",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="id",
        permissions=Permissions.read,
        aetheric_frame="frame",
        spellbook=_StubSpellbook(),
    )

def _ai_config(enabled: bool) -> Configuration:
    config = Configuration()
    config.with_defaults()
    config.with_rift_enabled(enabled)
    return config


def test_binding_profile_for_object_delegates_to_strategy(monkeypatch):
    captured = {}

    def fake_build(self, candidate):
        captured["show_dunders"] = self.show_dunders
        captured["max_repr"] = self.max_repr
        captured["candidate"] = candidate
        return "binding-profile"

    monkeypatch.setattr(BindingProfileStrategy, "build_profile", fake_build, raising=True)

    examiner = SpellExaminer(show_dunders=True, max_repr=42)
    target = object()
    result = examiner.binding_profile_for_object(target)
    assert result == "binding-profile"
    assert captured == {"show_dunders": True, "max_repr": 42, "candidate": target}


def test_inspect_aliases_binding_profile(monkeypatch):
    monkeypatch.setattr(
        BindingProfileStrategy,
        "build_profile",
        lambda self, candidate: "alias-profile",
        raising=True,
    )
    examiner = SpellExaminer()
    assert examiner.inspect(object()) == "alias-profile"


def test_resolution_profile_requires_spell(monkeypatch):
    examiner = SpellExaminer()
    with pytest.raises(TypeError):
        examiner.resolution_profile_for_spell("not-a-spell")  # type: ignore[arg-type]

    sentinel = object()
    monkeypatch.setattr(
        ResolutionProfileStrategy, "build_profile", lambda self, spell: sentinel, raising=True
    )
    spell = _spell()
    assert examiner.resolution_profile_for_spell(spell) is sentinel


def test_ai_profile_uses_or_builds_profiles(monkeypatch):
    binding_profile = object()
    resolution_profile = object()
    sentinel = object()

    def fake_ai(self, spell, binding_profile=None, resolution_profile=None):
        return (spell, binding_profile, resolution_profile, self.show_dunders, self.max_repr)

    monkeypatch.setattr(AIProfileStrategy, "build_profile", fake_ai, raising=True)

    examiner = SpellExaminer(show_dunders=True, max_repr=7, configuration=_ai_config(True))
    spell = _spell()

    # Provided profiles bypass builders
    result = examiner.ai_profile_for_spell(
        spell, binding_profile=binding_profile, resolution_profile=resolution_profile
    )
    assert result == (spell, binding_profile, resolution_profile, True, 7)

    # Missing profiles are built via strategies
    monkeypatch.setattr(
        BindingProfileStrategy, "build_profile", lambda self, obj: "built-binding", raising=True
    )
    monkeypatch.setattr(
        ResolutionProfileStrategy, "build_profile", lambda self, sp: "built-resolution", raising=True
    )
    result2 = examiner.ai_profile_for_spell(spell)
    assert result2 == (spell, "built-binding", "built-resolution", True, 7)


def test_ai_profile_requires_spell(monkeypatch):
    examiner = SpellExaminer()
    with pytest.raises(TypeError):
        examiner.ai_profile_for_spell("not-spell")  # type: ignore[arg-type]

def test_ai_profile_requires_opt_in(monkeypatch):
    spell = _spell()
    examiner = SpellExaminer()
    with pytest.raises(RuntimeError, match="AI profiles are disabled"):
        examiner.ai_profile_for_spell(spell)

    sentinel = object()
    bp = object()
    rp = object()

    monkeypatch.setattr(
        AIProfileStrategy,
        "build_profile",
        lambda self, spell, binding_profile=None, resolution_profile=None: sentinel,
        raising=True,
    )
    examiner = SpellExaminer(configuration=_ai_config(True))
    assert examiner.ai_profile_for_spell(spell, binding_profile=bp, resolution_profile=rp) is sentinel


def test_examine_binding_accepts_spell_and_raw(monkeypatch):
    monkeypatch.setattr(
        BindingProfileStrategy,
        "build_profile",
        lambda self, obj: ("binding", obj),
        raising=True,
    )
    examiner = SpellExaminer()
    raw_target = object()
    spell = _spell()

    assert examiner.examine(raw_target, SpellExaminationKind.BINDING) == ("binding", raw_target)
    assert examiner.examine(spell, SpellExaminationKind.BINDING) == ("binding", spell.spell)


def test_examine_resolution_and_ai_validate_types(monkeypatch):
    examiner = SpellExaminer(configuration=_ai_config(True))
    with pytest.raises(TypeError):
        examiner.examine(object(), SpellExaminationKind.RESOLUTION)
    with pytest.raises(TypeError):
        examiner.examine(object(), SpellExaminationKind.AI)

    monkeypatch.setattr(
        ResolutionProfileStrategy, "build_profile", lambda self, s: "res-profile", raising=True
    )
    monkeypatch.setattr(
        AIProfileStrategy,
        "build_profile",
        lambda self, spell, binding_profile=None, resolution_profile=None: "ai-profile",
        raising=True,
    )
    spell = _spell()
    assert examiner.examine(spell, SpellExaminationKind.RESOLUTION) == "res-profile"
    assert examiner.examine(spell, SpellExaminationKind.AI) == "ai-profile"


def test_examine_unknown_kind_raises():
    examiner = SpellExaminer()
    with pytest.raises(ValueError):
        examiner.examine(object(), kind="unknown")  # type: ignore[arg-type]


def test_binding_profile_strategy_constructed_per_call(monkeypatch):
    calls = []

    class FakeStrategy(BindingProfileStrategy):
        def __init__(self, show_dunders=False, max_repr=0):
            calls.append((show_dunders, max_repr))

        def build_profile(self, candidate):
            return candidate

    monkeypatch.setattr(
        "melder.spellbook.spell_crafter.spell_examiner.spell_examiner.BindingProfileStrategy",
        FakeStrategy,
        raising=True,
    )

    examiner = SpellExaminer(show_dunders=False, max_repr=10)
    target1 = object()
    target2 = object()
    assert examiner.binding_profile_for_object(target1) is target1
    assert examiner.inspect(target2) is target2
    assert calls == [(False, 10), (False, 10)]


def test_resolution_profile_strategy_constructed_each_time(monkeypatch):
    calls = []

    class FakeRes(ResolutionProfileStrategy):
        def __init__(self):
            calls.append("ctor")

        def build_profile(self, spell):
            return ("res", spell)

    monkeypatch.setattr(
        "melder.spellbook.spell_crafter.spell_examiner.spell_examiner.ResolutionProfileStrategy",
        FakeRes,
        raising=True,
    )

    examiner = SpellExaminer()
    spell = _spell()
    assert examiner.resolution_profile_for_spell(spell) == ("res", spell)
    assert examiner.resolution_profile_for_spell(spell) == ("res", spell)
    assert calls == ["ctor", "ctor"]


def test_ai_profile_strategy_receives_config(monkeypatch):
    captured = {}

    class FakeAI(AIProfileStrategy):
        def __init__(self, show_dunders=False, max_repr=0):
            captured["ctor"] = (show_dunders, max_repr)

        def build_profile(self, spell, binding_profile=None, resolution_profile=None):
            captured["payload"] = (spell, binding_profile, resolution_profile)
            return "ai"

    monkeypatch.setattr(
        "melder.spellbook.spell_crafter.spell_examiner.spell_examiner.AIProfileStrategy",
        FakeAI,
        raising=True,
    )
    examiner = SpellExaminer(show_dunders=True, max_repr=5, configuration=_ai_config(True))
    spell = _spell()
    bp = object()
    rp = object()
    assert examiner.ai_profile_for_spell(spell, binding_profile=bp, resolution_profile=rp) == "ai"
    assert captured["ctor"] == (True, 5)
    assert captured["payload"] == (spell, bp, rp)


def test_ai_profile_forces_dunder_visibility(monkeypatch):
    captured = {}

    class FakeAI(AIProfileStrategy):
        def __init__(self, show_dunders=False, max_repr=0):
            captured["ctor"] = (show_dunders, max_repr)

        def build_profile(self, spell, binding_profile=None, resolution_profile=None):
            return "ai"

    monkeypatch.setattr(
        "melder.spellbook.spell_crafter.spell_examiner.spell_examiner.AIProfileStrategy",
        FakeAI,
        raising=True,
    )
    examiner = SpellExaminer(show_dunders=False, max_repr=9, configuration=_ai_config(True))
    spell = _spell()
    assert examiner.ai_profile_for_spell(spell) == "ai"
    assert captured["ctor"] == (True, 9)


def test_examine_ai_with_provided_profiles_bypasses_build(monkeypatch):
    bp = object()
    rp = object()
    sentinel = object()

    def fake_ai(self, spell, binding_profile=None, resolution_profile=None):
        return (spell, binding_profile, resolution_profile, "ai")

    monkeypatch.setattr(AIProfileStrategy, "build_profile", fake_ai, raising=True)
    monkeypatch.setattr(
        BindingProfileStrategy, "build_profile", lambda self, o: (_ for _ in ()).throw(RuntimeError("should not call")), raising=True
    )
    monkeypatch.setattr(
        ResolutionProfileStrategy, "build_profile", lambda self, s: (_ for _ in ()).throw(RuntimeError("should not call")), raising=True
    )

    examiner = SpellExaminer(configuration=_ai_config(True))
    spell = _spell()
    result = examiner.examine(
        spell,
        SpellExaminationKind.AI,
        binding_profile=bp,
        resolution_profile=rp,
    )
    assert result == (spell, bp, rp, "ai")


def test_examine_binding_with_spell_and_raw_targets(monkeypatch):
    monkeypatch.setattr(
        BindingProfileStrategy,
        "build_profile",
        lambda self, obj: ("bp", obj),
        raising=True,
    )
    examiner = SpellExaminer()
    raw = object()
    spell = _spell()
    assert examiner.examine(raw, SpellExaminationKind.BINDING) == ("bp", raw)
    assert examiner.examine(spell, SpellExaminationKind.BINDING) == ("bp", spell.spell)


def test_binding_strategy_exception_bubbles(monkeypatch):
    def boom(self, obj):
        raise RuntimeError("bind-fail")

    monkeypatch.setattr(BindingProfileStrategy, "build_profile", boom, raising=True)
    examiner = SpellExaminer()
    with pytest.raises(RuntimeError, match="bind-fail"):
        examiner.binding_profile_for_object(object())


def test_ai_strategy_exception_bubbles(monkeypatch):
    def boom(self, spell, binding_profile=None, resolution_profile=None):
        raise RuntimeError("ai-fail")

    monkeypatch.setattr(AIProfileStrategy, "build_profile", boom, raising=True)
    examiner = SpellExaminer(configuration=_ai_config(True))
    with pytest.raises(RuntimeError, match="ai-fail"):
        examiner.ai_profile_for_spell(_spell())


def test_ai_strategy_instance_is_fresh_per_call(monkeypatch):
    instances = []

    class FakeAI(AIProfileStrategy):
        def __init__(self, show_dunders=False, max_repr=0):
            instances.append(self)

        def build_profile(self, spell, binding_profile=None, resolution_profile=None):
            return id(self)

    monkeypatch.setattr(
        "melder.spellbook.spell_crafter.spell_examiner.spell_examiner.AIProfileStrategy",
        FakeAI,
        raising=True,
    )

    examiner = SpellExaminer(configuration=_ai_config(True))
    spell = _spell()
    first = examiner.ai_profile_for_spell(spell)
    second = examiner.ai_profile_for_spell(spell)

    assert len(instances) == 2
    assert first != second
