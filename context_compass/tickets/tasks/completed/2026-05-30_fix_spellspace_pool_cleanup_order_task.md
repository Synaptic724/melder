# Task: Fix spellspace pool cleanup order
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Task ID: TASK-2026-05-30-fix-spellspace-pool-cleanup-order
- Story: none
- Status: done
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T13:56:00Z
- Updated: 2026-05-30T15:06:13Z

## Objective
Fix `Conduit._cleanup_spellspaces_for_pool()` so pooled spellspace cleanup runs
once per spellspace and does not iterate live structures that the cleanup call
itself mutates.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a proper cleanup-order fix with no
  defensive-programming widening, and the active board routes this narrow slice
  before code edits begin.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-29_investigate_conduit_and_spellspace_pool_reset_cost_task.md`
  - `tickets/tasks/2026-05-30_start_spellspace_meld_split_task.md`
- EXIT_GATE: `_cleanup_spellspaces_for_pool()` establishes a stable deduped
  cleanup set, clears live stack/registry state before spellspace cleanup
  mutates them, and narrow syntax validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the fix requires widening
  beyond `_cleanup_spellspaces_for_pool()` into broader pooling/reset redesign.

## Scope Boundaries
- In scope:
  - `Conduit._cleanup_spellspaces_for_pool()`
  - attention-board routing for this narrow fix
- Out of scope:
  - broader conduit reset redesign
  - spellspace pool redesign
  - tests beyond narrow syntax validation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested an implementation fix for the pool
  cleanup order after the reset-path review.

## Steps / Checklist
- [ ] Reconfirm the exact pool cleanup mutation hazard from live source.
- [ ] Patch `_cleanup_spellspaces_for_pool()` only.
- [ ] Run narrow syntax validation on the touched file.
- [ ] Summarize the fix and remaining reset-path debt separately from this
      patch.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one bounded cleanup-order fix in `Conduit._cleanup_spellspaces_for_pool()`
- one narrow validation result

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py`
- `codex/context_compass/tickets/tasks/2026-05-30_fix_spellspace_pool_cleanup_order_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/conduit/conduit.py`

## Risks / Rollback Notes
- Risk: changing iteration order without preserving dedupe could still double
  release spellspaces into the pool.
- Rollback: revert only the `_cleanup_spellspaces_for_pool()` ordering change.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into broader pooling redesign.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: exact cleanup-order hazard, concrete patch impact, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-30T14:02:18Z
  TYPE: MEASURE
  CLAIM: The conduit cleanup-order fix is now in the minimal form. The stack
    loop is back to the simple direct iteration over
    `self._spellspace_stack.get()`, then the active thread-local stack is
    cleared, and the remaining registry entries are drained in place with
    `self._spellspace_registry.pop().cleanup()`. This keeps your lean stack
    path and fixes only the unsafe direct set iteration in the second loop.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:381-394
  IMPACT: The fix now stays narrow: no merged worklist snapshot, no extra alias
    machinery, just one safe registry-drain change.
  NEXT: report the corrected minimal fix to the user and stop unless they want
    stronger validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T14:02:18Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed again after reducing the fix to the
    minimal form. `python -m py_compile src/melder/aether/conduit/conduit.py`
    completed successfully.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:381-394
  IMPACT: The minimal registry-drain patch parses cleanly.
  NEXT: if broader validation is wanted later, run the directly implicated
    conduit/spellspace pool tests in a separate slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T14:01:38Z
  TYPE: FACT
  CLAIM: The previous merged-worklist fix was heavier than this seam needs. The
    actual correctness bug is only the direct `for spellspace in
    self._spellspace_registry` iteration, because `spellspace.cleanup()` mutates
    that set through `discard(self)`. The minimal fix is to keep the active-stack
    cleanup loop simple and then destructively drain the live registry with
    `pop()` so each remaining spellspace is cleaned exactly once without a
    snapshot list.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:381-394
  - src/melder/aether/conduit/spell_space/spell_space.py:142-157
  IMPACT: The patch can stay correctness-driven without the extra merged alias
    worklist.
  NEXT: replace the merged-worklist version with the simpler stack-loop plus
    registry-pop drain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T13:59:06Z
  TYPE: FACT
  CLAIM: The active-stack side does not require an additional snapshot because
    `SpellSpaceThreadState.get()` already returns a detached list copy. The
    avoidable extra allocation in the current fix is the merged
    `list(dict.fromkeys([*stack, *registry]))` worklist. A stricter no-extra-
    snapshot fix can drain the detached stack first while using the live
    registry as the dedupe source, then drain the remaining registry entries
    in place.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:64-76
  - src/melder/aether/conduit/conduit.py:387-394
  - src/melder/aether/conduit/spell_space/spell_space.py:142-157
  IMPACT: We can preserve the cleanup-order fix without keeping the merged
    spellspace snapshot list.
  NEXT: replace the merged snapshot list with a destructive stack-first then
    registry-drain cleanup order in `Conduit._cleanup_spellspaces_for_pool()`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T13:57:11Z
  TYPE: MEASURE
  CLAIM: The cleanup-order fix is landed in `Conduit._cleanup_spellspaces_for_pool()`.
    The method now captures one deduped spellspace list from the active stack
    and registry, clears the live stack/registry first, and then calls
    `spellspace.cleanup()` once per spellspace. That removes the live-registry
    mutation-during-iteration bug and the double cleanup/release path for
    spellspaces that were present in both structures.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:381-394
  IMPACT: Pooled spellspace cleanup now respects the intended contract:
    spellspaces reset and return to their pool, but conduit-side cleanup no
    longer iterates structures that those cleanup calls mutate.
  NEXT: report the fix to the user and keep any remaining broader pooling/reset
    redesign separate from this patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T13:57:11Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed for the conduit cleanup-order fix.
    `python -m py_compile src/melder/aether/conduit/conduit.py` completed
    successfully.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:381-394
  IMPACT: The bounded cleanup-order patch parses cleanly.
  NEXT: if stronger validation is wanted later, run the directly implicated
    conduit/spellspace pool tests in their own slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T13:56:00Z
  TYPE: FACT
  CLAIM: The current pool cleanup bug is local to
    `Conduit._cleanup_spellspaces_for_pool()`. It iterates the active stack and
    then the live spellspace registry while calling `spellspace.cleanup()`, but
    the reusable spellspace cleanup path mutates that same registry and returns
    the spellspace to its pool. That means the current order is vulnerable to
    set-mutation iteration failure and duplicate cleanup/release of the same
    spellspace.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:381-399
  - src/melder/aether/conduit/spell_space/spell_space.py:116-126
  - src/melder/aether/conduit/spell_space/spell_space.py:142-157
  IMPACT: The correct fix is to establish the cleanup set before mutating live
    routing structures, clear the live stack/registry first, then call
    `spellspace.cleanup()` once per spellspace.
  NEXT: patch only `_cleanup_spellspaces_for_pool()` in `conduit.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to fix the local spellspace pool cleanup-order bug without
widening into a broader reset or pooling redesign.
