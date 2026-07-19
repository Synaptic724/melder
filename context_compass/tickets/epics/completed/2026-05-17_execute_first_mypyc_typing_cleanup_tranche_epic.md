# Epic: execute first mypyc typing cleanup tranche

- Completed: 2026-05-21T09:48:52Z
- Summary: Closed by explicit user request as a historical planning epic. It remains a record of the tranche framing and typing-policy decisions rather than a claim that every originally listed child task was completed under this epic.

## Metadata
- Epic ID: EPIC-2026-05-17-execute-first-mypyc-typing-cleanup-tranche
- Status: done
- Owner: mypy_1
- Agent Name: mypy_1
- Priority: p1
- Created: 2026-05-17T16:03:44Z
- Updated: 2026-05-21T09:48:52Z
- Target Window: 2026-Q2
- Related Program/Initiative: mypyc typing cleanup

## Problem / Opportunity
The `Experiments` analysis already decomposes the mypy/mypyc backlog into a
recommended order. The first ten items are the highest-leverage tranche because
they rebuild the type surface and stabilize the cleanup-nulling model before we
attempt deeper interface/runtime fixes. That tranche needs durable ticket state
so work can proceed without re-triaging the same first-order problems.

## MRP Alignment (Most Reasonable Product)
The right foundation is not "make mypy quieter." The right foundation is to
make the type surface reflect the real runtime contracts: imports resolve,
function signatures are explicit, cleanup-nulling is represented honestly, and
nullable post-cleanup access is narrowed deliberately instead of hidden behind
casts, `Any`, or fake structural shims where an honest `TYPE_CHECKING` import
would do.

## Ticket Contract
- ENTRY_GATE: this epic is routed on `attention_board.md` and all ten tranche
  tasks exist as ready work items assigned to `mypy_1`
- EXECUTION_BOUNDARY: only the first ten fix-order items from
  `Experiments/00_TOC.md` are in scope for this epic
- DEPENDENCIES: `Experiments/00_TOC.md`, `Experiments/07_fix_order.md`, and the
  active profile rule that prefers `TYPE_CHECKING` for typing-only imports
- EXIT_GATE: all ten tasks are accepted or explicitly superseded, experiment
  backlog lines are kept in sync with completed work, and board/closure sync is
  complete
- FAILURE_ESCALATION: raise `DECISION_REQUEST` when a fix path would require
  `Any`, semantic API drift, or fake structural shims beyond honest
  `TYPE_CHECKING` use

## Goals (Outcomes)
- Rebuild the first tranche of the mypy/mypyc backlog into executable tasks.
- Keep the tranche aligned to the repo's `TYPE_CHECKING`-first typing
  constraint.
- Give `mypy_1` a clean ordered queue that matches the existing experiments
  analysis.

## Non-Goals (Explicit Exclusions)
- Later fix-order items after the first ten.
- Broad production adoption of generated protocols outside the relevant tasks.
- Experiment backlog closure for items not directly solved by this tranche.

## Scope Boundaries
- In scope:
  - first ten items from the recommended fix order
  - task ordering and dependency framing for those ten items
  - explicit `TYPE_CHECKING`-first correction for the undefined-name tranche
- Out of scope:
  - items 11+ from the fix-order plan
  - unrelated runtime refactors outside the tranche

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested one epic and ten tasks for the first
  ten fix-order items and assigned the lane to `mypy_1`

## Success Metrics
- Ten ready tasks exist and match the first ten fix-order items.
- Task 2 is rewritten to be repo-compatible with `TYPE_CHECKING` as the
  default typing-only import path.
- The epic can serve as the single routing anchor for `mypy_1`.

## Requirements (Functional + Non-Functional)
- Preserve the existing fix-order ordering for items 1-10.
- Use repo-compatible wording for tranche 2: `TYPE_CHECKING` first, Protocols
  only when the structural contract is real.
- Keep task scopes narrow enough for sequential execution and experiment-line
  cleanup.

## Constraints / Assumptions
- The active profile prefers `typing.TYPE_CHECKING` for typing-only imports and
  still forbids PEP 604 unions in new code.
- Completed error lines should be removed from the live `Experiments` markdown
  backlog in the same pass as the code fix.
- This epic is planning/routing only; no direct source edits are required here.

