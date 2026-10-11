"""
Update existing tests whose assertions pin behaviour 0.2.8231 changes on purpose.

Usage: python apply_test_updates.py <tree root holding tests/>
"""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
path = root / "tests/unit/melder/aether/test_aetheric_frame.py"
data = path.read_bytes().decode("utf-8")
eol = "\r\n" if "\r\n" in data else "\n"
old_doc = "    - Lock is nulled." + eol
new_doc = ("    - The lock is kept: the cleanup-safe frame probes take it on a cleaned frame" + eol
           + "      (cross_object_lock_gaps, 0.2.8231)." + eol)
old_assert = "    assert not hasattr(frame, '_lock')" + eol
new_assert = "    assert isinstance(frame._lock, type(threading.RLock()))" + eol
assert data.count(old_doc) == 1 and data.count(old_assert) == 1
data = data.replace(old_doc, new_doc).replace(old_assert, new_assert)
path.write_bytes(data.encode("utf-8"))
print("updated", path.relative_to(root))

# The contract listing resolves through the Book (find_spell_by_id outbound, the per-peer contracted lookup inbound)
# instead of the Conduit lookups, which take the conduit lock (cross_object_lock_gaps, 0.2.8231).
path = root / "tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py"
data = path.read_bytes().decode("utf-8")
eol = "\r\n" if "\r\n" in data else "\n"
text = data.replace("\r\n", "\n")
old_add_local = '''    def add_local_spell(self, spell: FakeSpell) -> None:
        """Register a locally owned spell for lineage checks."""
'''
new_add_local = '''    def find_spell_by_id(self, spell_id: str) -> Optional[FakeSpell]:
        """Resolve a locally owned spell by version id, as Spellbook.find_spell_by_id answers from its id maps."""
        for spell in self._spells.values():
            if spell.spell_id == spell_id:
                return spell
        return None

    def add_local_spell(self, spell: FakeSpell) -> None:
        """Register a locally owned spell for lineage checks."""
'''
assert text.count(old_add_local) == 1
text = text.replace(old_add_local, new_add_local)
# New annotations use Optional, not PEP 604 (synaptic typing rule); this file had no typing import.
old_import = "from types import SimpleNamespace\n"
assert text.count(old_import) == 1
text = text.replace(old_import, old_import + "from typing import Optional\n")
old_test = '''def test_get_spells_in_contract_by_conduit_skips_outbound_resolution_exception(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """Verify outbound spell resolution exceptions are skipped instead of propagating."""
'''
new_test = '''def test_get_spells_in_contract_by_conduit_resolves_outbound_through_the_book_not_the_conduit_lookup(
    linked_pair: tuple[FakeConduit, FakeConduit],
) -> None:
    """
    Verify outbound spells are answered from this conduit's Book, never through the Conduit lookup.

    The listing holds the ward lock; the Conduit lookups take the conduit lock, which link and sever take before
    the ward lock, so calling them here deadlocked with a concurrent sever (cross_object_lock_gaps, 0.2.8231).
    A failing Conduit lookup therefore no longer matters: it is not called.
    """
'''
assert text.count(old_test) == 1
text = text.replace(old_test, new_test)
old_tail = '''    borrower.get_spell_by_id = MagicMock(side_effect=RuntimeError("lookup boom"))

    result = borrower._conduit_ward._get_spells_in_contract_by_conduit(owner._id)

    inbound = {sid: found for sid, found in result["inbound"]}
    assert inbound[inbound_spell.spell_id] is inbound_spell
    assert result["outbound"] == []
'''
new_tail = '''    borrower.get_spell_by_id = MagicMock(side_effect=RuntimeError("lookup boom"))

    result = borrower._conduit_ward._get_spells_in_contract_by_conduit(owner._id)

    inbound = {sid: found for sid, found in result["inbound"]}
    outbound = {sid: found for sid, found in result["outbound"]}
    assert inbound[inbound_spell.spell_id] is inbound_spell
    assert outbound[outbound_spell.spell_id] is outbound_spell
    borrower.get_spell_by_id.assert_not_called()
'''
assert text.count(old_tail) == 1
text = text.replace(old_tail, new_tail)
path.write_bytes(text.replace("\n", eol).encode("utf-8"))
print("updated", path.relative_to(root))
