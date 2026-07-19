# Task: Add Spell Invalidate Revalidation Helper
- Completed: 2026-05-16T17:35:29Z
- Summary: Closed after landing the dynamic-only `Spell.invalidate_spell(...)`
  helper, routing mutation invalidation through it, and validating the focused
  spell unit file.

## Metadata
- Task ID: TASK-2026-05-16-add-spell-invalidate-revalidation-helper
- Story:
- Epic: EPIC-2026-05-11-add-overrides-enabled-configuration-and-spell-gate
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-16T17:09:51Z
- Updated: 2026-05-16T17:35:29Z

## Objective
Add one spell-local helper that invalidates the spell for full next-meld
revalidation by clearing spell-local runtime state and delegating the lineage
gate change into `SpellSystemStates`.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved adding a reusable `Spell` helper
  instead of keeping duplicated inline invalidation logic.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell.py`
  - `src/melder/utilities/interfaces/ispell.py`
  - `tests/unit/melder/spellbook/test_spell.py`
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/tickets/tasks/2026-05-16_add_spell_invalidate_revalidation_helper_task.md`
- DEPENDENCIES:
  - existing mutation-override invalidation path in `Spell`
  - `SpellSystemStates.mark_structural_change(...)`
  - next-meld structural + deferred runtime resolution gates in `Meld`
- EXIT_GATE: `Spell` exposes a documented invalidate helper, mutation-override
  callers use it, and focused unit coverage proves the helper clears spell-local
  runtime state and marks the lineage gated for revalidation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the helper needs to
  broaden beyond spell-local invalidation into transfer-only disable semantics.

## Scope Boundaries
- In scope:
  - one spell-local invalidation helper
  - interface contract update
  - focused spell unit coverage
- Out of scope:
  - transfer disable semantics
  - later Phase 10-12 override pruning
  - broader spellbook/conduit invalidation redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the helper landed on `Spell` and `ISpell`, mutation
  callers now delegate to it, and the focused spell unit file passed.

## Steps / Checklist
- [x] Confirm the intended invalidation semantics with the user.
- [x] Route this exact helper slice on the board.
- [x] Add the helper to `Spell` with rich contract docstring.
- [x] Update `ISpell` to expose the helper.
- [x] Replace local duplicate invalidation code in mutation-override methods.
- [x] Add focused unit tests for the helper behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- `Spell.invalidate_spell_for_revalidation(...)` helper
- updated `ISpell` contract
- focused spell unit coverage for the helper

## Files / Paths Impacted
- `src/melder/spellbook/spell.py`
- `src/melder/utilities/interfaces/ispell.py`
- `tests/unit/melder/spellbook/test_spell.py`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/tickets/tasks/2026-05-16_add_spell_invalidate_revalidation_helper_task.md`

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/spellbook/test_spell.py`
- Result:
  - `84 passed, 2 warnings`

