# find_spell_by_id race - review of the Book-lock design (R4) and the adapted repair (R5)

melder_1, 2026-10-10. Ticket: tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md (Notes 14-20).
Base: 3d184cac (0.2.8228, branch codex_features2, HEAD of the repository). Nothing is applied to the repository:
every candidate ran only in scratch `git archive` exports under /tmp/cc_lookup on the device VM, CPython 3.14.7
free-threaded, -X gil=0 and -X gil=1. No notch, commit or push. MelderOps' baseline is untouched; D-10, D-11 and
D-20 and R2/R3 stay separate.

## 1. The access inventory holds (Note 14)

Nine live statements change `Spellbook._spells`: removal pop (spellbook.py:662), notch park pop (1510), notch
promote insert (1572), index destruction pop (4003) - all under `self._lock`; the transfer flip (pop 1448, insert
1456) and its rollback (pop 954, insert 960) under `SafeGuard` over both Book locks; and bind's publication insert
(5358) with no Book lock. Book teardown clears and deletes the map under the lock. No alias mutates it, and no
path cleans a SpellIndex while it is still in the map outside the lock. Full table:
`r4/spells_access_inventory.txt`.

## 2. R4 as written cannot land (Notes 15-16)

R4 holds the Book lock across the lookup's walk. Conjure holds the same lock across its whole pipeline
(`_conjure_within_transaction_window`), and two things inside that pipeline run on other threads and can call the
lookup:

- Phase 4 runs only on scheduler worker threads, and `AmbiguousProviderStrategy._describe_candidates` calls
  `find_spell_by_id`. With R4, the existing test
  `test_two_same_named_classes_in_two_categories_are_reported_with_both_addresses` stalls for the full 60 s
  barrier and fails with `PhaseTimeoutError("Phase 'validation' exceeded barrier timeout (60000 ms)")` instead of
  the readable `[AMBIGUOUS_PROVIDER]` report (3d184cac: 0.58 s). Log: `r4/runs/r4_literal_ambiguous_conjure_gil0.log`.
- Conduit lifecycle hooks run inside the same region. A post-created hook that waits for a lookup made on another
  thread blocks (bounded at 5 s in the probe; an unbounded join hangs for ever), both GIL modes.
  `r4/runs/probe_conjure_hook_foreign_lookup.log`.

Holding the lock only around a one-call snapshot (R4b) fails both identically. The rule: while conjure holds the
Book lock and waits on other threads, the lookup must not acquire that lock.

R4's writer half is sound and costs nothing in lock order: bind's very next statement (`_register_owned_spell_id`)
already takes the same lock, with the same locks and transaction claims held.

## 3. Proposed repair R5 (`proposal/proposed_patch_r5.diff`, 142 lines, 2 files, 3 methods)

- `Spellbook.find_spell_by_id`: R1's reader, unchanged in behaviour - walk `list(self._spells.items())`, a
  snapshot taken in one C call under the dict's own critical section, and probe each index with the new internal
  `SpellIndex._has_spell_unless_cleaned`. No lock is taken. The docstring now states why the lookup takes no lock,
  what the snapshot guarantees, the residual (below), and that the returned Spell is a borrowed reference, not a
  lease.
- `SpellIndex._has_spell_unless_cleaned`: reads `_cleaned` and the member set under the index's own lock and
  answers False for a cleaned index. `has_spell` is unchanged.
- `Spellbook.bind`: R4's publication lock - `_lookup_spells`, `_spells` and `_register_owned_spell_id` (the
  four active maps) publish inside one `with self._lock:`, as the notch promote path already does; `claim_lookup`
  and every registration callback stay outside it.

Locking, ownership, reentrancy: the reader adds no lock and no lock-order edge; the index lock it takes is a leaf,
taken alone, as `has_spell` takes it today. The writer change moves an existing acquisition two statements earlier
in the same context, so it adds no edge either; the lock is a reentrant RLock, so a bind on a thread that already
holds the Book lock (scan or bind inside conjure) re-enters. Nothing changes ownership: maps stay Book-owned,
Spells stay borrowed.

Semantics: the lookup answers for the map at its snapshot - a spell bound after it is not seen, an index cleaned
after it owns nothing. It never raises for a concurrent bind, removal, notch, transfer or rollback, and never
hides a spell whose index stays in place.

Residuals, documented in the docstring and pinned by the matrix: a lookup that overlaps a notch of its own
lineage can answer None (the snapshot falls between the notch's park and promote), and so can a lookup of an id
being moved between indexes (read in neither). 3d184cac answers None in both cases too, so R5 does not regress
them; a caller that needs a linearizable answer holds the Book lock across the call. Whole-book teardown between
the lookup's `check_cleaned` and its snapshot stays out of scope (AttributeError, as today).

## 4. Alternative R4' (linearizable lookups)

R4 plus phase 4's ambiguity report resolving candidates with `spellbook._spell_id_pool.get(candidate_id)` instead
of `find_spell_by_id` (a third file). It passes everything R5 passes, and also the notch and membership-move
cases. Costs: a conduit hook that waits on a foreign-thread lookup still deadlocks (a new contract to document:
lifecycle hooks must not wait on threads that read this Book); 3 unit tests of the strategy that stub
`find_spell_by_id` need rewriting; readers serialize on the Book lock (about -10% contended reader throughput on
two cores, flat +50-60 ns per call); and every future path that holds the Book lock while it waits on another
thread is a deadlock candidate - the Book lock is held across conjure, its user hooks, cleanup (which joins the
phase workers) and crystallizer emissions.

## 5. Evidence

Fair matrix (`r4/diagnostics/test_lookup_fair_matrix.py`, 17 tests): probe and writer on their own threads, Book
locks replaced by a watch that reports a party finding the lock held, Event handshakes, watchdogs only. Three
repetitions x two GIL modes per tree; every cell identical in all six runs (`r4/runs/matrix_table.txt`):

| tree | fails |
| --- | --- |
| 3d184cac | 14 of 17 (passes n1, h1, h2) |
| R1 | g1 notch gap, m1 membership move, l1 Book-locked walker vs bind |
| R4, R4' | h2 conduit hook waiting on a foreign lookup (and, for R4, the conjure-time ambiguity test) |
| **R5** | **g1, m1** (both also fail on 3d184cac) |
| NC1 = R5 without the snapshot | 13 |
| NC2 = R5 without the cleanup-safe probe | b, c, self-removal, g1, m1 |
| NC3 = R4's reader lock without the publication lock | a3, l1, h2 (the reviewer's negative control, reproduced) |

