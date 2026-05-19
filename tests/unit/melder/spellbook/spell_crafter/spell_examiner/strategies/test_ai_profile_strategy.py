from types import SimpleNamespace

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_crafter.spell_examiner.profiles import detailed_profile as ai_module, \
    general_profile as general_module
from melder.aether.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


class _StubSpellbook:
    def __init__(self) -> None:
        self._spell_system_states = object()


def _make_spell(spell_object, spell_type: SpellType) -> Spell:
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


def test_ai_profile_strategy_builds_class_profile(monkeypatch) -> None:
    """
    Purpose:
        Verify the detailed profile builds class and callable inspector payloads
        on completion.

    Returns:
        None.
    """
    binding_profile = object()
    resolution_profile = object()
    class_profile = SimpleNamespace(dynamic_access={})
    callable_profile = object()

    class DummyBindingStrategy:
        def __init__(self, *, show_dunders: bool = False, max_repr: int = 120) -> None:
            self.show_dunders = show_dunders
            self.max_repr = max_repr

        def build_profile(self, _candidate):
            return binding_profile

    class DummyResolutionStrategy:
        def build_profile(self, _spell):
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
    monkeypatch.setattr(
        ai_module.SpellDetailedProfile,
        "_inspect_class",
        lambda self, _spell: class_profile,
    )
    monkeypatch.setattr(
        ai_module.SpellDetailedProfile,
        "_inspect_callable",
        lambda self, _spell: callable_profile,
    )

    spell = _make_spell(object(), SpellType.SPELL)

    profile = ai_module.SpellDetailedProfile.create_from_target(
        spell,
        show_dunders=True,
        max_repr=33,
    )

    assert isinstance(profile, SpellDetailedProfile)
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile
    assert profile.class_profile is class_profile
    assert profile.callable_profile is callable_profile


def test_ai_profile_strategy_builds_callable_profile(monkeypatch) -> None:
    """
    Purpose:
        Verify the detailed profile builds callable payloads for callable spells.

    Returns:
        None.
    """
    binding_profile = object()
    resolution_profile = object()
    callable_profile = object()

    class DummyBindingStrategy:
        def __init__(self, *args, **kwargs) -> None:
            self._args = args
            self._kwargs = kwargs

        def build_profile(self, _candidate):
            return binding_profile

    class DummyResolutionStrategy:
        def build_profile(self, _spell):
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
    monkeypatch.setattr(
        ai_module.SpellDetailedProfile,
        "_inspect_callable",
        lambda self, _spell: callable_profile,
    )

    spell = _make_spell(lambda value: value, SpellType.METHOD)

    profile = ai_module.SpellDetailedProfile.create_from_target(spell)

    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile
    assert profile.class_profile is None
    assert profile.callable_profile is callable_profile


def test_ai_profile_strategy_fallback_callable_path(monkeypatch) -> None:
    """
    Purpose:
        Verify the detailed profile falls back to callable inspection for other
        callable spell targets.

    Returns:
        None.
    """
    binding_profile = object()
    resolution_profile = object()
    callable_profile = object()

    class DummyBindingStrategy:
        def __init__(self, *args, **kwargs) -> None:
            self._args = args
            self._kwargs = kwargs

        def build_profile(self, _candidate):
            return binding_profile

    class DummyResolutionStrategy:
        def build_profile(self, _spell):
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
    monkeypatch.setattr(
        ai_module.SpellDetailedProfile,
        "_inspect_callable",
        lambda self, _spell: callable_profile,
    )

    class CallableObject:
        def __call__(self, arg: int) -> int:
            return arg

    spell = _make_spell(CallableObject(), SpellType.EXISTING_CREATION)

    profile = ai_module.SpellDetailedProfile.create_from_target(spell)

    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile
    assert profile.class_profile is None
    assert profile.callable_profile is callable_profile


def test_ai_profile_strategy_collects_instance_members(monkeypatch) -> None:
    """
    Purpose:
        Verify the detailed profile collects instance-member payloads for
        instance-backed spell targets.

    Returns:
        None.
    """
    class DummyResolutionStrategy:
        def build_profile(self, _spell):
            return object()

    monkeypatch.setattr(
        general_module,
        "ResolutionProfileStrategy",
        DummyResolutionStrategy,
    )

    class CallableObject:
        def __init__(self):
            self.value = 42

        def __call__(self, arg: int) -> int:
            return arg + self.value

    instance = CallableObject()
    spell = _make_spell(instance, SpellType.EXISTING_CREATION)

    profile = ai_module.SpellDetailedProfile.create_from_target(spell)

    assert "value" in profile.instance_members
    assert profile.instance_members["value"]["kind"] == "instance_attribute"


def test_ai_profile_strategy_method_profile_includes_provenance() -> None:
    """
    Purpose:
        Verify the detailed profile callable inspection retains provenance data.

    Returns:
        None.
    """
    class Sample:
        def run(self, value: int) -> str:
            return str(value)

    spell = _make_spell(Sample.run, SpellType.METHOD)

    profile = ai_module.SpellDetailedProfile.create_from_target(
        spell,
        show_dunders=True,
    )
    callable_profile = profile.callable_profile

    assert callable_profile is not None
    assert callable_profile.name == "run"
    assert callable_profile.signature is not None
