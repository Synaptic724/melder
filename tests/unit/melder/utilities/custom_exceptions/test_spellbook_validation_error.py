from types import SimpleNamespace

from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


def test_spellbook_validation_error_includes_spell_summary() -> None:
    """
    Purpose:
        Ensure SpellbookValidationError summarizes broken spells.
    Contract:
        The message includes spell name, id, and frame information.
    Returns:
        None.
    Raises:
        AssertionError: If summary details are missing.
    """
    spell = SimpleNamespace(
        spell_name="RootSpell",
        spell_id="spell-1",
        spellframe="frame-1",
    )

    error = SpellbookValidationError([spell])
    message = str(error)

    assert "Broken spells" in message
    assert "RootSpell" in message
    assert "id=spell-1" in message
    assert "frame='frame-1'" in message


def test_spellbook_validation_error_handles_empty_list() -> None:
    """
    Purpose:
        Verify empty spell lists use the fallback message.
    Contract:
        The error message indicates no broken spells were supplied.
    Returns:
        None.
    Raises:
        AssertionError: If the fallback message is missing.
    """
    error = SpellbookValidationError([])
    assert "no broken spells" in str(error)
