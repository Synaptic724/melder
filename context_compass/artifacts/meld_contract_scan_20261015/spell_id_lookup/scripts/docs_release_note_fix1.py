"""
The running release note for fix #1 (find_spell_by_spell_id_2026_10_17): exact-once edits, all or nothing.

melder_1 (synaptic_python_developer), 2026-10-17. Usage: python docs_release_note_fix1.py <repo_root> [--check]

Header 0.2.8253 (the notch); a new Breaking section after the lookup section of 0.2.8229-0.2.8230; that section,
the 0.2.8249 notch section and the 0.2.8250 contract section renamed to the new lookups, their parked-spell_id
sentences put in the past; the four examples that call a lookup renamed; the notch refusal's message as the source
words it now; a Packaging bullet for the system documents and graph, one for the guides and walkthroughs, and the
rebuild line at 0.2.8253. The note is LF; every new line stays within 120 characters.
"""
import pathlib
import sys

DOC = "release_docs/next_version_release.md"


def T(s: str) -> str:
    """Drop the newline that follows an opening triple quote, so a block reads as it will be written."""
    return s[1:] if s.startswith("\n") else s


NEW_SECTION = T("""
## A spell_id lookup answers the spell it names: `find_spell_by_spell_id` and `get_spell_by_spell_id`

**Breaking change:** `Spellbook.find_spell_by_id` and `Conduit.get_spell_by_id` are renamed `find_spell_by_spell_id`
and `get_spell_by_spell_id`, with no alias - the old names raise `AttributeError`; the arguments are the same - and
they answer exactly the spell a spell_id names. A spell_id, the id `bind` and `bind_inactive` return, names one
version, and the lookups return that version, active or parked. Until 0.2.8253 a parked spell_id - a version staged
with `bind_inactive`, or one a notch moved away from - answered with the version its spell index had active in its
place. What an index has active is a lookup by the index:

```python
class ReportService:
    def render(self) -> str:
        return "v1"


class ReportServiceV2:
    def render(self) -> str:
        return "v2"


book = md.Spellbook()
v1 = book.bind(spell=ReportService, existence="unique")
reports = book.conjure(dynamic=True, name="reports")
index = reports.get_spell_by_spell_id(v1).spell_index
v2 = reports.bind_inactive(spell=ReportServiceV2, spell_index=index, existence="unique")

assert reports.get_spell_by_spell_id(v2).spell_id == v2        # the parked version; the old lookup answered v1
assert book.find_spell_by_spell_id(v2).spell_id == v2
assert reports.get_spell_by_index_id(index.id).spell_id == v1  # the version the index has active

reports.notch_spell(spell_index=index, spell=reports.get_spell_by_spell_id(v2))   # a no-op with the old lookup
assert reports.meld(spell_id=v2).render() == "v2"
```

- Code that passed a parked spell_id to reach the current version asks the index instead:
  `conduit.get_spell_by_index_id(conduit.get_spell_by_spell_id(spell_id).spell_index.id)`.
- `Conduit.get_spell_permissions(spell_id)` answers the permissions that version was bound with (for a parked
  spell_id it answered the active version's).
- `find_spell_by_spell_id` also answers a version moved out with `remove_from_spell_index` into an index of its own
  (it returned `None`). `get_spell_by_spell_id` still raises `ValueError` ("Spell version <id> not found in any
  conduit.") for such a version, because the index the move creates is missing from the frame's registry - a
  separate defect, with its own fix pending.
- `add_spell_to_contract(spell_id=...)` and `remove_spell_from_contract(spell_id=...)` take a parked spell_id. They
  raised `RuntimeError` "Provided spell_id '<parked>' does not match inspected ID '<active>'."; a grant now parks
  the copy on the borrower, as a grant of the parked `Spell` does. `get_spells_in_contract_by_conduit` lists each
  version this conduit granted with that version's own `Spell` (a parked grant was listed with the active one's).
- `transfer_spell_ownership(spell_id=...)` still moves the spell index the spell_id belongs to, with the version
  that index has active on this conduit. A spell_id this conduit cannot resolve to an active version of its index -
  another conduit's spell whose index this conduit neither owns nor borrows - is refused up front with
  `RuntimeError` "[CONDUIT] Transfer-ownership could not resolve the source spell on this conduit.", where the
  transfer failed later with "Source conduit does not own the spell.".
- In Rift rooms the command `get_spell_by_id` is now `get_spell_by_spell_id`, listed under that name by
  `list_supported_command_methods`, and both it and `get_spell_by_source_id` answer the spell their argument names:
  a capability or codegen room returns the `Spell`, a static room its live object. Nexus publishes the version each
  index has active, so a room refuses a parked version's spell_id or source id instead of answering another
  version. A static room's refusals name what was asked - "Spell id '<id>' is not live in frame '<frame>'." and
  "Spell '<source_id>' ..." where they said "Spell index '<index id>' ..."; a lookup by index id keeps that wording.

What stays the same: an active version's spell_id answers as before; a spell_id the Book does not own returns `None`
from `find_spell_by_spell_id`, and `get_spell_by_spell_id` raises `ValueError` for one no conduit of the frame
claims; neither takes a lock. `get_spell_by_index_id`, ownership transfers and dependency grants answer as before.
The contract lookups that resolve a granted spell_id through its index - `get_spell_in_contracts` and the versions
a conduit was granted in `get_spells_in_contract_by_conduit` - are unchanged. Nothing recorded, cached or persisted
changes.

""")

