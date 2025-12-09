import pytest

from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


class DummySpell:
    def __init__(self, name: str, spell_id: str, spellframe=None):
        self.spell_name = name
        self.spell_id = spell_id
        self.spellframe = spellframe


def test_spellbook_validation_error_builds_summary_and_stores_spells():
    broken = [
        DummySpell("SpellA", "id-a", spellframe="FrameA"),
        DummySpell("SpellB", "id-b", spellframe=None),
    ]

    err = SpellbookValidationError(broken)

    assert err.broken_spells == broken
    text = str(err)
    assert "Spellbook validation failed" in text
    assert "SpellA" in text and "id-a" in text
    assert "SpellB" in text and "id-b" in text


def test_spellbook_validation_error_handles_empty_list():
    err = SpellbookValidationError([])
    assert "no broken spells" in str(err).lower()
