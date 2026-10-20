# Repair proposal: Spellbook.find_spell_by_id under concurrent binds and removals

Status: PROPOSED for owner review (melder_1, 2026-10-10). Nothing is implemented: no change under `src/`, `tests/`,
`docs/` or `release_docs/`, no notch, commit or push. Ticket:
`context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md` (Notes 1-12).

## Source identity

- Branch `codex_features2` at `3d184cac699dfb5981449e8b841624e2eea59276` (Melder 0.2.8228), equal to the local
  `origin/codex_features2` ref (0 ahead / 0 behind; no fetch). Working tree equal to HEAD in content (1753 files
  differ only in CRLF endings); no uncommitted source change; the scan/bind work is committed in 3d184cac.
- The race surface (`find_spell_by_id`, `_get_spell_by_id_via_aether`, `bind`, `cleanup_and_remove_spell`,
  `_destroy_spell_index`, park/unpark, `transaction`, `SpellIndex.has_spell` / `cleanup`) is byte-identical at
  0.2.8226 (the MelderOps install), 0.2.8227 and 0.2.8228.
- Every run used a `git archive` export of 3d184cac on the device VM (CPython 3.14.7 free-threaded build, 2 vCPU,
  pytest 9.1.1), under `-X gil=0` and `-X gil=1`. The candidate repair was applied to separate scratch exports only.

## What is broken - a current, reproduced defect

`find_spell_by_id` walks the live `Spellbook._spells` dict with no lock. `bind` inserts into that dict inside its
mediator transaction window without `self._lock`; the remove, park and destroy paths pop under `self._lock`, which
the walk never takes; removals clean the popped index after releasing the lock. In every mode below the searched
spell is registered before the lookup and never touched - only ANOTHER spell changes:

| mode | interleaving | result on 3d184cac |
| --- | --- | --- |
| a | a bind or a removal between two steps of the walk | `RuntimeError: dictionary changed size during iteration` |
| b | the probed index is cleaned between `has_spell`'s check and its lock | `AttributeError: ... no attribute '_spells_in_index'` |
| c | the probed index is cleaned before `has_spell`'s check | `RuntimeError: SpellIndex has already been cleaned. ` |
| d | a removal plus a bind leave the size unchanged but resize the dict | NO exception: the walk skips entries and answers None |

Mode (d) is a silent wrong answer: the lookup returns None for a spell that is still registered. Modes a-d are
forced deterministically by `diagnostics/test_find_spell_by_id_race.py` (Event handshakes, no sleeps): 7 contract
tests fail and 6 characterization tests pass in 10 of 10 runs under each GIL mode, through `find_spell_by_id` and
through `Conduit.get_spell_by_id` on a dynamic root (the MelderOps path). The uninstrumented stress
(`diagnostics/stress_find_spell_by_id.py`, 4 writers binding and removing, 4 readers, 40 rounds) failed every
round under `gil=0` (1650 size-change errors and 4 wrong None results in 4,111,061 lookups) and no round under
`gil=1` (0 in 6,756,101): reachable under the GIL when the interleaving occurs, rare in practice. The MelderOps
report (5 of 40 on CPython 3.14.8t / melder 0.2.8226) is historical evidence of the same code; its two signatures
reproduce verbatim on 3d184cac.

## Proposed repair R1 (the smallest correct one)

Two private changes; no public API change; `SpellIndex.has_spell` keeps its contract (it still raises once cleaned).

```python
# src/melder/aether/spellbook/spellbook.py - Spellbook.find_spell_by_id
self.check_cleaned()
for spell_index, spell in list(self._spells.items()):          # was: self._spells.items()
    if spell_index._has_spell_unless_cleaned(spell_id):        # was: spell_index.has_spell(spell_id)
        return spell
return None

# src/melder/aether/spellbook/bind/spell_index.py - new internal probe
def _has_spell_unless_cleaned(self, spell_id: str) -> bool:
    with self._lock:
        if self._cleaned:
            return False
        return spell_id in self._spells_in_index
```

The full diff, with the docstring and comment changes, is `proposal/proposed_patch_r1.diff` (applies cleanly to
3d184cac with `patch -p1`).

- `list(self._spells.items())` is a one-call snapshot: CPython 3.14's `list_extend` holds the dict (its critical
  section on free-threaded builds) around `list_extend_dictitems`, which builds the pairs in C with no Python code
  in between. That fixes (a) and (d). `dict.copy()` is equally atomic but cost half to two thirds of the contended
  reader throughput (variant R1a, measured and rejected); `tuple(d.items())` is not atomic.
- The probe reads the cleaned flag and the member set under the index lock that `cleanup` holds while deleting the
  set, and treats a cleaned index as owning nothing. That fixes (b) and (c).

## Locking, ownership and reentrancy

- No new lock and no lock held across the walk. The snapshot takes only the dict's internal critical section for
  one C call; the probe takes each index's RLock in turn, exactly the lock `has_spell` takes today. No nesting, so
  no new lock-order edge. Bind, removal and park write paths are untouched (the 2026-06-14 precedent rejected
  write-path locking for gauntlet cost).
