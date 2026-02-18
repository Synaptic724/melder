# Epic: Hidden Blind Hard-MCQ Skill-Check System

## Metadata
- Epic ID: EPIC-2026-02-18-hidden-blind-hard-mcq-skillcheck
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T17:27:51Z
- Updated: 2026-02-18T17:48:29Z
- Target Window: 2026-Q1
- Related Program/Initiative: Compaction Fidelity Convergence

## Problem / Opportunity
Current skill-check behavior exposes predictable MCQ keys and legacy answer-file
patterns that let blind evaluation drift into low-fidelity scoring.

## MRP Alignment (Most Reasonable Product)
Build a durable hard-MCQ testing core with sealed answer keys, JSON submission,
scripted grading, and policy-level anti-cheat gates.

## Ticket Contract
- ENTRY_GATE: user requested full redesign of generator/grader and skill policy surfaces.
- EXECUTION_BOUNDARY: `skill_check/`, compaction onboarding skill docs, ticketing boards, and artifact docs.
- DEPENDENCIES: manifest metadata, attention board routing, and existing compaction policy gates.
- EXIT_GATE: discovery + implementation complete with active policy/skill integration and user acceptance.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` on unresolved conflicts between blind-mode anti-cheat and current certification gates.

## Goals (Outcomes)
- Deliver hard MCQ-only pool/exam/grader flow.
- Enforce hidden answer-key storage and scripted grading.
- Enforce one-question-per-100-LOC exam allocation.
- Expand pool depth to at least 10x current volume.
- Add new skills and update existing policy/compaction skills.

## Non-Goals (Explicit Exclusions)
- Runtime business logic changes under `src/`.
- UI redesign unrelated to skill-check flow.

## Scope Boundaries
- In scope:
  - hard MCQ pool builder
  - randomized exam markdown generator
  - JSON submission grader and rank output
  - policy + skill doc rewrites and additions
- Out of scope:
  - non-skill-check subsystem redesign
  - benchmark/codegen workstreams

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user confirmed continuing closure with current sealed-key model and requested finishing stories.

## Success Metrics
- Exam files contain MCQ-only questions.
- Pool size is >= 10x previous known question volume.
- Per-cycle exam generation uses `ceil(LOC/100)` per required doc.
- Grading uses sealed answer keys and JSON submissions only.
- Skill/policy docs reflect new behavior without mixed-format ambiguity.

## Requirements (Functional + Non-Functional)
- Functional:
  - build pool generator with difficult 3-lie/1-truth options
  - generate randomized exams and submission templates
  - grade submissions with deterministic score/rank output
  - persist reports for historical tracking
  - integrate onboarding/compaction skills and policy docs
- Non-Functional:
  - anti-cheat compliant flow
  - deterministic file contracts
  - no manual answer-key grading path

## Constraints / Assumptions
- Workspace-local sealed storage is policy-hidden, not OS-enforced secret storage.
- Existing legacy test artifacts may remain for compatibility while new flow is active.

## Dependencies / External References
- `context_compass/artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md`
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`

## Milestones (Track Progress)
- [x] Milestone 1: Discovery lane + artifact specification completed.
- [x] Milestone 2: Pool/exam/grader code implemented.
- [x] Milestone 3: Skill/policy integration applied.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-18-hidden-blind-hard-mcq-skillcheck - discovery and implementation for blind hard-MCQ pipeline + skills integration.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-02-18-hidden-key-vault-discovery-and-contract
- [x] Task: TASK-2026-02-18-hard-mcq-pool-generator-implementation
- [x] Task: TASK-2026-02-18-randomized-hard-mcq-exam-generator-implementation
- [x] Task: TASK-2026-02-18-json-grader-ranking-report-implementation
- [x] Task: TASK-2026-02-18-skill-and-policy-surface-integration
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Hard MCQ-only scripts exist and run end-to-end.
- Sealed key directory is used by generator/grader and excluded from git data files.
- Policy/compaction docs enforce blind JSON submission and scripted grading.
- New skill docs are created and added to role skill chain.

## Risks / Mitigations
- Risk: agent can still read sealed files in workspace.
  Mitigation: enforce policy contract and anti-cheat violation semantics.
- Risk: generated lies become obvious.
  Mitigation: deterministic near-truth mutation rules with strict wording proximity.

## Applicable Anti-Patterns
- [x] No epic-state transition without story-level evidence.
- [x] No closure while required stories are incomplete or unaccepted.
- [x] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Script validation:
  - `python -m py_compile` on new scripts
  - pool build command
  - exam generation command
  - grader command against JSON submission

## Rollout / Adoption Plan
1. Generate pool and exam for active cycle.
2. Submit blind JSON answers.
3. Grade and record results.
4. Use remediation output for next compaction cycle.

## Open Questions
- Should sealed key storage move outside workspace in a follow-up hardening lane?

## Decision Log
- Implemented hard-MCQ flow now; keep legacy assets as compatibility-only.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: epic closure

## Notes
- DATETIME: 2026-02-18T17:27:51Z
  TYPE: FACT
  CLAIM: User requested full redesign to blind JSON submission with hidden answer storage,
    difficult MCQ-only format, randomization, and 10x pool scaling.
  EVIDENCE:
  - skill_check/generate_bootstrap_suite.py:681-695
  - skill_check/tests/cycle_2026-02-18T162034Z/AGENTS_MD_1EECA99492.test.md:1-80
  IMPACT: Existing deterministic MCQ pattern must be replaced with hard blind pipeline.
  NEXT: implement scripts + policy/skill integration and validate end-to-end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:37:15Z
  TYPE: MEASURE
  CLAIM: Hard-MCQ pipeline executed end-to-end: pool build at 10x target,
    randomized exam generation, and JSON grading report output.
  EVIDENCE:
  - skill_check/build_hard_mcq_pool.py:1-376
  - skill_check/generate_hard_mcq_exam.py:1-259
  - skill_check/grade_hard_mcq_submission.py:1-215
  - skill_check/historical_test_results/cycle_2026-02-18T173500Z_hard_mcq_grade.md:1-66
  IMPACT: Epic is implementation-complete and pending user acceptance to close.
  NEXT: walkthrough results with user and confirm acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:48:29Z
  TYPE: FACT
  CLAIM: User accepted closing the active story/epic lane with sealed keys retained as long as testing workflow remains properly managed.
  EVIDENCE:
  - tickets/stories/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_story_completed.md:1-145
  - attention_board.md:1-43
  IMPACT: Epic closure conditions are satisfied and ticket chain can be archived.
  NEXT: move epic/story/tasks to completed and sync attention board anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic scope is implemented, validated, and accepted for closure.

## Closure Note
Closed after user confirmation to continue and finish the hard-MCQ story/epic lane.
