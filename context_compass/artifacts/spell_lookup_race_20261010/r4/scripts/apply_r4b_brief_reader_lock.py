"""Variant R4b: Book lock held only while taking a one-call snapshot of _spells (probe loop outside the lock)."""
import pathlib
import sys

path = pathlib.Path(sys.argv[1]) / "src/melder/aether/spellbook/spellbook.py"
text = path.read_text(encoding="utf-8")
old = """        self.check_cleaned()
        for spell_index, spell in self._spells.items():
            # SpellIndex is responsible for telling us whether it owns this version
            if spell_index.has_spell(spell_id):
                return spell

        return None
"""
new = """        self.check_cleaned()
        with self._lock:
            entries = list(self._spells.items())
        for spell_index, spell in entries:
            # SpellIndex is responsible for telling us whether it owns this version
            if spell_index.has_spell(spell_id):
                return spell

        return None
"""
assert text.count(old) == 1
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("R4b applied")