EDITS = [
    ("# Melder 0.2.8252\n\n**Unreleased**\n", "# Melder 0.2.8253\n\n**Unreleased**\n"),
    (T("""
`Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` on top of it, used to walk the Book's index map while
other threads bound, removed or parked spells. On the free-threaded build a lookup of a spell nobody was touching
could then raise `RuntimeError: dictionary changed size during iteration`, raise
`AttributeError: 'SpellIndex' object has no attribute '_spells_in_index'`, or return `None` for a spell that was
still registered. The lookup now answers from the Book's id maps: one read for a current version id, three for a
superseded or parked one, the same cost at any Book size, and no lock taken.
"""), T("""
`Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` on top of it (`find_spell_by_spell_id` and
`get_spell_by_spell_id` since 0.2.8253, next section), used to walk the Book's index map while other threads bound,
removed or parked spells. On the free-threaded build a lookup of a spell nobody was touching could then raise
`RuntimeError: dictionary changed size during iteration`, raise
`AttributeError: 'SpellIndex' object has no attribute '_spells_in_index'`, or return `None` for a spell that was
still registered. The lookup now answers from the Book's id maps: one read for an active version's spell_id, two
for a parked one, the same cost at any Book size, and no lock taken.
""")),
    (T("""
What stays the same: any id in a spell's version lineage resolves to the live spell that represents it now -
after a notch, an index move or an ownership transfer too - and an id the Book does not own still returns `None`,
as does a parked version moved out into an index of its own. Two answers sharpen: a parked version disposed while
a lookup runs returns `None` instead of raising, and a lookup that lands inside a notch or an ownership transfer
of that same lineage can return `None` for that instant, as a lookup inside a notch already could. The returned
spell is a reference you borrow, not a lease: a later removal, notch or transfer can retire or move it.
"""), T("""
What stays the same: a spell_id the Book does not own still returns `None`. Two answers sharpen: a parked version
disposed while a lookup runs no longer makes it raise - the lookup returns the spell it read, or `None` once the
spell_id has left the Book - and a lookup that lands inside a notch or an ownership transfer of that same spell can
return `None` for that instant, as a lookup inside a notch already could. The returned spell is a reference you
borrow, not a lease: a later removal, notch or transfer can retire or move it. What a spell_id answers changed at
0.2.8253 (next section).
""")),
    (T("""
`Conduit.get_spell_by_id` and `Conduit.get_conduit_by_spell_id` keep raising `ValueError` for an id no conduit in
the frame claims, as `get_*` lookups do (a `find_*` lookup returns `None`); their docstrings said they return
`None`, and now document the raise. `get_conduit_by_spell_id` is annotated as returning a `Conduit`.
"""), T("""
`Conduit.get_spell_by_spell_id` (`get_spell_by_id` until 0.2.8253) and `Conduit.get_conduit_by_spell_id` keep
raising `ValueError` for an id no conduit in the frame claims, as `get_*` lookups do (a `find_*` lookup returns
`None`); their docstrings said they return `None`, and now document the raise. `get_conduit_by_spell_id` is
annotated as returning a `Conduit`.
""")),
    ("\n## Index links, contract reads and binds across frames hold up under concurrent changes\n",
     "\n" + NEW_SECTION + "## Index links, contract reads and binds across frames hold up under concurrent changes\n"),
    ("index = book.find_spell_by_id(v1).spell_index\n", "index = book.find_spell_by_spell_id(v1).spell_index\n"),
    (T("""
`Conduit.notch_spell` makes one version of a spell index the active one - the notch in stage -> notch -> meld. Until
0.2.8249 it took only the version's `Spell`, and no public call returns the `Spell` of a staged version:
`bind_inactive` returns a spell_id, and `get_spell_by_id` / `find_spell_by_id` answer a staged (parked) spell_id
with the index's active version, so a notch to what they return changed nothing. `add_to_spell_index` and
`remove_from_spell_index` had the same gap, since they move only a parked version. From 0.2.8249 all three take the
spell_id `bind` or `bind_inactive` returned:
"""), T("""
`Conduit.notch_spell` makes one version of a spell index the active one - the notch in stage -> notch -> meld. Until
0.2.8249 it took only the version's `Spell`, and no public call returned the `Spell` of a staged version:
`bind_inactive` returns a spell_id, and until 0.2.8253 `get_spell_by_id` / `find_spell_by_id` answered a staged
(parked) spell_id with the index's active version, so a notch to what they returned changed nothing.
`add_to_spell_index` and `remove_from_spell_index` had the same gap, since they move only a parked version. From
0.2.8249 all three take the spell_id `bind` or `bind_inactive` returned:
""")),
    ("index = reports.get_spell_by_id(v1).spell_index\n", "index = reports.get_spell_by_spell_id(v1).spell_index\n"),
    (T("""
  own index - conduit.get_spell_by_id('<id>').spell_index - or move it onto this index with add_to_spell_index
  first." A refused notch changes nothing.
"""), T("""
  own index - conduit.get_spell_by_spell_id('<id>').spell_index - or move it onto this index with
  add_to_spell_index first." A refused notch changes nothing.
""")),
    (T("""
- A notch to the `Spell` that `get_spell_by_id` or `find_spell_by_id` returns for a parked spell_id is still a
  no-op: it is the active version. Name a parked version by its spell_id.
"""), T("""
- A notch to the `Spell` that `get_spell_by_id` or `find_spell_by_id` returned for a parked spell_id stayed a
  no-op: it was the active version. Since 0.2.8253 `get_spell_by_spell_id` and `find_spell_by_spell_id` return the
  parked version itself, so a notch to it moves the index ("A spell_id lookup answers the spell it names", above).
""")),
    (T("""
What stays the same: `spell=` on all three (a notch's target is now checked the same way), a notch to the active
version (it changes nothing), what the three verbs return, the answers of `get_spell_by_id` and `find_spell_by_id`,
borrowers following a notch, and what the index moves do.
"""), T("""
What stays the same: `spell=` on all three (a notch's target is now checked the same way), a notch to the active
version (it changes nothing), what the three verbs return, borrowers following a notch, and what the index moves
do.
""")),
    ("index = lender.get_spell_by_id(english).spell_index\n",
     "index = lender.get_spell_by_spell_id(english).spell_index\n"),
    ("clock_index = reports.get_spell_by_id(utc).spell_index\n",
     "clock_index = reports.get_spell_by_spell_id(utc).spell_index\n"),
    (T("""
- The packaged system documents describe how `find_spell_by_id` resolves version ids from the Book's id maps
  and why it takes no lock.
"""), T("""
- The packaged system documents describe how the spell_id lookup (`find_spell_by_spell_id` since 0.2.8253)
  answers from the Book's id maps and why it takes no lock.
""")),
    ("- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8252.\n", T("""
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the exact spell_id lookups: the renames, per-version permissions, the explicit index step of ownership
  transfer and the contract dependency walks, the exact grant check and the Rift rooms' lookups; the code-map
  extents of the changed files are remeasured, and their line citations remapped.
- The expert guide on bind hooks (`docs/expert/bind-hooks.md`) and the agent operations guide
  (`agents/MELDER_AGENT_OPERATIONS.md`) use the new names, and the guide's lookup trap now describes the exact
  lookup; the walkthroughs that call the lookups use the new names, and lessons 17 (notch-swapping a live object)
  and 26 (codegen create, modify, iterate) show a parked spell_id answering its own version.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8253.
""")),
]


def main() -> None:
    """Apply every edit exactly once to a copy in memory; write it unless --check."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    if len(args) != 1:
        raise SystemExit(__doc__)
    doc = pathlib.Path(args[0]).resolve() / DOC
    raw = doc.read_bytes()
    if b"\r" in raw:
        raise SystemExit("FAIL: the note is expected to be LF")
    text = raw.decode("utf-8")
    long_lines = []
    for old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"FAIL anchor count {n}: {old[:90]!r}")
        text = text.replace(old, new)
        long_lines += [ln for ln in new.split("\n") if len(ln) > 120]
    if long_lines:
        raise SystemExit("FAIL lines over 120: %r" % long_lines)
    left = [ln for ln in text.split("\n") if "find_spell_by_id" in ln or "get_spell_by_id" in ln]
    print(f"edits {len(EDITS)}; lines {text.count(chr(10))}; old names left on {len(left)} lines:")
    for ln in left:
        print("  ", ln[:150])
    if check:
        print("check only: nothing written")
        return
    doc.write_bytes(text.encode("utf-8"))
    if doc.read_bytes().decode("utf-8") != text:
        raise SystemExit("read-back mismatch")
    print("written", DOC)


if __name__ == "__main__":
    main()
