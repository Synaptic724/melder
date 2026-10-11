"""
Land the 0.2.8233 system-document edits (direct_spell_cleanup_lock_order_2026_10_11) in src_architecture.md and
src_components.md. Every edit asserts its anchor exactly once. Run after remap_citations_0_2_8233.py.

Usage: python land_docs_0_2_8233.py <system_docs dir> <verified_at timestamp>
"""
import pathlib
import sys

DOCS = pathlib.Path(sys.argv[1])
STAMP = sys.argv[2]


def edit(name: str, pairs: list[tuple[str, str]]) -> None:
    path = DOCS / name
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    for old, new in pairs:
        assert text.count(old) == 1, (name, old[:90], text.count(old))
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print("edited", name, len(pairs))


ARCH_INVARIANT = """- Direct spell cleanup (2026-10-11, 0.2.8233): `Spell.cleanup()` never holds the spell lock while it waits for or holds
  the Book, frame or Nexus locks. A direct call on a live spell (its Book is not driving the cleanup) decides under the
  spell lock (`Spell._direct_removal_route`), leaves it, and runs `Spellbook.cleanup_and_remove_spell` under the spell's
  own removal lock (`_removal_lock`, created on first use), which nothing else takes; the Book's call back with
  `_spellbook_cleanup` set runs the local teardown under the spell lock. Book teardown (`_cleanup_spells`, reached from
  root and frame teardown) and conjure, which holds the Book lock across its creation system (the structural hydration
  and `define_conduit_into_spells`), take spell locks under the Book lock, so the old order hung both threads when they
  met; two direct cleanups of one spell still serialize, on the removal lock. `cleanup_and_remove_spell` re-checks the
  Book under its lock: a Book torn down while the call waited returns for a Spell the teardown cleaned and raises the
  cleaned-Book RuntimeError otherwise. A teardown that starts after its first locked section is not ordered against the
  rest of the removal (callers quiesce removals before tearing a Book down).
  EVIDENCE: `src/melder/aether/spellbook/spell.py:Spell.cleanup`, `Spell._direct_removal_route`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook.cleanup_and_remove_spell`, `Spellbook._cleanup_spells` and
  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.define_conduit_into_spells`.
- Lock residuals (2026-10-11, 0.2.8232):"""

ARCH_FAILURE = """## Failure Modes and Error Paths
- A direct `Spell.cleanup()` no longer hangs against a concurrent teardown or conjure of its Spellbook (fixed in
  0.2.8233): the call held the spell lock while it waited for the Book lock, and root, Spellbook or frame teardown, or a
  conjure, held the Book lock while it waited for the spell lock. A direct call racing its Book's teardown now returns
  once the teardown has cleaned the spell, or raises RuntimeError "Spellbook has already been cleaned. ";
  `Spellbook.cleanup_and_remove_spell` waiting on a Book torn down meanwhile raises that error, or returns for a spell
  the teardown cleaned, instead of AttributeError "... has no attribute '_spells_by_id'".
  EVIDENCE: `src/melder/aether/spellbook/spell.py:Spell.cleanup` and
  `src/melder/aether/spellbook/spellbook.py:Spellbook.cleanup_and_remove_spell`.
"""

ARCH_HANDOFF = """## Context / Handoff Summary

2026-10-11 direct spell cleanup (0.2.8233): a direct `Spell.cleanup()` decides under the spell lock and runs the Book
removal outside it, serialized per spell by a removal lock nothing else takes, so it no longer hangs against Book, root
or frame teardown or a conjure of its Book, which take spell locks under the Book lock; `cleanup_and_remove_spell`
re-checks a Book torn down while it waits. The operational invariants (the 0.2.8232 entry's recorded residual is
closed), the failure modes and the code map carry it; the component map carries the per-component rules.

"""

edit("src_architecture.md", [
    ("- Lock residuals (2026-10-11, 0.2.8232):", ARCH_INVARIANT),
    ("""  (`_cleanup_spells`) and frame teardown take spell locks under the Book and frame locks the disposal needs. Recorded,
  not changed: a direct `Spell.cleanup()` of a live owned spell still calls `cleanup_and_remove_spell` under the spell
  lock (spell -> Book) against Book teardown's Book -> spell.
""", """  (`_cleanup_spells`) and frame teardown take spell locks under the Book and frame locks the disposal needs. A direct
  `Spell.cleanup()`, which still held the spell lock across its removal here, follows the same rule since 0.2.8233
  (entry above).
"""),
    ("## Failure Modes and Error Paths\n", ARCH_FAILURE),
    ("""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7533
  loc: 7533
  verified_at: 2026-10-11T20:29:47Z
  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind
    publishes its spell maps under the Book lock (0.2.8230); `cleanup_spell` decides through `_dispose_spell` and
    contracted lookups answer by key (0.2.8231); overlapping disposals refuse and `inspect_spell` asks the frames
    with no lock held (0.2.8232).
""", f"""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7564
  loc: 7564
  verified_at: {STAMP}
  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind
    publishes its spell maps under the Book lock (0.2.8230); `cleanup_spell` decides through `_dispose_spell` and
    contracted lookups answer by key (0.2.8231); overlapping disposals refuse and `inspect_spell` asks the frames
    with no lock held (0.2.8232); `cleanup_and_remove_spell` re-checks a Book torn down while it waits (0.2.8233).
"""),
    ("""- path: `src/melder/aether/spellbook/spell.py`
  start_line: 1
  end_line: 1770
  loc: 1770
  verified_at: 2026-10-11T08:43:02Z
  note: spell metadata and hooks; carries `spellframe_kind` and `implemented_protocols` (0.2.8222);
    `_spell_index_unless_cleaned`, the cleanup-safe index read (0.2.8229).
""", f"""- path: `src/melder/aether/spellbook/spell.py`
  start_line: 1
  end_line: 1854
  loc: 1854
  verified_at: {STAMP}
  note: spell metadata and hooks; carries `spellframe_kind` and `implemented_protocols` (0.2.8222);
    `_spell_index_unless_cleaned`, the cleanup-safe index read (0.2.8229); a direct `cleanup()` removes the spell
    outside the spell lock, under its removal lock (0.2.8233).
"""),
    ("## Context / Handoff Summary\n\n", ARCH_HANDOFF),
])

