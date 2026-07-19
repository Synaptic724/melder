# Task: Investigate Aether Logger Activation Defaults

## Metadata
- Task ID: TASK-2026-05-05-investigate-aether-logger-activation-defaults
- Story:
- Epic:
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-05T23:40:30Z
- Updated: 2026-05-05T23:40:30Z

## Objective
Investigate how the current channel logger and SafeLogger activation path works
across `AetherUtilitySystem`, `Aether`, and the major runtime objects so we can
decide how an Aether-level configuration switch should disable default logger
activation for conduits and related tools.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an investigation-first pass on the
  current logger activation default before implementation discussion.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aether_utility_system.py`
  - `src/melder/utilities/helpers/init_helpers.py`
  - `src/melder/utilities/logger/safe_logger.py`
  - `src/melder/aether/aether.py`
  - targeted constructor/logging call sites in `Conduit`, `Spellbook`, `Nexus`,
    and `Rift`
- DEPENDENCIES:
  - current Aether host contract
  - current logger attach paths in runtime objects
- EXIT_GATE: the current logger activation path, default behavior, and
  decision-relevant control seams are restated from source evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation proves the
  logger control point is split across multiple incompatible seams rather than
  one bounded Aether-level switch.

## Scope Boundaries
- In scope:
  - source investigation only
  - concrete call-path mapping
  - configuration-seam identification
- Out of scope:
  - implementing the config switch yet
  - broad runtime refactors
  - unrelated logging cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a source-level
  investigation of the logger activation defaults before we talk about the
  config shape.

## Steps / Checklist
- [ ] Read `AetherUtilitySystem`, `InitHelpers`, and `SafeLogger`.
- [ ] Trace default logger activation from `Aether` and major runtime objects.
- [ ] Record evidence-backed findings about the current default-on behavior.
- [ ] Identify the most honest Aether-level configuration seam for disabling it.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- source-backed logger activation map
- explicit discussion-ready seam for a future config switch

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-05_investigate_aether_logger_activation_defaults_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - manual source reads and focused search over logger attach paths

## Risks / Rollback Notes
- Risk: logger activation is more distributed than expected and the Aether
  switch will need more than one downstream gate.
  Rollback: keep the investigation bounded and surface the actual split
  seams before any implementation.

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
- DATETIME: 2026-05-05T23:40:30Z
  TYPE: PLAN
  CLAIM: The logger-default question needs a source-backed map before any config
    design. We need to know exactly where `AetherUtilitySystem` and
    `InitHelpers` are causing real logger attachment, which objects default to
    provider-backed channel loggers, and whether the clean disable seam is
    truly centralized enough to live at Aether configuration.
  EVIDENCE:
  - user_instruction: "first investigate that system and then we need to talk about implementing a configuration step"
  IMPACT: The next move is investigation only, not implementation theater.
  NEXT: trace the attach path through `AetherUtilitySystem`, `InitHelpers`,
    `SafeLogger`, `Aether`, `Conduit`, `Spellbook`, `Nexus`, and `Rift`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the logger-default investigation before any Aether-side config
switch is implemented.
