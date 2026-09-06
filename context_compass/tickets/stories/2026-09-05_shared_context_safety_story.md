# Story: Preserve shared context publication and active-reader lifetime

## Metadata
- Story ID: STORY-2026-09-05-shared-context-safety
- Epic: EPIC-2026-09-05-shared-context-rebuild-publication
- Status: in_progress
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-05T21:17:10Z
- Updated: 2026-09-05T21:17:10Z

## User Narrative
As a Melder user, I want concurrent shared-spell melds to see usable runtime contexts throughout
revalidation, without losing the lock-free ready path or hiding failures behind CI workarounds.

## Value / MRP Alignment
Publication and retirement are one correctness boundary. A context cannot be declared available
before its inputs exist, and a context already acquired by a permitted caller cannot be destroyed.

## Ticket Contract
- ENTRY_GATE: Certified codex_1, owner-approved repair direction, routed child task and source proof.
- EXECUTION_BOUNDARY: Epic S1-S3 are one atomic runtime delivery; S4 qualifies that delivery.
- DEPENDENCIES: Prior reproduction task and the parent epic's complete acceptance matrix.
- EXIT_GATE: Both child tasks meet their exit gates; owner accepts; workflows_1 receives qualification.
- FAILURE_ESCALATION: Raise required public-semantic changes or unavoidable hot-path cost for review.

## Requirements
- Preserve CounterSwitch and its one-builder protocol.
- Existing dynamic admission must cover context acquisition and execution with one balanced ticket.
- Coordinate overlapping affected scopes before input retirement; do not serialize unrelated melds.
- Rebuild errors release waiters without advertising ready or suppressing the original failure.
- Initial, deferred, cached, existing-instance and revalidation paths retain supported semantics.
- No runtime repair is substituted by a test skip, timeout relaxation, workflow edit or blanket lock.

## Scope Boundaries
- In scope: source-led protocol, controlled tests, publication/admission implementation and qualification.
- Out of scope: workflow policy, signing, commits, pushes, uploads, unrelated cleanup and refactors.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the proposed repair direction and test execution.

## Tasks
- [ ] `tickets/tasks/2026-09-05_shared_context_protocol_repair_task.md`: proof plus atomic S1-S3 repair.
- [ ] `tickets/tasks/2026-09-05_shared_context_qualification_task.md`: S4 tests, performance, docs/assets.

## Acceptance Criteria
- Parent epic regression matrix is accounted for with exact execution evidence and honest limits.
- No publication from unavailable inputs or retirement underneath admitted readers.
- No stranded pending latch, self-drain, or stale overlapping publication.
- Measured warm/cold behavior and current generated assets accompany the runtime handoff.

## Validation / Test Plan
Controlled component regressions, existing unit/integration cases, repeated cluster qualification,
supported local suite and hot/cold measurements. Hosted Linux/macOS/Windows confirmation stays explicit.

## Risks / Open Questions
Overlapping dependency ownership, nested admission, failure wakeup, and cache hydration must be
settled in the protocol task before the corresponding implementation tranche.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: linked through the child tasks; parent epic retains original reproduction proof.
- DISPOSITION: promote_to_documentation for patch contracts; retain core qualification proof.
- CLEANUP_TRIGGER: Owner-accepted parent closure, not child-task completion alone.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Cross-task decisions and delivery gates belong here; tactical proof remains in the child task.

## Notes
- DATETIME: 2026-09-05T21:17:10Z
  TYPE: DECISION
  CLAIM: Merge epic S1-S3 into one protocol/repair task because publication and reader lifetime
    must be delivered together; keep S4 qualification separately reviewable.
  EVIDENCE:
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:234-252
  IMPACT: No partial runtime fix is presented as completed while reader or dependency safety remains.
  NEXT: Implement controlled proof and finalize the atomic runtime contract in the child task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Owner accepts both child outcomes and the parent acceptance matrix.
- [ ] Boards and artifacts synchronized on closure.

## Context / Handoff Summary
Two child tasks deliver the four epic scopes. Runtime changes require complete patch contracts;
qualification reports exact revisions/platforms and leaves hosted work to workflows_1 and the owner.
