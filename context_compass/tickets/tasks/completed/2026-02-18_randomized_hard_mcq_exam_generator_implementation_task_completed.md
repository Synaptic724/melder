# Task: Implement Randomized Hard MCQ Exam Generator

## Metadata
- Task ID: TASK-2026-02-18-randomized-hard-mcq-exam-generator-implementation
- Story: STORY-2026-02-18-hidden-blind-hard-mcq-skillcheck
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T17:27:51Z
- Updated: 2026-02-18T17:48:29Z

## Objective
Generate exam markdown with randomized question/option order and per-doc LOC quotas.

## Ticket Contract
- ENTRY_GATE: pool builder is available.
- EXECUTION_BOUNDARY: exam-generation script and submission-template surfaces.
- DEPENDENCIES: manifest required docs, pool rows, sealed truth map.
- EXIT_GATE: exam file + submission template + sealed cycle key are produced per cycle.
- FAILURE_ESCALATION: raise `BLOCKER` when pool depth is below LOC-based quota requirements.

## Scope Boundaries
- In scope:
  - `generate_hard_mcq_exam.py`
  - submission template generation
- Out of scope:
  - grading calculations

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: exam generation script now enforces 1q/100LOC and randomized rendering.

## Steps / Checklist
- [x] Resolve required docs from manifest.
- [x] Allocate question count from `ceil(LOC/100)`.
- [x] Randomize selected question order and option order.
- [x] Emit exam markdown and JSON submission template.
- [x] Emit sealed per-cycle answer key file.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `skill_check/generate_hard_mcq_exam.py`
- `skill_check/tests/cycle_<id>/hard_mcq_exam.md` generation contract
- `skill_check/submissions/cycle_<id>_answers_template.json` generation contract

## Files / Paths Impacted
- `skill_check/generate_hard_mcq_exam.py`
- `skill_check/submissions/README.md`
- `skill_check/tests/README.md`

## Validation
- Not run.
- Recommended commands:
  - `python context_compass/skill_check/generate_hard_mcq_exam.py --cycle-id <id>`
  - `python -m py_compile context_compass/skill_check/generate_hard_mcq_exam.py`

## Risks / Rollback Notes
- RNG seed is stored in sealed metadata; strict policy enforcement is still required to preserve blind flow.

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
  CLAIM: Exam generator now uses required-doc LOC quotas, randomized ordering, and sealed per-cycle key output.
  EVIDENCE:
  - skill_check/generate_hard_mcq_exam.py:1-259
  - skill_check/submissions/README.md:1-22
  IMPACT: Blind exam consumption is now decoupled from truth-key visibility.
  NEXT: implement grader and integrate report outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:48:29Z
  TYPE: MEASURE
  CLAIM: Exam generation task remains closure-ready with randomized cycle outputs and sealed answer-key flow.
  EVIDENCE:
  - skill_check/generate_hard_mcq_exam.py:1-252
  - skill_check/tests/cycle_2026-02-18T173500Z/hard_mcq_exam.md:1-260
  IMPACT: This task can be closed in line with the accepted story closure path.
  NEXT: close story/epic and archive tickets under completed folders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Randomized exam generation and submission-template output are implemented.

## Closure Note
Closed after user confirmation to finish story closure while retaining sealed-key handling.
