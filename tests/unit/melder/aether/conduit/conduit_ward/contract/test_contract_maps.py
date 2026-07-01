"""
Unit tests for `Contract`'s per-ward detail maps (spell + index-link).

`Contract` is symmetric: each ward keeps its own map. The index-link maps
(`_index_details_a/_b`, `_add_index`/`_remove_index`/`_check_index_exists`/
`_get_index_detail_map`) mirror the spell maps (`_add`/`_remove`/`_check_if_exists`/
`_get_detail_map`). All accessors key off ward IDENTITY only, so these are unit
tested with sentinel ward objects (no live conduit graph needed).

Runtime: authored for Python 3.14t (import needs 3.14 deferred annotations).
"""

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import Detail, IndexDetail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason


def _contract():
    """Build a Contract over two sentinel wards; return (contract, ward_a, ward_b)."""
    ward_a = object()
    ward_b = object()
    return Contract(ward_a, ward_b), ward_a, ward_b


def _index_detail(index, permission=Permissions.read, sources=None):
    return IndexDetail(
        spell_index=index,
        selected_spell_id=index.selected_spell_id,
        permissions=permission,
        contract_type=ContractTypes.received,
        reason=DetailReason.manual,
        sources=sources,
    )


def _spell_detail(index, permission=Permissions.read):
    return Detail(
        spell_index=index,
        spell_id=index.selected_spell_id,
        permissions=permission,
        contract_type=ContractTypes.received,
        reason=DetailReason.manual,
    )


# --- index-link maps -------------------------------------------------------

def test_get_index_detail_map_returns_per_ward_map():
    contract, wa, wb = _contract()
    assert contract._get_index_detail_map(wa) is contract._index_details_a
    assert contract._get_index_detail_map(wb) is contract._index_details_b


def test_get_index_detail_map_invalid_ward_raises():
    contract, wa, wb = _contract()
    with pytest.raises(ValueError):
        contract._get_index_detail_map(object())


def test_add_index_new_returns_true():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    assert contract._add_index(wa, _index_detail(idx)) is True
    assert idx.id in contract._index_details_a


def test_add_index_merge_same_permission_returns_false():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add_index(wa, _index_detail(idx, Permissions.read))
    # Same index id + same permission -> merge, not a new insert.
    assert contract._add_index(wa, _index_detail(idx, Permissions.read)) is False


def test_add_index_different_permission_raises():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add_index(wa, _index_detail(idx, Permissions.read))
    with pytest.raises(RuntimeError):
        contract._add_index(wa, _index_detail(idx, Permissions.create))


def test_add_index_merges_sources_into_existing():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    first = _index_detail(idx, Permissions.read, sources={"root-a"})
    contract._add_index(wa, first)
    contract._add_index(wa, _index_detail(idx, Permissions.read, sources={"root-b"}))
    assert first.sources == {"root-a", "root-b"}


def test_remove_index_deletes_entry():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add_index(wa, _index_detail(idx))
    contract._remove_index(wa, idx.id)
    assert idx.id not in contract._index_details_a


def test_remove_index_is_idempotent():
    contract, wa, wb = _contract()
    contract._remove_index(wa, "no-such-index")  # must not raise


def test_check_index_exists_tracks_add_remove():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    assert contract._check_index_exists(wa, idx.id) is False
    contract._add_index(wa, _index_detail(idx))
    assert contract._check_index_exists(wa, idx.id) is True
    contract._remove_index(wa, idx.id)
    assert contract._check_index_exists(wa, idx.id) is False


def test_index_maps_are_isolated_per_ward():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add_index(wa, _index_detail(idx))
    assert contract._check_index_exists(wa, idx.id) is True
    assert contract._check_index_exists(wb, idx.id) is False


# --- spell maps ------------------------------------------------------------

def test_add_spell_new_returns_true():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    assert contract._add(wa, _spell_detail(idx)) is True
    assert "v1" in contract._get_detail_map(wa)


def test_add_spell_merge_same_permission_returns_false():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add(wa, _spell_detail(idx, Permissions.read))
    assert contract._add(wa, _spell_detail(idx, Permissions.read)) is False


def test_add_spell_different_permission_raises():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add(wa, _spell_detail(idx, Permissions.read))
    with pytest.raises(RuntimeError):
        contract._add(wa, _spell_detail(idx, Permissions.create))


def test_remove_spell_deletes_entry():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add(wa, _spell_detail(idx))
    contract._remove(wa, "v1")
    assert "v1" not in contract._get_detail_map(wa)


def test_check_if_exists_and_permissions():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add(wa, _spell_detail(idx, Permissions.read))
    assert contract._check_if_exists(wa, "v1") is True
    assert contract._check_if_exists_and_permissions(wa, "v1", Permissions.read) is True
    assert contract._check_if_exists_and_permissions(wa, "v1", Permissions.create) is False


def test_spell_maps_are_isolated_per_ward():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    contract._add(wa, _spell_detail(idx))
    assert contract._check_if_exists(wa, "v1") is True
    assert contract._check_if_exists(wb, "v1") is False


# --- cleanup ---------------------------------------------------------------

def test_clean_up_disposes_index_and_spell_details():
    contract, wa, wb = _contract()
    idx = SpellIndex("v1")
    index_detail = _index_detail(idx)
    spell_detail = _spell_detail(idx)
    contract._add_index(wa, index_detail)
    contract._add(wb, spell_detail)
    contract.cleanup()
    # Both details were cleaned during teardown -> guarded methods now raise.
    with pytest.raises(RuntimeError):
        index_detail.has_spell("v1")
    with pytest.raises(RuntimeError):
        spell_detail.has_spell("v1")


def test_cleanup_is_idempotent():
    contract, wa, wb = _contract()
    contract.cleanup()
    contract.cleanup()  # second call must be a no-op