COMP_SB_BULLET = """- `inspect_spell` holds `_lock` only while it walks its own `_spells` (0.2.8232). The frame-wide walk reads
  `list(frame._conduits.values())`, which root registration writes under the frame lock, and every
  `Aether._check_for_spell` runs with no lock held, because those take frame locks and frame teardown takes
  frame -> conduit -> Book.
- `cleanup_and_remove_spell` re-checks `_cleaned` under `_lock` (0.2.8233): its `check_cleaned()` runs before the
  lock, so a call can wait on `_lock` while `cleanup` tears the Book down and deletes the maps. Teardown cleans every
  active spell, so a Spell the teardown cleaned returns; anything else (an id, a parked or foreign Spell) raises the
  cleaned-Book RuntimeError. It runs the risk-manager, Aether/frame and Nexus calls and the final `Spell.cleanup()`
  outside `_lock`; a direct `Spell.cleanup()` now reaches it outside the spell lock too (Binding Pipeline), so the
  spell locks `_cleanup_spells` and conjure take under `_lock` never wait on it. A teardown that starts after its first
  locked section is not ordered against the rest of the removal.
"""

COMP_SPELL_BULLET = """- SpellIndex and Spell use RLock to protect mutation and cleanup.
- A direct `Spell.cleanup()` - one its Spellbook is not driving, `_spellbook_cleanup` unset - is removed through
  `Spellbook.cleanup_and_remove_spell` outside `_lock` (0.2.8233). `_direct_removal_route` decides under `_lock` and
  returns the Book and the spell's `_removal_lock` (created there on first use, None until then, deleted at cleanup);
  `cleanup` takes that lock, re-checks `_cleaned` and calls the Book, whose call back with `_spellbook_cleanup` set runs
  the local teardown under `_lock`. Before, `_lock` was held across the removal, which takes the Book lock, frame locks
  and the Nexus record, while Book teardown and conjure take `_lock` under the Book lock: both threads hung. Nothing
  else takes `_removal_lock`, so two direct cleanups of one spell still serialize (the second waits, then returns) and
  no lock-order cycle runs through it; a caller holding `with spell:` around a direct cleanup brings the old order
  back. Cost: about 1 us on a ~18 us direct cleanup; bind, Book teardown and meld unchanged (measured).
"""

COMP_HANDOFF = """## Context / Handoff Summary

2026-10-11 direct spell cleanup (0.2.8233): the Binding Pipeline carries the direct `Spell.cleanup` route (decision
under `_lock`, Book removal under the per-spell `_removal_lock`) and why; Spellbook Core carries
`cleanup_and_remove_spell`'s re-check of a Book torn down while it waits, the corrected nesting note of
`_dispose_spell` and the new failure entry; the code map extents of spell.py and spellbook.py are remeasured.

"""

edit("src_components.md", [
    ("""  `_lock` through `Spell._spell_index_unless_cleaned`, so the two locks are never nested there (a direct
  `Spell.cleanup` takes them spell -> Book, `_cleanup_spells` Book -> spell; corrected 0.2.8232, the note said the
  spell lock is never taken under `_lock`).""", """  `_lock` through `Spell._spell_index_unless_cleaned`, so the two locks are never nested there (`_cleanup_spells`
  and conjure take them Book -> spell, and since 0.2.8233 a direct `Spell.cleanup` no longer takes them the other
  way; corrected 0.2.8232, the note said the spell lock is never taken under `_lock`)."""),
    ("""- `inspect_spell` holds `_lock` only while it walks its own `_spells` (0.2.8232). The frame-wide walk reads
  `list(frame._conduits.values())`, which root registration writes under the frame lock, and every
  `Aether._check_for_spell` runs with no lock held, because those take frame locks and frame teardown takes
  frame -> conduit -> Book.
""", COMP_SB_BULLET),
    ("""- RuntimeError "cleanup_spell: spell <id> is already being disposed by another call." while another `cleanup_spell`
  of the same spell runs (0.2.8232; before, both disposed it and one failed part-way).
""", """- RuntimeError "cleanup_spell: spell <id> is already being disposed by another call." while another `cleanup_spell`
  of the same spell runs (0.2.8232; before, both disposed it and one failed part-way).
- RuntimeError "Spellbook has already been cleaned. " from `cleanup_and_remove_spell` when the Book is torn down while
  the call waits for `_lock` and the teardown did not clean the Spell given; it returns when the teardown did (0.2.8233;
  both raised AttributeError on the deleted maps).
"""),
    ("- SpellIndex and Spell use RLock to protect mutation and cleanup.\n", COMP_SPELL_BULLET),
    ("""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7533
  loc: 7533
  verified_at: 2026-10-11T20:29:47Z
""", f"""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7564
  loc: 7564
  verified_at: {STAMP}
"""),
    ("""- path: `src/melder/aether/spellbook/spell.py`
  start_line: 1
  end_line: 1770
  loc: 1770
  verified_at: 2026-10-11T08:43:02Z
""", f"""- path: `src/melder/aether/spellbook/spell.py`
  start_line: 1
  end_line: 1854
  loc: 1854
  verified_at: {STAMP}
"""),
    ("## Context / Handoff Summary\n\n", COMP_HANDOFF),
])
