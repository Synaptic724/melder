# Task: Remove Fidelity-Diff Gate Surfaces And Enforce Knowledge-Test-Only Gate

## Metadata
- Task ID: TASK-2026-02-18-remove-fidelity-diff-gate-surface
- Story: STORY-2026-02-18-knowledge-test-only-gate
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T18:14:27Z
- Updated: 2026-02-18T18:21:41Z

## Objective
Remove `fidelity_diff` as a gating requirement and keep `knowledge_test` as the
only certification/compaction completion gate.

## Ticket Contract
- ENTRY_GATE: story created and user requested immediate implementation.
- EXECUTION_BOUNDARY: compaction/certification policy docs and board schema.
- DEPENDENCIES: current hard-MCQ grading and certification contracts.
- EXIT_GATE: all gate surfaces are knowledge-test-only and references to required
  `DIFF_ONBOARDING_REPORT` are removed.
- FAILURE_ESCALATION: raise `CONFLICT` if a P0 policy contract requires parity
  metrics as a hard gate.

## Scope
- In scope:
  - `compacting_differential_board.md`
  - `AGENTS.MD`
  - `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
  - `agent_onboarding/default/general/skills/compaction_requirements.md`
  - `agent_onboarding/default/general/policies/policy_skills.md`
  - `agent_onboarding/default/general/skills/self_certification.md`
  - `agent_onboarding/default/general/skills/user_approved_certification.md`
  - `CONTEXT_COMPACTION.md`
- Out of scope:
  - phase12 tickets
  - runtime app code

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user accepted closure after implementation walkthrough.

## Steps
- [x] Rewrite differential board schema to knowledge-test-only required rows.
- [x] Remove `DIFF_ONBOARDING_REPORT` as mandatory certification evidence.
- [x] Update compaction onboarding and requirements docs to single-gate flow.
- [x] Update AGENTS/policy references to remove parity-gate language.
- [x] Validate by grep that gate-level docs no longer require `fidelity_diff`.

## Validation Plan
- `rg -n "fidelity_diff|DIFF_ONBOARDING_REPORT|system_skill_parity_rate|fidelity_parity_rate|fidelity_score" context_compass/compacting_differential_board.md context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md context_compass/agent_onboarding/default/general/skills/compaction_requirements.md context_compass/agent_onboarding/default/general/skills/self_certification.md context_compass/agent_onboarding/default/general/skills/user_approved_certification.md context_compass/agent_onboarding/default/general/policies/policy_skills.md context_compass/AGENTS.MD context_compass/CONTEXT_COMPACTION.md`

## Notes
- DATETIME: 2026-02-18T18:14:27Z
  TYPE: FACT
  CLAIM: Current gate surfaces still require parity/diff artifacts in multiple
    docs even though the user requested knowledge-test-only gating.
  EVIDENCE:
  - compacting_differential_board.md:7-104
  - AGENTS.MD:62-75
  - agent_onboarding/default/general/skills/self_certification.md:32-57
  IMPACT: Certification and re-entry guidance are currently multi-gate and must
    be simplified.
  NEXT: patch the listed docs and rerun validation search.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T18:17:15Z
  TYPE: FACT
  CLAIM: Gate surfaces were simplified to knowledge-test-only, removing
    fidelity-diff as required evidence.
  EVIDENCE:
  - compacting_differential_board.md:1-86
  - agent_onboarding/default/general/skills/compaction_diff_onboarding.md:1-101
  - agent_onboarding/default/general/skills/self_certification.md:1-64
  - agent_onboarding/default/general/skills/user_approved_certification.md:1-62
  - AGENTS.MD:58-111
  IMPACT: Certification and re-entry now depend on a single scored gate.
  NEXT: share change summary and get user acceptance for closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T18:21:41Z
  TYPE: FACT
  CLAIM: User requested final closure for this lane after the delivered implementation.
  EVIDENCE:
  - tickets/stories/completed/2026-02-18_knowledge_test_only_gate_story_completed.md:1-147
  - attention_board.md:21-39
  IMPACT: Task is eligible for done transition and completed-lane archival.
  NEXT: move task file to completed and sync board anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Noting Behavior
- Note focus: tactical findings, immediate impacts, and one-step continuation.

## Context / Handoff Summary
Task implementation is complete, accepted, and ready for completed-lane archival.

## Closure Note
Closed after user confirmation to finalize the knowledge-test-only gate update.
