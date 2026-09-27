# architecture_patch

## Metadata
- Patch ID: shared_context_rebuild_2026_09_26
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T13:57:58Z
- Updated: 2026-09-26T13:57:58Z
- Lineage: completes the September design (system_docs/patches/completed/shared_context_rebuild_2026_09_05/),
  adapted to source changes made since (Phase-5 target-only publication 2026-09-19, slot build guards 2026-09-25).

## Patch Scope and Non-Goals
- Objective: make a dynamic spell's shared CreationContext safe while a conduit-local rebuild replaces it. Two
  races are closed together: (1) a meld builds a context from the gap between Phase 5 clearing the phase-11 plan
  and Phase 11 republishing it ("Cannot build CreationContext before spell_codegen_creation exists"); (2) a meld
  keeps using a context that Phase 5 cleans under it (AttributeError on a deleted slot).
- Non-goals:
  - No change to revalidation itself: the same phases run with the same effect.
  - No change to automatic-mode doors or the fast meld door.
  - No change to CounterSwitch, CreationGate, existence semantics or public meld signatures.
  - Resets outside rebuild windows (ownership restamp, notch, teardown, transfer) are not drained.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Meld Resolution Runtime (doors, producers) | modify | admit before reading; producers enter a rebuild window | Spell gate field |
| Spell context lifecycle (Spell, CreationContextFactory, CreationContextRebuild) | modify | stable gate reference; failed-build release; finish the window | none |

## Interface and Boundary Deltas
- Private only. Spell gains `_creation_gate` (borrowed spell-index CreationGate, dynamic only) and
  `_creation_context_failure`. CreationContextFactory gains `resolve_spell_index_gate(spell)`. Meld gains
  `_rebuild_window(spell)` and `_execute_admitted(...)`. CreationContextRebuild (already in src, unused) is wired.
- Behaviour: dynamic melds take their spell-index ticket before reading the context instead of inside
  `CreationContext.execute*` (one ticket pair, moved, not added). A failed context build no longer strands the
  switch at pending.

## Cross-Component Invariants
- A dynamic meld holds exactly one spell-index ticket from before it reads the context until its executor returns.
- Every conduit-local rebuild of a dynamic spell (structural 1-4, resolution 5-11, deferred 8-11) runs inside a
  window that freezes and drains that spell's index gate before phases touch the plan or context, and publishes
  the rebuilt context before reopening.
- Lock order: rebuild window (gate transition lock, drain) BEFORE spell._lock. Reason: an Existence.unique build
  holds the spell lock while its meld holds a ticket.
- Producers run before admission, so no producer drains its own ticket.
- Warm reads stay lock-free; no new lock on any meld path.

## Migration and Rollout Order
1. Spell fields and factory failure release (apply_sept_spell_factory.py).
2. Window completion, Meld producers and dynamic doors (apply_sept_window_doors.py). Steps 1-2 are one unit.
3. Test stubs model the new fields; the two September regressions are unskipped (apply_sept_test_stubs.py).
4. Contract tests (apply_sept_tests.py).
5. Promote to src_architecture/src_components, graph descriptors and release note; assets rebuilt by the owner.

## Rollback Strategy
- Rollback trigger: a suite failure attributable to the six source files.
- Rollback steps: the worktree is shared by several agents, so rollback is a reverse edit of exactly these
  hunks (the apply scripts' blocks, inverted), never a file restore or checkout. Source steps 1-2 are one unit.
- Post-rollback verification: unit/component/integration suites and the concurrency file loop.

## Validation Expectations and Evidence Plan
- Before: concurrency file 7/40 runs failing; deterministic September regression fails
  (results/file_runs_40.txt). After: 40/40 green (results/file_runs_40_sept_final.txt), 18 new or changed tests
  that fail on unpatched source pass; suites equal to unpatched apart from the new passes
  (results/suite_comparison.txt, results/integration_patched.txt); warm meld within noise
  (results/warm_meld_bench.txt).

## Ticket Coverage Map
- Epic: none (successor to tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md)
- Story: none
- Tasks: tickets/tasks/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md

## Unknowns and Decision Requests
- RISK (not observed): many_only override hydration reads the live Phase-5 blueprint; an old plan's first
  override run that overlaps a rerun would read the new path registry. Under this patch that overlap cannot
  happen for dynamic melds (the window drains them); automatic mode is unchanged.
- Known limit: a meld whose own constructor melds the same spell through a conduit that must rebuild drains
  itself (30 s drain timeout, RuntimeError).
- DECISION_REQUEST: owner confirms the exact change before device source is edited.

## Context / Handoff Summary
- What changed: see component_patch_meld_runtime.md, component_patch_spell_context.md,
  code_description_patch_context_protocol.md.
- Next entrypoint: the task ticket's latest Notes NEXT.
