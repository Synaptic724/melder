# Task: fix spell crafter validation strategy optional spell cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-spell-crafter-validation-strategy-optional-spell-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T11:18:51Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current SpellCrafter validation-strategy mypy cluster by tightening
optional spell/frame/current-id narrowings and correcting any stale helper
typing that no longer matches the real strategy contracts.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded validation-strategy mypy cluster
  under `spell_crafter/validation/strategies`.
- EXECUTION_BOUNDARY:
  - directly implicated strategy files only:
    - `src/melder/spellbook/spell_crafter/validation/strategies/spellmap_shape_validation_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/self_validation_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/resolution_frame_presence_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/required_holes_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/parameter_policy_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/dangling_dependency_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/circular_dependency_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py`
    - `src/melder/spellbook/spell_crafter/validation/strategies/annotation_shape_guard_strategy.py`
  - directly implicated support contracts only if truth requires them:
    - `src/melder/spellbook/spell_crafter/validation/spell_validation_context.py`
    - `src/melder/utilities/interfaces/ispell.py`
    - `src/melder/utilities/interfaces/iaethericframeconfiguration.py`
- DEPENDENCIES:
  - current SpellCrafter validation context contract
  - no casts, no shims, no fake local protocols
- EXIT_GATE:
  - the targeted strategy-file mypy cluster is gone
  - any support-surface changes remain truthful and bounded
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the optionality is not local
  narrowing debt but a real public contract ambiguity

## Scope Boundaries
- In scope:
  - local strategy narrowings around optional spell/current/frame config
  - truthful support-contract adjustments if genuinely required
- Out of scope:
  - unrelated SpellCrafter or blueprint mypy debt
  - broader interface redesign beyond directly implicated seams

## Steps / Checklist
- [ ] inspect the strategy cluster and classify local vs contract truth issues
- [ ] patch the bounded strategies first
- [ ] patch support contracts only if the local fixes prove insufficient
- [ ] rerun targeted mypy on the strategy cluster
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded SpellCrafter validation-strategy typing fix

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/validation/strategies/spellmap_shape_validation_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/self_validation_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/resolution_frame_presence_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/required_holes_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/parameter_policy_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/dangling_dependency_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/circular_dependency_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/annotation_shape_guard_strategy.py`
- only if required by truthful fix:
  - `src/melder/spellbook/spell_crafter/validation/spell_validation_context.py`
  - `src/melder/utilities/interfaces/ispell.py`
  - `src/melder/utilities/interfaces/iaethericframeconfiguration.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spell_crafter\validation\strategies`

## Risks / Rollback Notes
- Medium risk. The likely fixes are local guards/narrowings, but one or two
  support contracts may still be lying about optionality.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T11:18:51Z
  TYPE: FACT
  CLAIM: The new spell-crafter strategy cluster looks mostly local. The bulk of
    the errors are direct uses of `context.spell` or `spell.spell_index.current`
    without proving they are non-None first, plus one likely stale helper in
    `binding_resolution_cycle_strategy` where a generic `object` parameter is
    carrying spell-specific assumptions.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/validation/strategies/spellmap_shape_validation_strategy.py:1-108
  - src/melder/spellbook/spell_crafter/validation/strategies/self_validation_strategy.py:1-57
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:1-183
  - src/melder/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:1-285
  IMPACT: This should mostly collapse via local early-return/fail-fast
    narrowings rather than widening public interfaces everywhere.
  NEXT: read the remaining implicated strategy files end-to-end, then patch the
    bounded local narrowings first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:18:51Z
  TYPE: FACT
  CLAIM: The support-contract change was small and truthful. `SpellValidationContext`
    now types `spell` as a required `ISpell`, which matches the constructor
    contract that already rejects `None`. The remaining optionality was handled
    locally where it is real: `spell_index.current` can still be absent, and
    frame-configuration reads can still fail in the contract-provider strategy.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/validation/spell_validation_context.py:58-108
  - src/melder/spellbook/spell_crafter/validation/strategies/self_validation_strategy.py:45-58
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:70-94
  - src/melder/spellbook/spell_crafter/validation/strategies/circular_dependency_strategy.py:54-79
  IMPACT: The cluster can be solved without widening public interfaces beyond
    the one context field that was already guaranteed by construction.
  NEXT: record the bounded validation result and close the lane to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T11:18:51Z
  TYPE: MEASURE
  CLAIM: The targeted validation-strategy cluster is green. The selected
    strategy files show no file-local mypy output, and the full spell-crafter
    validation unit ring passes after restoring the existing best-effort
    config-read behavior in `ContractProviderPresenceStrategy`.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/validation/spell_validation_context.py:1-133
  - src/melder/spellbook/spell_crafter/validation/strategies/spellmap_shape_validation_strategy.py:1-108
  - src/melder/spellbook/spell_crafter/validation/strategies/self_validation_strategy.py:1-59
  - src/melder/spellbook/spell_crafter/validation/strategies/resolution_frame_presence_strategy.py:1-69
  - src/melder/spellbook/spell_crafter/validation/strategies/required_holes_strategy.py:1-68
  - src/melder/spellbook/spell_crafter/validation/strategies/parameter_policy_strategy.py:1-131
  - src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py:1-97
  - src/melder/spellbook/spell_crafter/validation/strategies/dangling_dependency_strategy.py:1-79
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:1-183
  - src/melder/spellbook/spell_crafter/validation/strategies/circular_dependency_strategy.py:1-105
  - src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py:1-133
  - src/melder/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:1-280
  - src/melder/spellbook/spell_crafter/validation/strategies/annotation_shape_guard_strategy.py:1-164
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\spellbook\spell_crafter\validation\strategies 2>&1 | Select-String 'src\\melder\\spellbook\\spell_crafter\\validation\\strategies\\(spellmap_shape_validation_strategy|self_validation_strategy|resolution_frame_presence_strategy|required_holes_strategy|parameter_policy_strategy|existing_creation_compatibility_strategy|dangling_dependency_strategy|contract_provider_presence_strategy|circular_dependency_strategy|callable_profile_hygiene_strategy|binding_resolution_cycle_strategy|annotation_shape_guard_strategy)\\.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_crafter\validation` -> `211 passed, 1 warning`
  IMPACT: The user-supplied strategy cluster is fixed without shims. The only
    runtime-sensitive adjustment was preserving the existing best-effort
    configuration-read swallow behavior.
  NEXT: report the bounded fix and wait for the next exact bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active SpellCrafter validation-strategy lane. Current evidence says the first
pass should treat this as local optionality debt unless a support contract
proves genuinely stale.
