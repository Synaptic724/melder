"""Unit tests for the SpellframeKind vocabulary (what a spell's spellframe is)."""
from enum import Enum

from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind


def test_spellframe_kind_has_exactly_the_three_kinds() -> None:
    """A spellframe is bare, a string category or a Protocol contract - nothing else."""
    assert issubclass(SpellframeKind, Enum)
    assert [member.name for member in SpellframeKind] == ["none", "category", "contract"]


def test_spellframe_kind_values_equal_their_names() -> None:
    """The member value is its name, so a recorded crystal field round-trips by name."""
    for member in SpellframeKind:
        assert member.value == member.name
        assert SpellframeKind(member.value) is member
        assert SpellframeKind[member.name] is member


def test_spellframe_kind_is_exported_at_the_package_root() -> None:
    """Users read the kind off a Spell; the enum is importable from `melder` beside Existence."""
    import melder

    assert melder.SpellframeKind is SpellframeKind
    assert "SpellframeKind" in melder.__all__
