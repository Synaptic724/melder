# SKILL_CHECK_POLICY_MD_7D5A201CAB Answer Key

## Metadata (required)

- cycle_id: 2026-02-18T162034Z
- doc_id: SKILL_CHECK_POLICY_MD_7D5A201CAB
- source_path: skill_check/skill_check_policy.md
- source_title: skill_check_policy.md
- test_file: skill_check/tests/cycle_2026-02-18T162034Z/SKILL_CHECK_POLICY_MD_7D5A201CAB.test.md
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

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q001
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/skill_check_policy.md#skill-check-policy-skill-gate-first-scored-compaction-policy
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q002
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/skill_check_policy.md#1-core-intent-non-negotiable
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q003
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/skill_check_policy.md#2-artifacts-required
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q004
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/skill_check_policy.md#3-operating-model
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q005
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/skill_check_policy.md#a-bootstrap-generation-one-time-post-cert
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q006
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/skill_check_policy.md#b-post-compaction-re-entry-every-cycle
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q007
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/skill_check_policy.md#4-manifest-requirements
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q008
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/skill_check_policy.md#4-1-generation-timing
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q009
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/skill_check_policy.md#4-2-minimum-fields
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q010
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/skill_check_policy.md#5-skill-gate-onboard-contract-minimum-read-gate
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q011
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/skill_check_policy.md#6-test-authoring-model
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q012
- priority: P1
- correct_answer_ref: skill_check/skill_check_policy.md#7-test-quality-gate
- accepted_answer (short):
  - Identifies the `must_not` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q013
- priority: P1
- correct_answer_ref: skill_check/skill_check_policy.md#8-anti-cheat-protocol-strict
- accepted_answer (short):
  - Identifies the `sequence` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q014
- priority: P1
- correct_answer_ref: skill_check/skill_check_policy.md#9-scoring-model
- accepted_answer (short):
  - Identifies the `escalation` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q015
- priority: P2
- correct_answer_ref: skill_check/skill_check_policy.md#10-certification-gates
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high

### SKILL_CHECK_POLICY_MD_7D5A201CAB::Q016
- priority: P2
- correct_answer_ref: skill_check/skill_check_policy.md#11-diff-board-integration
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high
