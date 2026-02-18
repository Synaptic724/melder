# HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D Answer Key

## Metadata (required)

- cycle_id: 2026-02-18T162034Z
- doc_id: HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D
- source_path: skill_check/historical_test_results/historical_results_template.md
- source_title: historical_results_template.md
- test_file: skill_check/tests/cycle_2026-02-18T162034Z/HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D.test.md
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

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q001
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#historical-test-results-template-skill-check
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q002
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#cycle-metadata
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q003
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#cycle-summary-required
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q004
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#failed-weak-docs-required-if-any
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q005
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#fidelity-misses-policy-gate-first
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q006
- priority: P1
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#knowledge-misses-p0-first
- accepted_answer (short):
  - Identifies the `must_do` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q007
- priority: P1
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#remediation-plan-required-if-blocked
- accepted_answer (short):
  - Identifies the `must_not` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### HISTORICAL_RESULTS_TEMPLATE_MD_10A5A0042D::Q008
- priority: P2
- correct_answer_ref: skill_check/historical_test_results/historical_results_template.md#historical-test-results-template-skill-check
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high
