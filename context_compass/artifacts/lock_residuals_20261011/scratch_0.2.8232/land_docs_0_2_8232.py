"""
Land the 0.2.8232 system-document changes (lock_residuals_2026_10_11) in src_architecture.md and src_components.md.

Usage: python land_docs_0_2_8232.py <context_compass/system_docs> <verified_at UTC> <spellbook.py loc> <conduit.py loc>

Both documents are LF. Every edit asserts its anchor once. Regenerate both indexes afterwards.
"""
import pathlib
import sys

DOCS = pathlib.Path(sys.argv[1])
STAMP, SB_LOC, CD_LOC = sys.argv[2], sys.argv[3], sys.argv[4]


def edit(name: str, pairs: list[tuple[str, str]]) -> None:
    path = DOCS / name
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    for old, new in pairs:
        assert text.count(old) == 1, (name, old[:70], text.count(old))
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print("edited", name)


ARCH_INVARIANT = """- Lock residuals (2026-10-11, 0.2.8232): `Conduit.find_contracted_spell` takes no lock and walks a one-call copy of
  the Book's contracted peer ids, which a link or sever the peer starts writes under the Book lock while holding the
  peer's conduit lock, not this one; each peer is answered by the keyed, lock-free `_find_contracted_spell_by_id`.
  `Spellbook.inspect_spell` holds its Book lock only while it walks its own spells and `Conduit.inspect_spell` takes no
  conduit lock: the registry confirmations (`Aether._check_for_spell`) take frame locks, and frame teardown takes
  frame -> conduit -> Book (`AethericFrame._cleanup_data_structures` -> `Conduit.permanent_cleanup` ->
  `Spellbook.cleanup`), so holding either lock there could hang; the frame-wide walk reads a one-call copy of the
  frame's conduit map. `Spellbook._dispose_spell` marks the spell id in `_disposing_spell_ids` in the Book-locked
  section that decides ownership and clears it under the Book lock when the disposal ends, so two `cleanup_spell`
  calls of one spell never both dispose it. The spell lock is never held across a disposal: Book teardown
  (`_cleanup_spells`) and frame teardown take spell locks under the Book and frame locks the disposal needs. Recorded,
  not changed: a direct `Spell.cleanup()` of a live owned spell still calls `cleanup_and_remove_spell` under the spell
  lock (spell -> Book) against Book teardown's Book -> spell.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.find_contracted_spell`, `Conduit.inspect_spell`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook.inspect_spell`, `Spellbook._dispose_spell`,
  `Spellbook._cleanup_spells` and `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame.cleanup`.
"""

ARCH_FAILURE = """- Contracted lookups, object inspection and overlapping disposals no longer fail under concurrent changes (fixed in
  0.2.8232): `Conduit.find_contracted_spell` no longer raises RuntimeError "dictionary changed size during iteration"
  while a peer links or severs; `inspect_spell` no longer answers None for a registered object while a root registers
  or retires in the frame, and no longer holds the Book or conduit lock where a racing frame teardown could hang it; a
  `cleanup_spell` that overlaps another of the same spell raises RuntimeError "cleanup_spell: spell <id> is already
  being disposed by another call." (before, both disposed it and one failed part-way).
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.find_contracted_spell` and
  `src/melder/aether/spellbook/spellbook.py:Spellbook._dispose_spell`.
"""

ARCH_HANDOFF = """2026-10-11 lock residuals (0.2.8232): `find_contracted_spell` walks a one-call copy of the Book's contracted peer ids
with no lock, `inspect_spell` walks a one-call copy of the frame's conduits and holds no Book or conduit lock while it
asks the frames (which frame teardown could hang against), and `cleanup_spell` refuses a second disposal of a spell
while the first runs, through an id mark kept under the Book lock - not the spell lock, which Book and frame teardown
take under theirs. The operational invariants, the failure modes and the code map carry it; the component map carries
the per-component rules.

"""

