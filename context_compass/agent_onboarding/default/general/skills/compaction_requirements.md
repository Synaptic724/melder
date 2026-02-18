

# compaction_requirements (REONBOARD + Diff-Onboarding + Skill Gate)

Purpose
- Define deterministic rules for what must happen after any compaction/handoff.
- Prevent policy drift by enforcing:
  1) full re-onboarding (required reads),
  2) semantic parity measurement (Diff-Onboarding), and
  3) knowledge competence measurement (Skill Check).

Non-negotiable optimization target
- Fidelity-first, not compactness-first.
- Compaction summary should be as rich as platform limits allow.
- Target compaction summary mix: **~90% system/skills/policy** and **~10% operational pointers**.

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/CONTEXT_COMPACTION.md`
- `context_compass/compacting_differential_board.md`
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/config/context_compass_config.yaml`

Trigger events (any => enforce REONBOARD)
- context compaction (platform summarization)
- agent handoff
- fresh-session reset
- user declares onboarding untrustworthy (â€œyouâ€™re lyingâ€, â€œperformative complianceâ€, etc.)

Hard rule
- After a trigger event, **no tools, no edits, no execution, no planning** until:
  - Phase A (reads) is complete, and
  - Phase B (measurement + knowledge gate) is complete, and
  - Phase C certification is granted.

---

## Phase A â€” Deterministic Re-Onboarding Reads (mandatory)

Goal
- Re-establish canonical policy state by rereading required docs.
- No shortcuts and no â€œI already know thisâ€.

Required entrypoints (always)
1) `context_compass/config/context_compass_config.yaml`
2) `context_compass/SKILLS.MD`
3) resolve the active profile/role and read the full SKILLS chain (parent-first)
4) read all **Active skills / Required baseline skills** in the resolved chain

Notes
- Manual source-document reads are required.
- Onboarding dump artifacts are non-compliant.
- Performative onboarding is forbidden.

---

## Phase B â€” Measurement + Knowledge Gate (mandatory)

This phase is the core of compaction hardening.

### B0) Cycle initialization (required)
- Choose `cycle_id` (date + suffix; e.g., `2026-02-18T01`).
- Declare:
  - `NO_ACTION_TAKEN_YET: true`

### B1) Manifest regeneration (required)
- Regenerate the onboarding manifest (in-memory first) per:
  `context_compass/skill_check/skill_check_policy.md`.

Must compute
- `total_required_docs`
- `total_required_for_certification_docs`
- missing test artifacts list:
  - any required entry missing `test_file` or `answer_file` blocks certification

Hard rule
- If required test artifacts are missing, set:
  - `BLOCKED: MISSING_TEST_ARTIFACTS`
  - provide exact missing paths
  - stop and ask the user for instructions
  - do NOT request certification

### B2) Test quality gate (required)
Before using any test set for scoring:
- Ensure `test_quality_score >= knowledge_gate.test_quality_threshold`.
- If below threshold:
  - mark tests invalid
  - regenerate tests (post-cert) until threshold passes
  - until then: certification blocked (knowledge gate not runnable)

### B3) Skill Check execution (anti-cheat; strict)
Goal
- Measure competence at applying rules, not box-checking.

Anti-cheat protocol (non-negotiable)
1) Read `skill_check/tests/**` only.
2) Answer all questions (every question in the active test set).
3) Submit answers in chat with:
   - `SKILL_CHECK_SUBMISSION`
   - `cycle_id`
   - all answers by question_id
   - `ANSWERS_UNREAD: true`
4) Only after submission may you read:
   - `skill_check/test_answers/**`
5) Grade deterministically and compute:
   - per-doc scores
   - `knowledge_score`
   - `knowledge_pass_rate`
   - `p0_miss_count`
   - `critical_p0_miss_count`
   - rank band

Hard rule
- Any early read of `test_answers/**` invalidates the cycle:
  - `ANTI_CHEAT_VIOLATION: true`
  - certification blocked
  - rerun required

### B4) Diff-Onboarding (semantic parity) execution
Goal
- Measure what survived compaction in the summary-state.

Protocol (strict order)
1) For each parity item:
   - record `pre_read_recall` AND `summary_state` BEFORE rereading the source
2) Read the source section and record `ground_truth_state`
3) Classify diff and severity
4) Compute fidelity metrics:
   - `system_skill_doc_coverage`
   - `system_skill_parity_rate`
   - `policy_gate_miss_count`

### B5) Global scoring + pass/fail (required)
Compute:
- `fidelity_score = 100 * system_skill_parity_rate`
- `global_score = 0.6*knowledge_score + 0.4*fidelity_score`

Pass gates
- must satisfy BOTH:
  - `compaction_diff_onboarding.gates.*`
  - `knowledge_gate.*`

If fail
- Certification blocked.
- Provide remediation list:
  - missing artifacts
  - failed doc_ids
  - top missed question_ids + remediation_hint
  - top fidelity misses + next_compaction_hint

---

## Phase C â€” Certification Request (strict)

Only when Phase A + Phase B gates PASS:

Publish a **REONBOARD attestation** message that includes:

- `REONBOARD: COMPLETE`
- `ROLE_SKILLS_READ` (resolved chain, parent-first)
- `FILES_REREAD` (at minimum: `attention_board.md` + active tickets)
- `READ_INTEGRITY_PROOF` (concise comprehension proof; NOT tool logs)
- `DIFF_ONBOARDING_REPORT` (system_skill_doc_coverage, parity_rate, policy_gate_miss_count, top misses)
- `SKILL_GATE_REPORT` (knowledge_score, p0_miss_count, critical_p0_miss_count, global_score, rank, anti-cheat passed)
- `NO_ACTION_TAKEN_YET: true`

Then request user approval with the exact token:
- `CERTIFY: APPROVED`

Hard rules
- Do NOT request certification if any gate is failing or blocked.
- Do NOT debate; show evidence + remediation.

---

## Phase D â€” Post-Cert Updates (allowed only after `CERTIFY: APPROVED`)

After certification is granted:

1) Update measurement ledger
- Append cycle rows to `context_compass/compacting_differential_board.md`:
  - `row_type: fidelity_diff`
  - `row_type: knowledge_test`
- Add cycle summary metrics section entry.

2) Persist knowledge-gate state
- Write the regenerated manifest to:
  - `context_compass/skill_check/manifest/onboarding_manifest.yaml`
- Write a cycle report to:
  - `context_compass/skill_check/historical_test_results/`

3) Test regeneration (next cycle targeting)
- Generate new test variants for:
  - failed docs
  - weak docs
  - any doc with policy/sequence misses
- Always keep minimal P0 sentinel questions for critical docs, even if stable.

4) Compaction improvement payload
- Convert top misses into `next_compaction_hint` lines and ensure they are ready
  to be embedded into the next compaction summary.

Hard rule
- Phase D is the only time file edits are allowed in this workflow.