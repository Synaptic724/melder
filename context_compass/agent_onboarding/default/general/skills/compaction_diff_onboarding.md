# compaction_diff_onboarding (Hard MCQ Skill-Gate-First Mode)

Purpose
- Preserve compaction fidelity while validating real knowledge performance with
  blind hard-MCQ scoring.

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/compacting_differential_board.md`
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`

Trigger
- compaction event
- handoff event
- session reset with untrusted continuity

Hard rule
- No implementation work before measured re-entry and certification gates pass.

---

## Artifacts (required)

Public
- `skill_check/question_pool/hard_mcq_pool.jsonl`
- `skill_check/tests/cycle_<id>/hard_mcq_exam.md`
- `skill_check/submissions/cycle_<id>_answers.json`
- `skill_check/historical_test_results/cycle_<id>_hard_mcq_grade.md`

Sealed
- `skill_check/.sealed/pool_truth_keys.jsonl`
- `skill_check/.sealed/exams/cycle_<id>_answer_key.json`

---

## Cycle algorithm

### Step 0 - Enter measured mode
- Declare `NO_ACTION_TAKEN_YET: true`.
- Select `cycle_id`.

### Step 1 - Minimum readset
Read only:
1) active manifest metadata,
2) active hard-MCQ exam markdown,
3) submission schema,
4) grading policy.

Do not read:
- `skill_check/.sealed/**`
- `skill_check/test_answers/**`
- broad under-test skill docs before submission

### Step 2 - Blind submission
1) Answer all questions in JSON.
2) Submit JSON path and `ANSWERS_UNREAD: true`.
3) Lock submission before grading.

### Step 3 - Scripted grading
Run grader command only:
- `python context_compass/skill_check/grade_hard_mcq_submission.py --cycle-id <id> --submission <path>`

Capture:
- correct/incorrect/unanswered counts
- score
- rank
- per-doc misses

### Step 4 - Parity measurement
Run diff-onboarding parity checks and compute:
- `system_skill_doc_coverage`
- `system_skill_parity_rate`
- `policy_gate_miss_count`
- `fidelity_score`
- `global_score`

### Step 5 - Targeted relearn
- Re-read only failed/weak docs plus required P0 dependencies.
- Generate remediation and next-compaction hints.

### Step 6 - Gate outcome
Pass requires:
1) hard-MCQ score gates,
2) diff parity gates,
3) anti-cheat intact.

Hard outcomes:
- grading not run => `incomplete`
- sealed pre-read => `ANTI_CHEAT_VIOLATION: true`

---

## Required pre-cert reporting

Before requesting certification publish:
1) `SKILL_GATE_REPORT` (hard-MCQ score evidence)
2) `DIFF_ONBOARDING_REPORT` (semantic parity evidence)

Either missing blocks certification.
