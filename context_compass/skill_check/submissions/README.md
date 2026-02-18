# submissions

Purpose
- Store blind-answer JSON files for hard MCQ exam cycles.

Submission schema
```json
{
  "cycle_id": "2026-02-18T180000Z",
  "answers": {
    "<question_id>": "A",
    "<question_id>": "D"
  }
}
```

Rules
- Only answer letters `A|B|C|D` are valid.
- Missing or blank answers are graded as unanswered.
- Grading is done by:
  - `python context_compass/skill_check/grade_hard_mcq_submission.py --cycle-id <id> --submission <path>`
