"""
Unit tests - SpellIndex's selected-version probe (STORY-2026-10-15-release_managed_spell).

`SpellIndex._is_selected_unless_cleaned(spell_id)` answers whether a live index currently selects `spell_id`, and
False once the index is cleaned. ReleaseManagedSpell's cold resolver reads it for indexes it neither owns nor locks,
where the selected-id property (`selected_spell_id`) would meet a field a racing cleanup deletes.
"""
import threading

from melder.aether.spellbook.bind.spell_index import SpellIndex


def test_the_selected_version_answers_true() -> None:
    """The index's current selection."""
    index = SpellIndex("v1")
    assert index._is_selected_unless_cleaned("v1") is True


def test_a_member_that_is_not_selected_answers_false_until_selected() -> None:
    """Membership is not selection; a notch moves the answer."""
    index = SpellIndex("v1")
    index.update("v2")
    assert index._is_selected_unless_cleaned("v1") is False
    assert index._is_selected_unless_cleaned("v2") is True
    index.update("v1")
    assert index._is_selected_unless_cleaned("v1") is True
    assert index._is_selected_unless_cleaned("v2") is False


def test_an_id_outside_the_lineage_answers_false() -> None:
    """A stranger is never selected."""
    assert SpellIndex("v1")._is_selected_unless_cleaned("v9") is False


def test_a_cleaned_index_answers_false() -> None:
    """A cleaned index selects nothing, and the probe does not raise."""
    index = SpellIndex("v1")
    index.cleanup()
    assert index._is_selected_unless_cleaned("v1") is False


def test_the_probe_racing_cleanup_never_raises() -> None:
    """Probes from another thread across a cleanup answer True or False, never AttributeError."""
    for _ in range(200):
        index = SpellIndex("v1")
        answers = []
        errors = []
        start = threading.Barrier(2)

        def _probe() -> None:
            start.wait()
            try:
                for _ in range(50):
                    answers.append(index._is_selected_unless_cleaned("v1"))
            except BaseException as error:
                errors.append(error)

        thread = threading.Thread(target=_probe)
        thread.start()
        start.wait()
        index.cleanup()
        thread.join(timeout=10)
        assert errors == []
        assert set(answers) <= {True, False}
