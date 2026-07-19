# Task: fix aether mypyc nullable bootstrap cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-aether-mypyc-nullable-bootstrap-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T15:15:12Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `Aether` mypy/mypyc cluster by normalizing its bootstrap typing,
nullable fields, and missing signature annotations without changing runtime behavior.

## Ticket Contract
- ENTRY_GATE: the user-provided cluster is the `Aether` file group headed by
  `aether.py:67`, the nullable bootstrap redefinitions around lines 107-126, and
  the repeated `dict[str, AethericFrame] | None` indexing fallout that follows.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aether.py`
- DEPENDENCIES:
  - current `Aether` bootstrap and cleanup model
  - existing `IAether` surface already read this turn
- EXIT_GATE:
  - the targeted `Aether` cluster is gone
  - bootstrap/cleanup typing is coherent instead of mixing nullable placeholders
    with same-name redefinitions
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any apparent typing cleanup would
  force a semantic change to `Aether` boot or cleanup

## Scope Boundaries
- In scope:
  - `Aether` signature annotations
  - `Aether` bootstrap field typing and redefinition cleanup
  - `Aether` local nullable/union fallout tied to that bootstrap shape
- Out of scope:
  - broader imported-module mypy debt
  - other `Aether` collaborators unless the source fix absolutely requires them

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user supplied a bounded `Aether` mypy/mypyc cluster and
  source evidence points to one central nullable-bootstrap typing problem

## Steps / Checklist
- [ ] confirm the exact nullable-bootstrap pattern and dependent errors
- [ ] normalize `Aether` field initialization and signature annotations
- [ ] rerun targeted mypy for `aether.py`
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a bounded `Aether` bootstrap typing cleanup

## Files / Paths Impacted
- `src/melder/aether/aether.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\aether.py`

## Risks / Rollback Notes
- Medium risk. The fix touches bootstrap and cleanup typing, so I need to keep it
  semantically identical and avoid “clever” rewrites.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-18T15:15:12Z
  TYPE: FACT
  CLAIM: The `Aether` cluster has one clear center of gravity: bootstrap sets a
    bunch of instance fields to `None` for cleanup safety, then immediately
    redefines the same attributes with concrete types in the same `__init__`
    block. That creates the `no-redef` errors and also widens later reads into
    `Optional[...]` unions that drive most of the downstream indexing/attr errors.
  EVIDENCE:
  - src/melder/aether/aether.py:67-126
  - src/melder/aether/aether.py:230-799
  IMPACT: If I normalize the bootstrap shape cleanly, a large fraction of this
    reported cluster should collapse without any hacky per-line casts.
  NEXT: patch `Aether` to use one coherent bootstrap typing path and add the
    missing signature annotations before rerunning targeted mypy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T15:15:12Z
  TYPE: FACT
  CLAIM: After the bootstrap cleanup, only three `Aether`-local errors remain:
    two direct writes through `AethericFrame._configuration`, which is still
    inferred as `None`-typed on the frame class, and one `_get_cluster(...)`
    return type that still says `ConduitCluster` even though the live store is
    `IConduitCluster`.
  EVIDENCE:
  - src/melder/aether/aether.py:783-789
  - src/melder/aether/aether.py:1416-1427
  - src/melder/aether/aetheric_frame.py:96-105
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\aether.py 2>&1 | Select-String 'src\\melder\\aether\\aether.py:'`
  IMPACT: Finishing this lane cleanly requires one tiny direct collaborator annotation in
    `AethericFrame`; there is no honest one-file-only fix for those two assignment errors.
  NEXT: annotate `AethericFrame._configuration` and fix `_get_cluster(...)` to return
    `IConduitCluster`, then rerun targeted mypy on `aether.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T15:15:12Z
  TYPE: MEASURE
  CLAIM: The `Aether`-local mypy/mypyc cluster is gone.
  EVIDENCE:
  - src/melder/aether/aether.py:68-126
  - src/melder/aether/aether.py:232-246
  - src/melder/aether/aether.py:754-1946
  - src/melder/aether/aetheric_frame.py:96-105
  - src/melder/utilities/interfaces/iconduitcluster.py:1-79
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\aether.py 2>&1 | Select-String 'src\\melder\\aether\\aether.py:'` -> no output
  IMPACT: The user-requested `Aether` file cluster is fixed. Any remaining mypy output from a raw run is imported repo debt outside `aether.py` itself.
  NEXT: wait for the next exact cluster or continue only where the user directs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active `Aether` mypy/mypyc lane for the nullable-bootstrap cluster. The current
evidence points to one central source fix in `aether.py`, not scattered hacks.
