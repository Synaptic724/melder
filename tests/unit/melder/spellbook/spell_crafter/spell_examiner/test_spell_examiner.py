import types

import pytest

from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.spell_examiner import (
    SpellExaminer,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.ai_profile_strategy import (
    AIProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import (
    ResolutionProfileStrategy,
)
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


def test_spell_examiner_registers_default_profile_builders() -> None:
    """
    Verify the default profile builders are registered at construction.

    Returns:
        None.
    """
    examiner = SpellExaminer()

    assert examiner.has_profile_builder("binding") is True
    assert examiner.has_profile_builder("resolution") is True
    assert examiner.has_profile_builder("ai") is True
    assert examiner.list_profile_builder_names() == [
        "binding",
        "resolution",
        "ai",
    ]


def test_create_profile_binding_accepts_raw_object_and_spell(monkeypatch) -> None:
    """
    Verify binding-profile creation accepts raw objects and Spell instances.

    Args:
        monkeypatch:
            Pytest monkeypatch fixture.

    Returns:
        None.
    """
    monkeypatch.setattr(
        BindingProfileStrategy,
        "build_profile",
        lambda self, candidate: ("binding", candidate, self.show_dunders, self.max_repr),
        raising=True,
    )
    examiner = SpellExaminer()
    raw_target = object()
    spell = _spell()

    assert examiner.create_profile(raw_target, "binding", True, 42) == (
        "binding",
        raw_target,
        True,
        42,
    )
    assert examiner.create_profile(spell, "binding", False, 9) == (
        "binding",
        spell.spell,
        False,
        9,
    )


def test_create_profile_resolution_requires_spell(monkeypatch) -> None:
    """
    Verify resolution-profile creation requires a Spell instance.

    Args:
        monkeypatch:
            Pytest monkeypatch fixture.

    Returns:
        None.
    """
    examiner = SpellExaminer()
    with pytest.raises(TypeError, match="requires a Spell instance"):
        examiner.create_profile(object(), "resolution")

    monkeypatch.setattr(
        ResolutionProfileStrategy,
        "build_profile",
        lambda self, spell: ("resolution", spell),
        raising=True,
    )
    spell = _spell()
    assert examiner.create_profile(spell, "resolution") == ("resolution", spell)


def test_create_profile_ai_requires_spell_and_builds_from_default_subprofiles(
        monkeypatch,
) -> None:
    """
    Verify AI-profile creation requires a Spell and composes binding and
    resolution profiles through the default builders.

    Args:
        monkeypatch:
            Pytest monkeypatch fixture.

    Returns:
        None.
    """
    examiner = SpellExaminer()
    with pytest.raises(TypeError, match="requires a Spell instance"):
        examiner.create_profile(object(), "ai")

    monkeypatch.setattr(
        BindingProfileStrategy,
        "build_profile",
        lambda self, candidate: ("binding", candidate),
        raising=True,
    )
    monkeypatch.setattr(
        ResolutionProfileStrategy,
        "build_profile",
        lambda self, spell: ("resolution", spell),
        raising=True,
    )
    monkeypatch.setattr(
        AIProfileStrategy,
        "build_profile",
        lambda self, spell, binding_profile=None, resolution_profile=None: (
            "ai",
            spell,
            binding_profile,
            resolution_profile,
            self.show_dunders,
            self.max_repr,
        ),
        raising=True,
    )

    spell = _spell()
    result = examiner.create_profile(spell, "ai", False, 7)

    assert result == (
        "ai",
        spell,
        ("binding", spell.spell),
        ("resolution", spell),
        True,
        7,
    )


def test_register_profile_builder_replaces_and_lists_named_builders() -> None:
    """
    Verify custom builders can be registered and replaced by name.

    Returns:
        None.
    """
    examiner = SpellExaminer()

    def first_builder(target, show_dunders, max_repr):
        return ("custom", target, show_dunders, max_repr)

    def second_builder(target, show_dunders, max_repr):
        return ("custom-2", target, show_dunders, max_repr)

    examiner.register_profile_builder("custom", first_builder)
    assert examiner.has_profile_builder("custom") is True
    assert examiner.create_profile("x", "custom", True, 9) == (
        "custom",
        "x",
        True,
        9,
    )

    examiner.register_profile_builder("custom", second_builder)
    assert examiner.create_profile("x", "custom", False, 3) == (
        "custom-2",
        "x",
        False,
        3,
    )


def test_register_profile_builder_rejects_invalid_input() -> None:
    """
    Verify invalid profile-builder registration is rejected.

    Returns:
        None.
    """
    examiner = SpellExaminer()

    with pytest.raises(ValueError, match="profile_name cannot be empty"):
        examiner.register_profile_builder("", lambda target, show_dunders, max_repr: None)

    with pytest.raises(TypeError, match="builder must be callable"):
        examiner.register_profile_builder("bad", None)


def test_create_profile_rejects_unknown_profile_name() -> None:
    """
    Verify unknown profile names fail fast.

    Returns:
        None.
    """
    examiner = SpellExaminer()

    with pytest.raises(ValueError, match="not registered"):
        examiner.create_profile(object(), "unknown")


def test_spell_examiner_cleanup_clears_registry_and_id() -> None:
    """
    Verify cleanup drops the profile-builder registry and id.

    Returns:
        None.
    """
    examiner = SpellExaminer()

    examiner.cleanup()

    assert examiner.cleaned is True
    assert examiner._lock is None
    assert examiner._profile_builders_by_name is None
    assert examiner._id is None
