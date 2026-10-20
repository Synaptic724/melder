"""S6 turn-in: bring the epic's Build Specification up to what S6 built (B8, B9, B12), settle U9 in Open Questions,
add the S6 build decisions to the Decision Log, tick Milestones 2 and 3 and stamp Updated.

Run from the repository root: python s6_epic_spec.py <NOW>
"""
import pathlib
import sys

now = sys.argv[1]
EPIC = pathlib.Path("context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
text = EPIC.read_text(encoding="utf-8")
before_lines = text.splitlines()

B8 = """### B8 Ownership transfer (S6; as built in 0.2.8246, U9 settled)
- Rows, unchanged by S6 (S3 and S4 built them): `move_creations=True` (the default) - `_move_creations`
  (transfer_of_ownership.py:1508-1551) extracts every member's rows from the source store and restores them into
  the target, so the same pool object moves with its idle objects, recorded children and count, and the registry
  follows it (unregister at extract; register at restore, which replaces and cleans an empty pool a stamp composed).
  `move_creations=False` - `_teardown_creations` (1553-1586) takes the active member's rows (its pool among them)
  out of the source store and keeps them only for rollback; the old pool's idle objects stay undisposed and parked
  members' rows stay in the source store. Rollback (`_rollback_creations_move`, 1079-1104) puts the rows back.
- U9, settled by S6 (the story's FACT note of 2026-10-15T18:43:16Z): `_apply_notch` and `_reactivate_owned_spell`
  never re-stamp; a promoted version keeps the owner stamp it had. Until 0.2.8246 a transfer stamped only the active
  member and no rollback restored a stamp, so a parked version kept the source's store (after a notch on the target
  a managed meld raised the missing-pool error and a `unique` stored its object in the source's store) and a failed
  transfer left the active member on the target's store (a managed meld raised missing-pool, or leased from an
  empty pool left in the target; a `unique` built a second object there).
- The stamp follows the lineage both ways (S6). `_stamp_owner(spell, conduit, spellbook)` (1680-1725) stamps as
  conjure does: root id, name and store, dynamic flag, gate controller, the Book's caching posture. `_restamp(spell)`
  (1727-1776) registers the stamp-back to the source first, stamps onto the target and, for a managed version whose
  pool the target store did not hold, registers `_discard_composed_pool` (1778-1802) in a `finally`. The flip calls
  `_restamp` for the active member; `_migrate_inactive_members` (1588-1648) calls it, after its map rollback, for
  every moved parked member whose `_owner_creations` is set. A version never stamped moves as before.
- `Creations.discard_managed_quantity(spell_id, pool)` (creations.py:1200-1249) removes the pool only while it is
  the one under the id (identity check under the store lock), unregisters it after the lock, never cleans it (the
  caller does) and answers whether it removed it; a cleaned store raises its RuntimeError.
- Rollback order (registration reversed): the row rollbacks; each parked member (discard, stamp-back); the map
  rollback (`_rollback_inactive_members`); the active member (discard, stamp-back); `_rollback_spellbook_move`; the
  registry, contracts and validity. Rows go back before the stamps. A composed pool is empty when it is discarded
  (the lineage is disabled for the whole transfer), so nothing is disposed.
- Locks: the stamps run under both conduit locks and outside the Book locks, as the flip's stamp always did
  (conduit -> spell -> store leaf -> registry leaf); rollbacks hold no conduit lock; no new edge.
- After a no-move transfer a parked managed version has a pool in each root (the source keeps its old one with the
  parked rows); once that version is notched in on the target, a release by class finds two pools of the selected
  version and needs `conduit=` (a lease's own `release()` is unaffected).
- For the owner, not built (the S6 DECISION note, point 6): a version staged with `bind_inactive` before conjure is
  never stamped - conjure stamps `_spells` only (`define_conduit_into_spells`) and `_apply_notch` stamps nothing - so
  after a notch to it, its first meld raises "Spell has no configured CreationContextFactory." for every existence,
  and a managed consumer's per-creation read raises the missing-pool error. Stamping parked members at conjure
  would fix it and changes behaviour for every existence.
- Transfers are dynamic-only and dynamic plans read the pool per creation (B7), so a plan finds a moved pool through
  the target's store; no plan binds a pool that a transfer can move. A release racing a transfer can meet the gap
  between extract and restore and raises the not-managed ValueError for that call.

"""

start = text.index("### B8 Ownership transfer (S6)\n")
end = text.index("### B9 Lifecycle\n")
assert text.count("### B8 Ownership transfer (S6)\n") == 1 and text.count("### B9 Lifecycle\n") == 1
assert start < end
text = text[:start] + B8 + text[end:]

edits = [
    ("- Updated: 2026-10-15T18:15:07Z\n", f"- Updated: {now}\n"),
    (
        "| transfer, move (default) | moves to the target store | move | the agents' | entry stays valid |\n"
        "| transfer, no move | source pool kept for rollback only; target pool fresh | stay undisposed | the agents' |"
        " old out, new in |\n",
        "| transfer, move (default) | every version's pool moves to the target store | move | the agents' |"
        " stays valid; names the target root |\n"
        "| transfer, no move | active pool kept for rollback only; parked pools stay; the target's are fresh |"
        " stay undisposed | the agents' | old out, new in |\n"
        "| transfer that fails | back where they were; a pool a stamp composed is discarded | untouched | the agents' |"
        " as before |\n",
    ),
    (
        "- S6: transfer tests beside tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py"
        " and an\n  integration test (move, no move, rollback, parked members, releases keep working).\n",
        "- S6 (as built): tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_owner_stamps.py\n"
        "  (19: the flip's stamp and stamp-back, the discard of a composed pool, parked members of every existence, a raising\n"
        "  stamp, the rollback order), tests/unit/melder/aether/conduit/creations/test_creations_discard_managed_quantity.py\n"
        "  (11) and tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py (12: move, releases after\n"
        "  it, no move, parked versions notched in, failed transfers with and without a move, `unique` stamps).\n",
    ),
    (
        "## Open Questions\n"
        "- None open with the owner. U1-U8, U10 and U11 are settled (S2-S5); U9 is read in source by S6, which also raises\n"
        "  the stamping of a version notched in from before conjure (B8). For review: the build decisions (Decision Log).\n",
        "## Open Questions\n"
        "- For the owner (B8; the S6 story's DECISION note, point 6): should conjure stamp parked versions, so a version\n"
        "  staged with `bind_inactive` before conjure can be notched in? Today its first meld after the notch fails for every\n"
        "  existence; the fix changes behaviour for every existence and is not built.\n"
        "- Settled: U1-U11 (S2-S6). For review: the build decisions (Decision Log).\n",
    ),
    (
        "## Decision Log\n",
        "## Decision Log\n"
        "- 2026-10-15 (melder_0, S6 build decisions inside the owner's go-ahead, open to the owner's review): (1) the owner\n"
        "  stamp follows the lineage both ways - a transfer re-stamps every parked version that carries a stamp, and a failed\n"
        "  transfer stamps every member back and discards the empty pools its stamps composed - because a stamp that names the\n"
        "  wrong store is a record naming the wrong owner, for every existence (the probe's cases B, D, E, F and G); (2) rows\n"
        "  are unchanged: a pool moves as the row S3 and S4 built; (3) `Creations.discard_managed_quantity(spell_id, pool)`\n"
        "  joins the store verbs (identity-checked, unregisters, never cleans); (4) after a no-move transfer a parked managed\n"
        "  version keeps its old pool in the source with its other rows, so once it is notched in on the target a release by\n"
        "  class needs `conduit=`; (5) stamping versions staged before conjure is left to the owner (Open Questions).\n",
    ),
    (
        "- [ ] Milestone 2: Architecture patch doc written and linked; each story's component patch before its build.\n",
        "- [x] Milestone 2: Architecture patch doc written and linked; each story's component patch before its build.\n",
    ),
    (
        "- [ ] Milestone 3: S1-S6 landed (one notch each) with green tests in both GIL modes.\n",
        "- [x] Milestone 3: S1-S6 landed (one notch each) with green tests in both GIL modes.\n",
    ),
]
for old, new in edits:
    assert text.count(old) == 1, old[:80]
    text = text.replace(old, new)

after_lines = text.splitlines()
added = [line for line in after_lines if line not in set(before_lines)]
long = [line for line in added if len(line) > 120 and not line.startswith("|")]
assert not long, long
EPIC.write_text(text, encoding="utf-8")
print("epic spec updated:", len(before_lines), "->", len(after_lines), "lines;", len(added), "new lines")
