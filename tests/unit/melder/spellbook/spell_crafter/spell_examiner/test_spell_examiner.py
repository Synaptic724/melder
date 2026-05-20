import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner import (
    SpellExaminer,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


class _StubSpellbook:
    def __init__(self) -> None:
        self._spell_system_states = object()


def _spell() -> Spell:
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

    assert examiner.has_profile_builder("general") is True
    assert examiner.has_profile_builder("detailed") is True
    assert examiner.list_profile_builder_names() == [
        "general",
        "detailed",
    ]


def test_create_profile_general_accepts_raw_object_and_spell(monkeypatch) -> None:
    """
    Verify general-profile creation accepts raw objects and Spell instances.

    Args:
        monkeypatch:
            Pytest monkeypatch fixture.

    Returns:
        None.
    """
    monkeypatch.setattr(
        SpellGeneralProfile,
        "create_from_target",
        classmethod(lambda cls, target, show_dunders=False, max_repr=120: ("general", target, show_dunders, max_repr)),
        raising=True,
    )
    examiner = SpellExaminer()
    raw_target = object()
    spell = _spell()

    assert examiner.create_profile(raw_target, "general", True, 42) == (
        "general",
        raw_target,
        True,
        42,
    )
    assert examiner.create_profile(spell, "general", False, 9) == (
        "general",
        spell,
        False,
        9,
    )


def test_create_profile_detailed_accepts_raw_object_and_spell(monkeypatch) -> None:
    """
    Verify detailed-profile creation accepts raw objects and Spell instances.

    Args:
        monkeypatch:
            Pytest monkeypatch fixture.

    Returns:
        None.
    """
    monkeypatch.setattr(
        SpellDetailedProfile,
        "create_from_target",
        classmethod(lambda cls, target, show_dunders=False, max_repr=120: ("detailed", target, show_dunders, max_repr)),
        raising=True,
    )
    examiner = SpellExaminer()
    raw_target = object()
    spell = _spell()
    assert examiner.create_profile(raw_target, "detailed", False, 7) == (
        "detailed",
        raw_target,
        False,
        7,
    )
    assert examiner.create_profile(spell, "detailed", False, 7) == (
        "detailed",
        spell,
        False,
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
    assert not hasattr(examiner, '_profile_builders_by_name')
    assert not hasattr(examiner, '_id')


def test_spell_examiner_id_exposes_stable_value_and_cleanup_is_idempotent() -> None:
    """
    Verify the public id is readable before cleanup and cleanup stays idempotent.

    Returns:
        None.
    """
    examiner = SpellExaminer()
    examiner_id = examiner.id

    assert isinstance(examiner_id, str)
    assert examiner_id

    examiner.cleanup()

    with pytest.raises(RuntimeError, match="cleaned"):
        _ = examiner.id

    examiner.cleanup()
