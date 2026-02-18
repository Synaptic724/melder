# TEST_TEMPLATE_MD_ED5BCC15E4 Answer Key

## Metadata (required)

- cycle_id: 2026-02-18T162034Z
- doc_id: TEST_TEMPLATE_MD_ED5BCC15E4
- source_path: skill_check/tests/test_template.md
- source_title: test_template.md
- test_file: skill_check/tests/cycle_2026-02-18T162034Z/TEST_TEMPLATE_MD_ED5BCC15E4.test.md
- generated_at_utc: 2026-02-18T17:07:29Z

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

## Answers + rubrics

### TEST_TEMPLATE_MD_ED5BCC15E4::Q001
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/tests/test_template.md#test-template-skill-check
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q002
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/tests/test_template.md#metadata-required
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q003
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/tests/test_template.md#questions
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q004
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/tests/test_template.md#doc-id-q001
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q005
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/tests/test_template.md#doc-id-q002
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q006
- priority: P1
- correct_answer_ref: skill_check/tests/test_template.md#doc-id-q003
- accepted_answer (short):
  - Identifies the `must_do` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### TEST_TEMPLATE_MD_ED5BCC15E4::Q007
- priority: P1
- correct_answer_ref: skill_check/tests/test_template.md#test-template-skill-check
- accepted_answer (short):
  - Identifies the `must_not` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### TEST_TEMPLATE_MD_ED5BCC15E4::Q008
- priority: P2
- correct_answer_ref: skill_check/tests/test_template.md#metadata-required
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high
