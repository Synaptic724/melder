

# Answer Key Template (skill_check)

Use this template to create the answer key + grading rubric for a per-doc test.

File naming (recommended)
- `context_compass/skill_check/test_answers/cycle_<cycle_id>/<doc_id>.answers.md`

ANTI-CHEAT WARNING (non-negotiable)
- Do NOT read this file until AFTER you have submitted all answers.
- Early access invalidates the cycle.

---

## Metadata (required)

- cycle_id: <cycle_id>
- doc_id: <DOC_ID>
- source_path: <path relative to context_compass/>
- source_title: <title>
- test_file: <path to matching test file>
- generated_at_utc: <timestamp>

---

## Grading rules (required)

Result values:
- correct
- incorrect
- partial (allowed only for SHORT/SCENARIO, with explicit rubric below)

Severity values:
- low
- medium
- high
- critical

Hard rule
- Any CRITICAL P0 miss => doc FAIL.

---

## Answers + rubrics

### <doc_id>::Q001
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: <path>#<section>
- grading_notes:
  - <1â€“3 bullets explaining why>

### <doc_id>::Q002
- priority: P1
- correct_answer_ref: <path>#<section>
- accepted_answer (short):
  - <bullet 1>
  - <bullet 2>
- partial_credit_rule:
  - <what earns partial credit>
- severity: high

### <doc_id>::Q003
- priority: P0
- correct_answer_ref: <path>#<section>
- expected_steps:
  1) <step>
  2) <step>
  3) <step>
- partial_credit_rule:
  - <how partial is awarded>
- severity: critical