## Risks / Rollback Notes
- Risk: helper semantics accidentally drift into transfer-only hard-disable.
  Mitigation: keep the helper on the lighter `gated + structure_changed` path
  and avoid touching transfer code.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No silent semantics drift between spell-local invalidation and transfer disable.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-16T17:09:51Z
  TYPE: FACT
  CLAIM: The runtime already separates transfer-only hard disable from normal
    rebuild semantics. Transfer uses `disabled + transfer_in_progress`
    temporarily, then lifts the lineage into `gated + structure_changed`. The
    requested spell-local helper should model that lighter post-transfer
    posture, not the temporary transfer-only hard-disable.
  EVIDENCE:
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:184-221`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:518-551`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:995-1033`
  - `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:476-510`
  IMPACT: The helper should clear spell-local runtime state and mark the
    lineage structurally gated for rebuild without reusing transfer-only
    disable mechanics.
  NEXT: implement the helper on `Spell`, then route mutation-override callers
    through it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T17:17:37Z
  TYPE: FACT
  CLAIM: A full next-meld rebuild needs two independent levers. Structural
    gating alone reruns phases 1-4, but the deferred runtime plan path only
    reruns when `resolution_required` is true and `resolution_complete` is
    false. So the helper has to pair `mark_structural_change(...)` with local
    resolution-flag invalidation, not just clear the `CreationContext`.
  EVIDENCE:
  - `src/melder/aether/conduit/meld/meld.py:338-340`
  - `src/melder/aether/conduit/meld/meld.py:662-706`
  - `src/melder/aether/conduit/meld/meld.py:917-964`
  - `src/melder/spellbook/spell_crafter/spell_crafter.py:2789-2814`
  IMPACT: `invalidate_spell(...)` should clear spell-local runtime context,
    set `resolution_complete=False`, set `resolution_required=True`, and then
    mark the lineage structurally gated for revalidation.
  NEXT: implement the helper with those semantics and update mutation callers
    to use it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T17:18:48Z
  TYPE: FACT
  CLAIM: The helper is now implemented on `Spell` and exposed on `ISpell`.
    The implementation centralizes spell-local invalidation by clearing the
    cached `CreationContext`, forcing `resolution_complete=False` and
    `resolution_required=True`, and delegating the lineage gate into
    `SpellSystemStates.mark_structural_change(...)`. The mutation-overlay
    entrypoints now call that helper instead of open-coding the invalidation
    steps.
  EVIDENCE:
  - `src/melder/spellbook/spell.py:963-1015`
  - `src/melder/spellbook/spell.py:1658-1705`
  - `src/melder/spellbook/spell.py:1709-1752`
  - `src/melder/utilities/interfaces/ispell.py:241-258`
  IMPACT: The override lane now has one reusable spell-local invalidation seam
    that later override-posture and mutation callers can share without copying
    line-by-line revalidation logic.
  NEXT: run the focused spell unit test file and confirm the helper behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T17:19:19Z
  TYPE: MEASURE
  CLAIM: The focused spell unit file passed after landing the helper. The new
    helper tests verify the default reason, explicit reason override, and the
    no-states-registry fallback path, while the existing mutation-override
    tests still pass against the delegated helper path.
  EVIDENCE:
  - `tests/unit/melder/spellbook/test_spell.py:868-904`
  - validation_result: `python -m pytest -q tests/unit/melder/spellbook/test_spell.py` -> `83 passed, 2 warnings`
  IMPACT: The spell-local invalidation helper is ready for review and can now
    be reused by later override-posture work without reopening this basic seam.
  NEXT: return the helper slice for review and decide whether the next override
    tranche should wire this helper into override-posture changes too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T17:25:39Z
  TYPE: FACT
  CLAIM: The helper contract is now stricter. `Spell.invalidate_spell(...)`
    requires dynamic mode, and the focused unit file now covers that rejection
    path alongside the earlier default, explicit-reason, and no-states-registry
    cases.
  EVIDENCE:
  - `src/melder/spellbook/spell.py:963-1019`
  - `src/melder/utilities/interfaces/ispell.py:241-258`
  - `tests/unit/melder/spellbook/test_spell.py:868-919`
  IMPACT: The helper now matches the current override/mutation lane posture:
    this is a dynamic-runtime feature, not a general static spell utility.
  NEXT: return the tightened helper for review and confirm whether later
    override-posture callers should route through the same dynamic-only seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T17:25:39Z
  TYPE: MEASURE
  CLAIM: The focused spell unit file stayed green after adding the dynamic-mode
    requirement to `invalidate_spell(...)`.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/spellbook/test_spell.py` -> `84 passed, 2 warnings`
  IMPACT: The stricter contract is implemented and covered without breaking the
    existing spell helper and mutation-path tests.
  NEXT: keep the task in review and use the helper as the base seam for later
    override-posture invalidation work if accepted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task adds one spell-local invalidation helper for the override lane. The
helper should centralize the existing pattern of clearing spell-local runtime
state and marking the lineage gated for the next meld-driven rebuild.
