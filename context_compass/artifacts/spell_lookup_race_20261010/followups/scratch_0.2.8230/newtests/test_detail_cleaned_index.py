"""
Unit tests - contract details over an index its owner has cleaned (0.2.8230).

A `Detail` or `IndexDetail` holds the lineage's `SpellIndex`, which belongs to the Book that owns the lineage
and can be cleaned while the detail still holds it. Their `has_spell` reads membership through the index's
cleanup-safe probe, under the index lock, so a cleaned index answers False instead of raising AttributeError
for the member set its cleanup deleted.
"""

import pytest

from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.contract.details import Detail, IndexDetail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex


@pytest.mark.parametrize("detail_class", [Detail, IndexDetail])
def test_detail_has_spell_answers_false_once_the_owner_cleaned_the_index(detail_class: type) -> None:
    """
    Purpose:
        Pin both contract rows' membership answer across the owner's index cleanup.
    Contract:
        While the index is live the detail answers its lineage; once the owning Book cleans the index the
        detail, still live itself, answers False for the same id and does not raise.
    Args:
        detail_class: `Detail` (version snapshot row) or `IndexDetail` (subscription row).
    Raises:
        AssertionError: If the live answer is wrong, or the cleaned index raises or answers True.
    """
    index = SpellIndex("v1")
    index.add_member("v2")
    detail = detail_class(index, "v1", Permissions.read, ContractTypes.received, DetailReason.manual)
    try:
        assert detail.has_spell("v1") is True
        assert detail.has_spell("v2") is True
        assert detail.has_spell("v3") is False

        index.cleanup()

        assert detail.has_spell("v1") is False
        assert detail.has_spell("v2") is False
    finally:
        detail.cleanup()