The original 13 forced diagnostics on R5: 7 contract tests pass, 6 characterization tests fail, both GIL modes.

Regressions: the full test tree on full exports, 3d184cac against exactly the proposed R5 source, -X gil=0:
13,640 passed, 31 skipped, 17 xfailed, 2 xpassed on both, no failure (`r4/runs/suites/summary_full_tree_gil0.txt`).
The three ambiguity test files run directly: 49 passed on R5 (the full tree covers the other three).

Opposite-direction transfers (two dynamic roots, 6 movers each way, 2 readers, 60 s watchdog, with and without every
2nd transfer forced to fail after its flip, gil 0 and 1): no deadlock in any row; every forced failure rolls back;
every mover ends with exactly one owner; both Book locks free afterwards; stable lookups never fail on R5 or R4'
(`r4/runs/opposite_transfer_table.txt`). The matrix's t2 forces a transfer rollback inside a walk: 3d184cac hides
the searched spell after the resize, every candidate finds it. A bind forced to fail after publication behaves
identically on 3d184cac, R5 and R4': it raises, leaves the Book lock free, keeps its published entry (bind's
existing no-unpublish contract) and the next bind works (`r4/runs/probe_bind_failure_after_publication.log`).

Performance (nproc 2, `r4/runs/bench_table_gil*.txt`, `contended_*.log`): R5 adds 15-22 ns per call on a one-spell
Book and an O(n) snapshot to an early hit (+0.6 us at 64 spells, +5.1-5.3 us at 512); full walks and misses
within -1..+3%. Contended with writers it matches 3d184cac (688-735k vs 696-731k lookups/s at gil=0, and 3d184cac
raised 768-814 failures per 3 s window); readers-only it is 12-15% slower, because two readers contend on the
dict's critical section. R4' costs a flat 48-60 ns and about 10% of contended reader throughput. No meld door
calls the lookup.

## 6. Compatibility

- Public API unchanged. The lookup no longer raises RuntimeError("dictionary changed size during iteration"),
  AttributeError('_spells_in_index') or RuntimeError("SpellIndex has already been cleaned. ") for concurrent
  changes, and no longer silently misses a stable spell when the map resizes.
- A lookup racing a bind sees the map at its snapshot (it may not see the new spell); it did not see it reliably
  before either.
- `SpellIndex` gains one internal method. The bind publication now excludes Book-locked walkers (index-id lookup,
  inspection, the ward's local-id check, change control): matrix l1 proves the index-id walk no longer breaks.

## 7. Regression tests to land (on approval)

From the fair matrix, as a component test file under tests/component/melder/spellbook/: a1, a2, a3, b, c, d, p,
self-removal, n1, n2, t1, t2, l1, h1 and h2 (contract tests, green on R5); g1 and m1 as strict xfail naming the
documented limitation, so a later linearizable repair turns them into failures to update. Plus a unit test for
`_has_spell_unless_cleaned` (live member, non-member, cleaned index). The conjure-time ambiguity tests already in
the suite guard the lock-free reader.

## 8. Decisions for the owner

1. R5 (recommended: no lock edge, fixes every reported mode, no suite change) or R4' (linearizable, with the
   hook constraint, the phase-4 and unit-test changes and reader serialization). R4 as written: not recommended.
2. Separate follow-ups, not in this repair: (a) `Conduit.get_spell_by_id` raises ValueError("Spell version ...
   not found in any conduit.") with an ERROR log for an id no conduit claims (a removed spell, or one between
   owners in a transfer), while it and `Spellbook._get_conduit_by_spell_id` document None (aether.py:2478-2517) -
   MelderOps' path meets it; (b) R2, `has_spell`'s check-then-lock for its other callers; (c) the reviewer's list -
   permissions lookup (`Conduit.get_spell_permissions`, walks under the conduit lock only), command-system lookup,
   foreign-Book inspection and contract-proxy iteration - plus the other unlocked walkers in the inventory.
3. On approval the landing is a source change: patch lane (architecture, component and code-description docs),
   the next notch above 0.2.8228, a release-note section, src_components / src_architecture and the graph, the
   regression tests, then the build assets and llm_support rebuilt and checked last.

Not run: the owner's Windows tiers, hosted CI, the gauntlet, MelderOps' x40 closure run, the full tree under
-X gil=1 (the matrix, the transfers and the benchmarks ran under both modes), coverage.
