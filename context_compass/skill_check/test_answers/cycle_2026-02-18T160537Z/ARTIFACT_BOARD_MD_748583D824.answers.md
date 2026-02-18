# ARTIFACT_BOARD_MD_748583D824 Answer Key

## Metadata (required)

- cycle_id: 2026-02-18T160537Z
- doc_id: ARTIFACT_BOARD_MD_748583D824
- source_path: artifact_board.md
- source_title: artifact_board.md
- test_file: skill_check/tests/cycle_2026-02-18T160537Z/ARTIFACT_BOARD_MD_748583D824.test.md
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

### ARTIFACT_BOARD_MD_748583D824::Q001
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: artifact_board.md#artifact-board
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_BOARD_MD_748583D824::Q002
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: artifact_board.md#active-artifact-links
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_BOARD_MD_748583D824::Q003
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: artifact_board.md#active-artifact-details
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_BOARD_MD_748583D824::Q004
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: artifact_board.md#recently-cleared-artifacts
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_BOARD_MD_748583D824::Q005
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: artifact_board.md#artifact-board
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_BOARD_MD_748583D824::Q006
- priority: P1
- correct_answer_ref: artifact_board.md#active-artifact-links
- accepted_answer (short):
  - Identifies the `must_do` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### ARTIFACT_BOARD_MD_748583D824::Q007
- priority: P1
- correct_answer_ref: artifact_board.md#active-artifact-details
- accepted_answer (short):
  - Identifies the `must_not` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### ARTIFACT_BOARD_MD_748583D824::Q008
- priority: P2
- correct_answer_ref: artifact_board.md#recently-cleared-artifacts
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high
