"""Land the 0.2.8229 docs: src_architecture, src_components, release note. Exact anchors; keeps EOL."""
import datetime, pathlib, sys

REPO = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def loc(rel):
    return len((REPO / rel).read_bytes().decode("utf-8").splitlines())


SB, SP = loc("src/melder/aether/spellbook/spellbook.py"), loc("src/melder/aether/spellbook/spell.py")


def edit(rel, ops):
    path = REPO / rel
    data = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in data
    text = data.replace("\r\n", "\n")
    for kind, anchor, payload in ops:
        if text.count(anchor) != 1:
            raise SystemExit(f"{rel}: anchor x{text.count(anchor)}: {anchor[:70]!r}")
        if kind == "before":
            text = text.replace(anchor, payload + anchor, 1)
        elif kind == "after":
            text = text.replace(anchor, anchor + payload, 1)
        elif kind == "replace":
            text = text.replace(anchor, payload, 1)
        elif kind == "append_block":  # payload goes after the last non-blank line before anchor
            i = text.index(anchor)
            while text[i - 2:i] == "\n\n":
                i -= 1
            text = text[:i] + payload + text[i:]
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"{rel}: {len(ops)} edits ({'CRLF' if crlf else 'LF'})")


ARCH_INVARIANT = """- Lookup by version id (2026-10-11, 0.2.8229): `Spellbook.find_spell_by_id` answers from the Book's id maps and
  never iterates a live map. A current version id is one read of `_spells_by_id`; a superseded or parked id is a
  read of `_inactive_spells`, then of the parked Spell's index through `Spell._spell_index_unless_cleaned` (under
  that Spell's own lock, the one `Spell.cleanup` deletes `spell_index` under, which cleanup keeps), then of
  `_spells` for that index's live spell. Every owned lineage id is in one of the two maps: a notch parks the
  outgoing version, add/remove-from-index move only parked versions and repoint their index under the Book lock,
  parked disposal drops the id with its membership, and an ownership transfer migrates the whole lineage
  (`_flip_registry_and_spellbooks`, then `_migrate_inactive_members`). The lookup takes no Book lock, by design:
  conjure holds that lock while phase-4 workers (the ambiguity report calls the lookup) and conduit hooks run, and
  both may call it from other threads. A concurrent bind, removal, notch, index move or transfer therefore never
  makes it raise or skip a registered spell; a lookup inside a notch, or between a transfer's flip and its
  migration, answers None for that lineage, and the returned Spell is borrowed, not leased.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_id`,
  `src/melder/aether/spellbook/spell.py:Spell._spell_index_unless_cleaned`, `Spell.cleanup` and
  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:TransferOfOwnership.execute`.
"""

ARCH_FAILURE = """- `Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` through it, no longer fail while other spells are
  bound, removed or parked on other threads (fixed in 0.2.8229; MelderOps hit it on 0.2.8226, reproduced on
  0.2.8228). The old walk over the live index map raised RuntimeError "dictionary changed size during
  iteration", AttributeError "'SpellIndex' object has no attribute '_spells_in_index'" or RuntimeError
  "SpellIndex has already been cleaned.", or returned None for a spell that was still registered. A parked
  version disposed during a lookup now answers None instead of raising.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_id`.
"""

ARCH_HANDOFF = """2026-10-11 lookup by version id (0.2.8229): `Spellbook.find_spell_by_id` answers from the Book's id maps
(`_spells_by_id`, then `_inactive_spells` and the parked spell's index) instead of walking the live index map, so
concurrent binds and removals no longer make it raise or miss a registered spell; the new internal
`Spell._spell_index_unless_cleaned` keeps the parked branch safe against a concurrent disposal. The operational
invariants, the failure modes and the code map carry it; the component map carries the threading rationale.

"""

COMP_CORE_THREADING = """- `find_spell_by_id` is lock-free on purpose (0.2.8229): it reads `_spells_by_id`, then `_inactive_spells` and
  `Spell._spell_index_unless_cleaned`, then `_spells.get(index)` - single-key reads, never an iteration - so a
  concurrent writer can neither raise a size-change error in it nor make it skip an entry. A Book-lock reader was
  measured and rejected: conjure holds `_lock` across the creation pipeline while phase-4 workers
  (`AmbiguousProviderStrategy` calls the lookup) and conduit lifecycle hooks run, so a locked lookup on another
  thread stalled the conjure until the 60 s phase barrier timed out. A notch, and a transfer between
  `_flip_registry_and_spellbooks` and `_migrate_inactive_members`, are the only windows in which a lineage id
  briefly answers None.
"""

COMP_CORE_FAILURE = """- `find_spell_by_id` returns None for an id no local index claims - unknown, another Book's, a contracted
  spell's, a parked version split into a fresh index, a parked version disposed during the lookup - and raises
  only RuntimeError for a cleaned Book (0.2.8229; before, concurrent binds and removals made it raise the
  size-change RuntimeError or the SpellIndex AttributeError/RuntimeError, or miss a registered spell).
"""

COMP_BINDING_THREADING = """- `Spell._spell_index_unless_cleaned()` (0.2.8229) reads `spell_index` under the spell's `_lock` and answers
  None once `_cleaned` is set. `Spell.cleanup` sets `_cleaned` and deletes `spell_index` under that lock and keeps
  `_lock` itself, so the read never raises on a cleaned Spell; it holds no other lock, and an index move (which
  repoints `spell_index` under the Spellbook lock) is seen as the old or the new index.
"""

