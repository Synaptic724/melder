

# skill_check_policy (Knowledge Gate + Fidelity Convergence)

Status: active
Scope: post-compaction re-entry (REONBOARD) + steady-state skill competence enforcement
Owner: user authority (policy) + implementation agent (execution)

This document defines a fidelity-first compaction + knowledge-gate system.
It is designed to reduce policy drift after compaction by enforcing:
1) measured semantic parity (Diff Board), AND
2) measured skill competence (Skill Check tests).

---

## 1) Core intent (non-negotiable)

1. Compaction is not a â€œsmall cacheâ€ optimization.
2. Compaction summary should be as rich as platform limits allow.
3. Target mix in compaction summary is **~90% system/skills/policy** and **~10% operational pointers**.
4. The Diff Board is not the cache itself. It is the measurement ledger for cache fidelity and policy-gate integrity.
5. The Skill Check is not the cache itself. It is the measurement ledger for competence and correct gate execution.
6. The system must improve over cycles by measuring weaknesses, targeting them in next compaction, then retesting.

Compactness is a constraint. Fidelity is the objective.

---

## 2) Artifacts (required)

Root subsystem
- `context_compass/skill_check/`

Required structure
- `context_compass/skill_check/tests/`
- `context_compass/skill_check/test_answers/`
- `context_compass/skill_check/historical_test_results/`
- `context_compass/skill_check/manifest/`

Canonical manifest file (required)
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`

Templates (required)
- `context_compass/skill_check/tests/test_template.md`
- `context_compass/skill_check/test_answers/answer_template.md`
- `context_compass/skill_check/historical_test_results/historical_results_template.md`

Measurement ledger (required)
- `context_compass/compacting_differential_board.md`
  - MUST include both `fidelity_diff` rows and `knowledge_test` rows.

Config knobs (required)
- `context_compass/config/context_compass_config.yaml` (`knowledge_gate.*`)

---

## 3) Operating model: what happens when

### A) First-time install / bootstrap (one-time, post-cert)
If the `skill_check/` subsystem has just been added or the manifest/tests are missing:
- You still follow standard ONBOARD + certification gating (no pre-cert edits).
- After the user provides `CERTIFY: APPROVED`, your **first** post-cert action MUST be:
  1) Generate and write the onboarding manifest.
  2) Generate and write the full initial test set + answer set for all required manifest entries.
  3) Run the test quality rubric and regenerate until `test_quality_score >= threshold`.
  4) Stop. Do not begin normal work until the bootstrap artifacts exist.

This ensures that future compaction re-entry can run the knowledge gate deterministically.

### B) Post-compaction re-entry (every compaction/handoff)
After any compaction/handoff:
- REONBOARD is mandatory.
- Re-entry runs in **Diff-Onboarding + Skill-Check mode**.
- Before requesting certification, you MUST:
  1) measure semantic parity (Diff Board protocol), AND
  2) run the knowledge gate tests (Skill Check protocol), AND
  3) meet configured gates.

No exceptions.

---

## 4) Manifest requirement (yes, implement it)

### 4.1 Canonical file
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`

### 4.2 Manifest generation timing
- The manifest MUST be regenerated **at each onboarding start** (ONBOARD or REONBOARD) from canonical docs:
  - `context_compass/AGENTS.MD`
  - `context_compass/SKILLS.MD`
  - resolved role `SKILLS.MD` chain (parent-first)
  - required baseline skill/policy/behavior docs implied by that chain

No manual curation. The manifest is derived.

### 4.3 Deterministic manifest algorithm (required)
At onboarding start:

1) Resolve active profile/role from:
   - `context_compass/config/context_compass_config.yaml` (`profiles.active_profile`)
   - `context_compass/SKILLS.MD` (roles map)
2) Build the required doc set `D_required`:
   - Always include (system root):
     - `AGENTS.MD`
     - `config/context_compass_config.yaml`
     - `SKILLS.MD`
   - Include the resolved role `SKILLS.MD` chain (the SKILLS files themselves).
   - Include every path under **Active skills** / **Required baseline skills** in each resolved SKILLS file.
3) Normalize + dedupe paths (canonical form):
   - Use forward slashes in the manifest `path` field.
   - Keep paths relative to `context_compass/` (no leading `./`).
4) Assign `doc_type` deterministically:
   - `agents`: any `**/AGENTS.MD`
   - `skills`: any `**/SKILLS.MD` OR `**/skills/**`
   - `policy`: any `**/policies/**` OR files containing certification/tooling gates
   - `behavior`: any `**/behavioral_guidelines/**` OR workflow/communication behavior docs
   - If ambiguous, classify as `policy` when it defines MUST/DO NOT gates; otherwise `skills`.
5) Assign `priority` deterministically (default rules; override only in config):
   - `P0`:
     - root `AGENTS.MD`
     - `execution_contract.md` (even though behavioral, it shapes enforcement of gates)
     - certification docs
     - compaction requirements + diff onboarding docs
     - `policy_skills.md`
   - `P1`:
     - core workflow/ticketing/context docs that control correctness
   - `P2`:
     - nice-to-have guidance; style; optional heuristics
