"""
Unit tests for `IndexDetail` -- the index-link contract detail.

Covers the SpellIndex-contract ("index-link") detail object in isolation:
construction + type validation, the live-index membership oracle (`has_spell`),
selected-head repointing, source refcounting, cleanup/teardown, and the
regression guard that the reverted `_member_ids` tracking stays gone (the index
itself is the sole membership oracle).

Runtime: authored for Python 3.14t; these import the real melder modules which
require 3.14 deferred annotations, so they are executed by the user on 3.14t.
"""

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.conduit.conduit_ward.contract.details import IndexDetail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason


def _make_index(initial_id: str = "v1") -> SpellIndex:
    """Build a fresh single-member SpellIndex for detail construction."""
    return SpellIndex(initial_id)


def _make_detail(
    index: SpellIndex,
    permission: Permissions = Permissions.read,
    contract_type: ContractTypes = ContractTypes.received,
    reason: DetailReason = DetailReason.manual,
) -> IndexDetail:
    """Build an IndexDetail over `index` with the given grant metadata."""
    return IndexDetail(
        spell_index=index,
        selected_spell_id=index.selected_spell_id,
        permissions=permission,
        contract_type=contract_type,
        reason=reason,
    )


def test_init_sets_core_fields():
    idx = _make_index("v1")
    detail = _make_detail(idx, Permissions.read, ContractTypes.received, DetailReason.manual)
    assert detail.spell_index is idx
    assert detail.selected_spell_id == "v1"
    assert detail.permissions is Permissions.read
    assert detail.contract_type is ContractTypes.received
    assert detail.reason is DetailReason.manual


def test_init_default_reason_and_empty_sources():
    idx = _make_index("v1")
    detail = IndexDetail(
        spell_index=idx,
        selected_spell_id="v1",
        permissions=Permissions.create,
        contract_type=ContractTypes.initiated,
    )
    assert detail.reason is DetailReason.other
    assert detail.sources == set()


def test_init_preserves_supplied_sources():
    idx = _make_index("v1")
    detail = IndexDetail(
        spell_index=idx,
        selected_spell_id="v1",
        permissions=Permissions.read,
        contract_type=ContractTypes.received,
        sources={"root-a", "root-b"},
    )
    assert detail.sources == {"root-a", "root-b"}


def test_permissions_create_and_block_stored():
    idx = _make_index("v1")
    d_create = _make_detail(idx, Permissions.create)
    d_block = _make_detail(_make_index("w1"), Permissions.block)
    assert d_create.permissions is Permissions.create
    assert d_block.permissions is Permissions.block


def test_index_id_matches_index_id():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    assert detail.index_id == idx.id


def test_has_spell_reads_live_member_set():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    assert detail.has_spell("v1") is True
    assert detail.has_spell("missing") is False


def test_has_spell_follows_index_after_update():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    # The detail tracks the index, not a snapshot: a new member is visible at once.
    idx.update("v2")
    assert detail.has_spell("v2") is True
    assert detail.has_spell("v1") is True


def test_has_spell_follows_index_after_add_member():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    idx.add_member("v2")
    assert detail.has_spell("v2") is True
    # add_member does not move the selected head.
    assert detail.selected_spell_id == "v1"


def test_update_selected_repoints_head():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.update_selected("v2")
    assert detail.selected_spell_id == "v2"


def test_add_source_records_root():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.add_source("root-a")
    assert "root-a" in detail.sources


def test_add_source_none_is_ignored():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.add_source(None)
    assert detail.sources == set()


def test_remove_source_returns_true_when_emptied():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.add_source("root-a")
    assert detail.remove_source("root-a") is True
    assert detail.sources == set()


def test_remove_source_returns_false_when_sources_remain():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.add_source("root-a")
    detail.add_source("root-b")
    assert detail.remove_source("root-a") is False
    assert detail.sources == {"root-b"}


def test_remove_source_none_returns_false():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    assert detail.remove_source(None) is False


def test_type_validation_spell_index():
    with pytest.raises(TypeError):
        IndexDetail(
            spell_index="not-a-spell-index",
            selected_spell_id="v1",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
        )


def test_type_validation_permissions():
    idx = _make_index("v1")
    with pytest.raises(TypeError):
        IndexDetail(
            spell_index=idx,
            selected_spell_id="v1",
            permissions="read",
            contract_type=ContractTypes.received,
        )


def test_type_validation_contract_type():
    idx = _make_index("v1")
    with pytest.raises(TypeError):
        IndexDetail(
            spell_index=idx,
            selected_spell_id="v1",
            permissions=Permissions.read,
            contract_type="received",
        )


def test_type_validation_reason():
    idx = _make_index("v1")
    with pytest.raises(TypeError):
        IndexDetail(
            spell_index=idx,
            selected_spell_id="v1",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            reason="manual",
        )


def test_type_validation_sources_must_be_set():
    idx = _make_index("v1")
    with pytest.raises(TypeError):
        IndexDetail(
            spell_index=idx,
            selected_spell_id="v1",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            sources=["root-a"],
        )


def test_cleanup_is_idempotent_and_retains_lock():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.cleanup()
    assert detail._lock is not None
    detail.cleanup()  # second call is a no-op, must not raise


def test_cleanup_drops_index_reference_but_not_the_index():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.cleanup()
    # The IndexDetail borrows the index; cleanup drops the ref only.
    assert not hasattr(detail, "spell_index")
    # The borrowed index itself is owner-owned and stays usable.
    assert idx.has_spell("v1") is True


def test_methods_raise_after_cleanup():
    idx = _make_index("v1")
    detail = _make_detail(idx)
    detail.cleanup()
    with pytest.raises(RuntimeError):
        _ = detail.index_id
    with pytest.raises(RuntimeError):
        detail.update_selected("v2")
    with pytest.raises(RuntimeError):
        detail.has_spell("v1")


def test_no_member_ids_tracking_regression():
    # Reverted over-tracking: the index (_spells_in_index) is the sole member
    # oracle, so IndexDetail must NOT carry a member set or its accessors.
    idx = _make_index("v1")
    detail = _make_detail(idx)
    assert not hasattr(detail, "_member_ids")
    assert "_member_ids" not in IndexDetail.__slots__
    assert not hasattr(detail, "add_member")
    assert not hasattr(detail, "member_ids")
