"""Derive the R4' and negative-control scratch trees from cand_r4 and cand_r5 (exact, asserted replacements)."""
import pathlib
import shutil
import sys

base = pathlib.Path("/tmp/cc_lookup")
BOOK = "src/melder/aether/spellbook/spellbook.py"
STRATEGY = "src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py"


def derive(source: str, target: str, edits: list) -> None:
    """Copy `source` to `target` and apply (relative path, old, new) edits, each matching exactly once."""
    dst = base / target
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(base / source, dst, symlinks=True)
    for rel, old, new in edits:
        path = dst / rel
        text = path.read_text(encoding="utf-8")
        assert text.count(old) == 1, (target, rel, old[:60])
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("built", target)


# R4': R4 plus phase 4's ambiguity report reading the warm pool instead of find_spell_by_id.
derive("cand_r4", "cand_r4p", [(
    STRATEGY,
    '            candidate: "Spell | None" = spellbook.find_spell_by_id(candidate_id) if spellbook is not None else None\n',
    '            # One read of the warm pool (owned and contracted active spells by current id), not\n'
    '            # find_spell_by_id: conjure holds the Book lock while phase 4 runs on scheduler workers.\n'
    '            candidate: "Spell | None" = spellbook._spell_id_pool.get(candidate_id) if spellbook is not None else None\n',
)])

# NC1: R5 without the snapshot - the writer lock and the cleanup-safe probe over a live, unlocked walk.
derive("cand_r5", "cand_nc1", [(
    BOOK,
    "        for spell_index, spell in list(self._spells.items()):\n",
    "        for spell_index, spell in self._spells.items():\n",
)])

# NC2: R5 without the cleanup-safe probe - the snapshot walked with has_spell.
derive("cand_r5", "cand_nc2", [(
    BOOK,
    "            if spell_index._has_spell_unless_cleaned(spell_id):\n",
    "            if spell_index.has_spell(spell_id):\n",
)])

# NC3: R4's reader lock without the bind publication lock (the reviewer's negative control).
derive("cand_r4", "cand_nc3", [(
    BOOK,
    "                with self._lock:\n"
    "                    self._lookup_spells[new_spell._key] = spell_index\n"
    "                    self._spells[spell_index] = new_spell\n"
    "                self._register_owned_spell_id(new_spell.spell_id, new_spell)\n",
    "                self._lookup_spells[new_spell._key] = spell_index\n"
    "                self._spells[spell_index] = new_spell\n"
    "                self._register_owned_spell_id(new_spell.spell_id, new_spell)\n",
)])
