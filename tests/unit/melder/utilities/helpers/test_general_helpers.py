import pytest

from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.general_helpers import SpellInputUtils
from enum import Enum, StrEnum
from typing import Iterator


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


def test_spell_input_utils_describe_spell_id_prefers_names():
    """describe_spell_id quotes a known spell's name and shortens unknown ids."""
    from types import SimpleNamespace

    spells = {"a" * 64: SimpleNamespace(spell_name="CodecPacket")}

    assert SpellInputUtils.describe_spell_id("a" * 64, spells) == "'CodecPacket'"
    assert SpellInputUtils.describe_spell_id("b" * 64, spells) == "spell id " + "b" * 12
    assert SpellInputUtils.describe_spell_id(None, spells) == "an unknown spell"


@pytest.fixture
def enum_name_cache_isolated() -> Iterator[None]:
    """Keep each normalization contract independent of earlier cached inputs."""
    EnumHelpers.convert_enum_and_check.cache_clear()
    try:
        yield
    finally:
        EnumHelpers.convert_enum_and_check.cache_clear()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("lowercase", "lowercase"),
        ("LOWERCASE", "lowercase"),
        ("CLEANED", "CLEANED"),
        ("cleaned", "CLEANED"),
        ("ClEaNeD", "CLEANED"),
        ("mixed", "MiXeD"),
        ("MIXED", "MiXeD"),
        ("AlIaS", "CLEANED"),
    ],
)
def test_declared_enum_names_resolve_case_insensitively(
    enum_name_cache_isolated: None, value: str, expected: str,
) -> None:
    """Declared names, including aliases, resolve without requiring lowercase keys."""
    class State(Enum):
        """A mixed-case name vocabulary whose stored values are not its names."""
        lowercase = "payload-a"
        CLEANED = "payload-b"
        MiXeD = "payload-c"
        ALIAS = CLEANED

    result = EnumHelpers.convert_enum_and_check(value, State)
    assert result is State.__members__[expected]
    assert EnumHelpers.convert_enum_and_check(result, State) is result


@pytest.mark.parametrize("value", ["payload-b", " CLEANED", "CLEANED ", "", "missing"])
def test_enum_lookup_refuses_values_and_unrecognized_names(
    enum_name_cache_isolated: None, value: str,
) -> None:
    """Friendly lookup accepts member names only, without trimming or value coercion."""
    class State(Enum):
        """An enum whose payload deliberately differs from its declared name."""
        CLEANED = "payload-b"

    with pytest.raises(ValueError, match="Invalid value"):
        EnumHelpers.convert_enum_and_check(value, State)


@pytest.mark.parametrize("name", ["red", "RED", "ReD"])
def test_existing_lowercase_key_precedence_is_preserved(
    enum_name_cache_isolated: None, name: str,
) -> None:
    """Existing lowercase-key resolution remains stable for colliding declarations."""
    class Collision(Enum):
        """Distinct names which the old lowercase-key lookup resolves to red."""
        red = 1
        RED = 2

    assert EnumHelpers.convert_enum_and_check(name, Collision) is Collision.red


@pytest.mark.parametrize("warm_first", [False, True])
@pytest.mark.parametrize("use_keywords", [False, True])
def test_foreign_str_enum_cannot_pass_as_an_equal_raw_name(
    enum_name_cache_isolated: None, warm_first: bool, use_keywords: bool,
) -> None:
    """Foreign StrEnum input refuses cold and after an equal raw string warmed the cache."""
    class Foreign(StrEnum):
        """A foreign member which compares equal to the accepted raw name."""
        red = "red"

    if warm_first:
        if use_keywords:
            assert EnumHelpers.convert_enum_and_check(value="red", enum=Color) is Color.red
        else:
            assert EnumHelpers.convert_enum_and_check("red", Color) is Color.red
    with pytest.raises(ValueError, match="Expected a string or Color member"):
        if use_keywords:
            EnumHelpers.convert_enum_and_check(value=Foreign.red, enum=Color)
        else:
            EnumHelpers.convert_enum_and_check(Foreign.red, Color)
    assert EnumHelpers.convert_enum_and_check("red", Color) is Color.red


def test_own_str_enum_member_remains_typed_when_raw_string_was_cached(
    enum_name_cache_isolated: None,
) -> None:
    """A requested-family StrEnum member returns itself rather than another input type."""
    class State(StrEnum):
        """The requested family accepts its own member and its declared name."""
        CLEANED = "payload"

    assert EnumHelpers.convert_enum_and_check("cleaned", State) is State.CLEANED
    assert EnumHelpers.convert_enum_and_check(State.CLEANED, State) is State.CLEANED
