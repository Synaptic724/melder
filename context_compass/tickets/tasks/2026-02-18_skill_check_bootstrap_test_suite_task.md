# Task: Skill Check Bootstrap Test Suite Generation

## Metadata
- Task ID: TASK-2026-02-18-skill-check-bootstrap-test-suite
- Story: none
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:01:46Z
- Updated: 2026-02-18T16:01:46Z

## Objective
Generate the initial skill-check bootstrap artifacts so compaction cycles can run
with manifest-driven test/answer coverage.

## Ticket Contract
- ENTRY_GATE: user approved certification and explicitly requested test-suite
  build routed via attention board and tickets.
- EXECUTION_BOUNDARY: `skill_check/`, `attention_board.md`, and this task file.
- DEPENDENCIES: `skill_check/skill_check_policy.md` bootstrap requirements.
- EXIT_GATE: manifest populated for required docs, cycle test+answer files
  generated, and quality gate report published.
- FAILURE_ESCALATION: raise `BLOCKER` if generated suite misses required
  manifest test/answer pairs or fails policy quality threshold.

## Scope Boundaries
- In scope:
  - `skill_check/manifest/onboarding_manifest.yaml`
  - `skill_check/tests/`
  - `skill_check/test_answers/`
  - `skill_check/historical_test_results/`
  - `attention_board.md` active routing
- Out of scope:
  - runtime source code under `src/`
  - non-skill-check policy rewrites

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user requested immediate bootstrap suite generation for
  compaction readiness.

## Steps / Checklist
- [x] Route active attention to this task.
- [ ] Build deterministic required-doc manifest from onboarding chain.
- [ ] Generate cycle test files and answer files for required docs.
- [ ] Compute and record bootstrap quality scores per generated test file.
- [ ] Publish bootstrap summary and readiness state.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Populated onboarding manifest with required `test_file` and `answer_file`
  mappings.
- Generated cycle test set and answer set for required docs.
- Bootstrap quality summary artifact.

## Files / Paths Impacted
- `skill_check/manifest/onboarding_manifest.yaml`
- `skill_check/tests/cycle_<cycle_id>/`
- `skill_check/test_answers/cycle_<cycle_id>/`
- `skill_check/historical_test_results/cycle_<cycle_id>.md`
- `attention_board.md`
- `tickets/tasks/2026-02-18_skill_check_bootstrap_test_suite_task.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "doc_id:|required_for_certification: true" skill_check/manifest/onboarding_manifest.yaml`
  - `rg -n "test_quality_score:" skill_check/tests/cycle_*/*.test.md`
  - `rg -n "correct_answer_ref:" skill_check/test_answers/cycle_*/*.answers.md`

## Risks / Rollback Notes
- Bulk-generated content quality may drift below rubric threshold and require
  regeneration.
- Manifest/test mismatch would block compaction certification workflows.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: close ticket

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step
  continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T16:01:46Z
  TYPE: FACT
  CLAIM: Bootstrap artifacts are not yet generated; manifest remains placeholder
    with empty entries and policy requires immediate post-cert generation.
  EVIDENCE:
  - skill_check/manifest/onboarding_manifest.yaml:41-44
  - skill_check/skill_check_policy.md:63-65
  IMPACT: Compaction-ready skill checks are blocked until manifest and cycle
    files exist.
  NEXT: generate manifest entries and cycle test/answer artifacts for required
    docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task tracks bootstrap creation of skill-check manifest and initial cycle suite
required before robust compaction re-entry scoring.