6) Assign `required_for_certification`:
   - Default: `true` for all `P0` and `P1` docs.
   - Default: `false` for `P2` docs (may be tested opportunistically).
   - This default may be tightened in config.

### 4.4 Required manifest fields (minimum schema)
Each entry MUST include at least:

- `doc_id` (stable ID)
- `path` (canonical repo path relative to `context_compass/`)
- `doc_type` (`agents|skills|policy|behavior`)
- `priority` (`P0|P1|P2`)
- `required_for_certification` (bool)
- `test_file` (path under `skill_check/tests/`)
- `answer_file` (path under `skill_check/test_answers/`)
- `last_score` (0â€“100; default 0 for unrated)
- `last_cycle_id` (string or null)
- `status` (`unrated|pass|fail`)
- `requires_retest` (bool)

Hard rule
- Missing `test_file` OR missing `answer_file` for any `required_for_certification: true` entry:
  - blocks post-compaction certification
  - triggers remediation (see section 10)

### 4.5 Stable `doc_id` rule (deterministic)
`doc_id` MUST be stable across cycles unless the doc path changes.

Default rule (recommended):
- `doc_id = UPPERCASE(path) with '/' -> '__' and '.' -> '_'`
Example:
- path: `agent_onboarding/default/general/skills/compaction_requirements.md`
- doc_id: `AGENT_ONBOARDING__DEFAULT__GENERAL__SKILLS__COMPACTION_REQUIREMENTS_MD`

---

## 5) Test authoring model per skill/doc

### 5.1 Hybrid format (required)
- Not MCQ-only and not long-form-only.

Default mix (configurable):
- 70% MCQ (4 options, single best)
- 20% short answer (1â€“3 lines)
- 10% scenario/application

### 5.2 Question count by doc size (required)
Per doc test question count:
- Small: 8
- Medium: 12
- Large or critical: 16

Doc size classification (deterministic default):
- Large: priority `P0` OR doc LOC >= `codex.read_loc_max` OR doc defines multi-step gates
- Medium: typical skills/policy docs
- Small: short, single-purpose guidance docs

### 5.3 Priority distribution (required)
Default mix (configurable):
- 50% P0
- 35% P1
- 15% P2

Hard rule
- Every `P0` doc MUST include enough `P0` questions to detect gate drift.

### 5.4 Required question coverage per doc test (non-negotiable)
Every skill/doc test MUST include:

1) at least one **must-do rule** question (MUST)
2) at least one **must-not-do rule** question (DO NOT)
3) at least one **sequence/order gate** question (ordering constraint)
4) at least one **escalation/certification gate** question (what blocks, what requires user approval)
5) at least one **application scenario** question (apply rule to an example)

### 5.5 Source anchoring (required)
Every question MUST be anchored to canonical doc sections.

Minimum anchor payload per question:
- `source_path`
- `source_section` (header/anchor)
- (optional) `source_excerpt` (<= 25 words)

Hard rule
- If you cannot anchor a question to a doc section, do not include it.

---

## 6) Test + answer file format (deterministic)

### 6.1 Stable question IDs (required)
Each question MUST have a stable `question_id` within the doc:

- Format: `<doc_id>::Q###`
- Example: `AGENTS_MD::Q001`

### 6.2 Canonical templates
- Tests MUST follow: `skill_check/tests/test_template.md`
- Answers MUST follow: `skill_check/test_answers/answer_template.md`

Hard rule
- If a test deviates from the template, it is invalid.

---

## 7) Test quality rubric (must run before using tests)

### 7.1 Rubric categories (score out of 100)
Score each generated test set:

1) Coverage completeness: 25
2) Source anchoring quality: 20
3) Deterministic gradability: 20
4) Behavioral realism: 15
5) Anti-cheat robustness: 10
6) Atomic clarity (one claim per question): 10

### 7.2 Gate (non-negotiable)
- `test_quality_score >= knowledge_gate.test_quality_threshold` is required.

If below threshold:
- regenerate the test set (and answer key) until it passes.
- Do not proceed to knowledge scoring with a low-quality test set.

---

## 8) Anti-cheat protocol (strict)

Core rule
- The agent MUST NOT read `skill_check/test_answers/**` until AFTER full answers are submitted.

Evaluation sequencing (required)
1) Read `tests/*` only.
2) Submit full answers (all questions).
3) Post attestation:
   - `ANSWERS_UNREAD: true`
4) Only then may you read `test_answers/*` to grade.
5) Any early access to `test_answers/*` invalidates the cycle and forces rerun.

Hard rule
- If early access occurred: declare `ANTI_CHEAT_VIOLATION: true`, set cycle status FAIL, and restart the cycle.

---

## 9) Scoring and ranking

### 9.1 Per-doc skill score (required)
Compute per-doc score:

- `P0_score = percent_correct(P0 questions)`
- `P1_score = percent_correct(P1 questions)`
- `P2_score = percent_correct(P2 questions)`

Then:
- `doc_skill_score = 0.7*P0_score + 0.2*P1_score + 0.1*P2_score`

Critical rule
- Any **critical** P0 miss => doc FAIL regardless of total score.

### 9.2 Knowledge score (global)
Aggregate across required docs:

Default aggregation (deterministic):
- `knowledge_score = weighted_average(doc_skill_score, weight_by_priority)`
  - `P0 docs weight = 1.0`
  - `P1 docs weight = 0.7`
  - `P2 docs weight = 0.3` (if included)

### 9.3 Fidelity score (global)
Use Diff Board semantic parity metrics:

Default:
- `fidelity_score = 100 * system_skill_parity_rate`

### 9.4 Global score (required)
- `global_score = 0.6*knowledge_score + 0.4*fidelity_score`

### 9.5 Rank bands (required)
Rank bands (default):

- S: >=95 and zero critical P0 misses
- A: 90â€“94 and zero critical P0 misses
- B: 80â€“89 and <=1 non-critical P0 miss
- C: <80 or any critical P0 miss

---

## 10) Certification gates (strict)

Post-compaction certification is blocked unless all are true:

1) `global_score >= knowledge_gate.global_pass_threshold`
2) `policy_gate_miss_count == 0` (from fidelity diff rows; policy-gate distortions/drops)
3) `p0_critical_miss_count <= knowledge_gate.p0_critical_miss_max`
4) required consecutive pass cycles threshold respected
5) anti-cheat passed (no early answers access)
6) required manifest entries have tests + answers present

If blocked:
- Provide an explicit remediation list:
  - missing tests/answers
  - doc_ids failed
  - top incorrect question_ids + remediation_hint
  - top fidelity misses + next_compaction_hint

Hard rule
- Do NOT request `CERTIFY: APPROVED` when blocked.

---

## 11) Diff Board integration (required)

`context_compass/compacting_differential_board.md` MUST store both row types:

- `row_type: fidelity_diff`
- `row_type: knowledge_test`

Knowledge test row fields (minimum)
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

Cycle summary section MUST include:
1) system-skill coverage
2) fidelity parity rate
3) knowledge pass rate
4) P0 miss count
5) rank
6) delta vs previous cycle

---

## 12) Compaction cycle behavior (required)

Cycle 1 (first onboarding / bootstrap)
1) Build full manifest.
2) Generate full tests and answers for all required entries.
3) Run quality rubric and fix until pass.
4) Wait for compaction/handoff.
5) After compaction, run evaluation and grade.
6) Record baseline scores + weaknesses.

Cycle 2
1) Regenerate tests (new variants) for failed/weak skills.
2) Include P0 sentinel checks for all critical docs regardless of previous pass.
3) Retest and grade.
4) Update board with score deltas + remediation status.

Cycle N
1) Keep focused retests on weak areas.
2) Keep permanent minimal P0 sentinels.
3) Shrink total test volume only when stability streaks justify it.
4) Never skip policy-gate validation.

---

## 13) How to run one full post-compaction cycle (operator guide)

Pre-condition: compaction/handoff occurred.

0) STOP. No work actions. Enter REONBOARD.

1) Phase A (reads)
- Follow `agent_onboarding/default/general/skills/compaction_requirements.md` Phase A exactly.

2) Phase B (measurement + knowledge gate)
- Choose `cycle_id`.
- Regenerate manifest (in memory) and compute required test set.
- Answer tests WITHOUT reading answer keys.
- Post `SKILL_CHECK_SUBMISSION` in chat with:
  - cycle_id
  - all answers
  - `ANSWERS_UNREAD: true`
- Read answer keys and grade.
- Produce `SKILL_GATE_REPORT` in chat with:
  - knowledge_score, p0_miss_count, critical_miss_count, rank
  - top misses + remediation_hint
- Produce `DIFF_ONBOARDING_REPORT` in chat with:
  - system_skill_doc_coverage, parity_rate, policy_gate_miss_count
  - top misses + next_compaction_hint
- Compute `global_score` and pass/fail.

3) Phase C (attestation + certification request)
- Only if gates pass:
  - post REONBOARD attestation including DIFF + SKILL_GATE evidence
  - request `CERTIFY: APPROVED`

4) Phase D (post-cert updates)
- Write:
  - updated manifest to `skill_check/manifest/onboarding_manifest.yaml`
  - cycle rows into `compacting_differential_board.md` (both row types)
  - historical cycle report into `skill_check/historical_test_results/`
  - next-cycle test generation artifacts as needed

---

## 14) Non-negotiable discipline

- No pre-cert edits (except Phase D after user approval).
- No policy bypass options.
- No performative compliance (no fake â€œran testsâ€ claims).
- If anything is missing: declare `BLOCKED`, list what is missing, and ask the user for instructions.