COMP_HANDOFF = """2026-10-11 lookup by version id (0.2.8229): Spellbook Core carries why `find_spell_by_id` reads the id maps
without the Book lock (conjure holds it while phase-4 workers and hooks run) and its None windows (a notch, a
transfer between flip and migration); the Binding Pipeline carries `Spell._spell_index_unless_cleaned` and the
`_lock` that `Spell.cleanup` keeps; the code map's spellbook.py and spell.py extents are remeasured.

"""

RELEASE_SECTION = """## `Spellbook.find_spell_by_id` no longer fails while other spells change

`Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` on top of it, used to walk the Book's index map while
other threads bound, removed or parked spells. On the free-threaded build a lookup of a spell nobody was touching
could then raise `RuntimeError: dictionary changed size during iteration`, raise
`AttributeError: 'SpellIndex' object has no attribute '_spells_in_index'`, or return `None` for a spell that was
still registered. The lookup now answers from the Book's id maps: one read for a current version id, three for a
superseded or parked one, the same cost at any Book size, and no lock taken.

What stays the same: any id in a spell's version lineage resolves to the live spell that represents it now -
after a notch, an index move or an ownership transfer too - and an id the Book does not own still returns `None`,
as does a parked version moved out into an index of its own. Two answers sharpen: a parked version disposed while
a lookup runs returns `None` instead of raising, and a lookup that lands inside a notch or an ownership transfer
of that same lineage can return `None` for that instant, as a lookup inside a notch already could. The returned
spell is a reference you borrow, not a lease: a later removal, notch or transfer can retire or move it.

"""

edit("context_compass/system_docs/src_architecture.md", [
    ("replace", "- Doc ID: ARCH-SRC-2026-01-17\n- Status: in_progress\n- Owner:\n- Created: 2026-01-17\n- Updated: 2026-10-10\n",
     "- Doc ID: ARCH-SRC-2026-01-17\n- Status: in_progress\n- Owner:\n- Created: 2026-01-17\n- Updated: 2026-10-11\n"),
    ("before", "- Scan declarations (2026-10-10, 0.2.8228):", ARCH_INVARIANT),
    ("before", "- Breaking (0.2.8228): a module scan no longer registers", ARCH_FAILURE),
    ("replace", "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7341\n  loc: 7341\n"
                "  verified_at: 2026-10-10T09:33:01Z\n  note: Spellbook core and conjure pipeline.\n",
     f"- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: {SB}\n  loc: {SB}\n"
     f"  verified_at: {NOW}\n  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps"
     " (0.2.8229).\n"),
    ("replace", "- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: 1734\n  loc: 1734\n"
                "  verified_at: 2026-10-04T11:45:00Z\n",
     f"- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: {SP}\n  loc: {SP}\n"
     f"  verified_at: {NOW}\n"),
    ("replace", "  note: spell metadata and hooks; carries `spellframe_kind` and `implemented_protocols` (0.2.8222).\n",
     "  note: spell metadata and hooks; carries `spellframe_kind` and `implemented_protocols` (0.2.8222);\n"
     "    `_spell_index_unless_cleaned`, the cleanup-safe index read (0.2.8229).\n"),
    ("before", "2026-10-10 scan_bind option parity (0.2.8228): `scan_bind` takes", ARCH_HANDOFF),
])

edit("context_compass/system_docs/src_components.md", [
    ("replace", "- Doc ID: COMP-SRC-2026-01-17\n- Status: in_progress\n- Owner:\n- Created: 2026-01-17\n- Updated: 2026-10-10\n",
     "- Doc ID: COMP-SRC-2026-01-17\n- Status: in_progress\n- Owner:\n- Created: 2026-01-17\n- Updated: 2026-10-11\n"),
    ("append_block", "Invariants/Guarantees:\n- Conjure allowed once per Spellbook instance", COMP_CORE_THREADING),
    ("after", "Failure Modes:\n- `SpellbookValidationError` when Phase 1-4 produces broken spells.\n", COMP_CORE_FAILURE),
    ("after", "- SpellIndex and Spell use RLock to protect mutation and cleanup.\n", COMP_BINDING_THREADING),
    ("replace", "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7341\n  loc: 7341\n"
                "  verified_at: 2026-10-10T09:33:01Z\n",
     f"- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: {SB}\n  loc: {SB}\n"
     f"  verified_at: {NOW}\n"),
    ("replace", "- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: 1717\n  loc: 1717\n"
                "  verified_at: 2026-09-26T20:10:34Z\n",
     f"- path: `src/melder/aether/spellbook/spell.py`\n  start_line: 1\n  end_line: {SP}\n  loc: {SP}\n"
     f"  verified_at: {NOW}\n"),
    ("before", "2026-10-10 scan_bind option parity (0.2.8228): the Scan-Bind Module Scanner", COMP_HANDOFF),
])

edit("release_docs/next_version_release.md", [
    ("replace", "# Melder 0.2.8228\n", "# Melder 0.2.8229\n"),
    ("before", "## Packaging and documentation\n", RELEASE_SECTION),
    ("before", "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8228.",
     "- The packaged system documents describe how `find_spell_by_id` resolves version ids from the Book's id maps\n"
     "  and why it takes no lock.\n"),
    ("replace", "LLM bundles are rebuilt for 0.2.8228.", "LLM bundles are rebuilt for 0.2.8229."),
])
print("SB", SB, "SP", SP, "NOW", NOW)
