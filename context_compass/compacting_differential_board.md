# compacting_differential_board (Knowledge-Test Ledger)

Purpose
- Canonical measurement ledger for post-compaction cycles.
- Track scored knowledge performance only (`knowledge_test` rows).

Non-negotiable intent
- This board does not attest performance by prose.
- Cycle success is determined by graded test evidence only.
- `knowledge_score: Not run` means cycle status is `incomplete`.

Canonical references
- `context_compass/CONTEXT_COMPACTION.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `context_compass/skill_check/skill_check_policy.md`

---

## Cycle Summary (required)

Each compaction/re-entry cycle must add one summary row.

| cycle_id | knowledge_score | knowledge_pass_rate | p0_miss_count | critical_p0_miss_count | policy_gate_miss_count | rank | status | delta_vs_prev |
|---|---:|---:|---:|---:|---:|---|---|---|
|  | 0 | 0.00 | 0 | 0 | 0 | C | open | baseline |

Definitions
- `knowledge_score`: score from graded answers, never from attestation prose.
- `knowledge_pass_rate`: passed required docs / tested required docs.
- `status`: `pass | fail | incomplete | open`.
  - `incomplete` if grading was not run.

---

## Row Types (required)

All detail rows must include `row_type`:
1) `knowledge_test` (primary scored evidence)

---

## Knowledge Test Rows (row_type: knowledge_test)

Each row is one graded question outcome.

Columns
1) `cycle_id`
2) `row_type` (`knowledge_test`)
3) `doc_id`
4) `skill_id`
5) `question_id`
6) `priority`
7) `agent_answer`
8) `correct_answer_ref`
9) `result` (`correct|incorrect|partial`)
10) `miss_class` (`concept|policy|sequence|scope|application`)
11) `severity` (`low|medium|high|critical`)
12) `remediation_hint`
13) `next_compaction_hint`
14) `status` (`open|improving|stable`)
15) `streak`

Table
| cycle_id | row_type | doc_id | skill_id | question_id | priority | agent_answer | correct_answer_ref | result | miss_class | severity | remediation_hint | next_compaction_hint | status | streak |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | knowledge_test |  |  |  | P0 |  |  | incorrect | policy | critical |  |  | open | 0 |

---

## Operating Rules (hard)

1) Score-grounded completion
- Do not mark a cycle successful without graded `knowledge_test` evidence.
- `knowledge_score: Not run` must remain `incomplete`.

2) Anti-cheat ordering
- `agent_answer` rows require blind submission before answer-key reads.

3) Required remediation linkage
- Every incorrect/partial question must include:
  - `remediation_hint`
  - `next_compaction_hint`

4) Adaptive shrink compatibility
- Stable streaks can reduce question volume for stable docs.
- P0 sentinel coverage remains permanent.

5) No performative compliance
- No fake "tests were run" claims.
- Evidence fields must map to actual sources or graded outputs.
