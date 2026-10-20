"""
Apply R5 to a 3d184cac tree: R1's lock-free reader (one-call snapshot + cleanup-safe index probe) in
Spellbook.find_spell_by_id, plus R4's narrow publication lock in Spellbook.bind.
"""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
book_path = root / "src/melder/aether/spellbook/spellbook.py"
index_path = root / "src/melder/aether/spellbook/bind/spell_index.py"
book = book_path.read_text(encoding="utf-8")
index = index_path.read_text(encoding="utf-8")

edits_book = [
(
"""            - Ownership is decided by `SpellIndex.has_spell`, which tests
              MEMBERSHIP of the index's version lineage rather than equality
              with the currently selected id. A superseded or parked version id
""",
"""            - Ownership is decided by the index's membership test (the
              `SpellIndex.has_spell` semantics, read through
              `SpellIndex._has_spell_unless_cleaned`), which tests MEMBERSHIP of
              the index's version lineage rather than equality with the
              currently selected id. A superseded or parked version id
""",
),
(
"""        Threading:
            Does not acquire `self._lock`. The returned object is a live
            reference, so a concurrent removal or graft can invalidate it after
            this returns. Callers that need the result to stay valid must hold
            the lock across their own use of it.
""",
"""        Threading:
            Does not acquire `self._lock`, by design: conjure holds that lock
            while it waits on phase-scheduler workers and while it runs the
            conduit lifecycle hooks, and both can call this lookup from another
            thread (phase 4's ambiguity report does), so a lookup that waited for
            the lock would stall conjure. Every writer of the local spell map
            holds `self._lock`; this lookup walks a snapshot of the map taken in
            one call (`list(self._spells.items())`), so a concurrent bind,
            removal, notch or transfer can neither break the walk nor hide a
            registered spell whose index it leaves in place. The answer reflects
            the map at the snapshot: a spell bound after it is not seen by this
            call, and an index cleaned after it is skipped as owning nothing.
            A notch or an index-membership move of the searched lineage that
            overlaps the call can make it answer None: the snapshot can fall
            between the notch's park and promote, and a moved id can be read in
            neither index. A caller that needs a linearizable answer holds the
            lock across the call (it is reentrant).
            The returned `Spell` is a borrowed reference, not a lease: once this
            returns, a concurrent removal, notch or transfer can retire or move
            it. Callers that need it to stay valid must hold the lock across
            their own use of it.
""",
),
(
"""        self.check_cleaned()
        for spell_index, spell in self._spells.items():
            # SpellIndex is responsible for telling us whether it owns this version
            if spell_index.has_spell(spell_id):
                return spell

        return None
""",
"""        self.check_cleaned()
        # Walk a snapshot taken in one call, never the live map, and take no lock:
        # conjure holds `self._lock` while phase workers and lifecycle hooks may call
        # this from other threads. Walking the live dict while a writer changed it
        # raised "dictionary changed size during iteration", or - when a removal and
        # a bind left its size unchanged but resized it - silently skipped entries and
        # answered None for a registered spell. `list(dict.items())` copies the
        # entries inside one C call that holds the dict throughout (its critical
        # section on free-threaded builds) and runs no Python code, so no insert or
        # pop can interleave with it.
        for spell_index, spell in list(self._spells.items()):
            # SpellIndex is responsible for telling us whether it owns this version.
            # An index removed after the snapshot is cleaned outside the Spellbook
            # lock; a cleaned index owns nothing, so the probe answers False for it
            # instead of raising.
            if spell_index._has_spell_unless_cleaned(spell_id):
                return spell

        return None
""",
),
(
"""                registration_started = True
                self._lookup_spells[new_spell._key] = spell_index
                self._spells[spell_index] = new_spell
                self._register_owned_spell_id(new_spell.spell_id, new_spell)
""",
"""                registration_started = True
                # Publish into the four active maps under the Book lock, as every other
                # writer of `_spells` does (removal, notch park and promote, index
                # destruction, transfer and its rollback), so walks that hold the lock
                # never meet this insert mid-walk. Narrow on purpose: claim_lookup above
                # and the registration callbacks below stay outside it. It adds no
                # lock-order edge: _register_owned_spell_id always took this lock here.
                with self._lock:
                    self._lookup_spells[new_spell._key] = spell_index
                    self._spells[spell_index] = new_spell
                    self._register_owned_spell_id(new_spell.spell_id, new_spell)
""",
),
]
for old, new in edits_book:
    assert book.count(old) == 1, old[:70]
    book = book.replace(old, new, 1)

old_index = """        with self._lock:
            return spell_id in self._spells_in_index

    def is_empty(self) -> bool:
"""
new_index = '''        with self._lock:
            return spell_id in self._spells_in_index

    def _has_spell_unless_cleaned(self, spell_id: str) -> bool:
        """
        Internal

        Return whether `spell_id` is a member of this index, answering False once
        the index is cleaned.

        Purpose:
            Membership probe for lock-free walks over spell maps
            (`Spellbook.find_spell_by_id`), which can reach an index after its
            removal cleaned it outside the Spellbook lock. A cleaned index owns
            nothing, so for such a walk "not a member" is the truthful answer,
            where `has_spell` raises.

        Contract:
            - Same membership semantics as `has_spell` (the whole version
              lineage, not only the selected id) while the index is live.
            - Never raises for a cleaned index; returns False.

        Threading:
            Reads the cleaned flag and the member set under `self._lock`, the lock
            `cleanup` holds while it marks the index cleaned and deletes the
            member set, so a concurrent cleanup cannot tear the answer.

        Args:
            spell_id (str): The spell id to check.

        Returns:
            bool: True if this live index's member set contains `spell_id`;
            False otherwise, and False once the index is cleaned.
        """
        with self._lock:
            if self._cleaned:
                return False
            return spell_id in self._spells_in_index

    def is_empty(self) -> bool:
'''
assert index.count(old_index) == 1
index = index.replace(old_index, new_index, 1)
book_path.write_text(book, encoding="utf-8")
index_path.write_text(index, encoding="utf-8")
print("R5 applied to", root)
