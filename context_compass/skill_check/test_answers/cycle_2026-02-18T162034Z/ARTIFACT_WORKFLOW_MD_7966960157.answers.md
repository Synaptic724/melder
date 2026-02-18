# ARTIFACT_WORKFLOW_MD_7966960157 Answer Key

## Metadata (required)

- cycle_id: 2026-02-18T162034Z
- doc_id: ARTIFACT_WORKFLOW_MD_7966960157
- source_path: agent_onboarding/default/engineer/examples/artifact_workflow.md
- source_title: artifact_workflow.md
- test_file: skill_check/tests/cycle_2026-02-18T162034Z/ARTIFACT_WORKFLOW_MD_7966960157.test.md
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

### ARTIFACT_WORKFLOW_MD_7966960157::Q001
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#engineer-example-artifact-workflow
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_WORKFLOW_MD_7966960157::Q002
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#idea-spellbook-cleanup-ordering
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_WORKFLOW_MD_7966960157::Q003
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#why-now
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_WORKFLOW_MD_7966960157::Q004
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#early-hypothesis
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_WORKFLOW_MD_7966960157::Q005
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#risk-notes
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### ARTIFACT_WORKFLOW_MD_7966960157::Q006
- priority: P1
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#promote-when
- accepted_answer (short):
  - Identifies the `must_do` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### ARTIFACT_WORKFLOW_MD_7966960157::Q007
- priority: P1
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#todo-spellbook-cleanup-ordering
- accepted_answer (short):
  - Identifies the `must_not` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### ARTIFACT_WORKFLOW_MD_7966960157::Q008
- priority: P2
- correct_answer_ref: agent_onboarding/default/engineer/examples/artifact_workflow.md#story-spellbook-cleanup-ordering
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high
