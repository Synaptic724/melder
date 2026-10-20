"""Apply R4 (reviewer design: Book lock across find_spell_by_id's walk + narrow lock at bind publication)."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
path = root / "src/melder/aether/spellbook/spellbook.py"
text = path.read_text(encoding="utf-8")

old_doc = """        Threading:
            Does not acquire `self._lock`. The returned object is a live
            reference, so a concurrent removal or graft can invalidate it after
            this returns. Callers that need the result to stay valid must hold
            the lock across their own use of it.
"""
new_doc = """        Threading:
            Holds `self._lock` across the walk, so the selection is made against
            one consistent state of this Book's active map: every writer of that
            map holds the same lock (bind's publication, removal, notch park and
            promote, index destruction, and ownership transfer and its rollback).
            The lock is reentrant, so a caller that already holds it may call
            this. `SpellIndex.has_spell` takes each index's own lock inside the
            walk; index locks are leaves and call out to nothing.
            The returned `Spell` is a borrowed reference, not a lease: once this
            returns, a concurrent removal, notch or transfer can retire or move
            it. Callers that need it to stay valid must hold the lock across
            their own use of it.
"""
old_body = """        self.check_cleaned()
        for spell_index, spell in self._spells.items():
            # SpellIndex is responsible for telling us whether it owns this version
            if spell_index.has_spell(spell_id):
                return spell

        return None
"""
new_body = """        self.check_cleaned()
        with self._lock:
            for spell_index, spell in self._spells.items():
                # SpellIndex is responsible for telling us whether it owns this version
                if spell_index.has_spell(spell_id):
                    return spell

        return None
"""
old_bind = """                registration_started = True
                self._lookup_spells[new_spell._key] = spell_index
                self._spells[spell_index] = new_spell
                self._register_owned_spell_id(new_spell.spell_id, new_spell)
"""
new_bind = """                registration_started = True
                # Publish into the active maps under the Book lock: find_spell_by_id
                # walks `_spells` under it, and every other writer of the map holds it.
                # Narrow on purpose: claim_lookup above and the registration callbacks
                # below run outside it.
                with self._lock:
                    self._lookup_spells[new_spell._key] = spell_index
                    self._spells[spell_index] = new_spell
                self._register_owned_spell_id(new_spell.spell_id, new_spell)
"""
for old, new in ((old_doc, new_doc), (old_body, new_body), (old_bind, new_bind)):
    assert text.count(old) == 1, old[:60]
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
print("R4 applied to", path)
