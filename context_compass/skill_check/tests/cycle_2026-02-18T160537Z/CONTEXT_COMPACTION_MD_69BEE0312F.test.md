# CONTEXT_COMPACTION_MD_69BEE0312F Test

## Metadata (required)

- cycle_id: 2026-02-18T160537Z
- doc_id: CONTEXT_COMPACTION_MD_69BEE0312F
- source_path: agent_onboarding/default/general/skills/context_compaction.md
- source_title: context_compaction.md
- doc_type: skills
- priority: P1
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

### CONTEXT_COMPACTION_MD_69BEE0312F::Q001
- priority: P0
- format: MCQ
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#context-compaction-policy-fidelity-first
- tags: [must_do]
Question:
Which action best satisfies the `must_do` rule for `agent_onboarding/default/general/skills/context_compaction.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### CONTEXT_COMPACTION_MD_69BEE0312F::Q002
- priority: P0
- format: MCQ
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#purpose
- tags: [must_not]
Question:
Which action best satisfies the `must_not` rule for `agent_onboarding/default/general/skills/context_compaction.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### CONTEXT_COMPACTION_MD_69BEE0312F::Q003
- priority: P0
- format: MCQ
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#objective-and-weighting
- tags: [sequence]
Question:
Which action best satisfies the `sequence` rule for `agent_onboarding/default/general/skills/context_compaction.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### CONTEXT_COMPACTION_MD_69BEE0312F::Q004
- priority: P0
- format: MCQ
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#compaction-summary-rule
- tags: [escalation]
Question:
Which action best satisfies the `escalation` rule for `agent_onboarding/default/general/skills/context_compaction.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### CONTEXT_COMPACTION_MD_69BEE0312F::Q005
- priority: P1
- format: MCQ
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#required-schema-system-first
- tags: [application]
Question:
Which action best satisfies the `application` rule for `agent_onboarding/default/general/skills/context_compaction.md`?

Options:
A) Ignore the explicit gate and continue execution.
B) Follow the stated rule and record evidence before proceeding.
C) Skip required reads because similar docs were read earlier.
D) Defer the rule until after implementation.

### CONTEXT_COMPACTION_MD_69BEE0312F::Q006
- priority: P1
- format: SHORT
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#required-review-set-before-compaction-handoff
- tags: [must_do]
Question:
State the `must_do` requirement and one concrete consequence if it is ignored.

Answer length constraint:
- 1-3 lines

### CONTEXT_COMPACTION_MD_69BEE0312F::Q007
- priority: P1
- format: SHORT
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#post-compaction-re-entry
- tags: [must_not]
Question:
State the `must_not` requirement and one concrete consequence if it is ignored.

Answer length constraint:
- 1-3 lines

### CONTEXT_COMPACTION_MD_69BEE0312F::Q008
- priority: P2
- format: SCENARIO
- source_anchor: agent_onboarding/default/general/skills/context_compaction.md#context-compaction-policy-fidelity-first
- tags: [sequence]
Scenario:
A compaction recovery session starts and an operator wants to skip one required gate.

Prompt:
Describe the compliant `sequence` response sequence for `agent_onboarding/default/general/skills/context_compaction.md`.
