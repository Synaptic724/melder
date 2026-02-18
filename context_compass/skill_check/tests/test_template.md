

# Test Template (skill_check)

Use this template to create per-doc tests.

File naming (recommended)
- `context_compass/skill_check/tests/cycle_<cycle_id>/<doc_id>.test.md`

Hard rules
- Stable question IDs: `<doc_id>::Q###`
- Every question MUST include:
  - priority (P0/P1/P2)
  - format (MCQ/SHORT/SCENARIO)
  - source anchor (path + section)
- Tests MUST be source-anchored to canonical docs.
- Do NOT place answers in this file.

---

## Metadata (required)

- cycle_id: <cycle_id>
- doc_id: <DOC_ID>
- source_path: <path relative to context_compass/>
- source_title: <title>
- doc_type: agents|skills|policy|behavior
- priority: P0|P1|P2
- question_count: <n>
- format_mix_target: { mcq: 0.70, short: 0.20, scenario: 0.10 }
- priority_mix_target: { p0: 0.50, p1: 0.35, p2: 0.15 }
- test_quality_score: <0-100> (must be >= threshold)
- test_quality_breakdown:
  - coverage_completeness: <0-25>
  - source_anchoring_quality: <0-20>
  - deterministic_gradability: <0-20>
  - behavioral_realism: <0-15>
  - anti_cheat_robustness: <0-10>
  - atomic_clarity: <0-10>

---

## Questions

### <doc_id>::Q001
- priority: P0
- format: MCQ
- source_anchor: <path>#<section>
- tags: [must_do|must_not|sequence|escalation|application]
Question:
<text>

Options:
A) <text>
B) <text>
C) <text>
D) <text>

### <doc_id>::Q002
- priority: P1
- format: SHORT
- source_anchor: <path>#<section>
- tags: [must_do|sequence]
Question:
<text>

Answer length constraint:
- 1â€“3 lines

### <doc_id>::Q003
- priority: P0
- format: SCENARIO
- source_anchor: <path>#<section>
- tags: [application|policy|sequence]
Scenario:
<text>

Prompt:
<text>