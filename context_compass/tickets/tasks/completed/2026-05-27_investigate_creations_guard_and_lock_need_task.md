# Task: Investigate Creations guard and lock need

## Metadata
- Task ID: TASK-2026-05-27-investigate-creations-guard-and-lock-need
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p0
- Created: 2026-05-27T00:00:00Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Audit `Creations` for removable guards and whether its explicit `RLock` still
needs to exist now that plain/raw and disposable/tuple storage are split and
Python 3.14t dict operations are internally locked.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the lane to investigation-only on
  `Creations` guards and lock need.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/creations/creations.py`
  - directly implicated hot runtime callsites in
    `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-26_implement_plain_ref_creation_storage_for_non_disposable_entries_task.md`
  - `tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
  - `tickets/epics/2026-05-24_melder_runtime_performance_optimization_epic.md`
- EXIT_GATE: the audit clearly separates removable guards from correctness-
  carrying guards and explains whether `_lock` can be reduced or must stay.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if proving the lock-removal case
  requires widening into broader conduit/meld/transaction redesign.

## Scope Boundaries
- In scope:
  - `Creations` cleaned-state guards
  - `Creations` explicit `RLock` usage
  - whether internal dict locks are enough for the current multi-structure
    mutations
  - directly implicated generated miss/create lock usage only as evidence
- Out of scope:
  - code changes
  - wider `Meld` cleanup
  - scheduler or transaction redesign

## Steps / Checklist
- [ ] Read `creations.py` guard and lock sites.
- [ ] Read the directly implicated generated `caller_creations._lock` sites.
- [ ] Separate hot-path lock-free behavior from maintenance/destructive paths.
- [ ] Summarize removable-guard candidates and the real lock-necessity story.

## Validation
- Not run.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-27T00:00:00Z
  TYPE: FACT
  CLAIM: `Creations` itself is already mostly lock-free on the hot path. The
    split storage add/get methods do not take `self._lock`; the explicit lock is
    only used on cleanup, extract, restore, and pooled reset paths. The
    directly generated hot runtime still takes `caller_creations._lock` on
    singleton/shared/spellspace miss paths before create/register, which means
    the real contention question is not the add/get surface in `Creations.py`
    but the emitted miss/create critical sections in `creation_context_codegen.py`.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:86-96
  - src/melder/aether/conduit/creations/creations.py:341-412
  - src/melder/aether/conduit/creations/creations.py:444-644
  - src/melder/aether/conduit/creations/creations.py:825-875
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:547-579
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:690-797
  IMPACT: The broad claim “remove the `Creations` lock because dicts already
    lock themselves” is too coarse. The plain add/get surface is already there.
    The explicit `Creations._lock` is currently protecting multi-structure
    mutation (`_creations`, `_disposable_creations`, `_disposal_stack`,
    `_spellspace_disposal_stacks`) during cleanup, extract/restore, and pool
    reset.
  NEXT: explain which guards/locks are probably removable and which still carry
    real correctness under the current storage model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to answer one narrow question: which `Creations` guards and
lock sites are actually still needed after the storage-model split.

