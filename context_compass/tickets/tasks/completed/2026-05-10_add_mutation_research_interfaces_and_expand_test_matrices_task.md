# Task: Add Mutation Research Interfaces And Expand Test Matrices

- Completed: 2026-07-11T19:30:00Z
- Summary: Closed superseded with its parent epic (owner directive). The five
  May interfaces and their test matrix died with the deleted skeleton
  (verified 2026-07-11: zero i*mutation* files, zero importers in src/melder).
  The rebuilt program replaced them with truthful concrete types
  (TYPE_CHECKING-first house style) and its own owner-run-green suites.

## Metadata
- Task ID: TASK-2026-05-10-add-mutation-research-interfaces-and-expand-test-matrices
- Story:
- Epic: EPIC-2026-05-10-design-mutation-research-runtime-surfaces
- Status: superseded
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T23:22:05Z
- Updated: 2026-05-10T23:44:41Z

## Objective
Add the missing interface layer for the five new mutation-research root objects
and expand the new test surface aggressively across unit/component/integration
levels.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the five core interfaces plus a
  much larger mutation-research test matrix after the Aether move landed.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/i*mutation*.py`
  - `src/melder/mutation_research/**`
  - new mutation-research tests under `tests/unit/`, `tests/component/`, and
    `tests/integration/`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-10_move_mutation_research_to_aether_and_scaffold_runtime_surfaces_task.md`
- EXIT_GATE: the five interfaces exist and the mutation-research root/config/
  placeholder surfaces have a materially larger test matrix.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the requested test scale
  would force filler tests rather than meaningful contract coverage.

## Scope Boundaries
- In scope:
  - five interface files
  - unit/component/integration test expansion
  - direct import/type usage updates when useful
- Out of scope:
  - new runtime mutation behavior beyond what is needed for testability
  - broad interface aggregator rewiring in `__init__.py`

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked for the interfaces and a much
  larger mutation-research test surface after the ownership move.

## Steps / Checklist
- [ ] Add the five mutation-research interface files.
- [ ] Expand the unit matrix substantially.
- [ ] Add component tests for the new Aether-owned root/config/placeholders.
- [ ] Add integration tests for the moved retrieval/runtime seams.
- [ ] Run focused validation.

## Deliverables
- five interface files
- expanded unit/component/integration mutation-research test surface

## Files / Paths Impacted
- src/melder/utilities/interfaces/i*mutation*.py
- src/melder/mutation_research/**
- tests/unit/melder/mutation_research/**
- tests/component/melder/mutation_research/**
- tests/integration/melder/mutation_research/**

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: hitting the requested test count with low-value filler.
  Rollback: prefer dense parameterized contract matrices over fake existence
  checks, and stop if the new tests stop carrying real signal.

## Applicable Anti-Patterns
- [ ] No filler tests just to inflate count.
- [ ] No `__init__.py` export wiring for the new interfaces.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.

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
- DATETIME: 2026-05-10T23:22:05Z
  TYPE: PLAN
  CLAIM: The move/scaffold tranche exposed the next concrete gap: the five
    new mutation-research root objects still need their interface files, and
    the new mutation-research-specific test surface is still much smaller than
    the user wants. The next implementation slice is therefore interfaces first
    and then a broad parameterized test-matrix expansion around the new
    Aether-owned root/config/placeholder surfaces.
  EVIDENCE:
  - user_instruction: "also make sure the interfaces for all htese core objects exist ,specifcially the 5 in mutation_research"
  - user_instruction: "we need at least like 100 extra unittests and 40 component and 40 integration just ensure those exist"
  - filesystem_inventory: `src/melder/utilities/interfaces/` currently has no mutation-research interface files
  IMPACT: The next patch should stay on the mutation-research root/config/
    placeholder seam and build real contract matrices instead of drifting into
    unrelated runtime work.
  NEXT: add the five interfaces and then expand the new test tree aggressively.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T23:24:30Z
  TYPE: FACT
  CLAIM: The missing interface layer is now confirmed. The new
    `src/melder/mutation_research/` root contains five core files
    (`mutation_research`, `mutation_configuration`,
    `mutation_configuration_builder`, `mutation_conduit`, `mutation_frame`),
    but `src/melder/utilities/interfaces/` had no matching mutation-research
    interface files yet. The current test surface was also heavily skewed
    toward the moved Aether/conduit ownership ring rather than dedicated
    mutation-research unit/component/integration matrices.
  EVIDENCE:
  - filesystem_inventory: `src/melder/mutation_research/*.py`
  - filesystem_inventory: `src/melder/utilities/interfaces/` file list
  - filesystem_inventory: `tests/unit/melder/mutation_research/` existed but component/integration mutation-research roots did not
  IMPACT: The right next move is interface files first, then dense
    mutation-research-specific test matrices instead of only relying on the
    ownership-move regression ring.
  NEXT: finish the interface layer and start adding the dedicated
    mutation-research unit/component/integration matrix files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T23:28:24Z
  TYPE: MEASURE
  CLAIM: The interface layer and the large mutation-research-specific test
    matrices are now landed and green. The five interface files now exist for:
    - `MutationResearch`
    - `MutationResearchConfiguration`
    - `MutationResearchConfigurationBuilder`
    - `MutationConduit`
    - `MutationFrame`
    And the new mutation-research-specific matrix ring now collects:
    - unit: 112 tests
    - component: 40 tests
    - integration: 40 tests
    for 192 collected tests total across the new files.
  EVIDENCE:
  - src/melder/utilities/interfaces/imutationresearch.py:1-76
  - src/melder/utilities/interfaces/imutationresearchconfiguration.py:1-34
  - src/melder/utilities/interfaces/imutationresearchconfigurationbuilder.py:1-34
  - src/melder/utilities/interfaces/imutationconduit.py:1-23
  - src/melder/utilities/interfaces/imutationframe.py:1-23
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:1-130
  - tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py:1-170
  - tests/component/melder/mutation_research/test_mutation_research_root_component.py:1-145
  - tests/integration/melder/mutation_research/test_mutation_research_root_integration.py:1-153
  - validation_result:
    `python -m py_compile src/melder/utilities/interfaces/imutationresearch.py src/melder/utilities/interfaces/imutationresearchconfiguration.py src/melder/utilities/interfaces/imutationresearchconfigurationbuilder.py src/melder/utilities/interfaces/imutationconduit.py src/melder/utilities/interfaces/imutationframe.py tests/unit/melder/mutation_research/test_mutation_research_root.py tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py tests/component/melder/mutation_research/test_mutation_research_root_component.py tests/integration/melder/mutation_research/test_mutation_research_root_integration.py`
  - validation_result:
    `python -m pytest --collect-only -q -p no:cacheprovider tests/unit/melder/mutation_research/test_mutation_research_root.py tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py tests/component/melder/mutation_research/test_mutation_research_root_component.py tests/integration/melder/mutation_research/test_mutation_research_root_integration.py` -> `192 tests collected`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/mutation_research/test_mutation_research_root.py tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py tests/component/melder/mutation_research/test_mutation_research_root_component.py tests/integration/melder/mutation_research/test_mutation_research_root_integration.py` -> `192 passed`
  IMPACT: The moved Aether-owned mutation-research seam now has its own
    interface layer and a large dedicated test surface rather than relying only
    on the broader Aether/conduit regression ring.
  NEXT: return the interface/test-matrix slice for review before choosing the
    next mutation-runtime behavior change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T23:44:41Z
  TYPE: FACT
  CLAIM: The new mutation-research root objects now actually use the interface
    layer rather than just having interface files beside them. `MutationResearch`
    implements `IMutationResearch`, the configuration object and builder
    implement their new interfaces, and the placeholder `MutationConduit` /
    `MutationFrame` classes now type their mutation-research references against
    `IMutationResearch` instead of leaving them untyped.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1-40
  - src/melder/mutation_research/mutation_research.py:206-280
  - src/melder/mutation_research/mutation_configuration.py:1-20
  - src/melder/mutation_research/mutation_configuration_builder.py:1-24
  - src/melder/mutation_research/mutation_conduit.py:1-20
  - src/melder/mutation_research/mutation_frame.py:1-20
  - validation_result:
    `python -m py_compile src/melder/mutation_research/mutation_research.py src/melder/mutation_research/mutation_configuration.py src/melder/mutation_research/mutation_configuration_builder.py src/melder/mutation_research/mutation_conduit.py src/melder/mutation_research/mutation_frame.py src/melder/utilities/interfaces/imutationresearch.py src/melder/utilities/interfaces/imutationresearchconfiguration.py src/melder/utilities/interfaces/imutationresearchconfigurationbuilder.py src/melder/utilities/interfaces/imutationconduit.py src/melder/utilities/interfaces/imutationframe.py tests/unit/melder/mutation_research/test_mutation_research_root.py tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py tests/component/melder/mutation_research/test_mutation_research_root_component.py tests/integration/melder/mutation_research/test_mutation_research_root_integration.py`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/mutation_research/test_mutation_research_root.py tests/unit/melder/mutation_research/test_mutation_research_root_matrix.py tests/component/melder/mutation_research/test_mutation_research_root_component.py tests/integration/melder/mutation_research/test_mutation_research_root_integration.py` -> `192 passed`
  IMPACT: The mutation-research seam now has both the interface files and the
    actual interface-based typing on the new root/config/placeholder objects.
  NEXT: return this refinement for review and then choose the next runtime
    behavior tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the follow-on interface layer and the large mutation-research
test-matrix expansion after the Aether migration landed.
