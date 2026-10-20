"""S2 fix: import ManagedSpellMode at runtime beside Existence, so the bind verbs' VALUE-format signatures resolve.

At 0.2.8241 every annotation of Spellbook.bind / bind_inactive, Conduit.bind / bind_inactive, Spell.__init__,
scan_bind and ScanBindMetadata.__init__ resolved at runtime; the S2 TYPE_CHECKING-only ManagedSpellMode import made
`inspect.signature(...)` raise NameError for each. ManagedSpellMode is a dependency-free enum sibling of Existence,
which each module already imports at runtime for the same parameter.
"""
import pathlib

TYPE_CHECKING_LINE = "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n"
EXISTENCE_LINE = "from melder.aether.spellbook.existence.existence import Existence\n"
RUNTIME_LINE = "from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n"

for path_text in (
    "src/melder/aether/spellbook/spellbook.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/spellbook/spell.py",
    "src/melder/aether/spellbook/bind/scan.py",
    "src/melder/aether/spellbook/spellbinder.py",
):
    path = pathlib.Path(path_text)
    text = path.read_text(encoding="utf-8")
    assert text.count(TYPE_CHECKING_LINE) == 1, (path_text, "type-checking import")
    assert text.count(EXISTENCE_LINE) == 1, (path_text, "existence import")
    assert RUNTIME_LINE not in text.splitlines(keepends=True), (path_text, "already runtime")
    text = text.replace(TYPE_CHECKING_LINE, "", 1)
    text = text.replace(EXISTENCE_LINE, EXISTENCE_LINE + RUNTIME_LINE, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("edited", path_text)
