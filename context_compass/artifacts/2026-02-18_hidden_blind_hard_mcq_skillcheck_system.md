# Artifact: Hidden Blind Hard-MCQ Skill-Check System

Created: 2026-02-18T17:27:51Z
Owner: codex
Status: active

## Objective
Implement a hard multiple-choice testing system where:
1) question pools are large and difficult,
2) exam answers are submitted blindly in JSON,
3) grading is performed against sealed answer keys,
4) score/rank outputs are deterministic and auditable.

## User-directed requirements
- Build a new test generator.
- Save answer truth records to a location the agent should not inspect before submission.
- Build a grader that uses that sealed location and submission JSON.
- MCQ only; no short or long answers.
- Randomize question order and option order.
- Generate a pool with at least 10x current question volume.
- Use one exam question per 100 LOC for required docs.
- Use difficult options: three close deterministic lies plus one truth.
- Add new skills and edit existing skills/policies to enforce this flow.

## Implemented architecture
1) Pool builder
- `context_compass/skill_check/build_hard_mcq_pool.py`
- Outputs:
  - public pool: `skill_check/question_pool/hard_mcq_pool.jsonl`
  - sealed truth mapping: `skill_check/.sealed/pool_truth_keys.jsonl`

2) Exam generator
- `context_compass/skill_check/generate_hard_mcq_exam.py`
- Uses required docs from manifest and applies `ceil(LOC/100)` quota per doc.
- Outputs:
  - exam markdown: `skill_check/tests/cycle_<id>/hard_mcq_exam.md`
  - submission template: `skill_check/submissions/cycle_<id>_answers_template.json`
  - sealed per-cycle key: `skill_check/.sealed/exams/cycle_<id>_answer_key.json`

3) Grader
- `context_compass/skill_check/grade_hard_mcq_submission.py`
- Inputs:
  - submission JSON
  - sealed per-cycle answer key
- Outputs:
  - markdown report and JSON report in `skill_check/historical_test_results/`

## Skill/policy integration surfaces
- `skill_check/skill_check_policy.md` (rewritten for hard-MCQ + sealed flow)
- `agent_onboarding/default/general/skills/compaction_requirements.md` (updated)
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md` (updated)
- Added skills:
  - `agent_onboarding/default/general/skills/hard_mcq_skillcheck_protocol.md`
  - `agent_onboarding/default/general/skills/hard_mcq_question_pool_design.md`

## Anti-cheat contract
- `.sealed/**` is private grading material.
- Pre-submission reads of `.sealed/**` are policy violations.
- Grading must be script-driven, not manual key review.

## Open follow-up
- Optional future hardening can move sealed keys outside workspace or behind user-only runtime secrets.
