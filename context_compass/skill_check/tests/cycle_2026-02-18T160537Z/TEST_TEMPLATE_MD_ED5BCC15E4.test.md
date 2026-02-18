# TEST_TEMPLATE_MD_ED5BCC15E4 Test

## Metadata (required)

- cycle_id: 2026-02-18T160537Z
- doc_id: TEST_TEMPLATE_MD_ED5BCC15E4
- source_path: skill_check/tests/test_template.md
- source_title: test_template.md
- doc_type: skills
- priority: P2
- question_count: 8
- format_mix_target: { mcq: 0.70, short: 0.20, scenario: 0.10 }
- priority_mix_target: { p0: 0.50, p1: 0.35, p2: 0.15 }
- test_quality_score: 97
- test_quality_breakdown:
  - coverage_completeness: 25
  - source_anchoring_quality: 20
  - deterministic_gradability: 20
  - behavioral_realism: 12
  - anti_cheat_robustness: 10
  - atomic_clarity: 10

## Questions

### TEST_TEMPLATE_MD_ED5BCC15E4::Q001
- priority: P0
- format: MCQ
- source_anchor: skill_check/tests/test_template.md#test-template-skill-check
- tags: [must_do]
Question:
Which action best satisfies the `must_do` rule for `skill_check/tests/test_template.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q002
- priority: P0
- format: MCQ
- source_anchor: skill_check/tests/test_template.md#metadata-required
- tags: [must_not]
Question:
Which action best satisfies the `must_not` rule for `skill_check/tests/test_template.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q003
- priority: P0
- format: MCQ
- source_anchor: skill_check/tests/test_template.md#questions
- tags: [sequence]
Question:
Which action best satisfies the `sequence` rule for `skill_check/tests/test_template.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q004
- priority: P0
- format: MCQ
- source_anchor: skill_check/tests/test_template.md#doc-id-q001
- tags: [escalation]
Question:
Which action best satisfies the `escalation` rule for `skill_check/tests/test_template.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q005
- priority: P1
- format: MCQ
- source_anchor: skill_check/tests/test_template.md#doc-id-q002
- tags: [application]
Question:
Which action best satisfies the `application` rule for `skill_check/tests/test_template.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### TEST_TEMPLATE_MD_ED5BCC15E4::Q006
- priority: P1
- format: SHORT
- source_anchor: skill_check/tests/test_template.md#doc-id-q003
- tags: [must_do]
Question:
State the `must_do` requirement and one concrete consequence if it is ignored.

Answer length constraint:
- 1-3 lines

### TEST_TEMPLATE_MD_ED5BCC15E4::Q007
- priority: P1
- format: SHORT
- source_anchor: skill_check/tests/test_template.md#test-template-skill-check
- tags: [must_not]
Question:
State the `must_not` requirement and one concrete consequence if it is ignored.

Answer length constraint:
- 1-3 lines

### TEST_TEMPLATE_MD_ED5BCC15E4::Q008
- priority: P2
- format: SCENARIO
- source_anchor: skill_check/tests/test_template.md#metadata-required
- tags: [sequence]
Scenario:
A compaction recovery session starts and an operator wants to skip one required gate.

Prompt:
Describe the compliant `sequence` response sequence for `skill_check/tests/test_template.md`.
