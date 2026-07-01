"""
Unit tests for the multi-member `SpellIndex` model.

Focuses on the membership surface added/relied on by the genuine index-operations
work: `add_member` (stage without selecting), `remove_member` (discard, keep the
selected head), `update` (select + record), `is_empty`, `is_sole_member`, and the
member-set snapshot semantics. A SpellIndex holds a SET of member ids with one
active `selected_spell_id`; the member set is the ownership/existence oracle.

Runtime: authored for Python 3.14t (import needs 3.14 deferred annotations).
"""

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex


def test_initial_index_is_single_member():
    idx = SpellIndex("v1")
    assert idx.spells_in_index() == {"v1"}
    assert idx.selected_spell_id == "v1"
    assert idx.is_sole_member("v1") is True
    assert idx.is_empty() is False


def test_update_selects_and_records_member():
    idx = SpellIndex("v1")
    idx.update("v2")
    assert idx.selected_spell_id == "v2"
    assert idx.spells_in_index() == {"v1", "v2"}


def test_update_builds_multi_member_lineage():
    idx = SpellIndex("v1")
    idx.update("v2")
    idx.update("v3")
    assert idx.selected_spell_id == "v3"
    assert idx.spells_in_index() == {"v1", "v2", "v3"}


def test_add_member_records_without_selecting():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    assert idx.spells_in_index() == {"v1", "v2"}
    assert idx.selected_spell_id == "v1"


def test_add_member_is_idempotent():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    idx.add_member("v2")
    assert idx.spells_in_index() == {"v1", "v2"}


def test_add_member_then_has_spell():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    assert idx.has_spell("v1") is True
    assert idx.has_spell("v2") is True
    assert idx.has_spell("v3") is False


def test_remove_member_discards_and_keeps_selected():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    idx.add_member("v3")
    idx.remove_member("v2")
    assert idx.spells_in_index() == {"v1", "v3"}
    assert idx.selected_spell_id == "v1"


def test_remove_member_is_idempotent_for_missing():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    idx.remove_member("missing")
    assert idx.spells_in_index() == {"v1", "v2"}


def test_remove_member_does_not_touch_selected_head():
    idx = SpellIndex("v1")
    idx.update("v2")  # select v2, members {v1, v2}
    idx.remove_member("v1")
    assert idx.selected_spell_id == "v2"
    assert idx.spells_in_index() == {"v2"}


def test_is_sole_member_true_for_only_member():
    idx = SpellIndex("v1")
    assert idx.is_sole_member("v1") is True


def test_is_sole_member_false_when_multi():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    assert idx.is_sole_member("v1") is False


def test_is_sole_member_false_for_non_member():
    idx = SpellIndex("v1")
    assert idx.is_sole_member("other") is False


def test_is_sole_member_true_after_removing_down_to_one():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    idx.add_member("v3")
    idx.remove_member("v2")
    idx.remove_member("v3")
    assert idx.is_sole_member("v1") is True


def test_is_empty_false_with_members():
    idx = SpellIndex("v1")
    assert idx.is_empty() is False


def test_is_empty_true_after_removing_all_members():
    idx = SpellIndex("v1")
    idx.remove_member("v1")
    assert idx.is_empty() is True
    assert idx.is_sole_member("v1") is False


def test_membership_methods_raise_after_cleanup():
    idx = SpellIndex("v1")
    idx.cleanup()
    with pytest.raises(RuntimeError):
        idx.add_member("v2")
    with pytest.raises(RuntimeError):
        idx.remove_member("v1")
    with pytest.raises(RuntimeError):
        idx.is_empty()
    with pytest.raises(RuntimeError):
        idx.is_sole_member("v1")
