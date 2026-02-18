# Task: Discover Skill-Gate Onboarding Minimum Readset Contract

## Metadata
- Task ID: TASK-2026-02-18-skill-gate-onboarding-minimum-readset-discovery
- Story: STORY-2026-02-18-skill-gate-first-compaction-discovery
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T16:53:27Z
- Updated: 2026-02-18T17:07:51Z

## Objective
Define a deterministic minimum-read `skill_gate_onboard` stage at compaction
exit so testing is measured before full role reread and answer-key access.

## Ticket Contract
- ENTRY_GATE: story is active and attention board routes to this task.
- EXECUTION_BOUNDARY: compaction onboarding/policy docs and task/story/epic
  routing files only.
- DEPENDENCIES: current compaction onboarding algorithm and anti-cheat policy.
- EXIT_GATE: minimum readset + exclusions + sequence constraints documented with
  implementation-ready notes.
- FAILURE_ESCALATION: raise `CONFLICT` if onboarding gates mandate rereads that
  invalidate blind-measurement intent.

## Scope Boundaries
- In scope:
  - `compaction_diff_onboarding.md` and `skill_check_policy.md` sequencing map
  - explicit minimum readset proposal before blind testing
  - explicit exclusion list (docs under test, answer keys)
- Out of scope:
  - code/policy implementation edits beyond discovery notes
  - scoring schema redesign (covered by sibling task)

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: first discovery lane activated to establish measurement-
  first onboarding sequence.

## Steps / Checklist
- [x] Map current post-compaction step order from canonical docs.
- [x] Identify what must be read to run tests safely without bias.
- [x] Propose `skill_gate_onboard` minimum readset and forbidden pre-test reads.
- [x] Define handoff contract to blind test submission phase.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Discovery note with:
  - minimum required readset before testing
  - prohibited readset before testing
  - order constraints and gating language

## Files / Paths Impacted
- `tickets/tasks/2026-02-18_skill_gate_onboarding_minimum_readset_discovery_task.md`
- (discovery references only)
  - `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
  - `skill_check/skill_check_policy.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "Step 1|Step 2|Step 3|No tool use" context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
  - `rg -n "Anti-cheat|answers|test_answers" context_compass/skill_check/skill_check_policy.md`

## Risks / Rollback Notes
- If minimum readset is underspecified, measurement flow may become brittle.
- If minimum readset is overspecified, test measurement may remain inflated.

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
  CLAIM: Current compaction diff onboarding orders manifest regeneration before
    skill-check execution but does not define a dedicated minimum-read onboarding
    mode that protects test-blindness from broad rereads.
  EVIDENCE:
  - agent_onboarding/default/general/skills/compaction_diff_onboarding.md:54-81
  - agent_onboarding/default/general/skills/compaction_diff_onboarding.md:24-30
  IMPACT: A discovery-defined minimum readset is needed to avoid contaminating
    post-compaction measurement.
  NEXT: extract required vs prohibited pre-test reads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T17:07:51Z
  TYPE: FACT
  CLAIM: Skill-gate-first contract is now implemented in policy docs, replacing
    pre-test full-reread behavior with minimum-read onboarding and targeted
    post-score relearn sequencing.
  EVIDENCE:
  - agent_onboarding/default/general/skills/compaction_requirements.md:61-90
  - agent_onboarding/default/general/skills/compaction_requirements.md:126-137
  - agent_onboarding/default/general/skills/compaction_diff_onboarding.md:54-71
  IMPACT: Compaction re-entry now measures blind test performance before
    relearning, which matches the requested convergence loop.
  NEXT: hand off to schema realignment and cycle-lifecycle tasks for closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task outcome captured and implemented: minimum-read skill-gate onboarding is now
the enforced pre-test stage in compaction policy surfaces.
