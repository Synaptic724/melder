"""S2 correction (owner, 2026-10-15: "use TYPECHECKING"): ManagedSpellMode goes back to a TYPE_CHECKING import.

Undoes s2_apply_runtime_mode_import.py: removes the runtime import beside Existence and restores the import inside
each module's TYPE_CHECKING block, at the place it had (before or after the named anchor line).
"""
import pathlib

RUNTIME_LINE = "from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode"
TYPE_CHECKING_LINE = "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode"

# (file, anchor line inside the TYPE_CHECKING block, insert "after" or "before" it)
PLACES = (
    ("src/melder/aether/spellbook/spellbook.py", "    from melder.aether.conduit.conduit import Conduit", "after"),
    ("src/melder/aether/conduit/conduit.py", "    from melder.aether.spellbook.bind.spell_index import SpellIndex", "after"),
    ("src/melder/aether/spellbook/spell.py", "    from melder.aether.spellbook.spellbook import Spellbook", "before"),
    ("src/melder/aether/spellbook/bind/scan.py", "    from melder.aether.spellbook.spellbook import Spellbook", "before"),
    ("src/melder/aether/spellbook/spellbinder.py", "    from melder.aether.spellbook.spell import Spell", "before"),
)

for path_text, anchor, where in PLACES:
    path = pathlib.Path(path_text)
    lines = path.read_text(encoding="utf-8").split("\n")
    assert lines.count(RUNTIME_LINE) == 1, (path_text, "runtime import")
    assert lines.count(TYPE_CHECKING_LINE) == 0, (path_text, "already TYPE_CHECKING")
    assert lines.count(anchor) == 1, (path_text, "anchor", lines.count(anchor))
    lines.remove(RUNTIME_LINE)
    at = lines.index(anchor)
    lines.insert(at + 1 if where == "after" else at, TYPE_CHECKING_LINE)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("reverted", path_text)
