# ARTIFACT_BOARD_MD_748583D824 Test

## Metadata (required)

- cycle_id: 2026-02-18T162034Z
- doc_id: ARTIFACT_BOARD_MD_748583D824
- source_path: artifact_board.md
- source_title: artifact_board.md
- doc_type: skills
- priority: P1
- question_count: 8
- base_question_count: 8
- stability_streak: 0
- shrink_applied: false
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

### ARTIFACT_BOARD_MD_748583D824::Q001
- priority: P0
- format: MCQ
- source_anchor: artifact_board.md#artifact-board
- tags: [must_do]
Question:
Which action best satisfies the `must_do` rule for `artifact_board.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### ARTIFACT_BOARD_MD_748583D824::Q002
- priority: P0
- format: MCQ
- source_anchor: artifact_board.md#active-artifact-links
- tags: [must_not]
Question:
Which action best satisfies the `must_not` rule for `artifact_board.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### ARTIFACT_BOARD_MD_748583D824::Q003
- priority: P0
- format: MCQ
- source_anchor: artifact_board.md#active-artifact-details
- tags: [sequence]
Question:
Which action best satisfies the `sequence` rule for `artifact_board.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### ARTIFACT_BOARD_MD_748583D824::Q004
- priority: P0
- format: MCQ
- source_anchor: artifact_board.md#recently-cleared-artifacts
- tags: [escalation]
Question:
Which action best satisfies the `escalation` rule for `artifact_board.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### ARTIFACT_BOARD_MD_748583D824::Q005
- priority: P1
- format: MCQ
- source_anchor: artifact_board.md#artifact-board
- tags: [application]
Question:
Which action best satisfies the `application` rule for `artifact_board.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### ARTIFACT_BOARD_MD_748583D824::Q006
- priority: P1
- format: SHORT
- source_anchor: artifact_board.md#active-artifact-links
- tags: [must_do]
Question:
State the `must_do` requirement and one concrete consequence if it is ignored.

Answer length constraint:
- 1-3 lines

### ARTIFACT_BOARD_MD_748583D824::Q007
- priority: P1
- format: SHORT
- source_anchor: artifact_board.md#active-artifact-details
- tags: [must_not]
Question:
State the `must_not` requirement and one concrete consequence if it is ignored.

Answer length constraint:
- 1-3 lines

### ARTIFACT_BOARD_MD_748583D824::Q008
- priority: P2
- format: SCENARIO
- source_anchor: artifact_board.md#recently-cleared-artifacts
- tags: [sequence]
Scenario:
A compaction recovery session starts and an operator wants to skip one required gate.

Prompt:
Describe the compliant `sequence` response sequence for `artifact_board.md`.
