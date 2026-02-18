# Story: Remove Fidelity Diff Gate And Keep Knowledge-Test-Only Certification

## Metadata
- Story ID: STORY-2026-02-18-knowledge-test-only-gate
- Epic: EPIC-2026-02-18-skill-gate-first-compaction-measurement-loop
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T18:14:27Z
- Updated: 2026-02-18T18:21:41Z

## User Narrative
As a maintainer, I want fidelity-diff gating removed so certification is driven
only by graded knowledge-test outcomes.

## Value / MRP Alignment
This simplifies the compaction loop into one measurable gate and removes mixed
signal semantics between parity diagnostics and scored test evidence.

## Ticket Contract
- ENTRY_GATE: user explicitly requested removing `fidelity_diff` as a gate.
- EXECUTION_BOUNDARY: compaction gate docs/policies/board schema only.
- DEPENDENCIES: active skill-check grading pipeline and certification docs.
- EXIT_GATE: gate language and board schema are knowledge-test-only.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing parity gates conflicts
  with required certification policy constraints.

## Requirements (Functional)
- Remove `fidelity_diff` as a required row type and certification gate.
- Keep `knowledge_test` as the only scoring/certification gate.
- Remove mandatory `DIFF_ONBOARDING_REPORT` requirements from gate surfaces.

## Requirements (Non-Functional)
- Preserve anti-cheat ordering.
- Keep cycle status semantics deterministic (`Not run` => `incomplete`).

## Scope Boundaries
- In scope:
  - `compacting_differential_board.md`
  - post-compaction gate policy docs and certification docs
- Out of scope:
  - phase12 performance lanes
  - unrelated runtime code

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user confirmed closure after walkthrough of the gate simplification changes.

## Dependencies / Related Work
- `tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md`
- `skill_check/skill_check_policy.md`
- `compacting_differential_board.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-18-remove-fidelity-diff-gate-surface - remove
      fidelity-diff gate semantics from board/policy/certification docs.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `fidelity_diff` is no longer required for cycle completion or certification.
- `knowledge_test` is the single required gate for cycle completion.
- Certification docs no longer require `DIFF_ONBOARDING_REPORT`.

## Validation / Test Plan
- `rg -n "fidelity_diff|DIFF_ONBOARDING_REPORT|parity" context_compass/compacting_differential_board.md context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md context_compass/agent_onboarding/default/general/skills/compaction_requirements.md context_compass/agent_onboarding/default/general/skills/self_certification.md context_compass/agent_onboarding/default/general/skills/user_approved_certification.md context_compass/agent_onboarding/default/general/policies/policy_skills.md context_compass/AGENTS.MD`

## UX / API / Data Notes
- `compacting_differential_board.md` remains the ledger path but switches to
  knowledge-test-only schema.

## Risks / Mitigations
- Risk: removing parity gates could reduce qualitative drift visibility.
  Mitigation: keep parity diagnostics optional and non-gating where needed.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should optional parity diagnostics live in a separate non-gating board?

## Decision Log
- Knowledge-test-only gate model accepted as the active certification path.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-02-18T18:14:27Z
  TYPE: FACT
  CLAIM: User requested stripping out fidelity-diff and keeping knowledge-test as
    the only gate.
  EVIDENCE:
  - compacting_differential_board.md:1-130
  - skill_check/skill_check_policy.md:1-132
  IMPACT: Gate surfaces must be simplified to one measurable certification path.
  NEXT: create linked task and patch board/policy docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T18:17:15Z
  TYPE: FACT
  CLAIM: Required gate surfaces now enforce knowledge-test-only certification and
    no longer require fidelity-diff evidence.
  EVIDENCE:
  - compacting_differential_board.md:1-86
  - agent_onboarding/default/general/skills/compaction_requirements.md:1-116
  - agent_onboarding/default/general/policies/policy_skills.md:25-30
  IMPACT: Story implementation is complete and ready for user acceptance.
  NEXT: present results and request closure confirmation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T18:21:41Z
  TYPE: FACT
  CLAIM: User confirmed closure for this lane after receiving the implementation summary.
  EVIDENCE:
  - tickets/tasks/completed/2026-02-18_remove_fidelity_diff_gate_surface_task_completed.md:1-102
  - attention_board.md:21-39
  IMPACT: Story can transition to done and be archived to completed routing.
  NEXT: move story/task to completed and sync attention board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story implementation is complete, accepted, and ready for completed-lane archiving.

## Closure Note
Closed after user confirmation to finish this gate-simplification lane.
