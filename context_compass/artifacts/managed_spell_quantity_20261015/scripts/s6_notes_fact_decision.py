"""S6: append the FACT (U9 + probe A-G) and DECISION (owner stamp follows the lineage) notes to the S6 story.

Run from the repository root: python s6_notes_fact_decision.py <NOW>
"""
import pathlib
import sys

NOW = sys.argv[1]
STORY = pathlib.Path("context_compass/tickets/stories/2026-10-15_managed_ownership_transfer_story.md")
T = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"
A = "context_compass/artifacts/managed_spell_quantity_20261015"

FACT = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U9 answered: `_apply_notch` and `_reactivate_owned_spell` never re-stamp a member's owner; the promoted
    version keeps the stamp it had. A transfer re-stamps only the active member: the flip calls `_add_owned_conduit`
    with the target's store (for a managed version `ensure_managed_quantity` composes an empty target pool),
    `_migrate_inactive_members` moves the parked members' maps and `_owner_conduit_id` only, and neither rollback
    (`_rollback_spellbook_move`, `_rollback_inactive_members`) restores a stamp. The probe on 0.2.8245 (gil1): A
    (move, active only) and C (no move) work as designed. B - a version parked after conjure moves its pool to the
    target but keeps the source's store, so after a notch on the target its meld raises the missing-pool error.
    D - a failed moving transfer puts the pool back in the source while the spell keeps the target's store: the
    owner's meld raises missing-pool. E - a failed no-move transfer leaves the target an empty registered pool and
    the spell on the target's store: the owner's meld builds into the target's pool and a release by class raises
    "Session is managed by 2 pools". F - the same for `unique`: after a failed transfer the owner's meld builds a
    second object into the target's store. G - a `unique` version parked after conjure, moved and notched in on the
    target stores its object in the source's store. Every case is a record that names the wrong owner store.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3826-3966
  - src/melder/aether/spellbook/spellbook.py:1563-1621
  - src/melder/aether/spellbook/spell.py:1661-1717
  - {T}:367-507
  - {T}:936-1002
  - {T}:1079-1104
  - {T}:1383-1665
  - src/melder/aether/conduit/creations/creations.py:1116-1172
  - src/melder/aether/conduit/creations/creations.py:1476-1697
  - {A}/probes/probe_s6_managed_transfer.py:1-257
  - {A}/runs/s6_probe_managed_transfer_before_gil1.txt:1-41
  IMPACT: S6 is a stamping fix, not a row fix: rows already move and roll back (S3, S4); the owner stamp does not
    follow them. The same wrong stamp breaks `unique` (F, G), so the fix covers every existence.
  NEXT: Record the fix design (DECISION), then the component and code-description patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

DECISION = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner stamp follows the lineage both ways. (1) The flip stamps through a helper that first registers
    the rollback stamping the active member back onto the source root, the way conjure stamps (the root's id, name,
    store, dynamic flag and gate controller, the Book's caching posture). (2) `_migrate_inactive_members` re-stamps
    every parked member that carries a stamp (`_owner_creations` set) onto the target the same way, each with its
    stamp-back; a version never stamped (staged before conjure) keeps today's behaviour. (3) A stamp that composed a
    pool the target store did not hold registers a rollback removing exactly that pool -
    `Creations.discard_managed_quantity(spell_id, pool)`, an identity-checked pop under the store lock, unregistered
    after it - and cleaning it; it is empty, because the lineage is disabled for the whole transfer, so nothing is
    disposed, and a pool the target already held is never touched. (4) Rows are unchanged: move takes every member's
    rows to the target (replacing the composed pools), no-move takes the active member's rows out and leaves parked
    rows in the source store; rollback runs in reverse, so rows go back before the stamps. (5) Locks: the stamps run
    under both conduit locks and outside the Book locks, as the flip's stamp already does (conduit -> spell -> store
    leaf -> registry leaf); rollbacks hold no conduit lock; no new edge. (6) Raised to the owner, not built here: a
    version staged with `bind_inactive` before conjure is never stamped (conjure stamps `_spells` only), so notching
    it in fails for every existence; the fix is to stamp parked members at conjure, outside this story.
  EVIDENCE:
  - {T}:1383-1665
  - src/melder/aether/conduit/creations/creations.py:1476-1697
  - src/melder/aether/spellbook/spellbook_creation_system.py:1331-1382
  - src/melder/aether/spellbook/spellbook.py:5285-5306
  IMPACT: Fixes B, D, E, F and G without touching how rows move; `_rollback_spellbook_move` and
    `_rollback_inactive_members` keep their signatures and bodies (their unit tests call them directly). Recorded for
    the patch: after a no-move transfer a parked managed version has a pool in each root (the source keeps its old one,
    as no-move keeps parked rows), so once that version is notched in, a release by class needs `conduit=`.
  NEXT: Write the S6 component and code-description patches and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = STORY.read_text(encoding="utf-8")
marker = "\n## Closure Confirmation"
assert text.count(marker) == 1
text = text.replace(marker, "\n" + FACT + "\n" + DECISION + marker, 1)
old = "- Updated: 2026-10-15T18:18:41Z"
assert text.count(old) == 1
text = text.replace(old, f"- Updated: {NOW}", 1)
old = "- [ ] Read `_apply_notch` (U9), the flip and `_migrate_inactive_members` whole."
assert text.count(old) == 1
text = text.replace(old, "- [x] Read `_apply_notch` (U9), the flip and `_migrate_inactive_members` whole.", 1)
old = "## Open Questions\n- U9 (epic B8).\n"
assert text.count(old) == 1
text = text.replace(old, "## Open Questions\n- U9 answered (FACT note of " + NOW + "): a notch never re-stamps.\n"
                    "- For the owner: stamping versions staged before conjure (DECISION note, point 6).\n", 1)
old = "## Decision Log\n- None yet.\n"
assert text.count(old) == 1
text = text.replace(old, "## Decision Log\n- " + NOW + " (melder_0): the owner stamp follows the lineage both ways"
                    " - parked members\n  re-stamped, stamps rolled back, composed pools discarded (DECISION note).\n", 1)
old = "- Next: read the transfer path and `_apply_notch` whole, then probe a managed transfer as it stands."
assert text.count(old) == 1
text = text.replace(old, "- Next: the S6 component and code-description patches and the mapping note, then red tests.", 1)
old = "- State: in_progress on 0.2.8245 (PLAN note)."
assert text.count(old) == 1
text = text.replace(old, "- State: in_progress on 0.2.8245; U9 answered and the probe read (FACT), the fix designed"
                    " (DECISION).", 1)
STORY.write_text(text, encoding="utf-8")
long_lines = [ln for ln in text.splitlines() if len(ln) > 120 and not ln.lstrip().startswith(("- ", "|"))]
print("long prose lines:", len(long_lines))
for ln in long_lines:
    print(len(ln), ln[:80])
