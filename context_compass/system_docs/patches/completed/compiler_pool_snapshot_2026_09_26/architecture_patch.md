# architecture_patch

## Metadata
- Patch ID: compiler_pool_snapshot_2026_09_26
- Status: draft
- Owner: user (implementation: melder_0)
- Created: 2026-09-26T21:20:00Z
- Ticket: tickets/tasks/2026-09-26_snapshot_phase5_live_spell_pool_task.md

## Objective
Compiler passes that run outside a transaction (meld-time structural reruns, conduit-local resolution,
deferred 8-11) read the Spellbook's active spell pool while binds, notches, contract grants and transfers
change it under the Spellbook lock. Every such pass must read one consistent copy of the pool, so a
concurrent change can neither abort the pass nor silently drop part of its analysis.

## Non-goals
- No new lock, no change to who writes the pool or how.
- No change to which spells a pass sees when no write lands during it.
- Conjure-time sweeps inside the CONJURE transaction and the Nexus relationship publisher are not changed.

## Changed Components
- SpellCompiler and Validation Pipeline: Phase 3 candidate scans, three Phase-4 validation strategies,
  Phase 5 (frame-wide and local), Phase 6 frame-wide, the Phase-8 pool walk.

## Invariants
- I1: a pass iterates `pool.copy()`, taken in one call, never the live dict. The copy is atomic: the dict's
  own lock on free-threaded builds, the GIL otherwise.
- I2: Phase 5 uses the same copy for its visible set and every spell lookup in the pass.
- I3: Phase 5 admits only ids present in its adjacency snapshot (ids with a registered SpellSystemState).
  Bind publishes the pool entry before registering the state; a spell in that gap is left to the
  revalidation its bind schedules. Such an id makes today's pass raise, so steady state is unchanged.
- I4: the Spellbook lock is not taken by any pass (no lock-order change).

## Interface Deltas
- None. Private reads only; no signature, return value or error text changes.

## Migration Order
1. Regression tests (red on the current tree). 2. Edits in the listed files. 3. Tests green; suites on
3.14t and GIL. 4. Canonical docs, graph, 0.2.72 notch, release entry, assets, LLM bundles.

## Rollback
- Revert the edits; no persisted format, cache generation or public surface changes.

## Ticket Coverage Matrix
| section | implementation | validation |
| --- | --- | --- |
| I1 | copies at each iteration site | mutating-pool regression tests per pass |
| I2, I3 | Phase 5 frame-wide and local | pool entry without state; mutating pool |
| I4 | no lock added | code review of the diff |
