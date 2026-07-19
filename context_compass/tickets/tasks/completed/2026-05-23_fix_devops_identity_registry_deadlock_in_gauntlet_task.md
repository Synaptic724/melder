# Task: Fix devops identity and registry deadlock in gauntlet path

## Metadata
- Task ID: TASK-2026-05-23-fix-devops-identity-registry-deadlock-in-gauntlet
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-23T20:44:43Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Fix the runtime deadlock exposed by the Melder gauntlet's lesser-conduit churn
so the benchmark can run at realistic threaded job counts without hanging.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the lane from blind benchmark
  reruns to deadlock analysis after the threaded Melder-only benchmark hung.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/dev_ops/devops_identity.py`
  - `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
  - directly implicated benchmark validation only
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-23_fix_melder_only_gauntlet_benchmark_task.md`
- EXIT_GATE: the identity/registry deadlock is removed, focused benchmark
  validation completes at a multi-threaded setting that previously hung, and
  the fix is documented truthfully.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the deadlock root cause
  widens beyond the identity/registry path into conduit/ward lock-order
  redesign.

## Scope Boundaries
- In scope:
  - identity cleanup vs registry refresh/register lock ordering
  - registry rebuild behavior that runs while identities are mutating
  - focused gauntlet validation
- Out of scope:
  - unrelated benchmark semantics changes
  - broad conduit/ward architecture cleanup unless directly required
  - general performance optimization

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the threaded gauntlet hang now has a concrete runtime
  deadlock candidate in the dev-ops identity/registry path.

## Steps / Checklist
- [ ] Confirm the lock-order deadlock path in identity cleanup/registry rebuild.
- [ ] Patch the identity/registry interaction to remove the cycle.
- [ ] Re-run focused Melder gauntlet validation at the previously hanging
      multi-threaded settings.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one evidence-backed runtime deadlock diagnosis
- one narrow runtime fix in the identity/registry path
- one focused multi-threaded gauntlet validation result

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-23_fix_devops_identity_registry_deadlock_in_gauntlet_task.md`
- `codex/context_compass/attention_board.md`
- `src/melder/aether/aetheric_frame/dev_ops/devops_identity.py`
- `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
- `benchmarks/testing_other_di/test_melder_gauntlet.py` (validation only unless
  a tiny benchmark-side adjustment is strictly required)

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q -s benchmarks\testing_other_di\test_melder_gauntlet.py`

## Risks / Rollback Notes
- Risk: the deadlock may also involve conduit/ward cleanup lock ordering.
- Rollback: keep the fix limited to the identity/registry cycle first; if the
  hang persists, stop and split the next runtime seam explicitly instead of
  widening blindly.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No benchmark rerun spam without a code-backed deadlock theory.

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
- Note focus: deadlock facts, lock-order impact, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:37:34Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this remaining active lane for closure and
    requested that it be turned in and moved to the completed task set.
  EVIDENCE:
  - user_instruction
  IMPACT: This task is closed and should no longer route active work on the
    attention board.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-23T20:44:43Z
  TYPE: FACT
  CLAIM: The strongest current deadlock candidate is the identity/registry
    lock-order cycle in the lesser-conduit churn path, not the benchmark
    harness. `Conduit` creation attaches and refreshes a `DevopsIdentity`,
    which drives registry relation rebuilds; lesser-conduit cleanup later calls
    `self._transaction_identity.cleanup()`. `DevopsIdentity.cleanup()` currently
    calls `registry.unregister_identity(...)` while still holding the identity
    lock, and the registry rebuild path iterates live identities and reads
    `identity.metadata` while holding the registry lock. Under concurrent
    create/cleanup, that creates a classic identity-lock -> registry-lock vs
    registry-lock -> identity-lock cycle.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:172-212
  - src/melder/aether/conduit/conduit.py:356-404
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:106-148
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:287-337
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:235-289
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:383-425
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1175-1201
  IMPACT: The next fix should target the identity/registry interaction first,
    because that is the narrowest code path that explains why 1-thread and
    small 2/3-thread bounded runs pass while higher concurrent lesser-conduit
    churn hangs.
  NEXT: patch `DevopsIdentity.cleanup()` and/or registry relation rebuild so
    registry calls no longer occur while an identity lock is held.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T20:50:00Z
  TYPE: FACT
  CLAIM: The first narrow fix is now landed in `DevopsIdentity.cleanup()`.
    Cleanup no longer calls `registry.unregister_identity(...)` while still
    holding the identity lock. Instead it snapshots the attached registry and
    owner key, clears the registry reference, performs unregister outside the
    identity lock, and only then finishes the identity teardown.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:106-151
  IMPACT: This removes the exact lock-order inversion that was possible between
    identity cleanup and registry-side relation rebuild, without widening into
    broader conduit or ward cleanup changes yet.
  NEXT: rerun the Melder gauntlet at the previously hanging 3-thread / 5-job
    setting and see whether this narrow cycle removal is sufficient.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T20:52:00Z
  TYPE: MEASURE
  CLAIM: The narrow identity/registry lock-order fix is sufficient for the
    previously bad benchmark shape. The remade Melder-only gauntlet now
    completes cleanly at `1` iteration, `3` threads, `10` request scopes,
    `5` worker-A jobs, and `5` worker-B jobs. That exact shape previously sat
    hung until interrupted.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:106-151
  - validation_result: `MELDER_GAUNTLET_ITERS=1 MELDER_GAUNTLET_THREADS=3 MELDER_GAUNTLET_REQUEST_SCOPES=10 MELDER_GAUNTLET_WORKER_A_JOBS=5 MELDER_GAUNTLET_WORKER_B_JOBS=5 .\\.venv_new\\Scripts\\python.exe -m pytest -q -s benchmarks\\testing_other_di\\test_melder_gauntlet.py`
  IMPACT: The current hang was a real runtime deadlock in the identity/registry
    path, and the benchmark file is now unblocked for realistic threaded
    validation.
  NEXT: sync the benchmark-fix task state to reflect that the remade file now
    validates cleanly after the runtime deadlock fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the runtime deadlock fix that blocks the Melder gauntlet under
higher concurrent lesser-conduit churn. The current leading candidate is the
identity-lock / registry-lock inversion in dev-ops identity cleanup and
registry-side relation rebuild.

