# Task: Implement Phase Component CProfile Harness

## Metadata
- Task ID: TASK-2026-02-14-implement-phase-component-cprofile-harness
- Story: STORY-2026-02-14-phase-component-cprofile-harness
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Implement a deterministic component test harness that executes phase groups via
direct spell facades (no scheduler orchestration) and emits profile/timing
output aligned with the discovery contract.

## Scope Boundaries
- In scope:
- Add component harness test module for phase-group direct-call execution.
- Implement toggle matrix and profile-output schema from discovery.
- Out of scope:
- Optimization changes to runtime phase logic.
- Interpretation/ranking of outputs.

## Steps / Checklist
- [x] Implement harness fixture/build helpers and deterministic target selection.
- [x] Implement group executors for `1-4`, `5-7 conduit`, `5-7 local`, `8-11 conduit`.
- [x] Implement summary and optional `[PROFILE]` pstats output.
- [x] Update linked story/task notes with evidence and execution guidance.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- New component harness test module with direct-call phase profiling support.
- Deterministic run path for baseline measurement tasks.

## Files / Paths Impacted
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`
- `context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md`
- `context_compass/tasks/2026-02-14_implement_phase_component_cprofile_harness_task.md`

## Validation
- Ran:
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`
- Result:
  - `1 passed, 3 warnings in 0.33s`
- Output artifact:
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt`

## Risks / Rollback Notes
- Risk: Harness accidentally calls scheduler paths and pollutes measurements.
- Rollback: Keep direct-call-only execution and remove scheduler-dependent code.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Harness build and validation are complete: all phase-group paths run and pytest passes after replacing invalid `spell.crafter` access with `_ensure_crafter()`-based access.
  EVIDENCE: tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:150-209, tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:278-398, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:51-52
  IMPACT: Phase baseline measurement execution can proceed with a stable harness in this branch.
  NEXT: Record measured outputs into the four phase baseline discovery tasks and unblock backlog ranking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented component harness module with direct-call group runners for `1-4`, `5-7 conduit`, `5-7 local`, and `8-11`, including cold/warm variants and standardized `[PHASE_PROFILE]`/`[PROFILE]` output.
  EVIDENCE: tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:1
  IMPACT: Baseline measurement task can now run and capture real phase metrics.
  NEXT: Execute the harness test with `pytest -q -s` and record measured outputs into phase baseline tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Existing component tests use an autouse Aether reset fixture and a `_make_spellbook()` helper with `phase_scheduler_workers_per_spellbook=1`, which is the correct deterministic pattern for the harness.
  EVIDENCE: tests/component/melder/spellbook/test_spellbook_component_spell.py:16, tests/component/melder/spellbook/test_spellbook_component_spell.py:40, tests/component/melder/spellbook/spell_crafter/phases/test_spellbook_component_spell_crafter_phase5.py:23, tests/component/melder/spellbook/spell_crafter/phases/test_spellbook_component_spell_crafter_phase5.py:45
  IMPACT: Harness implementation should reuse this fixture/config style to stay consistent with component-tier conventions.
  NEXT: Implement harness module under `tests/component/melder/spellbook/` using the same fixture pattern.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Harness discovery contract is review-complete and specifies direct-call group sequencing plus profile output shape.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_component_cprofile_harness_task.md:34
  IMPACT: Implementation can proceed without further contract ambiguity.
  NEXT: Implement the harness module in component tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Execution task is implemented and validated. The harness run output is captured
at `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt`.
Next step is baseline measurement ticket updates and backlog unblocking.
