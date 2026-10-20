"""S8: the notch to 0.2.8248 and the running release note (exact replacements, LF).

Run from the repository root: python s8_notch_release_note.py
Refuses unless `__version__` reads 0.2.8247 (read at landing, never reserved) and every old text occurs once.
"""
import pathlib

VERSION = pathlib.Path("src/melder/__version__.py")
NOTE = pathlib.Path("release_docs/next_version_release.md")

SECTION = '''## A version staged before `conjure` melds after a notch

`bind_inactive` now behaves the same before and after `conjure()`. A version staged with `bind_inactive` on a
Spellbook before its `conjure()` was never wired to the root conduit, so once `notch_spell` made it the active
version, its first meld raised `RuntimeError` ("Spell has no configured CreationContextFactory.") whatever its
existence, and a managed version raised `MeldExecutionError` ("... has no pool to lease from ..."). Staging after
`conjure()` was the only way that worked. From 0.2.8248 `conjure()` wires every version staged before it, exactly as
`bind_inactive` wires one staged after it:

```python
book = md.Spellbook()
v1 = book.bind(spell=ReportService, existence="unique", binding_name="v1")
index = book.find_spell_by_id(v1).spell_index
v2 = book.bind_inactive(spell=ReportServiceV2, spell_index=index, existence="unique", binding_name="v2")
root = book.conjure(dynamic=True)           # wires v2 as well as v1

# after root.notch_spell(spell_index=index, spell=<v2's Spell>):
service = root.meld(spell_id=v2)            # a ReportServiceV2; RuntimeError before 0.2.8248
```

- Every existence: `unique`, `unique_per_conduit`, `many`, `managed_spell_quantity`, existing objects and
  functions. A managed version staged before `conjure()` has its pool from `conjure()` on, and
  `ReleaseManagedSpell().describe(cls)` lists it.
- Until its notch a staged version stays off resolution, as before: a meld of its id raises `KeyError` ("No spell
  found with spell_id ..."), and a staged existing object is not stored in the root's creations.
- The missing-pool message no longer names that cause or tells you to stage after `conjure()`: "Managed spell
  'Parser' has no pool to lease from: its owner root was torn down, or its owner store holds no pool for this
  version. Meld it through a live root that owns it."

What stays the same: active versions, a `bind_inactive` after `conjure()`, `notch_spell`, ownership transfers,
spell ids and records. Restore and the spell-index graft stage versions after `conjure()`, so they worked before and
behave as before.

## Packaging and documentation
'''

NOTE_EDITS = [
    ("# Melder 0.2.8247\n", "# Melder 0.2.8248\n"),
    ("- A version staged with `bind_inactive` before `conjure` carries no owner record; a transfer moves it as before.\n",
     "- A version staged with `bind_inactive` before `conjure` has carried an owner record since 0.2.8248 (`conjure`\n"
     "  gives it one), so a transfer moves that record like any other version's.\n"),
    ("Every managed spell version now has a pool in the store of the root conduit that owns it (0.2.8243): conjure\n"
     "gives each active version its pool, and so does a later `bind` or `bind_inactive` on the root.",
     "Every managed spell version now has a pool in the store of the root conduit that owns it (0.2.8243): conjure\n"
     "gives each version its pool - the active ones, and since 0.2.8248 the ones staged with `bind_inactive` before\n"
     "it - and so does a later `bind` or `bind_inactive` on the root."),
    ("  an object built fresh by own-parameter overrides gives that object to the pool when it is released.\n\n"
     "Pools follow an ownership transfer (0.2.8246).",
     "  an object built fresh by own-parameter overrides gives that object to the pool when it is released.\n"
     "- Compiled plans cached before managed spells existed are retired: the creation cache moves to generation 21\n"
     "  (0.2.8248). Every release change already makes the first `conjure()` after an upgrade compile cold, so nothing\n"
     "  else changes.\n\n"
     "Pools follow an ownership transfer (0.2.8246)."),
    ("## Packaging and documentation\n", SECTION),
    ("- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8247.\n",
     "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
     "  describe `conjure()` wiring the versions staged before it and the creation cache's generation 21; the code-map\n"
     "  extents of the five changed files are remeasured, and line citations into `spellbook.py`,\n"
     "  `spellbook_creation_system.py` and `transfer_of_ownership.py` that had drifted point at their code again.\n"
     "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8248.\n"),
]


def main() -> None:
    """Notch, then edit the note; nothing is written unless every check passes."""
    version = VERSION.read_bytes().decode("utf-8")
    if version.count('__version__ = "0.2.8247"\n') != 1:
        raise SystemExit("__version__ is not 0.2.8247: read it again and take the next number")
    note = NOTE.read_bytes().decode("utf-8")
    assert "\r\n" not in note and "\r\n" not in version
    for old, new in NOTE_EDITS:
        count = note.count(old)
        if count != 1:
            raise SystemExit(f"release note: expected one occurrence, found {count}: {old[:80]!r}")
        note = note.replace(old, new)
    VERSION.write_bytes(version.replace('__version__ = "0.2.8247"\n', '__version__ = "0.2.8248"\n').encode("utf-8"))
    NOTE.write_bytes(note.encode("utf-8"))
    long_lines = [n for n, line in enumerate(note.split("\n"), 1) if len(line) > 120]
    print("notched 0.2.8248; release note lines", len(note.split("\n")) - 1, "long lines", long_lines)


if __name__ == "__main__":
    main()
