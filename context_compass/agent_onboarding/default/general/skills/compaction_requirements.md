# compaction_requirements (REONBOARD + Hard MCQ Measurement Loop)

Purpose
- Define deterministic behavior after compaction/handoff.
- Enforce minimum-read skill-gate onboarding and score-grounded grading.

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/skill_check/manifest/onboarding_manifest.yaml`

Trigger events (any => enforce REONBOARD)
- context compaction
- agent handoff
- fresh-session reset
- user distrust challenge on onboarding integrity

Hard rule
- After trigger: no implementation action until measured re-entry gates complete.

---

## Phase A - Re-entry bootstrap reads (mandatory)

Required reads
1) `context_compass/AGENTS.MD`
2) `agent_onboarding/default/general/skills/execution_contract.md`
3) `agent_onboarding/default/general/skills/compaction_requirements.md`
4) `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
5) `skill_check/skill_check_policy.md`
6) `skill_check/manifest/onboarding_manifest.yaml`
7) `config/context_compass_config.yaml`
8) `attention_board.md` + active ticket paths

---

## Phase B - skill_gate_onboard minimum readset (mandatory)

Goal
- Read only enough to execute a blind hard-MCQ cycle.

Required minimum readset
1) Active manifest metadata.
2) Active exam markdown (`skill_check/tests/cycle_<id>/hard_mcq_exam.md`).
3) Submission schema in `skill_check/submissions/README.md`.
4) Grading contract in `skill_check/skill_check_policy.md`.

Prohibited before submission
- Any file under `skill_check/.sealed/**`.
- Any file under legacy `skill_check/test_answers/**`.
- Broad reread of under-test docs for memorization.

---

## Phase C - blind submission + grading (mandatory)

### C1) Initialize cycle
- Generate or receive `cycle_id`.
- Declare `NO_ACTION_TAKEN_YET: true`.

### C2) Blind submission
1) Read exam markdown only.
2) Produce JSON answers using required schema.
3) Save submission under `skill_check/submissions/cycle_<id>_answers.json`.
4) Post in chat:
   - `SKILL_CHECK_SUBMISSION`
   - `cycle_id`
   - `submission_path`
   - `ANSWERS_UNREAD: true`

### C3) Scripted grading
1) Run:
   - `python context_compass/skill_check/grade_hard_mcq_submission.py --cycle-id <id> --submission <path>`
2) Do not manually inspect sealed key files.
3) Capture outputs:
   - total correct/incorrect/unanswered
   - score
   - rank
   - per-doc misses

Hard rules
- Sealed key reads before submission => `ANTI_CHEAT_VIOLATION: true`.
- A cycle without grader output is `incomplete`.

---

## Phase D - targeted relearn (mandatory)

1) Build weak-doc list from grader misses.
2) Re-read failed/weak docs only plus required P0 dependencies.
3) Record remediation and unresolved weak areas.
4) Promote misses to `next_compaction_hint` entries.

---

## Phase E - certification request (strict)

Publish REONBOARD attestation with:
- `REONBOARD: COMPLETE`
- `ROLE_SKILLS_READ`
- `SKILL_GATE_ONBOARD_READSET`
- `FILES_REREAD`
- `READ_INTEGRITY_PROOF`
- `SKILL_GATE_REPORT` (score, rank, misses, anti-cheat status)
- `NO_ACTION_TAKEN_YET: true`

Then request user token:
- `CERTIFY: APPROVED`

---

## Phase F - post-cert updates

1) Refresh hard-MCQ pool:
   - `python context_compass/skill_check/build_hard_mcq_pool.py --multiplier 10`
2) Generate fresh exam:
   - `python context_compass/skill_check/generate_hard_mcq_exam.py --cycle-id <next_id>`
3) Preserve sealed key files as local private artifacts.
4) Persist grading report under `historical_test_results/`.

Hard rule
- Only Phase F writes new cycle generation artifacts.
