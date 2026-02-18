# Task: Define Sealed Key Vault And Blind Submission Contract

## Metadata
- Task ID: TASK-2026-02-18-hidden-key-vault-discovery-and-contract
- Story: STORY-2026-02-18-hidden-blind-hard-mcq-skillcheck
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T17:27:51Z
- Updated: 2026-02-18T17:48:29Z

## Objective
Define file contracts for hidden answer records and blind JSON submissions.

## Ticket Contract
- ENTRY_GATE: story routed and policy mismatch identified.
- EXECUTION_BOUNDARY: `skill_check/.sealed`, submission schema docs, and policy hooks.
- DEPENDENCIES: skill-check policy, manifest-required cycle flow.
- EXIT_GATE: sealed storage + submission schema documented and implemented.
- FAILURE_ESCALATION: raise `BLOCKER` if sealed and public artifacts cannot be separated.

## Scope Boundaries
- In scope:
  - sealed key paths
  - anti-cheat contract text
  - JSON submission schema
- Out of scope:
  - question-generation logic

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: sealed storage and submission contract implemented.

## Steps / Checklist
- [x] Define sealed answer-key storage paths.
- [x] Define blind JSON submission schema.
- [x] Add anti-cheat language for sealed pre-read violations.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `.sealed` storage contract and README.
- Submission schema documentation.

## Files / Paths Impacted
- `skill_check/.sealed/README.md`
- `skill_check/submissions/README.md`
- `skill_check/skill_check_policy.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "sealed|submission|ANTI-CHEAT" context_compass/skill_check/skill_check_policy.md`

## Risks / Rollback Notes
- Policy-only hiding cannot prevent intentional manual reads outside workflow.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T17:27:51Z
  TYPE: FACT
  CLAIM: Sealed answer records and JSON submission schema are now explicitly separated from public exam artifacts.
  EVIDENCE:
  - skill_check/.sealed/README.md:1-14
  - skill_check/submissions/README.md:1-22
  - skill_check/skill_check_policy.md:29-39
  IMPACT: Blind-answer workflow now has clear public/private file boundaries.
  NEXT: build generator and grader that enforce these boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:48:29Z
  TYPE: FACT
  CLAIM: User accepted continuing closure with sealed key storage retained, and requested completion of the active story lane.
  EVIDENCE:
  - tickets/stories/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_story_completed.md:1-145
  - attention_board.md:1-40
  IMPACT: Closure checklist is complete and board sync can proceed.
  NEXT: move ticket chain to completed and update routing anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Sealed storage and blind submission contracts are implemented and ready for script consumption.

## Closure Note
Closed after user confirmation to finish story closure with sealed-key policy retained.