- Reentrancy is unchanged: a caller holding an index's RLock re-enters it in the probe as it does in `has_spell`.
- Ownership is unchanged. The snapshot is a local list of borrowed `(SpellIndex, Spell)` references dropped at
  return; it can keep a concurrently removed spell's objects alive until the call returns, nothing longer.
- The banned-patterns rule on snapshotting owned registries is met: the snapshot is required for correctness and
  the reason is written at the site and in the docstring.

## Compatibility risks

- Semantics are those of the snapshot instant: a spell bound after it is not seen by that call; an index cleaned
  after it is skipped, so a lookup racing the removal of the SEARCHED spell answers None (a removal that finished
  first) or the spell (one that had not) - never an exception. A lookup racing a notch can return the outgoing
  active spell. All three are within the documented contract ("a concurrent removal or graft can invalidate it").
- No caller relied on the exceptions: the Melder callers (Phase-4 ambiguity report, restore and graft binds, ward
  link/contract/transfer resolution through `Conduit.get_spell_by_id`) treat None as "not found".
- Residual, unchanged: a Spellbook cleaned concurrently with the lookup can still raise (use after cleanup is a
  caller contract violation). The other `_spells` walkers and the SpellIndex check-then-lock pattern are not
  touched (scope options below).
- Cost (single thread, median of alternated runs, both GIL modes): an early hit pays the snapshot, +20..50 ns at 1
  spell, +0.1 us at 8, +0.75..0.9 us at 64, +5.5..5.7 us at 512; a full walk or a miss is within -4%..+2%.
  Contended (2 readers + 2 writers): reader and writer throughput equal to 3d184cac within noise, no failures.
  `find_spell_by_id` has no caller on the meld door path; the gauntlet was not run (owner-run).

## Regression tests (to land with R1)

- `tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id_concurrency.py`: the 7 contract
  tests of the diagnostics (modes a1, a2, b, c, p, d and the searched-spell removal), with their harness. They
  fail on 3d184cac and pass with R1 in 10 of 10 runs per GIL mode. They pause through `SpellIndex.has_spell` and
  the chosen index's `_lock`, the only seams that force the interleavings deterministically; that coupling is
  documented in the file. The characterization tests are evidence only and do not land.
- `tests/unit/melder/spellbook/bind/test_spell_index_membership.py`: `_has_spell_unless_cleaned` answers True for
  the selected and a superseded member, False for a non-member, False (no raise) once cleaned.
- Existing directories run on 3d184cac and on R1 (6,388 tests: unit spellbook and conduit, component spellbook
  and conduit, integration spellbook, aether/conduit, conduit and crystallizer): identical results, all green.

## Scope options (not in R1)

- R1c, keys-only snapshot: `list(self._spells)` plus one `self._spells.get(index)` on a hit. Early hit +1.3 us at
  512, full walk about 15% faster than today, contended readers about 5-8% lower, one more read of the live map
  and a branch for an index popped between the probe and the get. Only if early-hit latency on large books
  matters more than the simpler loop.
- R2, SpellIndex check-then-lock: `has_spell`, `__enter__`, `spells_in_index` and the other members check
  `_cleaned` before taking the lock, so any reader racing a cleanup gets AttributeError instead of the documented
  RuntimeError. Fixing it (check inside the lock; `__enter__` acquires, then checks and releases on failure)
  gives every `has_spell` caller the documented error. Eight sibling walks were located by search outside the
  Spellbook (ticket Note 4); their locking is unread. A follow-up task.
- R3, the other `_spells` walkers: `_find_spell_index_by_index_id` (behind `Spellbook.get_spell_by_index_id`),
  `inspect_spell` and `_check_all_spells` walk under `self._lock`, which excludes the pops but not bind's insert;
  `_publish_nexus_state_for_conjure` walks with no lock. Same mechanism by reading; not reproduced. A follow-up
  task reusing this harness, or folded into R1 if the owner wants the class consistent in one change.
- Not recommended: making `bind` take `self._lock` for its map writes. It would serialize the locked readers but
  adds a lock to the bind path and does nothing for the unlocked lookup.

## Decisions for the owner

1. Approve R1 as the repair (recommended), or choose R1c.
2. R2 and R3: separate follow-up tasks (recommended) or folded into this change.
3. On approval, the landing is a source change: patch lane per patch_framework_gating (architecture, component
   and code-description patch docs - the change is concurrency-sensitive), the next notch above 0.2.8228, a
   running release-note entry, system-document and graph updates, then the asset and llm_support rebuild last.

D-10, D-11 and D-20 are separate, open and untouched by this work.

## Validation status

- Run here: the diagnostics, stress, benchmarks and the 6,388-test comparison listed above (logs in `runs/`).
- Not run: the full test tree, the owner's Windows tiers, hosted CI, the gauntlet, and MelderOps' x40 closure run
  (MelderOps was not contacted, per the owner).
