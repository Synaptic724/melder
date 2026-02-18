# Hard MCQ Test Template (skill_check)

Use this template to create per-cycle hard MCQ exam files.

File naming (recommended)
- `context_compass/skill_check/tests/cycle_<cycle_id>/hard_mcq_exam.md`

Hard rules
- MCQ only.
- Each question has 4 options.
- Exactly one option is true.
- Public exam files must not include explicit answer keys.

---

## Metadata (required)

- cycle_id: <cycle_id>
- question_count: <n>
- question_quota_rule: 1 question per 100 LOC for each required doc
- format: MCQ-only

---

## Question block format

### Q001 (<question_id>)
- source: <path>#<section>
- doc_id: <doc_id>
- difficulty: hard

Prompt:
<text>

A) <text>
B) <text>
C) <text>
D) <text>
