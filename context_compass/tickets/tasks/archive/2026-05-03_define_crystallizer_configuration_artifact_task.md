# Task: Define Crystallizer Configuration Artifact

## Metadata
- Task ID: TASK-2026-05-03-define-crystallizer-configuration-artifact
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-03T17:13:48Z
- Updated: 2026-05-03T17:13:48Z

## Objective
Capture one dedicated artifact describing the crystallizer configuration
surface for synthetic-module copy mode, registration, file-location discovery,
and snapshot/rebuild implications.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a new artifact called
  `crystallizer configuration` and called out the exact content to capture.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/artifacts/`
  - `codex/context_compass/artifact_board.md`
  - this task ticket
  - the crystallizer epic
- DEPENDENCIES:
  - `artifacts/2026-04-26_crystallizer_philosophy.md`
  - `artifacts/2026-05-02_file_to_memory_bridge_mechanic.md`
  - current synthetic-module and loader discussions
- EXIT_GATE: the artifact exists, is linked in the board, and the
  crystallizer lane records it as active durable context.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested artifact would
  contradict the current explicit reload/loader boundary around physical to
  synthetic morphing.

## Scope Boundaries
- In scope:
  - synthetic-module copy mode as a configuration feature
  - root reference target and path target mapping
  - registration and location-discovery expectations
  - snapshot/byte-copy/rebuild implications
- Out of scope:
  - production implementation
  - performance changes
  - broad mutation semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested this artifact and asked that
  the prior drift be corrected.

## Steps / Checklist
- [ ] Write the `crystallizer configuration` artifact.
- [ ] Link it in `artifact_board.md`.
- [ ] Record the artifact in the crystallizer epic and this task notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one crystallizer configuration artifact

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-03_define_crystallizer_configuration_artifact_task.md
- codex/context_compass/artifacts/crystallizer_configuration.md
- codex/context_compass/artifact_board.md
- codex/context_compass/tickets/epics/2026-04-26_design_crystallizer_asset_provenance_epic.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/artifacts/crystallizer_configuration.md`

## Risks / Rollback Notes
- Risk: the artifact overstates dynamic physical->synthetic swapping despite
  the recent experiment showing reload boundaries matter.
  Rollback: keep the feature explicitly tied to bootstrap/rebuild boundaries.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/crystallizer_configuration.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-03T17:13:48Z
  TYPE: PLAN
  CLAIM: The next bounded move is to capture the synthetic-module copy mode as
    an explicit crystallizer configuration artifact rather than leaving the
    registration, path-target, file-location, and snapshot/rebuild rules only
    in transient chat.
  EVIDENCE:
  - user_instruction: "make sure you make an artifact called crystallizer configuration"
  - user_instruction: "make sure you map all this stuff in there likw how we register it and we need to locate its actual file location"
  IMPACT: The crystallizer lane needs one dedicated artifact for the
    configuration feature so later snapshot/loader work has a stable reference.
  NEXT: write the artifact and wire it into the board and epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the dedicated `crystallizer configuration` artifact for
synthetic-module copy mode and its registration/snapshot implications.
