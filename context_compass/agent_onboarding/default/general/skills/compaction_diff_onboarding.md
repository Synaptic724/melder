

# compaction_diff_onboarding (Diff-Onboarding + Skill-Check Mode)

Purpose
- Preserve decision-critical context across compactions by enforcing two measured loops:
  1) **Fidelity loop (Diff Board):** semantic parity between compaction summary state and canonical docs.
  2) **Knowledge loop (Skill Check):** competence at applying the rules (gates, sequences, must-do/must-not).

Non-negotiable optimization target
- Fidelity-first, not compactness-first.
- Compaction summary should be as rich as platform limits allow.
- Target compaction summary mix: **~90% system/skills/policy** and **~10% operational pointers**.

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/CONTEXT_COMPACTION.md`
- `context_compass/compacting_differential_board.md`
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`
- `context_compass/config/context_compass_config.yaml`

Trigger
- Run this mode after any:
  - compaction event
  - handoff event
  - fresh-session reset where the model context is not continuous

Hard rule
- No tool use, edits, execution, or planning until the REONBOARD attestation is complete and the user grants certification.

---

## Artifacts (required)

Fidelity artifacts
- `context_compass/compacting_differential_board.md`
  - stores `row_type: fidelity_diff` items

Knowledge artifacts
- `context_compass/skill_check/manifest/onboarding_manifest.yaml` (generated)
- `context_compass/skill_check/tests/**`
- `context_compass/skill_check/test_answers/**` (LOCKED until answer submission)
- `context_compass/skill_check/historical_test_results/**`

---

## Cycle algorithm (required)

### Step 0 â€” Enter measured mode
- Declare `NO_ACTION_TAKEN_YET: true`.
- Choose a `cycle_id` (date-based + suffix; e.g., `2026-02-18T01`).

### Step 1 â€” Regenerate onboarding manifest (in-memory first)
1) Regenerate the manifest from canonical docs per:
   `context_compass/skill_check/skill_check_policy.md`.
2) Determine:
   - required docs set
   - required_for_certification set
3) Identify missing test artifacts:
   - missing `test_file` or `answer_file` for required entries blocks certification.

### Step 2 â€” Run Skill Check (knowledge gate)
Goal: measure competence and policy-gate correctness **without** answer-key leakage.

Protocol (anti-cheat; strict)
1) Read `skill_check/tests/**` only.
2) Answer every question (all docs included in the cycle set).
3) Submit answers (in chat) and include:
   - `ANSWERS_UNREAD: true`
4) Only after submission may you read `skill_check/test_answers/**` to grade.
5) Grade deterministically, compute:
   - per-doc `doc_skill_score`
   - `knowledge_score`
   - `p0_miss_count` + `critical_p0_miss_count`
   - rank band
6) Convert misses into next-compaction reinforcement:
   - each incorrect/partial question MUST produce a `next_compaction_hint`
     that can be embedded into the next compaction summary.

### Step 3 â€” Run Diff-Onboarding (fidelity loop)
Goal: measure semantic parity between compaction summary state and canonical docs.

Protocol (strict order)
1) For each target doc section/item:
   - record `pre_read_recall` AND `summary_state` BEFORE rereading sources
2) Reread source doc section(s) and record `ground_truth_state`
3) Classify:
   - `diff_type`: retained_exact | retained_paraphrase | distorted | dropped
   - `distortion_class`: value | scope | dependency | sequence | policy | none
   - `severity`: low | medium | high | critical
4) Compute cycle metrics (see below)
5) Convert misses into `next_compaction_hint` corrections

### Step 4 â€” Compute cycle metrics (required)
Fidelity metrics (system-first)
- `system_skill_doc_coverage`
- `system_skill_parity_rate`
- `policy_gate_miss_count`

Knowledge metrics
- `knowledge_score`
- `knowledge_pass_rate`
- `p0_miss_count`
- `critical_p0_miss_count`

Global metrics
- `fidelity_score = 100 * system_skill_parity_rate`
- `global_score = 0.6*knowledge_score + 0.4*fidelity_score`
- `rank`

Operational sanity check (secondary)
- `resume_correctness`: were the first next-actions still correct after re-entry?

### Step 5 â€” Gates and outcomes (strict)
Pass requires:
- Diff gates from `compaction_diff_onboarding.gates.*` AND
- Knowledge gates from `knowledge_gate.*`

If fail:
- Certification is blocked.
- Provide an explicit remediation list.
- Do NOT offer bypass options.

If pass:
- Include both reports in the REONBOARD attestation and request `CERTIFY: APPROVED`.

---

## Adaptation rules (required)

These rules drive compaction improvement, not intuition.

Fidelity diffs
1) If `dropped`:
   - raise priority (toward P0)
   - simplify and re-state as a more atomic item
2) If `distorted`:
   - split into smaller atomic claims
   - prefer MUST/DO NOT phrasing, explicit scope, explicit sequence
3) If retained for `streak >= 3`:
   - may demote from P0 â†’ P1 if NOT a policy gate
4) If a source doc changes materially:
   - reset affected items to `open` and streak = 0

Knowledge misses
1) If miss_class = `policy` or `sequence`:
   - mark severity at least `high` (often `critical`)
   - generate explicit next-compaction hint with ordering language
2) If repeated misses for the same concept:
   - generate a tighter, more explicit question next cycle
   - add a sentinel question variant (P0) until streak stabilizes

---

## Required reporting (pre-cert)

Before requesting certification after compaction/handoff, you MUST publish:

1) `DIFF_ONBOARDING_REPORT` (system-skill parity evidence)
2) `SKILL_GATE_REPORT` (knowledge-gate evidence, anti-cheat passed)

Both are required. Either missing blocks certification.