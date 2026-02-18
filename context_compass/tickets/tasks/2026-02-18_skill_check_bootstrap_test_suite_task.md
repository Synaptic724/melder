# Task: Skill Check Bootstrap Test Suite Generation

## Metadata
- Task ID: TASK-2026-02-18-skill-check-bootstrap-test-suite
- Story: none
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:01:46Z
- Updated: 2026-02-18T16:43:50Z

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
- [x] Build deterministic required-doc manifest from onboarding chain.
- [x] Generate cycle test files and answer files for required docs.
- [x] Compute and record bootstrap quality scores per generated test file.
- [x] Publish bootstrap summary and readiness state.
- [x] Implement adaptive suite maintenance: stability-driven shrink metadata and
      compaction cleanup to keep a single fresh cycle.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
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
- `skill_check/generate_bootstrap_suite.py`
- `attention_board.md`
- `tickets/tasks/2026-02-18_skill_check_bootstrap_test_suite_task.md`

## Validation
- Ran: `python context_compass/skill_check/generate_bootstrap_suite.py`
  - cycle_id: `2026-02-18T162034Z`
  - total_docs: `81`
  - required_for_certification_docs: `27`
  - total_questions: `752`
  - stable_docs: `0`
  - shrink_applied_docs: `0`
  - avg_test_quality_score: `97.00`
  - removed_test_cycle_dirs: `1`
  - removed_answer_cycle_dirs: `1`
  - removed_historical_cycle_files: `1`
- Ran: `python -c "import py_compile; py_compile.compile('context_compass/skill_check/generate_bootstrap_suite.py', doraise=True)"`.
- Recommended commands:
  - `rg -n "doc_id:|required_for_certification: true|stability_streak:" skill_check/manifest/onboarding_manifest.yaml`
  - `rg -n "question_count:|base_question_count:|shrink_applied:" skill_check/tests/cycle_*/*.test.md`
  - `rg -n "removed_test_cycle_dirs:|removed_answer_cycle_dirs:" skill_check/historical_test_results/cycle_*.md`

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

- DATETIME: 2026-02-18T16:05:37Z
  TYPE: FACT
  CLAIM: Bootstrap generator populated the manifest and generated a full cycle
    suite with quality score 97 for each generated test file.
  EVIDENCE:
  - skill_check/manifest/onboarding_manifest.yaml:5-20
  - skill_check/historical_test_results/cycle_2026-02-18T160537Z.md:15-20
  - skill_check/generate_bootstrap_suite.py:1-445
  IMPACT: Skill-check bootstrap gates are now materially satisfied for manifest
    and artifact presence.
  NEXT: enforce single-suite state by removing older generated cycle artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T16:08:25Z
  TYPE: MEASURE
  CLAIM: Cleanup pass removed the older cycle (`2026-02-18T160455Z`) so only
    the latest suite (`2026-02-18T160537Z`) remains referenced and stored.
  EVIDENCE:
  - skill_check/manifest/onboarding_manifest.yaml:18-19
  - skill_check/historical_test_results/cycle_2026-02-18T160537Z.md:1-20
  IMPACT: The test system now has a single active bootstrap suite, matching the
    requested state.
  NEXT: confirm suite shape with user and continue compaction-prep work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T16:21:08Z
  TYPE: FACT
  CLAIM: Generator now supports compaction refresh maintenance by regenerating a
    fresh cycle, pruning stale cycle artifacts, and carrying stability metadata
    for future shrink decisions.
  EVIDENCE:
  - skill_check/generate_bootstrap_suite.py:1-971
  - skill_check/historical_test_results/cycle_2026-02-18T162034Z.md:1-35
  - agent_onboarding/default/general/skills/compaction_requirements.md:192-204
  IMPACT: Single-suite policy is now enforced automatically; future graded
    cycles can reduce total questions once streak thresholds are met.
  NEXT: confirm whether grading writes `status/last_score/requires_retest` and
    `stability_streak` values back to manifest for shrink activation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T16:43:50Z
  TYPE: MEASURE
  CLAIM: Compacting diff cycle `2026-02-18T1623Z-F01` was recorded with 10
    fidelity claims and full parity on the sampled system-skill claim set.
  EVIDENCE:
  - compacting_differential_board.md:24-123
  IMPACT: Fidelity loop is now represented in the canonical board; knowledge
    test rows remain outstanding for full cycle completion.
  NEXT: run skill-gate grading and append `knowledge_test` rows for the same
    cycle id.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task now contains a single active maintained suite (`cycle_2026-02-18T162034Z`)
and one compacting diff cycle entry (`2026-02-18T1623Z-F01`) in the
differential board; fidelity evidence is present and knowledge evidence is
pending.
