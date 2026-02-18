

# compacting_differential_board (Fidelity + Knowledge Ledger)

Purpose
- Provide a living measurement ledger for:
  1) **Fidelity parity**: what system/skills/policy knowledge survived compaction.
  2) **Knowledge competence**: whether the agent can correctly apply the rules (gates, sequences, must-do/must-not).

Non-negotiable intent
- This board is NOT the cache.
- This board measures the cache (compaction summary state) against canonical repo truth.
- The system improves over cycles by:
  measure â†’ correct next compaction â†’ retest â†’ converge.

Canonical references
- `context_compass/CONTEXT_COMPACTION.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `context_compass/skill_check/skill_check_policy.md`

---

## Cycle Summary (required)

Each compaction/re-entry cycle MUST add one cycle summary row.

| cycle_id | system_skill_coverage | fidelity_parity_rate | knowledge_pass_rate | p0_miss_count | policy_gate_miss_count | knowledge_score | fidelity_score | global_score | rank | delta_vs_prev | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
|  | 0/0 (0.00) | 0.00 | 0.00 | 0 | 0 | 0 | 0 | 0 | C | 0 | open |

Definitions
- `system_skill_coverage`: docs/items covered Ã· required (system/skills/policy domain)
- `fidelity_parity_rate`: retained_exact + retained_paraphrase Ã· total (system/skills/policy)
- `knowledge_pass_rate`: docs with status=pass Ã· docs tested (required_for_certification)
- `p0_miss_count`: total incorrect/partial P0 questions across the cycle
- `policy_gate_miss_count`: number of fidelity diffs classified as policy-gate distortions/drops
- `global_score = 0.6*knowledge_score + 0.4*fidelity_score`
- `delta_vs_prev`: summary of change (+/-) vs previous cycle (fidelity + knowledge + global)

---

## Row Types (required)

All rows MUST include `row_type`:

1) `row_type: fidelity_diff`
- semantic parity measurement between compaction summary state and canonical docs

2) `row_type: knowledge_test`
- question-level knowledge gate evidence (tests)

---

## Fidelity Diff Rows (row_type: fidelity_diff)

Each row is one atomic retention item (not a paragraph blob).

Columns
1. `cycle_id`
2. `row_type` (always `fidelity_diff`)
3. `claim_id` (stable ID like `C-P0-001`)
4. `domain` (`system_skill` | `operational`)
5. `priority` (`P0` | `P1` | `P2`)
6. `source_doc_path`
7. `source_doc_title`
8. `evidence_path` (path:line_start-line_end)
9. `pre_read_recall`
10. `ground_truth`
11. `diff_type` (`retained_exact` | `retained_paraphrase` | `distorted` | `dropped`)
12. `distortion_class` (`value` | `scope` | `dependency` | `sequence` | `policy` | `none`)
13. `severity` (`low` | `medium` | `high` | `critical`)
14. `impact`
15. `next_compaction_hint`
16. `status` (`open` | `improving` | `stable`)
17. `streak_retained`

Table
| cycle_id | row_type | claim_id | domain | priority | source_doc_path | source_doc_title | evidence_path | pre_read_recall | ground_truth | diff_type | distortion_class | severity | impact | next_compaction_hint | status | streak_retained |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | fidelity_diff |  | system_skill | P0 |  |  |  |  |  |  |  |  |  |  | open | 0 |

---

## Knowledge Test Rows (row_type: knowledge_test)

Each row is one question result.

Columns (minimum required by policy)
1. `cycle_id`
2. `row_type` (always `knowledge_test`)
3. `doc_id`
4. `skill_id` (can equal doc_id if 1:1)
5. `question_id`
6. `priority`
7. `agent_answer`
8. `correct_answer_ref` (path#section or path:line)
9. `result` (`correct` | `incorrect` | `partial`)
10. `miss_class` (`concept` | `policy` | `sequence` | `scope` | `application`)
11. `severity` (`low` | `medium` | `high` | `critical`)
12. `remediation_hint`
13. `next_compaction_hint`
14. `status` (`open` | `improving` | `stable`)
15. `streak`

Table
| cycle_id | row_type | doc_id | skill_id | question_id | priority | agent_answer | correct_answer_ref | result | miss_class | severity | remediation_hint | next_compaction_hint | status | streak |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | knowledge_test |  |  |  | P0 |  |  | incorrect | policy | critical |  |  | open | 0 |

---

## Operating rules (hard)

1) No performative compliance
- Rows must be grounded in doc-backed truth.
- No fake â€œI ran testsâ€ claims.

2) System-skill dominance
- The board prioritizes system/skills/policy parity over operational routing.

3) Next-compaction hints are mandatory
- Every miss (fidelity or knowledge) must generate a concrete hint.

4) Streak rules (default)
- When retained/pass streak >= 3, status may move to `stable`.
- Stable does not mean â€œignoreâ€; P0 sentinels remain permanent.