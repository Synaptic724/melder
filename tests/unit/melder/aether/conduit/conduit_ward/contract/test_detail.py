"""
Unit tests for the spell-level `Detail` contract entry.

`Detail` snapshots a contracted spell version: it carries the lineage
(`spell_index`), the captured `spell_id`, the granted `permissions`, the
`contract_type` direction, a `reason`, and refcount `sources`. `has_spell`
reads the live lineage member set. These are the per-member entries the
index-link auto-generates as bookkeeping.

Runtime: authored for Python 3.14t (import needs 3.14 deferred annotations).
"""

import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason


def _make_detail(
    index: SpellIndex,
    permission: Permissions = Permissions.read,
) -> Detail:
    """Build a Detail over `index`'s selected spell id."""
    return Detail(
        spell_index=index,
        spell_id=index.selected_spell_id,
        permissions=permission,
        contract_type=ContractTypes.received,
        reason=DetailReason.manual,
    )


def test_init_sets_core_fields():
    idx = SpellIndex("v1")
    detail = _make_detail(idx, Permissions.create)
    assert detail.spell_index is idx
    assert detail.spell_id == "v1"
    assert detail.permissions is Permissions.create
    assert detail.contract_type is ContractTypes.received
    assert detail.reason is DetailReason.manual


def test_init_default_reason_and_empty_sources():
    idx = SpellIndex("v1")
    detail = Detail(
        spell_index=idx,
        spell_id="v1",
        permissions=Permissions.read,
        contract_type=ContractTypes.initiated,
    )
    assert detail.reason is DetailReason.other
    assert detail.sources == set()


def test_has_spell_reads_live_member_set():
    idx = SpellIndex("v1")
    detail = _make_detail(idx)
    assert detail.has_spell("v1") is True
    assert detail.has_spell("missing") is False
    idx.update("v2")
    assert detail.has_spell("v2") is True


def test_add_and_remove_source_refcount():
    idx = SpellIndex("v1")
    detail = _make_detail(idx)
    detail.add_source("root-a")
    detail.add_source("root-b")
    assert detail.sources == {"root-a", "root-b"}
    assert detail.remove_source("root-a") is False
    assert detail.remove_source("root-b") is True
    assert detail.sources == set()


def test_add_source_none_ignored():
    idx = SpellIndex("v1")
    detail = _make_detail(idx)
    detail.add_source(None)
    assert detail.sources == set()


def test_type_validation_spell_index():
    with pytest.raises(TypeError):
        Detail(
            spell_index="nope",
            spell_id="v1",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
        )


def test_type_validation_permissions():
    idx = SpellIndex("v1")
    with pytest.raises(TypeError):
        Detail(
            spell_index=idx,
            spell_id="v1",
            permissions="read",
            contract_type=ContractTypes.received,
        )


def test_type_validation_contract_type():
    idx = SpellIndex("v1")
    with pytest.raises(TypeError):
        Detail(
            spell_index=idx,
            spell_id="v1",
            permissions=Permissions.read,
            contract_type="received",
        )


def test_cleanup_idempotent_and_retains_lock():
    idx = SpellIndex("v1")
    detail = _make_detail(idx)
    detail.cleanup()
    assert detail._lock is not None
    detail.cleanup()


def test_has_spell_raises_after_cleanup():
    idx = SpellIndex("v1")
    detail = _make_detail(idx)
    detail.cleanup()
    with pytest.raises(RuntimeError):
        detail.has_spell("v1")
