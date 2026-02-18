

# Historical Test Results Template (skill_check)

File naming (recommended)
- `context_compass/skill_check/historical_test_results/cycle_<cycle_id>.md`

Purpose
- Preserve cycle-by-cycle evidence of:
  - knowledge competence
  - compaction fidelity parity
  - rank progression
  - remediation status

---

## Cycle metadata
- cycle_id: <cycle_id>
- generated_at_utc: <timestamp>
- active_profile: <profile>
- resolved_role_chain:
  - <role>
  - <role>
- compaction_event: true|false
- notes: <optional>

---

## Cycle summary (required)
- system_skill_doc_coverage: <x>/<y> (= <rate>)
- system_skill_parity_rate: <rate>
- policy_gate_miss_count: <n>
- knowledge_score: <0-100>
- knowledge_pass_rate: <rate>
- p0_miss_count: <n>
- critical_p0_miss_count: <n>
- fidelity_score: <0-100>
- global_score: <0-100>
- rank: S|A|B|C
- delta_vs_previous_cycle:
  - fidelity_parity_rate: <+/->
  - knowledge_score: <+/->
  - global_score: <+/->

---

## Failed / weak docs (required if any)
| doc_id | priority | last_score | status | top_misses (question_id) | remediation_hint | next_compaction_hint |
|---|---|---:|---|---|---|---|
|  | P0 |  | fail |  |  |  |

---

## Fidelity misses (policy-gate first)
| item_id | source_doc_path | source_section | diff_type | distortion_class | severity | next_compaction_hint |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

---

## Knowledge misses (P0 first)
| doc_id | question_id | priority | miss_class | severity | remediation_hint | next_compaction_hint |
|---|---|---|---|---|---|---|
|  |  | P0 | policy | critical |  |  |

---

## Remediation plan (required if blocked)
- <bullet list of next steps>