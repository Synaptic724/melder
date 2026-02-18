# Task: Discover Failed-Doc Targeted Relearn Contract

## Metadata
- Task ID: TASK-2026-02-18-failed-doc-targeted-relearn-discovery
- Story: STORY-2026-02-18-skill-gate-first-compaction-discovery
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:53:27Z
- Updated: 2026-02-18T17:07:51Z

## Objective
Define how graded misses produce a mandatory failed-doc reread set and targeted
re-onboarding pass before the next cycle.

## Ticket Contract
- ENTRY_GATE: scored-cycle schema discovery is complete.
- EXECUTION_BOUNDARY: relearn gating docs, manifest fields, and cycle reporting
  behavior only.
- DEPENDENCIES: graded `knowledge_test` evidence and miss classification data.
- EXIT_GATE: explicit failed-doc reread algorithm with guardrails and required
  artifacts is documented.
- FAILURE_ESCALATION: raise `CONFLICT` if reread requirements break anti-cheat
  sequencing or certification gate ordering.

## Scope Boundaries
- In scope:
  - failed-doc set derivation from misses
  - mandatory reread + evidence contract
  - manifest field update expectations (`status`, `last_score`,
    `requires_retest`, `stability_streak`)
- Out of scope:
  - initial blind-test onboarding
  - next-cycle shrink algorithm internals

## State Transition Event
- from_state: ready
- to_state: ready
- transition_reason: queued pending score-schema discovery completion.

## Steps / Checklist
- [x] Define failure/weakness thresholds that trigger targeted rereads.
- [x] Define mandatory reread set composition (failed docs + P0 dependencies).
- [x] Define required evidence recording for relearn completion.
- [x] Define how relearn updates manifest and board statuses.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Discovery spec for targeted relearn routing and state updates.

## Files / Paths Impacted
- `tickets/tasks/2026-02-18_failed_doc_targeted_relearn_discovery_task.md`
- (discovery references only)
  - `skill_check/skill_check_policy.md`
  - `skill_check/manifest/onboarding_manifest.yaml`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "Cycle 2|Cycle N|failed|weak|sentinel|Shrink total test volume" context_compass/skill_check/skill_check_policy.md`
  - `rg -n "last_score|status|requires_retest|stability_streak" context_compass/skill_check/manifest/onboarding_manifest.yaml`

## Risks / Rollback Notes
- Over-broad reread sets reduce the intended cycle-size convergence.
- Under-broad reread sets risk repeating misses without correction.

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
  CLAIM: Policy intent already expects focused retests and permanent P0
    sentinels, with shrink only when stability streaks justify it.
  EVIDENCE:
  - skill_check/skill_check_policy.md:383-392
  - skill_check/skill_check_policy.md:345-359
  IMPACT: Discovery should convert this intent into explicit failed-doc reread
    gating and state-update rules.
  NEXT: define failed-doc derivation and reread evidence contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:07:51Z
  TYPE: FACT
  CLAIM: Targeted relearn is now explicit policy: failed/weak docs plus
    required P0 dependencies are reread after grading, replacing pre-test
    full-role reread behavior.
  EVIDENCE:
  - agent_onboarding/default/general/skills/compaction_requirements.md:126-137
  - agent_onboarding/default/general/skills/compaction_diff_onboarding.md:94-98
  - skill_check/skill_check_policy.md:241-249
  IMPACT: Relearning scope is now auditably tied to scored misses and supports
    convergence toward smaller cycles.
  NEXT: close cycle reset/shrink task and sync routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task outcome captured and implemented: targeted failed-doc relearn behavior is
now policy-enforced across compaction and skill-check docs.
