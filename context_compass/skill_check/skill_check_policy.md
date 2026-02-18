# skill_check_policy (Hard MCQ Blind-Submission Policy)

Status: active
Scope: post-compaction knowledge measurement and scoring workflow
Owner: user authority (policy) + implementation agent (execution)

This policy defines the current skill-check system:
1) hard MCQ pool build,
2) blinded exam generation,
3) JSON submission,
4) sealed-key grading,
5) score/rank reporting and remediation routing.

---

## 1) Core intent (non-negotiable)

1. Compaction success must be score-grounded.
2. Question format is MCQ only.
3. Each question must contain:
   - 1 true statement,
   - 3 difficult deterministic lies that are close to the truth.
4. Exam volume is `1 question per 100 LOC` for each required doc.
5. A cycle is incomplete until grading has been run.

---

## 2) Artifact layout (required)

Public artifacts
- `context_compass/skill_check/question_pool/hard_mcq_pool.jsonl`
- `context_compass/skill_check/tests/cycle_<id>/hard_mcq_exam.md`
- `context_compass/skill_check/submissions/cycle_<id>_answers.json`
- `context_compass/skill_check/historical_test_results/cycle_<id>_hard_mcq_grade.md`

Sealed artifacts (private)
- `context_compass/skill_check/.sealed/pool_truth_keys.jsonl`
- `context_compass/skill_check/.sealed/exams/cycle_<id>_answer_key.json`

Hard rule
- Sealed artifacts must never be embedded into public exam markdown files.

---

## 3) Pool build contract (required)

Build command
- `python context_compass/skill_check/build_hard_mcq_pool.py --multiplier 10`

Requirements
1) Pool size target must be >= `10x` current known question count.
2) Pool rows must not expose explicit answer keys.
3) Truth mapping must be written to sealed storage.
4) Question options must be close-match statements, not obvious distractors.

---

## 4) Exam generation contract (required)

Generation command
- `python context_compass/skill_check/generate_hard_mcq_exam.py --cycle-id <id>`

Requirements
1) Resolve required docs from manifest.
2) Allocate `ceil(LOC/100)` questions per required doc.
3) Randomize selected question order.
4) Randomize option order per question.
5) Write answer keys only to sealed cycle key file.
6) Emit a JSON submission template for the cycle.

---

## 5) Submission contract (required)

Submission schema
```json
{
  "cycle_id": "2026-02-18T180000Z",
  "answers": {
    "<question_id>": "A"
  }
}
```

Rules
1) Allowed values are `A|B|C|D`.
2) Missing/blank answers are scored as unanswered.
3) Submission is considered blind until grading begins.

---

## 6) Grading contract (required)

Grading command
- `python context_compass/skill_check/grade_hard_mcq_submission.py --cycle-id <id> --submission <path>`

Required outputs
1) Total correct/incorrect/unanswered counts.
2) Score percentage.
3) Rank (`S|A|B|C|D`).
4) Per-doc score breakdown.
5) Persisted cycle report under `historical_test_results/`.

---

## 7) Anti-cheat protocol (strict)

1) Read only exam markdown before submission.
2) Do not read sealed key artifacts before submission.
3) Do not grade until JSON answers are fully submitted.
4) Any sealed pre-read is an anti-cheat violation.

---

## 8) Certification gates

Certification remains blocked unless:
1) Grading has been executed for the active cycle.
2) `knowledge_score`/rank thresholds are met by configured policy.
3) Critical policy-gate misses are zero.
4) Anti-cheat protocol is intact.

Hard rule
- `knowledge_score: Not run` or missing grade report means cycle status is `incomplete`.

---

## 9) Maintenance

After accepted cycle closure:
1) Refresh pool with multiplier target.
2) Generate fresh exam for next cycle.
3) Keep sealed keys local and private.
4) Track score trends in historical results.

---

## 10) Legacy compatibility note

Legacy mixed-format test artifacts may still exist under `test_answers/`.
The active flow is hard-MCQ + sealed-key grading only.
