"""
Unit: SpellbookValidationError's `preface` - one line placed before the report (patch failed_notch_refusal_2026_10_18;
STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers). `Conduit.notch_spell` passes it when it refuses a
notch, so the first line says the notch did not happen; without it the message is unchanged.
"""
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, List, cast

import pytest

from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell


def _broken_spell() -> List[Spell]:
    """
    One spell stand-in whose Phase-4 result holds one error, as the renderer reads it.

    Returns:
        List[Spell]: A one-spell list for the error's `broken_spells`.
    """
    issue = SpellValidationIssue(
        severity="error", code="SELF_DEPENDENCY", message="Spell 'SelfMade' depends on itself.",
        source="SomeStrategy", details={},
    )
    spell = SimpleNamespace(
        spell_name="SelfMade",
        spell_id="spell-1",
        spellframe="greeter",
        validation_result_phase4=SimpleNamespace(issues=[issue]),
        validation_result_phase6=SimpleNamespace(errors=[], warnings=[]),
    )
    return [cast("Spell", spell)]


def test_without_a_preface_the_message_is_unchanged() -> None:
    """
    Contract:
        - `preface=None` (the default) renders the same message, starting with the report's first line.
    """
    spells = _broken_spell()

    plain = str(SpellbookValidationError(spells))
    explicit = str(SpellbookValidationError(spells, preface=None))

    assert explicit == plain
    assert plain.splitlines()[0] == "Spellbook validation failed. Broken spells: SelfMade."


def test_a_preface_is_the_first_line_and_the_report_follows_unchanged() -> None:
    """
    Contract:
        - The preface is the first line; the lines after it are the message without a preface, byte for byte.
        - `broken_spells` is kept as given.
    """
    spells = _broken_spell()
    preface = "notch_spell refused: 'SelfMade' (spell_id spell-1) failed its structural check."

    error = SpellbookValidationError(spells, preface=preface)

    lines = str(error).splitlines()
    assert lines[0] == preface
    assert "\n".join(lines[1:]) == str(SpellbookValidationError(spells))
    assert error.broken_spells is spells


def test_a_preface_goes_before_the_message_of_an_error_with_no_broken_spells() -> None:
    """With no spells and no diagnostics the message is its one fallback line; a preface still comes first."""
    error = SpellbookValidationError([], preface="notch_spell refused.")

    assert str(error).splitlines() == [
        "notch_spell refused.",
        "SpellbookValidationError raised with no broken spells.",
    ]


@pytest.mark.parametrize("preface", [42, b"bytes", ["a line"]])
def test_a_preface_that_is_not_a_string_is_refused(preface: Any) -> None:
    """A non-str preface raises TypeError naming the type it got; nothing is built."""
    with pytest.raises(TypeError, match=r"takes one line of text, a non-empty str; got " + type(preface).__name__):
        SpellbookValidationError(_broken_spell(), preface=preface)


def test_an_empty_preface_is_refused() -> None:
    """An empty preface would add a blank first line, so it is refused like a non-str one."""
    with pytest.raises(TypeError, match=r"takes one line of text, a non-empty str; got an empty str"):
        SpellbookValidationError(_broken_spell(), preface="")


@pytest.mark.parametrize("preface", ["first\nsecond", "first\r\nsecond", "ends with a break\n", "first\u2028second"])
def test_a_preface_with_a_line_break_is_refused(preface: str) -> None:
    """A preface with a line break would put a second line before the report, so it is refused too."""
    with pytest.raises(TypeError, match=r"takes one line of text, a non-empty str; got a str with a line break"):
        SpellbookValidationError(_broken_spell(), preface=preface)
