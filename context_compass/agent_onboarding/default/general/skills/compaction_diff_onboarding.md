# compaction_diff_onboarding (Skill-Gate-First Diff-Onboarding Mode)

Purpose
- Preserve decision-critical context across compactions using two measured loops:
  1) **Knowledge loop (primary):** blind scored answers vs answer keys.
  2) **Fidelity loop (secondary):** semantic parity between compaction summary
     state and canonical docs.

Non-negotiable optimization target
- Fidelity-first compaction content with score-grounded post-compaction
  certification.
- Target compaction summary mix: **~90% system/skills/policy** and
  **~10% operational pointers**.

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/CONTEXT_COMPACTION.md`
- `context_compass/compacting_differential_board.md`
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`
- `context_compass/config/context_compass_config.yaml`

Trigger
- Run after any compaction event, handoff event, or fresh-session reset where
  context continuity is not trusted.

Hard rule
- No tooling, edits, execution, or planning until REONBOARD attestation is
  complete and user certification is granted.

---

## Artifacts (required)

Scored evidence artifacts
- `context_compass/compacting_differential_board.md`
  - `row_type: knowledge_test` (question-level scored evidence)
  - `row_type: fidelity_diff` (parity diagnostics)

Skill-check artifacts
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`
- `context_compass/skill_check/tests/**`
- `context_compass/skill_check/test_answers/**` (locked until answer submission)
- `context_compass/skill_check/historical_test_results/**`

---

## Cycle algorithm (required)

### Step 0 - Enter measured mode
- Declare `NO_ACTION_TAKEN_YET: true`.
- Choose `cycle_id` (for example: `2026-02-18T01`).

### Step 1 - `skill_gate_onboard` (minimum readset)
Read only what is required for unbiased testing:
1) active manifest metadata
2) active test files
3) anti-cheat/grading policy
4) board schema for scored row recording

Do not read:
- answer keys
- broad under-test skill docs
- full role baseline docs before blind submission

### Step 2 - Blind skill check submission
1) Read `skill_check/tests/**` only.
2) Answer all required questions.
3) Submit `SKILL_CHECK_SUBMISSION` with `ANSWERS_UNREAD: true`.
4) Only after submission, read `skill_check/test_answers/**` and grade.

Compute:
- per-doc score
- `knowledge_score`
- `knowledge_pass_rate`
- `p0_miss_count`
- `critical_p0_miss_count`
- `rank`

### Step 3 - Diff-Onboarding parity measurement
For each parity item:
1) capture `summary_state` before reread
2) reread source and capture `ground_truth_state`
3) classify diff:
   - `diff_type`: retained_exact | retained_paraphrase | distorted | dropped
   - `distortion_class`: value | scope | dependency | sequence | policy | none
   - `severity`: low | medium | high | critical

Compute:
- `system_skill_doc_coverage`
- `system_skill_parity_rate`
- `policy_gate_miss_count`
- `fidelity_score = 100 * system_skill_parity_rate`
- `global_score = 0.6*knowledge_score + 0.4*fidelity_score`

### Step 4 - Targeted relearn (post-score)
1) Build failed/weak doc set from graded misses.
2) Reread failed/weak docs only plus required P0 dependencies.
3) Produce `next_compaction_hint` entries for misses.

### Step 5 - Gates and outcome
Pass requires both:
- diff gates from `compaction_diff_onboarding.gates.*`
- knowledge gates from `knowledge_gate.*`

Hard outcomes:
- `knowledge_score: Not run` => cycle is `incomplete`.
- early answer-key access => `ANTI_CHEAT_VIOLATION: true` and fail.
- if fail/incomplete: certification blocked with remediation list.
- if pass: include both reports in REONBOARD attestation and request
  `CERTIFY: APPROVED`.

---

## Adaptation rules (required)

Knowledge misses drive next cycle density:
1) `policy` or `sequence` misses => severity at least `high` (often `critical`).
2) repeated misses => tighter question variants next cycle.
3) failed/weak docs remain dense or increase.

Stability-driven shrink:
1) stable docs may shrink only after configured streak threshold.
2) P0 sentinel questions are permanent and never removed.

Fidelity misses improve compaction summary:
1) `dropped` => raise priority and make claim more atomic.
2) `distorted` => split into smaller must/do-not claims with explicit ordering.

---

## Required pre-cert reporting

Before requesting certification after compaction/handoff, publish:
1) `SKILL_GATE_REPORT` (primary scored evidence)
2) `DIFF_ONBOARDING_REPORT` (secondary parity evidence)

Either missing blocks certification.
