"""
Edge-case unit tests for the index-link contract objects.

Fills out the contract-model coverage: SpellIndex hash/membership interplay,
IndexDetail/Detail cleanup field-drops and instance-isolated sources, and the
Contract source-refcount removal (`_remove_source`) + ward lookup
(`_find_spell_in_ward`) paths.

Runtime: authored for Python 3.14t (import needs 3.14 deferred annotations).
"""

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import Detail, IndexDetail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason


def _index_detail(index, permission=Permissions.read, sources=None):
    return IndexDetail(
        spell_index=index,
        selected_spell_id=index.selected_spell_id,
        permissions=permission,
        contract_type=ContractTypes.received,
        reason=DetailReason.manual,
        sources=sources,
    )


def _spell_detail(index, permission=Permissions.read, sources=None):
    return Detail(
        spell_index=index,
        spell_id=index.selected_spell_id,
        permissions=permission,
        contract_type=ContractTypes.received,
        reason=DetailReason.manual,
        sources=sources,
    )


def _contract():
    wa, wb = object(), object()
    return Contract(wa, wb), wa, wb


# --- SpellIndex membership/hash interplay ---------------------------------

def test_is_sole_member_false_after_update_adds_member():
    idx = SpellIndex("v1")
    idx.update("v2")
    assert idx.is_sole_member("v2") is False


def test_is_sole_member_true_after_update_then_remove_old():
    idx = SpellIndex("v1")
    idx.update("v2")
    idx.remove_member("v1")
    assert idx.is_sole_member("v2") is True


def test_hash_stable_across_add_and_remove_member():
    idx = SpellIndex("v1")
    h = hash(idx)
    idx.add_member("v2")
    idx.remove_member("v2")
    assert hash(idx) == h


def test_update_same_id_twice_keeps_single_member():
    idx = SpellIndex("v1")
    idx.update("v1")
    assert idx.spells_in_index() == {"v1"}
    assert idx.selected_spell_id == "v1"


def test_selected_head_unaffected_by_add_member():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    idx.add_member("v3")
    assert idx.selected_spell_id == "v1"


def test_spells_in_index_empty_after_removing_all():
    idx = SpellIndex("v1")
    idx.remove_member("v1")
    assert idx.spells_in_index() == set()


def test_has_spell_false_after_remove_member():
    idx = SpellIndex("v1")
    idx.add_member("v2")
    idx.remove_member("v2")
    assert idx.has_spell("v2") is False


# --- IndexDetail cleanup field-drops + isolation ---------------------------

def test_index_detail_cleanup_drops_grant_fields():
    detail = _index_detail(SpellIndex("v1"))
    detail.cleanup()
    assert not hasattr(detail, "permissions")
    assert not hasattr(detail, "contract_type")
    assert not hasattr(detail, "reason")
    assert not hasattr(detail, "sources")


def test_index_detail_update_selected_multiple_times():
    detail = _index_detail(SpellIndex("v1"))
    detail.update_selected("v2")
    detail.update_selected("v3")
    assert detail.selected_spell_id == "v3"


def test_index_detail_index_id_stable_across_selected_change():
    idx = SpellIndex("v1")
    detail = _index_detail(idx)
    before = detail.index_id
    detail.update_selected("v2")
    assert detail.index_id == before == idx.id


def test_index_details_have_independent_source_sets():
    d1 = _index_detail(SpellIndex("v1"))
    d2 = _index_detail(SpellIndex("w1"))
    d1.add_source("root-a")
    assert "root-a" not in d2.sources


# --- Detail cleanup + isolation --------------------------------------------

def test_detail_spell_id_distinct_from_index_after_update():
    idx = SpellIndex("v1")
    detail = _spell_detail(idx)
    idx.update("v2")
    # The Detail's captured spell_id does not move with the lineage head.
    assert detail.spell_id == "v1"
    assert idx.selected_spell_id == "v2"


def test_detail_cleanup_drops_spell_id():
    detail = _spell_detail(SpellIndex("v1"))
    detail.cleanup()
    assert not hasattr(detail, "spell_id")


