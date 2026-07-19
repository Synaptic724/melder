# Task: fix injection plan cleaned runtime failure

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-18-fix-injection-plan-cleaned-runtime-failure
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T13:09:20Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the first real pytest runtime failure where `Spellbook.conjure()` aborts in
the `execution_plan` phase because `InjectionPlan` is missing `_cleaned`.

## Ticket Contract
- ENTRY_GATE: full-suite pytest stop-on-first-failure run produced a concrete
  runtime traceback rooted in `InjectionPlan`
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/blueprints/injection_plan.py`
  - `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
  - directly implicated shared cleanup/base files only if required by the concrete fix
- DEPENDENCIES:
  - the failing conduit component test path
- EXIT_GATE: the original failing test no longer dies with missing `_cleaned`
  during `Spellbook.conjure()`
- FAILURE_ESCALATION: raise `BLOCKER` if the failure is actually rooted in a
  broader cleanup contract outside the bounded blueprint plan ring

## Scope Boundaries
- In scope:
  - `InjectionPlan` / `OccurrencePlan` cleaned-state initialization and runtime contract
  - directly implicated plan-builder or cleanup base wiring only if required
- Out of scope:
  - unrelated blueprint typing cleanup
  - unrelated component/integration failures after this first blocker

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user redirected work to fixing the first real pytest failure

## Steps / Checklist
- [ ] inspect the failing `InjectionPlan` and adjacent `OccurrencePlan` runtime construction path
- [ ] patch the concrete cleaned-state/runtime contract so conjure can complete
- [ ] rerun the original failing pytest test
- [ ] if green, continue to the next failure only after documenting it
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- runtime fix for the first pytest blocker in the blueprint execution-plan ring

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/injection_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- directly implicated shared cleanup files only if needed by truthful replacement

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\component\melder\aether\conduit\test_conduit_component_creations.py::test_component_conduit_meld_many_registers_multiple_creations`

## Risks / Rollback Notes
- Medium risk. The runtime failure smells like a concrete cleanup/base-class
  initialization break, but the two plan classes may share a broader flawed pattern.

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
- DATETIME: 2026-05-18T13:09:20Z
  TYPE: FACT
  CLAIM: The first full-suite pytest blocker is not in the ACL lane. It fails
    in the conduit component creation path because `Spellbook.conjure()`
    reaches the `execution_plan` phase and aborts on
    `AttributeError: InjectionPlan object has no attribute '_cleaned'`, which
    is wrapped by `PhaseExecutionError`.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:274-274
  - src/melder/spellbook/spellbook.py:3762-3762
  - src/melder/spellbook/spellbook_creation_system.py:162-162
  - src/melder/spellbook/spellbook_creation_system.py:252-252
  - src/melder/spellbook/spellbook_creation_system.py:1214-1214
  - src/melder/utilities/synchronization/phase_scheduler.py:562-562
  IMPACT: The first actionable runtime defect is the blueprint execution-plan
    ring, so this new lane should stay focused there until the original test
    stops failing.
  NEXT: inspect `InjectionPlan` and `OccurrencePlan` construction/cleanup
  initialization paths before editing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:11:39Z
  TYPE: FACT
  CLAIM: Direct runtime probing shows `InjectionPlan` does initialize
    `_cleaned`, but `OccurrencePlan` does not. The concrete cause is the class
    base order: `OccurrencePlan` inherits `IOccurrencePlan` before
    `Cleanable`, so `super().__init__()` never reaches `Cleanable.__init__()`
    and the cleaned-state slot is never initialized.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:336-391
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:99-197
  - src/melder/utilities/general_base/cleanable.py:20-30
  IMPACT: The first fix should target `OccurrencePlan` directly. If the
    original failing test still reports an `InjectionPlan` cleaned-state issue
    afterward, that will be a second defect, not the same one.
  NEXT: change `OccurrencePlan` to inherit `Cleanable` first, then rerun the
    original failing pytest test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:12:14Z
  TYPE: FACT
  CLAIM: The concrete runtime patch is in: `OccurrencePlan` now inherits
    `Cleanable` first, so `super().__init__()` reaches
    `Cleanable.__init__()` and initializes `_cleaned` on live Phase 8 plan
    objects.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:99-197
  IMPACT: The next rerun will tell us whether the original pytest blocker was
    entirely this Phase 8 lifecycle defect or whether a second plan-class issue
    is stacked behind it.
  NEXT: rerun the original failing component test with verbose traceback.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:12:44Z
  TYPE: MEASURE
  CLAIM: The original failing component test is now green after the
    `OccurrencePlan` inheritance-order fix. The `Spellbook.conjure()` path for
    `Existence.many` no longer aborts in the `execution_plan` phase on missing
    `_cleaned`.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:99-197
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:274-274
  IMPACT: The first concrete pytest blocker is cleared, so the next useful step
    is another suite rerun in stop-on-first-failure mode to surface the next
    real failure.
  NEXT: rerun `pytest -vv -x --tb=long` across the suite and capture the next
    failing test if one exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Bounded runtime-fix lane for the first pytest blocker in the blueprint
execution-plan path.
