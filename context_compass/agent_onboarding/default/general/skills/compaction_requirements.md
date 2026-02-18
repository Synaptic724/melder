# compaction_requirements (REONBOARD + Skill-Gate-First Measurement Loop)

Purpose
- Define deterministic rules for what must happen after any compaction/handoff.
- Prevent policy drift by enforcing:
  1) minimum-read skill-gate onboarding,
  2) blind scored testing before answer-key access,
  3) targeted relearn from misses,
  4) fresh-cycle regeneration with adaptive shrink.

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
- user declares onboarding untrustworthy ("you're lying", "performative compliance", etc.)

Hard rule
- After a trigger event, **no tools, no edits, no execution, no planning** until:
  - Phase A is complete,
  - Phase B/C scored measurement is complete,
  - Phase D targeted relearn is complete,
  - Phase E certification is granted.

---

## Phase A - Re-Entry Bootstrap Reads (mandatory)

Goal
- Re-establish policy and workflow gates needed to run honest measurement.
- Do not perform a full role baseline reread in this phase.

Required bootstrap reads
1) `context_compass/AGENTS.MD`
2) `context_compass/agent_onboarding/default/general/skills/execution_contract.md`
3) `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
4) `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
5) `context_compass/skill_check/skill_check_policy.md`
6) `context_compass/skill_check/manifest/onboarding_manifest.yaml`
7) `context_compass/config/context_compass_config.yaml`
8) `context_compass/attention_board.md` + active ticket paths

Notes
- Manual source-document reads are required.
- Onboarding dump artifacts are non-compliant.
- Performative onboarding is forbidden.

---

## Phase B - `skill_gate_onboard` Minimum Readset (mandatory)

Goal
- Read only the minimum required to execute an unbiased scored cycle.

Required minimum readset
1) Active manifest metadata and required-doc/test mapping.
2) Active cycle test files in `skill_check/tests/**`.
3) Anti-cheat and grading rules in `skill_check_policy.md`.
4) Board schema required to record scored rows in
   `compacting_differential_board.md`.

Prohibited before blind submission
- Any file under `skill_check/test_answers/**`.
- Broad reread of under-test skill docs for memorization.
- Full role baseline reread prior to scoring.

Hard rule
- If test artifacts for required docs are missing:
  - set `BLOCKED: MISSING_TEST_ARTIFACTS`,
  - list exact missing paths,
  - stop and request user instructions.

---

## Phase C - Blind Skill Check + Grading (mandatory)

### C1) Cycle initialization
- Choose `cycle_id` (for example: `2026-02-18T01`).
- Declare `NO_ACTION_TAKEN_YET: true`.

### C2) Blind submission (anti-cheat)
1) Read `skill_check/tests/**` only.
2) Answer all required questions.
3) Submit in chat with:
   - `SKILL_CHECK_SUBMISSION`
   - `cycle_id`
   - all answers by `question_id`
   - `ANSWERS_UNREAD: true`

### C3) Grading (after submission only)
1) Read `skill_check/test_answers/**`.
2) Grade deterministically and compute:
   - per-doc scores
   - `knowledge_score`
   - `knowledge_pass_rate`
   - `p0_miss_count`
   - `critical_p0_miss_count`
   - `rank`
3) Run Diff-Onboarding parity measurement and compute:
   - `system_skill_doc_coverage`
   - `system_skill_parity_rate`
   - `policy_gate_miss_count`
4) Compute:
   - `fidelity_score = 100 * system_skill_parity_rate`
   - `global_score = 0.6*knowledge_score + 0.4*fidelity_score`

Hard rules
- Early read of `test_answers/**` sets `ANTI_CHEAT_VIOLATION: true` and blocks certification.
- A cycle with `knowledge_score: Not run` is `incomplete` and cannot pass.

---

## Phase D - Targeted Relearn (mandatory)

Goal
- Re-onboard only weak areas after scoring.

Protocol
1) Build failed/weak set from graded misses.
2) Re-read failed/weak docs only, plus required P0 dependencies.
3) Record relearn completion evidence and unresolved weak areas.
4) Convert misses to explicit `next_compaction_hint` entries.

Hard rule
- Do not replace targeted relearn with full-role baseline rereads unless the user explicitly directs it.

---

## Phase E - Certification Request (strict)

Only when Phase A/B/C/D gates pass:

Publish a `REONBOARD` attestation with:
- `REONBOARD: COMPLETE`
- `ROLE_SKILLS_READ` (resolved role chain)
- `SKILL_GATE_ONBOARD_READSET` (minimum-read files used pre-test)
- `FILES_REREAD` (at minimum: `attention_board.md` + active tickets)
- `READ_INTEGRITY_PROOF` (concise comprehension proof; no tool logs)
- `DIFF_ONBOARDING_REPORT` (coverage, parity, policy_gate_miss_count, top misses)
- `SKILL_GATE_REPORT` (knowledge_score, p0 misses, critical misses, global_score, rank, anti-cheat passed)
- `NO_ACTION_TAKEN_YET: true`

Then request user approval with exact token:
- `CERTIFY: APPROVED`

Hard rule
- Do not request certification when any gate is failing, incomplete, or blocked.

---

## Phase F - Post-Cert Updates (allowed only after `CERTIFY: APPROVED`)

1) Update measurement ledger
- Append cycle rows to `context_compass/compacting_differential_board.md`:
  - `row_type: knowledge_test` (primary scored evidence)
  - `row_type: fidelity_diff` (secondary parity diagnostics)
- Append cycle summary metrics with explicit pass/incomplete status.

2) Persist knowledge-gate state
- Write updated manifest to `context_compass/skill_check/manifest/onboarding_manifest.yaml`.
- Persist cycle report in `context_compass/skill_check/historical_test_results/`.

3) Regenerate and reset suite
- Run:
  - `python context_compass/skill_check/generate_bootstrap_suite.py --compaction-event`
- Keep one active cycle only:
  - prune stale `skill_check/tests/cycle_*`,
  - prune stale `skill_check/test_answers/cycle_*`,
  - prune stale `skill_check/historical_test_results/cycle_*.md`.

4) Adaptive shrink and reinforcement
- Failed/weak docs stay dense or increase.
- Stable docs may shrink only when streak thresholds are met.
- Permanent P0 sentinel coverage is never removed.

Hard rule
- Phase F is the only phase where this workflow writes files.
