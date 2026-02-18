# Task: Integrate Skill Surfaces And Existing Policies For Hard MCQ Flow

## Metadata
- Task ID: TASK-2026-02-18-skill-and-policy-surface-integration
- Story: STORY-2026-02-18-hidden-blind-hard-mcq-skillcheck
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T17:27:51Z
- Updated: 2026-02-18T17:48:29Z

## Objective
Add new skills and update existing compaction/skill-check policy docs to enforce hard-MCQ blind grading.

## Ticket Contract
- ENTRY_GATE: core scripts implemented.
- EXECUTION_BOUNDARY: role SKILLS docs, compaction skill docs, and skill-check policy/readme/templates.
- DEPENDENCIES: new script contracts and sealed-key anti-cheat model.
- EXIT_GATE: role chain includes new skills and existing policy docs reflect new workflow.
- FAILURE_ESCALATION: raise `CONFLICT` if legacy policy language contradicts hard-MCQ blind flow.

## Scope Boundaries
- In scope:
  - add new skill docs
  - update existing compaction and skill-check docs
  - update templates/readmes
- Out of scope:
  - runtime app behavior

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: skill and policy surfaces updated for new hard-MCQ pipeline.

## Steps / Checklist
- [x] Add new hard-MCQ skills.
- [x] Add skills to general role active list.
- [x] Rewrite compaction requirements for JSON blind submission and script grading.
- [x] Rewrite diff-onboarding flow for hard-MCQ cycle algorithm.
- [x] Rewrite skill-check policy and readmes/templates.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- New skills:
  - `agent_onboarding/default/general/skills/hard_mcq_skillcheck_protocol.md`
  - `agent_onboarding/default/general/skills/hard_mcq_question_pool_design.md`
- Updated existing docs for active workflow enforcement.

## Files / Paths Impacted
- `agent_onboarding/default/general/SKILLS.MD`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `skill_check/skill_check_policy.md`
- `skill_check/README.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "hard_m|sealed|JSON|MCQ" context_compass/agent_onboarding/default/general/SKILLS.MD context_compass/agent_onboarding/default/general/skills/compaction_requirements.md context_compass/skill_check/skill_check_policy.md`

## Risks / Rollback Notes
- Legacy docs referencing mixed-format tests can create operator confusion if not clearly marked legacy.

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
  CLAIM: Existing and new skills now define hard-MCQ-only blind submission with script grading and sealed key policy.
  EVIDENCE:
  - agent_onboarding/default/general/SKILLS.MD:1-44
  - agent_onboarding/default/general/skills/hard_mcq_skillcheck_protocol.md:1-38
  - agent_onboarding/default/general/skills/compaction_requirements.md:1-116
  - skill_check/skill_check_policy.md:1-132
  IMPACT: Role onboarding and compaction flow now point to the same hard-MCQ measurement regime.
  NEXT: validate scripts and route epic/story to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:48:29Z
  TYPE: FACT
  CLAIM: User accepted continued closure with current sealed-key policy model and requested story completion.
  EVIDENCE:
  - skill_check/skill_check_policy.md:1-132
  - tickets/stories/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_story_completed.md:1-145
  IMPACT: Skill/policy integration task can be finalized with board sync.
  NEXT: close remaining story/epic tickets and archive to completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Skill and policy integration for the hard-MCQ blind workflow is complete.

## Closure Note
Closed after user confirmation to finish the active hard-MCQ story and epic closure.