def test_details_have_independent_source_sets():
    d1 = _spell_detail(SpellIndex("v1"))
    d2 = _spell_detail(SpellIndex("w1"))
    d1.add_source("root-a")
    assert "root-a" not in d2.sources


def test_detail_custom_reason_stored():
    detail = Detail(
        spell_index=SpellIndex("v1"),
        spell_id="v1",
        permissions=Permissions.read,
        contract_type=ContractTypes.initiated,
        reason=DetailReason.dependency,
    )
    assert detail.reason is DetailReason.dependency


# --- Contract _remove_source / _find_spell_in_ward -------------------------

def test_find_spell_in_ward_returns_ward_a():
    contract, wa, wb = _contract()
    contract._add(wa, _spell_detail(SpellIndex("v1")))
    assert contract._find_spell_in_ward("v1") is wa


def test_find_spell_in_ward_returns_ward_b():
    contract, wa, wb = _contract()
    contract._add(wb, _spell_detail(SpellIndex("v1")))
    assert contract._find_spell_in_ward("v1") is wb


def test_find_spell_in_ward_returns_none_when_absent():
    contract, wa, wb = _contract()
    assert contract._find_spell_in_ward("nope") is None


def test_remove_source_deletes_detail_when_last_source_removed():
    contract, wa, wb = _contract()
    contract._add(wa, _spell_detail(SpellIndex("v1"), sources={"root-a"}))
    assert contract._remove_source(wa, "v1", "root-a") is True
    assert "v1" not in contract._get_detail_map(wa)


def test_remove_source_keeps_detail_when_sources_remain():
    contract, wa, wb = _contract()
    contract._add(wa, _spell_detail(SpellIndex("v1"), sources={"root-a", "root-b"}))
    assert contract._remove_source(wa, "v1", "root-a") is False
    assert contract._check_if_exists(wa, "v1") is True


def test_remove_source_none_root_drops_whole_detail():
    contract, wa, wb = _contract()
    contract._add(wa, _spell_detail(SpellIndex("v1"), sources={"root-a"}))
    assert contract._remove_source(wa, "v1", None) is True
    assert "v1" not in contract._get_detail_map(wa)


def test_remove_source_missing_spell_returns_false():
    contract, wa, wb = _contract()
    assert contract._remove_source(wa, "no-such-spell", "root-a") is False


def test_get_detail_map_invalid_ward_raises():
    contract, wa, wb = _contract()
    with pytest.raises(ValueError):
        contract._get_detail_map(object())


def test_index_and_spell_maps_are_independent():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add_index(wa, _index_detail(idx))
    # Adding an index-link does not populate the spell-detail map.
    assert contract._check_index_exists(wa, idx.id) is True
    assert contract._check_if_exists(wa, "v1") is False


def test_add_index_second_distinct_index_is_new():
    contract, wa, wb = _contract()
    idx_a = SpellIndex("v1")
    idx_b = SpellIndex("w1")
    assert contract._add_index(wa, _index_detail(idx_a)) is True
    assert contract._add_index(wa, _index_detail(idx_b)) is True
    assert contract._check_index_exists(wa, idx_a.id) is True
    assert contract._check_index_exists(wa, idx_b.id) is True


def test_remove_missing_spell_detail_is_noop():
    contract, wa, wb = _contract()
    contract._remove(wa, "no-such-spell")  # must not raise


def test_check_index_exists_false_on_other_ward():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add_index(wb, _index_detail(idx))
    assert contract._check_index_exists(wa, idx.id) is False


def test_clear_contract_disposes_spell_details():
    contract, wa, wb = _contract()
    detail = _spell_detail(SpellIndex("v1"))
    contract._add(wa, detail)
    contract._clear_contract()
    assert contract._details_a == {}
    with pytest.raises(RuntimeError):
        detail.has_spell("v1")


def test_index_detail_has_spell_follows_member_removal():
    # The IndexDetail is the membership oracle by delegation: it tracks the live
    # index, so a member dropped from the index disappears from has_spell at once.
    idx = SpellIndex("v1")
    idx.add_member("v2")
    detail = _index_detail(idx)
    assert detail.has_spell("v2") is True
    idx.remove_member("v2")
    assert detail.has_spell("v2") is False
