import pytest

from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell import Spell
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.general_base.cleanable import Cleanable


class _StubSpellbook:
    _spell_system_states = object()


def _make_spell():
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


class _CleanableStub(Cleanable):
    __slots__ = Cleanable.__slots__ + ["cleaned_calls"]

    def __init__(self):
        super().__init__()
        self.cleaned_calls = 0

    def cleanup(self):
        if self._cleaned:
            return
        self.cleaned_calls += 1
        self._cleaned = True


class _BoomCleanable(Cleanable):
    __slots__ = Cleanable.__slots__

    def cleanup(self):
        raise RuntimeError("boom")


def test_metadata_copied_and_fields_assigned():
    meta = {"x": 1}
    spell = _make_spell()
    binding = object()
    resolution = object()
    profile = SpellDetailedProfile(
        binding_profile=binding,
        resolution_profile=resolution,
        metadata=meta,
    )

    assert profile.binding_profile is binding
    assert profile.resolution_profile is resolution
    assert profile.metadata is not meta
    assert profile.metadata == {"x": 1}
    assert profile.instance_members == {}
    assert profile.dynamic_access == {}

    meta["x"] = 2
    assert profile.metadata["x"] == 1


def test_cleanup_cascades_and_nulls_references():
    spell = _make_spell()
    binding = _CleanableStub()
    resolution = _CleanableStub()
    class_prof = _CleanableStub()
    callable_prof = _CleanableStub()
    profile = SpellDetailedProfile(
        binding_profile=binding,
        resolution_profile=resolution,
        class_profile=class_prof,
        callable_profile=callable_prof,
        metadata={"y": 2},
    )

    profile.cleanup()

    for stub in (binding, resolution, class_prof, callable_prof):
        assert getattr(stub, 'cleaned', False) or stub.cleaned_calls > 0
    assert not hasattr(profile, 'binding_profile')
    assert not hasattr(profile, 'resolution_profile')
    assert not hasattr(profile, 'class_profile')
    assert not hasattr(profile, 'callable_profile')
    assert not hasattr(profile, 'metadata')
    assert not hasattr(profile, 'instance_members')
    assert not hasattr(profile, 'dynamic_access')
    assert profile.cleaned is True


def test_cleanup_idempotent():
    profile = SpellDetailedProfile(
        binding_profile=_CleanableStub(),
        resolution_profile=_CleanableStub(),
    )
    profile.cleanup()
    # should not raise on repeat
    profile.cleanup()
    assert profile.cleaned is True


def test_cleanup_swallows_child_errors():
    profile = SpellDetailedProfile(
        binding_profile=_BoomCleanable(),
        resolution_profile=_BoomCleanable(),
        metadata={"a": 1},
    )
    profile.cleanup()
    assert profile.cleaned is True
    assert not hasattr(profile, "metadata")

