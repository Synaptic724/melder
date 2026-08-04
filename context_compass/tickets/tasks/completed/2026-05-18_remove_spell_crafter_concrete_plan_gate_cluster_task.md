# Task: remove spell crafter concrete plan gate cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-remove-spell-crafter-concrete-plan-gate-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:30:51Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Remove the over-strict Phase 9/10/11 concrete plan/blueprint runtime gates in
`SpellCrafter` so the implementation matches its declared protocol contracts.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first non-Nexus suite failure is
  `test_build_execution_plan_variant_delegates_to_builder`
  raising `TypeError: SpellCrafter requires the concrete OccurrencePlan for Phase 11 building.`
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/spell_crafter.py`
  - directly implicated unit tests in
    `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- DEPENDENCIES:
  - current non-Nexus suite-driving lane
  - `IOccurrencePlan`, `IInjectionPlan`, and `IRootResolutionBlueprint`
    protocol contracts
- EXIT_GATE:
  - the targeted builder-wrapper unit test is green
  - the Phase 9/10/11 helper cluster no longer demands “concrete” objects on
    top of protocol-typed signatures
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if source evidence shows any of
  these concrete runtime checks are intentional contract boundaries

## Scope Boundaries
- In scope:
  - removing the Phase 9/10/11 concrete runtime gates in `SpellCrafter`
  - the directly implicated unit expectations if needed
- Out of scope:
  - broader SpellCrafter redesign
  - unrelated test drift outside this concrete-gate cluster

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live non-Nexus blocker is a bounded
  concrete-gate mismatch inside SpellCrafter Phase 9/10/11 helpers

## Steps / Checklist
- [ ] confirm the live concrete-gate cluster and protocol signatures
- [ ] remove the smallest set of bogus runtime gates
- [ ] rerun the targeted builder-wrapper unit test
- [ ] continue to the next non-Nexus blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a bounded Phase 9/10/11 concrete-gate cleanup in `SpellCrafter`

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\spellbook\spell_crafter\test_spell_crafter.py::test_build_execution_plan_variant_delegates_to_builder`

## Risks / Rollback Notes
- Low to medium risk. The change should only remove redundant runtime checks,
  but the cluster touches multiple phase helpers.

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
- DATETIME: 2026-05-18T14:30:51Z
  TYPE: FACT
  CLAIM: The next non-Nexus blocker is another over-strict runtime gate cluster.
    `_build_execution_plan_variant(...)` is annotated to accept
    `IOccurrencePlan` / `IInjectionPlan`, but it still raises unless the values
    pass explicit concrete runtime checks; the same pattern also exists in the
    Phase 9 and Phase 10 helper paths.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4818-4822
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4889-4892
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5130-5174
  - src/melder/utilities/interfaces/ioccurrenceplan.py:1-49
  - src/melder/utilities/interfaces/iinjectionplan.py:1-24
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:6604-6648
  IMPACT: The broad non-Nexus suite stops on redundant runtime type gates even
    though the helper signatures already declare protocol contracts.
  NEXT: remove the concrete runtime checks from the Phase 9/10/11 helper
    cluster, then rerun the direct builder-wrapper unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:30:51Z
  TYPE: FACT
  CLAIM: The Phase 9/10/11 helper cluster now trusts its declared protocol
    contracts. `InjectionPlanBuilder`, `PatchMapBuilder`, and
    `ExecutionPlanBuilder` are invoked directly from the helper inputs without
    the old “concrete” runtime type checks.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4816-4818
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4890-4894
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5152-5157
  IMPACT: The helper cluster is back in sync with its protocol-typed signatures
    and should stop rejecting legitimate protocol-shaped test inputs.
  NEXT: rerun the direct builder-wrapper unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-18T14:30:51Z
  TYPE: MEASURE
  CLAIM: The targeted concrete-gate cleanup lane is green.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4816-4818
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4890-4894
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5152-5157
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\spellbook\spell_crafter\test_spell_crafter.py::test_build_execution_plan_variant_delegates_to_builder` -> `1 passed`
  IMPACT: This non-Nexus blocker is cleared, so the next useful move is another
    stop-on-first suite pass.
  NEXT: rerun `pytest -vv -x --tb=long -k "not nexus and not rift"` and route
    the next failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active lane for the next non-Nexus blocker. Current evidence points to a small
cluster of redundant concrete-runtime gates in SpellCrafter Phase 9/10/11
helpers that should be removed to match the declared protocol contracts.
