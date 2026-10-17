"""
Test doubles for fix #1's explicit index steps (run after codemod_tests.py).

Usage: python apply_test_doubles.py <root> [--check]

The ownership transfer's spell_id handles and the contract dependency walks now find a spell by spell_id and then
ask its index for the spell it has active: they read `Spell._spell_index_unless_cleaned()` and, in the walks, the
owner Book's `_find_spell(index)`. The unit doubles gain those two reads, mirroring the runtime contract (the index
while live, None once cleaned; the Book's active spell for the index under its lock), and the ward's transfer test
expects the spell the index step returns. Exact-once anchors; nothing is written when one misses, or with --check.
"""
import pathlib
import sys

WARD_CONTRACTS = "tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py"
WARD = "tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py"
TRANSFER = "tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py"
TRANSFER_CONTRACTS = "tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py"

BUILD_SPELL_OLD = """    spell._add_owned_conduit = _add_owned_conduit
    return spell
"""
BUILD_SPELL_NEW = """    def _spell_index_unless_cleaned() -> Optional[SpellIndex]:
        \"\"\"
        Return the spell's current index, as `Spell._spell_index_unless_cleaned` does for a live spell.

        Returns:
            Optional[SpellIndex]: The index the spell belongs to now.
        \"\"\"
        return spell.spell_index

    spell._add_owned_conduit = _add_owned_conduit
    spell._spell_index_unless_cleaned = _spell_index_unless_cleaned
    return spell
"""

EDITS = {
    WARD_CONTRACTS: [
        (
            """    def add_version(self, version_id: str) -> None:
        \"\"\"Advance the lineage to a new version for tests.\"\"\"
        self.spell_index.update(version_id)
        self.spell_id = version_id
""",
            """    def add_version(self, version_id: str) -> None:
        \"\"\"Advance the lineage to a new version for tests.\"\"\"
        self.spell_index.update(version_id)
        self.spell_id = version_id

    def _spell_index_unless_cleaned(self) -> Optional[SpellIndex]:
        \"\"\"Return this spell's index, or None once cleaned, as `Spell._spell_index_unless_cleaned` does.\"\"\"
        with self._lock:
            if self._cleaned:
                return None
            return self.spell_index
""",
        ),
        (
            """    def find_spell_by_spell_id(self, spell_id: str) -> Optional[FakeSpell]:
        \"\"\"Resolve a locally owned spell by spell_id, as Spellbook.find_spell_by_spell_id answers from its id maps.\"\"\"
        for spell in self._spells.values():
            if spell.spell_id == spell_id:
                return spell
        return None
""",
            """    def find_spell_by_spell_id(self, spell_id: str) -> Optional[FakeSpell]:
        \"\"\"Resolve a locally owned spell by spell_id, as Spellbook.find_spell_by_spell_id answers from its id maps.\"\"\"
        for spell in self._spells.values():
            if spell.spell_id == spell_id:
                return spell
        return None

    def _find_spell(self, spell_index: SpellIndex) -> Optional[FakeSpell]:
        \"\"\"Return the local spell an index has active, under the Book lock, as Spellbook._find_spell does.\"\"\"
        with self._lock:
            return self._spells.get(spell_index)
""",
        ),
    ],
    WARD: [
        (
            """    \"\"\"
    Verify _transfer_spell_ownership performs preflight and execute via TransferOfOwnership.
    \"\"\"
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
""",
            """    \"\"\"
    Verify _transfer_spell_ownership resolves a spell_id handle to the spell its index has active - the spell that
    owns the spell_id, then its index through `get_spell_by_index_id` - and performs preflight and execute via
    TransferOfOwnership.
    \"\"\"
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
""",
        ),
        (
            """    mock_transfer.assert_called_once_with(
        source_conduit=ward._conduit,
        target_conduit=target_conduit,
        spell=ward._conduit.get_spell_by_spell_id.return_value,
""",
            """    member = ward._conduit.get_spell_by_spell_id.return_value
    ward._conduit.get_spell_by_index_id.assert_called_once_with(
        member._spell_index_unless_cleaned.return_value.id
    )
    mock_transfer.assert_called_once_with(
        source_conduit=ward._conduit,
        target_conduit=target_conduit,
        spell=ward._conduit.get_spell_by_index_id.return_value,
""",
        ),
    ],
    TRANSFER: [(BUILD_SPELL_OLD, BUILD_SPELL_NEW)],
    TRANSFER_CONTRACTS: [(BUILD_SPELL_OLD, BUILD_SPELL_NEW)],
}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    if len(args) != 1:
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0]).resolve()
    out = {}
    for rel, edits in EDITS.items():
        raw = (root / rel).read_bytes()
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8").replace("\r\n", "\n") if crlf else raw.decode("utf-8")
        for old, new in edits:
            count = text.count(old)
            if count != 1:
                raise SystemExit(f"FAIL anchor count {count} in {rel}: {old[:80]!r}")
            text = text.replace(old, new)
        out[rel] = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
        print(f"ok {rel} edits={len(edits)} crlf={crlf}")
    if check:
        print("check only: nothing written")
        return
    for rel, data in out.items():
        (root / rel).write_bytes(data)
    print(f"written {len(out)} files")


if __name__ == "__main__":
    main()
