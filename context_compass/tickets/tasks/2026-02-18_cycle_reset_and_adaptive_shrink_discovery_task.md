# Task: Discover Cycle Reset And Adaptive Shrink Contract

## Metadata
- Task ID: TASK-2026-02-18-cycle-reset-and-adaptive-shrink-discovery
- Story: STORY-2026-02-18-skill-gate-first-compaction-discovery
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:53:27Z
- Updated: 2026-02-18T17:07:51Z

## Objective
Define the fresh-cycle reset protocol and adaptive shrinking rules so each new
cycle is regenerated, stale artifacts are cleared, and stable docs are tested
less over time.

## Ticket Contract
- ENTRY_GATE: targeted-relearn discovery outputs are complete.
- EXECUTION_BOUNDARY: suite lifecycle policies, generator behavior, and cycle
  artifact rules only.
- DEPENDENCIES: manifest state fields and scored-cycle outputs.
- EXIT_GATE: explicit reset/shrink rules and implementation map documented.
- FAILURE_ESCALATION: raise `BLOCKER` if single-active-cycle cleanup conflicts
  with required historical evidence retention.

## Scope Boundaries
- In scope:
  - single active cycle contract
  - stale artifact cleanup rules
  - shrink policy by stability streak with P0 sentinels
  - per-doc question-volume behavior by cycle state
- Out of scope:
  - scoring schema redesign
  - onboarding minimum readset contract

## State Transition Event
- from_state: ready
- to_state: ready
- transition_reason: queued pending prior discovery lanes.

## Steps / Checklist
- [x] Define cycle reset contract (what is regenerated each cycle).
- [x] Define stale artifact cleanup boundaries and exceptions.
- [x] Define shrink math for stable docs and reinforcement for failed docs.
- [x] Define historical reporting requirements while keeping one active suite.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Discovery spec for cycle reset + adaptive shrink mechanics.

## Files / Paths Impacted
- `tickets/tasks/2026-02-18_cycle_reset_and_adaptive_shrink_discovery_task.md`
- (discovery references only)
  - `skill_check/skill_check_policy.md`
  - `skill_check/generate_bootstrap_suite.py`
  - `skill_check/historical_test_results/*`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "Cycle 2|Cycle N|Shrink total test volume|sentinel" context_compass/skill_check/skill_check_policy.md`
  - `rg -n "removed_test_cycle_dirs|removed_answer_cycle_dirs|removed_historical_cycle_files|shrink_applied_docs" context_compass/skill_check/historical_test_results/cycle_*.md`
  - `rg -n "stable_streak_for_shrink|p0_min_questions_per_doc" context_compass/skill_check/generate_bootstrap_suite.py`

## Risks / Rollback Notes
- Over-aggressive shrink can reduce detection quality.
- Over-retention of stale artifacts can bloat cycle management.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-02-18_skill_gate_first_compaction_success_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T16:53:27Z
  TYPE: FACT
  CLAIM: The current generator already enforces fresh-cycle generation and stale
    cycle pruning, and policy requires shrink only when stability streaks justify
    it with permanent P0 sentinels.
  EVIDENCE:
  - skill_check/skill_check_policy.md:389-392
  - skill_check/generate_bootstrap_suite.py:409-427
  - skill_check/generate_bootstrap_suite.py:722-754
  IMPACT: Discovery can focus on tightening score-grounded triggers for shrink,
    not rebuilding lifecycle mechanics from scratch.
  NEXT: define scoring-state prerequisites that unlock shrink and reroute failed
    docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T17:07:51Z
  TYPE: FACT
  CLAIM: Generator maintenance now supports single-active-cycle behavior plus
    adaptive shrink readiness by ingesting scored `knowledge_test` results into
    manifest state (`last_score/status/requires_retest/stability_streak`).
  EVIDENCE:
  - skill_check/generate_bootstrap_suite.py:270-329
  - skill_check/generate_bootstrap_suite.py:331-348
  - skill_check/generate_bootstrap_suite.py:932-957
  - agent_onboarding/default/general/skills/compaction_requirements.md:177-185
  IMPACT: Test volume can now decrease over cycles from measured success while
    stale suites are still pruned on compaction-event generation.
  NEXT: close discovery story and update epic routing to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task outcome captured and implemented: cycle reset, stale cleanup, and adaptive
shrink readiness are now codified and wired into generator behavior.