edit("src_architecture.md", [
    ("- Cross-object locks (2026-10-11, 0.2.8231): a reader and a writer of one map take the same lock, or the reader\n",
     ARCH_INVARIANT + "- Cross-object locks (2026-10-11, 0.2.8231): a reader and a writer of one map take the same lock, or the "
     "reader\n"),
    ("- Index-link notifications, contract reads and binds across frames no longer fail under concurrent changes (fixed in\n",
     ARCH_FAILURE + "- Index-link notifications, contract reads and binds across frames no longer fail under concurrent changes "
     "(fixed in\n"),
    ("""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7468
  loc: 7468
  verified_at: 2026-10-11T18:42:56Z
  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind
    publishes its spell maps under the Book lock (0.2.8230); `cleanup_spell` decides through `_dispose_spell` and
    contracted lookups answer by key (0.2.8231).
""", f"""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: {SB_LOC}
  loc: {SB_LOC}
  verified_at: {STAMP}
  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind
    publishes its spell maps under the Book lock (0.2.8230); `cleanup_spell` decides through `_dispose_spell` and
    contracted lookups answer by key (0.2.8231); overlapping disposals refuse and `inspect_spell` asks the frames
    with no lock held (0.2.8232).
"""),
    ("""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7157
  loc: 7157
  verified_at: 2026-10-11T18:42:56Z
  note: conduit lifecycle and meld facade; `cleanup_spell` emits the index destroy the Book reports (0.2.8231).
""", f"""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: {CD_LOC}
  loc: {CD_LOC}
  verified_at: {STAMP}
  note: conduit lifecycle and meld facade; `cleanup_spell` emits the index destroy the Book reports (0.2.8231);
    `find_contracted_spell` and `inspect_spell` take no conduit lock (0.2.8232).
"""),
    ("## Context / Handoff Summary\n\n2026-10-11 cross-object locks (0.2.8231):",
     "## Context / Handoff Summary\n\n" + ARCH_HANDOFF + "2026-10-11 cross-object locks (0.2.8231):"),
])

