"""
Unit tests for the `SpellStateChangeReason` values added for index operations.

`selected_different_spell` tags a notch (a general selection, NOT a mutation) and
`cleaned_up_spell` tags disposal via `cleanup_spell`. These are threaded into the
spell-owned invalidation so a lineage and its dependents carry the right reason.

Runtime: authored for Python 3.14t.
"""

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)


def test_selected_different_spell_exists_and_is_member():
    assert isinstance(SpellStateChangeReason.selected_different_spell, SpellStateChangeReason)
    assert SpellStateChangeReason.selected_different_spell in SpellStateChangeReason


def test_cleaned_up_spell_exists_and_is_member():
    assert isinstance(SpellStateChangeReason.cleaned_up_spell, SpellStateChangeReason)
    assert SpellStateChangeReason.cleaned_up_spell in SpellStateChangeReason


def test_notch_and_cleanup_reasons_are_distinct():
    assert (
        SpellStateChangeReason.selected_different_spell
        is not SpellStateChangeReason.cleaned_up_spell
    )
    assert SpellStateChangeReason.selected_different_spell is not SpellStateChangeReason.other
    assert SpellStateChangeReason.cleaned_up_spell is not SpellStateChangeReason.other


def test_reason_names_are_stable():
    assert SpellStateChangeReason.selected_different_spell.name == "selected_different_spell"
    assert SpellStateChangeReason.cleaned_up_spell.name == "cleaned_up_spell"
