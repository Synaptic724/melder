# Task: Implement codegen_monitor.py

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-monitor-py
- Story: STORY-2026-04-25-codegen-system-observability-directory
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T11:19:06Z

## Objective
Implement the explicit codegen monitor seam for overwatch/sentinel integration.

## Ticket Contract
- ENTRY_GATE: the observability directory story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_observability_directory_story.md`
  - transaction context task
- EXIT_GATE: monitoring integration exists in one explicit file rather than a
  vague hook-dispatch bucket.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if monitor responsibilities need
  a second file before implementation.

## Scope Boundaries
- In scope:
  - monitor integration seam only
- Out of scope:
  - logging
  - durable history

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: monitor integration is a distinct observability concern.

## Steps / Checklist
- [ ] Implement monitor seam.
- [ ] Keep overwatch/sentinel integration explicit.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- monitor integration file

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: monitor becomes a generic hook bucket.
  Rollback: keep it explicit and transaction-lifecycle-focused.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: Monitoring should be explicit and should not drift back into a generic
    hook dispatcher.
  EVIDENCE:
  - user_instruction: agreement on monitor/history/logger separation
  - tickets/stories/2026-04-25_codegen_system_observability_directory_story.md:1-102
  IMPACT: This file keeps overwatch/sentinel integration visible and bounded.
  NEXT: implement it as the thin room-event bridge without waiting on any
    private logger/history files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-25T11:19:06Z
  TYPE: FACT
  CLAIM: `codegen_monitor.py` is now implemented as the thin codegen lifecycle
    bridge over room events. It owns one `CodegenEventPublisher` and does not
    own retained history or workflow state.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py:1-129
  - src/melder/aether/nexus/rift/codegen_system/observability/codegen_event_publisher.py:1-178
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-378
  IMPACT: Monitoring is now explicit without drifting back into a generic hook
    bucket or private cache owner.
  NEXT: close this task when the user accepts the observability slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the codegen monitor file.
