# Task: Rank Phase12 Codegen Hotspot Operations

## Metadata
- Task ID: TASK-2026-02-18-codegen-phase12-hotspot-op-priority-map
- Story: STORY-2026-02-18-codegen-baseline-and-hotspot-map
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T10:23:20Z
- Updated: 2026-02-18T10:24:50Z

## Objective
Produce a ranked list of concrete phase12/codegen operations using pinned deep
profile evidence from mixed and override routes.

## Ticket Contract
- ENTRY_GATE: baseline mean task notes exist and story is active.
- EXECUTION_BOUNDARY: profile-driven hotspot mapping for `creation_context`, `phase12_*`, and `patch_maps`.
- DEPENDENCIES: pinned deep profile JSON and source symbol reads.
- EXIT_GATE: ranked ops list with evidence and first implementation target selected.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if profiler evidence conflicts with route priority policy.

## Scope Boundaries
- In scope:
  - `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
  - `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- Out of scope:
  - spellspace-specific route decisions
  - branch-level structural experiments

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: route baseline is available and hotspot mapping is now executable.

## Steps / Checklist
- [x] Extract mixed + override top cumulative functions from pinned deep profile.
- [x] Filter to phase12/codegen symbols and map to concrete source lines.
- [x] Rank ops by route weight and cumulative profile contribution.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Ranked phase12/codegen ops list.
- First implementation target recommendation.

## Files / Paths Impacted
- `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`
- `tickets/tasks/2026-02-18_codegen_phase12_hotspot_op_priority_map_task.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "_execute_with_overrides|_phase12_executor|patch_maps|warm_override|warm_mixed" benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`

## Risks / Rollback Notes
- Risk: front-door meld overhead could obscure executor-level costs.
  - Mitigation: prioritize symbols that are phase12/codegen specific in ranked list.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T10:23:20Z
  TYPE: FACT
  CLAIM: Override-route hotspots consistently include `CreationContext._execute_with_overrides`, generated `<melder_phase12_overrides_executor>._phase12_executor`, and patch-map apply/target-resolution functions.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:427-434
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:595-616
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:665-665
  IMPACT: First implementation tranche should target override path internals before low-yield root micro-ops.
  NEXT: Rank these ops against mixed-route no-overrides executor costs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:23:20Z
  TYPE: FACT
  CLAIM: Mixed-route profile surfaces generated no-overrides executor plus `_get_existing_creation` and `_construct_spell_instance` as core phase12/codegen costs.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:217-336
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1054-1289
  IMPACT: No-overrides generated lane remains a secondary target after override-route dispatch work.
  NEXT: Publish final ranked op order into the parent story notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:24:50Z
  TYPE: DECISION
  CLAIM: First implementation target is `CreationContext._execute_with_overrides` dispatch path, ahead of patch-map and no-overrides executor work.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:427-434
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:595-616
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:565-739
  IMPACT: Next code-change tranche can stay narrow while attacking the highest override-path hotspot.
  NEXT: Create and execute a focused implementation task for override dispatch micro-optimizations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task is active and focused on ranking concrete phase12/codegen symbols from
pinned deep profiles. Next step is finalizing op order and selecting first
implementation target.
