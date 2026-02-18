# Task: Implement Hard MCQ Pool Generator

## Metadata
- Task ID: TASK-2026-02-18-hard-mcq-pool-generator-implementation
- Story: STORY-2026-02-18-hidden-blind-hard-mcq-skillcheck
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T17:27:51Z
- Updated: 2026-02-18T17:48:29Z

## Objective
Create a pool builder that produces difficult MCQ-only question inventory at >=10x scale.

## Ticket Contract
- ENTRY_GATE: sealed-storage contract exists.
- EXECUTION_BOUNDARY: pool builder code and pool README only.
- DEPENDENCIES: manifest docs and current question-count baseline.
- EXIT_GATE: script emits public pool + sealed truth map at target volume.
- FAILURE_ESCALATION: raise `CONFLICT` if deterministic lies cannot stay close to source truth.

## Scope Boundaries
- In scope:
  - `build_hard_mcq_pool.py`
  - `question_pool/README.md`
- Out of scope:
  - exam rendering
  - grading output

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: hard-MCQ pool builder implemented with 10x scaling and deterministic lie generation.

## Steps / Checklist
- [x] Implement claim extraction from source docs.
- [x] Implement deterministic lie mutations (modality/sequence/scope).
- [x] Implement target-size generation loop (>=10x baseline).
- [x] Emit public pool and sealed truth map files.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `skill_check/build_hard_mcq_pool.py`
- `skill_check/question_pool/hard_mcq_pool.jsonl` generation contract

## Files / Paths Impacted
- `skill_check/build_hard_mcq_pool.py`
- `skill_check/question_pool/README.md`
- `skill_check/.sealed/pool_truth_keys.jsonl` (runtime output)

## Validation
- Not run.
- Recommended commands:
  - `python context_compass/skill_check/build_hard_mcq_pool.py --multiplier 10`
  - `python -m py_compile context_compass/skill_check/build_hard_mcq_pool.py`

## Risks / Rollback Notes
- Excessively templated lies can become pattern-learnable over many cycles.

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
  CLAIM: Pool builder now extracts source claims and generates difficult 3-lie/1-truth MCQs at configurable multiplier depth.
  EVIDENCE:
  - skill_check/build_hard_mcq_pool.py:1-376
  - skill_check/question_pool/README.md:1-20
  IMPACT: Exam generator can pull randomized hard questions without exposing truth keys.
  NEXT: implement exam generator with LOC quota and randomized option ordering.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:48:29Z
  TYPE: MEASURE
  CLAIM: Pool generation task is accepted for closure with hard-MCQ generation behavior preserved.
  EVIDENCE:
  - skill_check/build_hard_mcq_pool.py:1-432
  - tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md:1-196
  IMPACT: Task closure criteria are satisfied for this implementation unit.
  NEXT: complete story/epic closure and board routing update.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Hard-MCQ pool generation is implemented and ready for exam selection logic.

## Closure Note
Closed after user confirmation to continue and finish the active hard-MCQ story chain.
