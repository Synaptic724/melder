# skill_check_policy (Skill-Gate-First Scored Compaction Policy)

Status: active
Scope: post-compaction REONBOARD measurement loop + cycle maintenance
Owner: user authority (policy) + implementation agent (execution)

This policy defines a score-grounded compaction loop:
1) minimum-read `skill_gate_onboard`,
2) blind test submission,
3) deterministic grading,
4) targeted relearn,
5) fresh-cycle reset with adaptive shrink.

---

## 1) Core intent (non-negotiable)

1. Compaction is not a "small cache" optimization.
2. Compaction summaries should use as much budget as platform limits allow.
3. Summary mix target is **~90% system/skills/policy** and **~10% operational pointers**.
4. Post-compaction success is score-grounded:
   - primary evidence: `knowledge_test` scored rows,
   - secondary evidence: `fidelity_diff` parity diagnostics.
5. A cycle with `knowledge_score: Not run` is `incomplete`, not pass.

Compactness is a constraint. Fidelity + competence are objectives.

---

## 2) Artifacts (required)

Root subsystem
- `context_compass/skill_check/`

Required structure
- `context_compass/skill_check/tests/`
- `context_compass/skill_check/test_answers/`
- `context_compass/skill_check/historical_test_results/`
- `context_compass/skill_check/manifest/`

Canonical files
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`
- `context_compass/compacting_differential_board.md`

Templates
- `context_compass/skill_check/tests/test_template.md`
- `context_compass/skill_check/test_answers/answer_template.md`
- `context_compass/skill_check/historical_test_results/historical_results_template.md`

Config knobs
- `context_compass/config/context_compass_config.yaml` (`knowledge_gate.*`)

---

## 3) Operating model

### A) Bootstrap generation (one-time, post-cert)
If manifest/tests are missing:
1) generate manifest from canonical docs,
2) generate full test+answer suite,
3) enforce test quality threshold,
4) stop when bootstrap artifacts exist.

### B) Post-compaction re-entry (every cycle)
Before certification:
1) run `skill_gate_onboard` minimum-read stage,
2) run blind submission + grading,
3) run diff-onboarding parity measurement,
4) run targeted failed-doc relearn,
5) meet configured pass gates.

No exceptions.

---

## 4) Manifest requirements

### 4.1 Generation timing
Regenerate manifest at onboarding start from canonical docs:
- `context_compass/AGENTS.MD`
- `context_compass/SKILLS.MD`
- resolved role `SKILLS.MD` chain
- required baseline docs implied by that chain

### 4.2 Minimum fields
Each entry must include:
- `doc_id`
- `path`
- `doc_type` (`agents|skills|policy|behavior`)
- `priority` (`P0|P1|P2`)
- `required_for_certification`
- `test_file`
- `answer_file`
- `last_score`
- `last_cycle_id`
- `status` (`unrated|pass|fail`)
- `requires_retest`
- `stability_streak`

Hard rule
- Missing `test_file` or `answer_file` on any required entry blocks certification.

---

## 5) `skill_gate_onboard` contract (minimum-read gate)

Required pre-test reads:
1) active manifest metadata
2) active cycle tests
3) anti-cheat + grading rules
4) board schema for score recording

Forbidden pre-test reads:
- any `skill_check/test_answers/**`
- broad under-test skill-doc rereads for memorization
- full role baseline rereads prior to blind submission

---

## 6) Test authoring model

Hybrid mix (default):
- 70% MCQ
- 20% short
- 10% scenario

Question count baseline:
- small: 8
- medium: 12
- large/P0: 16

Coverage requirements per doc test:
1) must-do rule
2) must-not rule
3) sequence/order gate
4) escalation/certification gate
5) application scenario

Every question must be source-anchored.

---

## 7) Test quality gate

Rubric score out of 100:
1) coverage completeness: 25
2) source anchoring quality: 20
3) deterministic gradability: 20
4) behavioral realism: 15
5) anti-cheat robustness: 10
6) atomic clarity: 10

Gate:
- `test_quality_score >= knowledge_gate.test_quality_threshold`

If below threshold:
- regenerate tests/answers; block scoring until passing.

---

## 8) Anti-cheat protocol (strict)

1) Read tests only.
2) Submit all answers first (`ANSWERS_UNREAD: true`).
3) Read answer keys only after submission.
4) Grade deterministically.

Hard rule:
- early answer-key access => `ANTI_CHEAT_VIOLATION: true`, cycle fail, rerun required.

---

## 9) Scoring model

Per-doc skill score:
- `doc_skill_score = 0.7*P0 + 0.2*P1 + 0.1*P2`

Critical rule:
- any critical P0 miss => doc fail.

Global scores:
- `knowledge_score = weighted_average(doc_skill_score)`
- `fidelity_score = 100 * system_skill_parity_rate`
- `global_score = 0.6*knowledge_score + 0.4*fidelity_score`

Rank bands (default):
- S: >=95 and zero critical P0 misses
- A: 90-94 and zero critical P0 misses
- B: 80-89 and <=1 non-critical P0 miss
- C: <80 or any critical P0 miss

---

## 10) Certification gates

Certification blocked unless all pass:
1) `global_score >= knowledge_gate.global_pass_threshold`
2) `policy_gate_miss_count == 0`
3) `critical_p0_miss_count <= knowledge_gate.p0_critical_miss_max`
4) anti-cheat passed
5) required manifest entries have test+answer artifacts

Hard rules:
- do not request `CERTIFY: APPROVED` when blocked.
- `knowledge_score: Not run` blocks certification.

---

## 11) Diff board integration

`context_compass/compacting_differential_board.md` must include:
- `row_type: knowledge_test` (primary scored evidence)
- `row_type: fidelity_diff` (secondary parity evidence)

`knowledge_test` minimum fields:
1) `cycle_id`
2) `doc_id`
3) `skill_id`
4) `question_id`
5) `priority`
6) `agent_answer`
7) `correct_answer_ref`
8) `result` (`correct|incorrect|partial`)
9) `miss_class` (`concept|policy|sequence|scope|application`)
10) `severity`
11) `remediation_hint`
12) `next_compaction_hint`
13) `status`
14) `streak`

Cycle summary must include:
1) `knowledge_score`
2) `knowledge_pass_rate`
3) `p0_miss_count`
4) `fidelity_parity_rate`
5) `global_score`
6) explicit cycle status (`pass|fail|incomplete`)

---

## 12) Targeted relearn contract

After grading:
1) derive failed/weak docs from misses,
2) reread failed/weak docs + required P0 dependencies only,
3) record relearn evidence + unresolved weaknesses,
4) generate `next_compaction_hint` corrections from misses.

Full baseline rereads are not the default relearn path.

---

## 13) Fresh-cycle reset and adaptive shrink

After certification:
1) regenerate manifest + suite (`--compaction-event` flow),
2) keep one active cycle only (prune stale cycle dirs/files),
3) failed/weak docs remain dense or increase,
4) stable docs may shrink only after streak threshold,
5) never remove P0 sentinel minimum coverage.

---

## 14) Non-negotiable discipline

- no pre-cert edits outside measurement workflow.
- no bypass options for anti-cheat, grading, or gate checks.
- no performative "ran tests" claims.
- if blocked, publish `BLOCKED` with exact missing artifacts or failed gates.
