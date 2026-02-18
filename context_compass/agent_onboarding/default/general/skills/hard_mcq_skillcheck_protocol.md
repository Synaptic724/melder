# hard_mcq_skillcheck_protocol

Purpose
- Define the operational protocol for hard-MCQ skill checks.

Non-negotiable rules
1) Questions are MCQ only.
2) One question has one truth plus three difficult deterministic lies.
3) Submission is JSON-only.
4) Grading is script-only from sealed keys.

Commands
1) Build pool:
   - `python context_compass/skill_check/build_hard_mcq_pool.py --multiplier 10`
2) Generate exam:
   - `python context_compass/skill_check/generate_hard_mcq_exam.py --cycle-id <id>`
3) Grade submission:
   - `python context_compass/skill_check/grade_hard_mcq_submission.py --cycle-id <id> --submission <path>`

Blindness rules
- Read exam markdown and submission docs only before submission.
- Do not read `.sealed` artifacts before submission.
- Do not read legacy `test_answers/` artifacts for hard-MCQ cycles.

Submission schema
```json
{
  "cycle_id": "<id>",
  "answers": {
    "<question_id>": "A|B|C|D"
  }
}
```

Failure conditions
- Sealed pre-read => anti-cheat violation.
- Missing grader run => cycle incomplete.