COMP_SB_DISPOSE_OLD = """  `Spell.cleanup` deletes them only after the Book has popped it - and a spell no longer in them is classified outside
  `_lock` through `Spell._spell_index_unless_cleaned`, because `Spell.cleanup` takes the spell lock before `_lock`.
  `_dispose_spell` returns the destroyed index's id (None when the index survived), which `Conduit.cleanup_spell`
  emits to index-link borrowers.
"""
COMP_SB_DISPOSE_NEW = """  `Spell.cleanup` deletes them only after the Book has popped it - and a spell no longer in them is classified outside
  `_lock` through `Spell._spell_index_unless_cleaned`, so the two locks are never nested there (a direct
  `Spell.cleanup` takes them spell -> Book, `_cleanup_spells` Book -> spell; corrected 0.2.8232, the note said the
  spell lock is never taken under `_lock`). `_dispose_spell` returns the destroyed index's id (None when the index
  survived), which `Conduit.cleanup_spell` emits to index-link borrowers.
- A `cleanup_spell` that overlaps another of the same spell refuses (0.2.8232): `_dispose_spell` adds the id to
  `_disposing_spell_ids` in the `_lock` section that decides ownership - only when it will dispose the spell (owned,
  and not the active member of a multi-member index) - and discards it under `_lock` in a `finally` when the disposal
  ends; a call that finds the id raises RuntimeError before it reads the spell. The spell lock is not held across the
  disposal: the disposal takes `_lock` and the frame lock (`AethericFrame.unregister_conduit_spells`), and Book and
  frame teardown take the spell lock under those, so it would hang against them. The mark costs a set probe and one
  short `_lock` section (about 0.1 us on a 20 us disposal, measured).
- `inspect_spell` holds `_lock` only while it walks its own `_spells` (0.2.8232). The frame-wide walk reads
  `list(frame._conduits.values())`, which root registration writes under the frame lock, and every
  `Aether._check_for_spell` runs with no lock held, because those take frame locks and frame teardown takes
  frame -> conduit -> Book.
"""
COMP_SB_FAIL_OLD = """- RuntimeError "cleanup_spell: spell <id> has already been disposed." for a spell already disposed (0.2.8231; it
  raised AttributeError), besides the "not owned by this spellbook" and multi-member refusals.
"""
COMP_SB_FAIL_NEW = COMP_SB_FAIL_OLD + """- RuntimeError "cleanup_spell: spell <id> is already being disposed by another call." while another `cleanup_spell`
  of the same spell runs (0.2.8232; before, both disposed it and one failed part-way).
"""
COMP_CD_THREAD_OLD = """  this conduit waits for it. The old unlocked pre-read of `spell.spell_index` raised AttributeError for a disposed
  spell and could disagree with what the Book then did.
"""
COMP_CD_THREAD_NEW = """  this conduit waits for it. The old unlocked pre-read of `spell.spell_index` raised AttributeError for a disposed
  spell and could disagree with what the Book then did. Of two overlapping calls for one spell the Book disposes it
  once and refuses the other (0.2.8232), so the destroy is emitted once.
- `find_contracted_spell` and `inspect_spell` take no conduit lock (0.2.8232). `find_contracted_spell` walks a
  one-call copy of the Book's contracted peer ids - a link or sever the peer starts writes them under the Book lock
  holding the peer's conduit lock, so this conduit's lock never excluded it - and answers each peer through the
  keyed, lock-free `Spellbook._find_contracted_spell_by_id`; holding the conduit lock also made its parked-copy
  branch take a spell lock under it. `inspect_spell` held the conduit lock across the Book's inspection, which takes
  frame locks, while frame teardown takes the frame lock and then each conduit's lock (`permanent_cleanup`).
"""
COMP_CD_FAIL_OLD = """- RuntimeError from `cleanup_spell` for a spell already disposed ("cleanup_spell: spell <id> has already been
  disposed."; 0.2.8231, it raised AttributeError), not owned by this conduit's Book, or the active member of a
  multi-member index.
"""
COMP_CD_FAIL_NEW = """- RuntimeError from `cleanup_spell` for a spell already disposed ("cleanup_spell: spell <id> has already been
  disposed."; 0.2.8231, it raised AttributeError), being disposed by another call ("... is already being disposed by
  another call."; 0.2.8232), not owned by this conduit's Book, or the active member of a multi-member index.
"""
COMP_HANDOFF = """2026-10-11 lock residuals (0.2.8232): Spellbook Core carries the in-flight disposal mark, the corrected nesting note
and `inspect_spell`'s lock scope; the Conduit Runtime carries the lock-free `find_contracted_spell` and
`inspect_spell` and the single destroy emission of overlapping disposals; the code map extents of the changed files
are remeasured.

"""

edit("src_components.md", [
    (COMP_SB_DISPOSE_OLD, COMP_SB_DISPOSE_NEW),
    (COMP_SB_FAIL_OLD, COMP_SB_FAIL_NEW),
    (COMP_CD_THREAD_OLD, COMP_CD_THREAD_NEW),
    (COMP_CD_FAIL_OLD, COMP_CD_FAIL_NEW),
    ("""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: 7468
  loc: 7468
  verified_at: 2026-10-11T18:42:56Z
""", f"""- path: `src/melder/aether/spellbook/spellbook.py`
  start_line: 1
  end_line: {SB_LOC}
  loc: {SB_LOC}
  verified_at: {STAMP}
"""),
    ("""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: 7157
  loc: 7157
  verified_at: 2026-10-11T18:42:56Z
""", f"""- path: `src/melder/aether/conduit/conduit.py`
  start_line: 1
  end_line: {CD_LOC}
  loc: {CD_LOC}
  verified_at: {STAMP}
"""),
    ("## Context / Handoff Summary\n\n2026-10-11 cross-object locks (0.2.8231):",
     "## Context / Handoff Summary\n\n" + COMP_HANDOFF + "2026-10-11 cross-object locks (0.2.8231):"),
])
