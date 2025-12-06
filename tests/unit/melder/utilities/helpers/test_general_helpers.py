import pytest

from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.general_helpers import SpellInputUtils
from enum import Enum


class Color(Enum):
    red = 1
    blue = 2


def test_convert_enum_accepts_enum_member():
    assert EnumHelpers.convert_enum_and_check(Color.red, Color) is Color.red


def test_convert_enum_accepts_string_case_insensitive():
    assert EnumHelpers.convert_enum_and_check("RED", Color) is Color.red
    assert EnumHelpers.convert_enum_and_check("blue", Color) is Color.blue


def test_convert_enum_rejects_invalid_string():
    with pytest.raises(ValueError):
        EnumHelpers.convert_enum_and_check("green", Color)


def test_convert_enum_rejects_none():
    with pytest.raises(ValueError):
        EnumHelpers.convert_enum_and_check(None, Color)


def test_convert_enum_rejects_wrong_enum_type():
    class Other(Enum):
        green = 1
    with pytest.raises(ValueError):
        EnumHelpers.convert_enum_and_check(Other.green, Color)


def test_spell_input_utils_normalize_frame_key_variants():
    class Frame:
        pass

    assert SpellInputUtils.normalize_frame_key(Frame) == "frame"
    assert SpellInputUtils.normalize_frame_key("MyFrame") == "myframe"
    assert SpellInputUtils.normalize_frame_key(123) == "123"


def test_spell_input_utils_binding_and_spell_name():
    class Spell:
        pass

    assert SpellInputUtils.normalize_spell_name(Spell) == "Spell"
    assert SpellInputUtils.normalize_binding_name(None) == "__default__"
    assert SpellInputUtils.normalize_binding_name("Primary") == "primary"
    assert SpellInputUtils.normalize_binding_name("__default__") == "__default__"


def test_spell_input_utils_make_spell_key_from_parts():
    frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
        spellframe="Frame", spell_name="Spell", binding_name="Primary"
    )
    assert frame_key == "frame"
    assert bind_key == "primary"


def test_spell_input_utils_normalize_spell_key_requires_input():
    with pytest.raises(ValueError):
        SpellInputUtils.normalize_spell_key(spell=None, spellframe=None)

    class Spell:
        pass

    fk, bk = SpellInputUtils.normalize_spell_key(spell=Spell, spellframe=None, binding_name=None)
    assert fk == "spell"
    assert bk == "__default__"

    fk2, bk2 = SpellInputUtils.normalize_spell_key(spell=None, spellframe="Frame", binding_name="Alt")
    assert fk2 == "frame"
    assert bk2 == "alt"


def test_spell_input_utils_normalize_spell_key_with_string_spell():
    fk, bk = SpellInputUtils.normalize_spell_key(spell="MySpell", spellframe=None, binding_name="B")
    # Strings are treated as plain objects; spell_name resolves to type name "str"
    assert fk == "str"
    assert bk == "b"


def test_spell_input_utils_normalize_spell_key_prefers_spellframe():
    fk, bk = SpellInputUtils.normalize_spell_key(spell=None, spellframe="MyFrame", binding_name=None)
    assert fk == "myframe"
    assert bk == "__default__"