## Dependencies / External References
- `Experiments/00_TOC.md`
- `Experiments/07_fix_order.md`
- `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/typing.md`
- `codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md`

## Milestones (Track Progress)
- [ ] Milestone 1: type-surface tranche defined
      - all tasks for items 1-6 exist and are ready
- [ ] Milestone 2: cleanup-nulling tranche defined
      - all tasks for items 7-10 exist and are ready

## Stories (Required to Complete)
- [ ] Story: none

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-05-17-resolve-missing-implementation-or-stub-import
- [ ] Task: TASK-2026-05-17-resolve-undefined-type-names-and-forward-interface-references
- [ ] Task: TASK-2026-05-17-add-missing-function-and-method-annotations
- [ ] Task: TASK-2026-05-17-add-missing-variable-and-slots-annotations
- [ ] Task: TASK-2026-05-17-fix-exit-return-signature
- [ ] Task: TASK-2026-05-17-make-implicit-optional-parameter-defaults-explicit
- [ ] Task: TASK-2026-05-17-annotate-cleanup-nulled-fields-as-nullable
- [ ] Task: TASK-2026-05-17-narrow-nullable-lock-context-access
- [ ] Task: TASK-2026-05-17-narrow-nullable-deque-queue-list-cleanup-access
- [ ] Task: TASK-2026-05-17-narrow-nullable-event-and-signal-cleanup-access
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The first ten fix-order items exist as concrete tasks.
- The queue is assigned to `mypy_1`.
- The `TYPE_CHECKING`-first correction is explicit in the relevant task.

## Risks / Mitigations
- Risk: task 2 drifts back toward fake protocol/interface indirection when a
  `TYPE_CHECKING` import would be enough.
  Mitigation: make the `TYPE_CHECKING`-first correction explicit in the task
  and epic.
- Risk: tasks become too broad and recreate the original classification problem.
  Mitigation: keep one backlog group per task.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required tasks are incomplete or unaccepted.
- [ ] No tranche claims without source evidence from experiment docs and ticket notes.

## Validation / Test Approach
- Planning validation only.
- Confirm each task lines up with the first ten fix-order items and the repo's
  type-policy constraints.

## Rollout / Adoption Plan
- Route active work through this epic.
- `mypy_1` starts at task 1 and advances in order unless a task creates a
  dependency-based reorder note.

## Open Questions
- None at epic-creation time; task-specific uncertainty should be raised inside
  the individual tasks.

## Decision Log
- 2026-05-17: Item 2 is intentionally rewritten to prefer `TYPE_CHECKING` for
  typing-only imports, in line with the active profile rules.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-05-17T16:03:44Z
  TYPE: FACT
  CLAIM: The first ten recommended fix-order items are the right execution
    tranche to turn into concrete tasks because they rebuild the type surface
    first and then normalize the large cleanup-nulling lane.
  EVIDENCE:
  - Experiments/00_TOC.md:87-97
  - Experiments/07_fix_order.md:55-74
  IMPACT: The epic can map directly onto the existing analysis instead of
    inventing a new ordering.
  NEXT: create ten ready tasks aligned to those ten items and assign them to
    `mypy_1`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-17T16:03:44Z
  TYPE: DECISION
  CLAIM: The undefined-name/import tranche is corrected locally to prefer
    `TYPE_CHECKING` for typing-only imports; the repo-compatible fix space is
    normal imports, quoted annotations, local runtime imports, and
    interface/protocol extraction only when the structural contract is real.
  EVIDENCE:
  - Experiments/07_fix_order.md:59-60
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/typing.md:16-21
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:68-70
  IMPACT: Task 2 must not copy the generic experiment advice literally.
  NEXT: encode that correction directly in the task objective and constraints.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T09:48:52Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this epic for turn-in as a historical planning anchor even though the original ten-task tranche was not fully closed within this epic.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: The epic can move to `completed/` as accepted historical planning state without misrepresenting later tranche execution as complete.
  NEXT: move the epic to `tickets/epics/completed/` and add a compact closure anchor to the board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-task tradeoffs, and tranche order.
- Add notes when ordering, assignment, or scope boundaries change.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
This epic is the ordered first-ten-item execution lane for the mypy/mypyc
cleanup effort. It exists only to route `mypy_1` through the first tranche of
the already-classified experiments backlog without redoing the classification
work.
