# ATTENTION_BOARD_MD_4477E44E1B Answer Key

## Metadata (required)

- cycle_id: 2026-02-18T160537Z
- doc_id: ATTENTION_BOARD_MD_4477E44E1B
- source_path: attention_board.md
- source_title: attention_board.md
- test_file: skill_check/tests/cycle_2026-02-18T160537Z/ATTENTION_BOARD_MD_4477E44E1B.test.md
- generated_at_utc: 2026-02-18T16:05:37Z

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

### ATTENTION_BOARD_MD_4477E44E1B::Q001
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: attention_board.md#attention-board
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ATTENTION_BOARD_MD_4477E44E1B::Q002
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: attention_board.md#active-items
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ATTENTION_BOARD_MD_4477E44E1B::Q003
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: attention_board.md#active-attention-details
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ATTENTION_BOARD_MD_4477E44E1B::Q004
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: attention_board.md#recently-closed-anchors
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ATTENTION_BOARD_MD_4477E44E1B::Q005
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: attention_board.md#attention-board
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ATTENTION_BOARD_MD_4477E44E1B::Q006
- priority: P1
- correct_answer_ref: attention_board.md#active-items
- accepted_answer (short):
  - Identifies the `must_do` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### ATTENTION_BOARD_MD_4477E44E1B::Q007
- priority: P1
- correct_answer_ref: attention_board.md#active-attention-details
- accepted_answer (short):
  - Identifies the `must_not` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### ATTENTION_BOARD_MD_4477E44E1B::Q008
- priority: P2
- correct_answer_ref: attention_board.md#recently-closed-anchors
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high
