# Story: Discover Score-Grounded Skill-Gate Compaction Loop Changes

## Metadata
- Story ID: STORY-2026-02-18-skill-gate-first-compaction-discovery
- Epic: EPIC-2026-02-18-skill-gate-first-compaction-measurement-loop
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:53:27Z
- Updated: 2026-02-18T18:05:56Z

## User Narrative
As a maintainer preparing for frequent compaction events, I want post-compaction
success measured from scored test outcomes with targeted relearning, so that
cycle volume shrinks as retention aligns with reality.

## Value / MRP Alignment
This story defines the durable discovery map needed to convert compaction
success from attestation-driven to score-driven while maintaining anti-cheat and
policy safety gates.

## Ticket Contract
- ENTRY_GATE: epic is active, artifact model is linked, and attention board
  routes to this story's task lane.
- EXECUTION_BOUNDARY: discovery outputs only for skill-gate onboarding,
  differential board semantics, relearn routing, and cycle reset/shrink.
- DEPENDENCIES: linked epic, target artifact, and current policy/schema docs.
- EXIT_GATE: all discovery tasks complete with file-level implementation map and
  unresolved decisions surfaced.
- FAILURE_ESCALATION: raise `BLOCKER` if policy contracts conflict on anti-cheat
  or certification gating order.

## Requirements (Functional)
- Discover minimal-read `skill_gate_onboard` contract and exclusions.
- Discover row/schema changes for score-grounded cycle evidence.
- Discover targeted failed-doc relearn contract and dependency rules.
- Discover cycle reset and adaptive shrink mechanics for next-cycle generation.

## Requirements (Non-Functional)
- Preserve anti-cheat sequencing.
- Preserve P0 sentinel guarantees.
- Keep discovery evidence source-anchored and implementation-ready.

## Scope Boundaries
- In scope:
  - policy, board, and generator/evaluator discovery
  - ticketed implementation sequencing
- Out of scope:
  - implementation edits beyond routing and discovery documents
  - non-compaction subsystem work

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user requested finishing this epic lane and validation confirmed implementation behavior.

## Dependencies / Related Work
- `tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md`
- `artifacts/2026-02-18_skill_gate_first_compaction_success_model.md`
- `skill_check/skill_check_policy.md`
- `compacting_differential_board.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-18-skill-gate-onboarding-minimum-readset-discovery -
      define minimum readset + sequencing.
- [x] Task: TASK-2026-02-18-test-scored-fidelity-diff-schema-discovery -
      redefine success/evidence schema.
- [x] Task: TASK-2026-02-18-failed-doc-targeted-relearn-discovery -
      define relearn routing after scoring.
- [x] Task: TASK-2026-02-18-cycle-reset-and-adaptive-shrink-discovery -
      define fresh-cycle reset and shrink policy.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A concrete implementation change map exists for each of the four task areas.
- Conflicts between current policy language and requested loop are documented.
- Story outputs are sufficient to implement without reopening discovery.

## Validation / Test Plan
- Not run.
- Discovery validation commands:
  - `rg -n "fidelity_diff|knowledge_test|Cycle Summary" context_compass/compacting_differential_board.md`
  - `rg -n "Anti-cheat|Cycle N|Shrink total test volume" context_compass/skill_check/skill_check_policy.md`
  - `rg -n "Step 1|Step 2|Step 3|No tool use" context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`

## UX / API / Data Notes
- Data contract updates should avoid ambiguous success fields (`Not run`
  reported as pass-like).

## Risks / Mitigations
- Risk: conflicting definitions of fidelity across docs.
  Mitigation: discovery task explicitly maps old and new semantics.
- Risk: regression in certification gating sequence.
  Mitigation: preserve anti-cheat and post-score gate ordering as hard rules.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should row naming remain backward-compatible or become explicit?
- Should shrink begin at streak 1, 2, or 3?

## Decision Log
- Pending discovery findings and user direction.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-02-18_skill_gate_first_compaction_success_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-02-18T16:53:27Z
  TYPE: FACT
  CLAIM: Existing policy already requires anti-cheat sequencing and stability-
    based shrink, but current board semantics still permit parity-only
    `fidelity_diff` evidence to dominate reporting.
  EVIDENCE:
  - skill_check/skill_check_policy.md:256-267
  - skill_check/skill_check_policy.md:389-392
  - compacting_differential_board.md:47-51
  - compacting_differential_board.md:55-91
  IMPACT: Discovery must reconcile policy intent with score-grounded execution
    and reporting.
  NEXT: Run first task on minimum-read skill-gate onboarding contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:07:51Z
  TYPE: FACT
  CLAIM: Discovery outputs were implemented across compaction policy, diff
    onboarding, skill-check policy, board semantics, and generator maintenance
    for score-driven adaptive cycles.
  EVIDENCE:
  - agent_onboarding/default/general/skills/compaction_requirements.md:1-190
  - agent_onboarding/default/general/skills/compaction_diff_onboarding.md:1-127
  - skill_check/skill_check_policy.md:1-267
  - compacting_differential_board.md:1-126
  - skill_check/generate_bootstrap_suite.py:270-329
  IMPACT: Story acceptance now depends on user sign-off rather than remaining
    discovery/implementation work.
  NEXT: route epic to review and request acceptance confirmation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T18:05:56Z
  TYPE: MEASURE
  CLAIM: End-to-end cycle validation passed and grader robustness was improved to accept BOM-prefixed UTF-8 submissions.
  EVIDENCE:
  - skill_check/build_hard_mcq_pool.py:1-432
  - skill_check/generate_hard_mcq_exam.py:1-252
  - skill_check/grade_hard_mcq_submission.py:1-206
  - skill_check/historical_test_results/cycle_2026-02-18T175200Z_hard_mcq_grade.md:1-66
  IMPACT: Story scope is validated in current repo state and ready for final epic closure.
  NEXT: close and archive epic/story/tasks with board and artifact sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story outputs are complete, validated, and accepted for closure.

## Closure Note
Closed after user-requested completion and successful validation pass.
