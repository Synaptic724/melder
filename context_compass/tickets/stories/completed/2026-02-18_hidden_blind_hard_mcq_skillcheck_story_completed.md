# Story: Discover And Implement Hidden Blind Hard-MCQ Skill-Check Flow

## Metadata
- Story ID: STORY-2026-02-18-hidden-blind-hard-mcq-skillcheck
- Epic: EPIC-2026-02-18-hidden-blind-hard-mcq-skillcheck
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T17:27:51Z
- Updated: 2026-02-18T17:48:29Z

## User Narrative
As a maintainer approaching compaction cycles, I want blind hard-MCQ testing with
sealed grading so reported fidelity reflects real measured answers.

## Value / MRP Alignment
This story upgrades the measurement loop from predictable template outcomes to
scripted blind scoring with stronger anti-cheat and harder question quality.

## Ticket Contract
- ENTRY_GATE: epic is active and attention board routes to this lane.
- EXECUTION_BOUNDARY: hard-MCQ pool/exam/grader code plus skill/policy docs and ticket artifacts.
- DEPENDENCIES: onboarding manifest, skill-check policy, compaction onboarding docs.
- EXIT_GATE: all implementation tasks complete with validation evidence and routing sync.
- FAILURE_ESCALATION: raise `BLOCKER` if sealed-key storage cannot be used by grader.

## Requirements (Functional)
- Build hard-MCQ pool script with 10x target scaling.
- Build randomized exam markdown generator with 1 question per 100 LOC.
- Build JSON submission grader with rank output.
- Update skills and policy docs to enforce new workflow.

## Requirements (Non-Functional)
- Preserve blind flow until submission.
- Ensure deterministic grading outputs.
- Keep MCQ distractors difficult and close to truth.

## Scope Boundaries
- In scope:
  - `skill_check/` script and policy surfaces
  - onboarding compaction skill docs
  - ticket/board routing and artifact links
- Out of scope:
  - non-skill-check application runtime changes

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user confirmed continuation and requested finishing story closure.

## Dependencies / Related Work
- `tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md`
- `artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-18-hidden-key-vault-discovery-and-contract - define sealed key storage and anti-cheat contract.
- [x] Task: TASK-2026-02-18-hard-mcq-pool-generator-implementation - build 10x hard-MCQ pool generator.
- [x] Task: TASK-2026-02-18-randomized-hard-mcq-exam-generator-implementation - build random exam markdown generator.
- [x] Task: TASK-2026-02-18-json-grader-ranking-report-implementation - build JSON grader and ranking output.
- [x] Task: TASK-2026-02-18-skill-and-policy-surface-integration - update/add skills and existing policy docs.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- New scripts run end-to-end for pool, exam, and grading.
- Sealed key directory is used and git-ignored for key files.
- MCQ-only policy and compaction skill docs are updated.
- New skills are added to general skill chain.

## Validation / Test Plan
- `python -m py_compile context_compass/skill_check/build_hard_mcq_pool.py context_compass/skill_check/generate_hard_mcq_exam.py context_compass/skill_check/grade_hard_mcq_submission.py`
- `python context_compass/skill_check/build_hard_mcq_pool.py --multiplier 10`
- `python context_compass/skill_check/generate_hard_mcq_exam.py --cycle-id <id>`
- `python context_compass/skill_check/grade_hard_mcq_submission.py --cycle-id <id> --submission <path>`

## UX / API / Data Notes
- Submission API is file-based JSON with fixed answer-letter schema.

## Risks / Mitigations
- Risk: sealed key policy can still be bypassed by manual reads.
  Mitigation: explicit anti-cheat violation semantics in policy and compaction skills.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should a future hardening lane externalize sealed keys beyond workspace?

## Decision Log
- Keep legacy mixed-format artifacts as compatibility-only while switching active flow.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-02-18T17:27:51Z
  TYPE: FACT
  CLAIM: Existing generator hardcodes one MCQ truth option (`B`) and does not support blind JSON grading.
  EVIDENCE:
  - skill_check/generate_bootstrap_suite.py:681-695
  - skill_check/generate_bootstrap_suite.py:747-756
  IMPACT: Real knowledge measurement requires full pipeline replacement.
  NEXT: implement hard-MCQ pool/exam/grader and skill/policy integration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:37:15Z
  TYPE: FACT
  CLAIM: Story deliverables are implemented: scripts, policy rewrites, new skills,
    and board/artifact routing are all updated for blind hard-MCQ flow.
  EVIDENCE:
  - skill_check/build_hard_mcq_pool.py:1-376
  - skill_check/skill_check_policy.md:1-132
  - agent_onboarding/default/general/skills/hard_mcq_skillcheck_protocol.md:1-38
  - attention_board.md:21-43
  IMPACT: Story is now review-ready pending user acceptance confirmation.
  NEXT: share outcome details and request acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:48:29Z
  TYPE: FACT
  CLAIM: User confirmed to continue and finish stories with sealed keys retained if testing remains properly managed.
  EVIDENCE:
  - tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md:1-196
  - attention_board.md:1-43
  IMPACT: Story is accepted for closure and can be moved to completed routing.
  NEXT: close epic, sync attention board, and archive related tasks.
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
Story implementation is complete and accepted for closure.

## Closure Note
Closed after user confirmation to continue and finalize the hard-MCQ story lane.
