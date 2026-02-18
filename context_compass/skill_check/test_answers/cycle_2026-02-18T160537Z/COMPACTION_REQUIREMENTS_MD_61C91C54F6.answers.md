# COMPACTION_REQUIREMENTS_MD_61C91C54F6 Answer Key

## Metadata (required)

- cycle_id: 2026-02-18T160537Z
- doc_id: COMPACTION_REQUIREMENTS_MD_61C91C54F6
- source_path: agent_onboarding/default/general/skills/compaction_requirements.md
- source_title: compaction_requirements.md
- test_file: skill_check/tests/cycle_2026-02-18T160537Z/COMPACTION_REQUIREMENTS_MD_61C91C54F6.test.md
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

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q001
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-diff-onboarding-skill-gate
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q002
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#phase-a-deterministic-re-onboarding-reads-mandatory
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q003
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#phase-b-measurement-knowledge-gate-mandatory
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q004
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b0-cycle-initialization-required
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q005
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b1-manifest-regeneration-required
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q006
- priority: P0
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b2-test-quality-gate-required
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q007
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b3-skill-check-execution-anti-cheat-strict
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q008
- priority: P0
- correct_answer: B
- severity: critical
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b4-diff-onboarding-semantic-parity-execution
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q009
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b5-global-scoring-pass-fail-required
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q010
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#phase-c-certification-request-strict
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q011
- priority: P1
- correct_answer: B
- severity: high
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#phase-d-post-cert-updates-allowed-only-after-certify-approved
- grading_notes:
  - Correct option preserves policy gates and ordering constraints.
  - Incorrect options represent bypasses or unsupported shortcuts.

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q012
- priority: P1
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-diff-onboarding-skill-gate
- accepted_answer (short):
  - Identifies the `must_not` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q013
- priority: P1
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#phase-a-deterministic-re-onboarding-reads-mandatory
- accepted_answer (short):
  - Identifies the `sequence` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q014
- priority: P1
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#phase-b-measurement-knowledge-gate-mandatory
- accepted_answer (short):
  - Identifies the `escalation` rule in this document.
  - Names one concrete impact of violating the rule.
- partial_credit_rule:
  - Partial credit if rule is correct but impact is vague.
- severity: high

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q015
- priority: P2
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b0-cycle-initialization-required
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high

### COMPACTION_REQUIREMENTS_MD_61C91C54F6::Q016
- priority: P2
- correct_answer_ref: agent_onboarding/default/general/skills/compaction_requirements.md#b1-manifest-regeneration-required
- expected_steps:
  1) Stop at the active gate boundary.
  2) Apply the required rule with explicit evidence.
  3) Request the required approval token before continuing.
- partial_credit_rule:
  - Partial credit if sequence is mostly correct but one gate is omitted.
- severity: high
