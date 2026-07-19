# Task: Move MutationResearch To Aether And Scaffold Runtime Surfaces

- Completed: 2026-07-11T19:30:00Z
- Summary: Closed done with its parent epic (owner directive). The core
  outcome STANDS: MutationResearch is the Aether-hosted singleton root with
  MutationResearchConfiguration + builder (all live in the shipped system).
  The placeholder MutationConduit/MutationFrame scaffolds were later deleted
  by owner ruling (no conduit/frame mutation dimension) in the ResearchSet
  rebuild.

## Metadata
- Task ID: TASK-2026-05-10-move-mutation-research-to-aether-and-scaffold-runtime-surfaces
- Story:
- Epic: EPIC-2026-05-10-design-mutation-research-runtime-surfaces
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T23:04:37Z
- Updated: 2026-05-10T23:17:36Z

## Objective
Move `MutationResearch` ownership from `AethericFrame` to `Aether`, then
scaffold the first Aether-owned mutation runtime surfaces:
- `MutationResearchConfiguration`
- `MutationResearchConfigurationBuilder`
- placeholder `MutationConduit`
- placeholder `MutationFrame`

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the migration, the new
  `src/melder/mutation_research` directory already exists, and the broader
  runtime-surface epic is in place.
- EXECUTION_BOUNDARY:
  - `src/melder/mutation_research/**`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/conduit/conduit.py`
  - focused unit/integration tests directly affected by the ownership move
- DEPENDENCIES:
  - `tickets/epics/2026-05-10_design_mutation_research_runtime_surfaces_epic.md`
  - `artifacts/2026-05-09_mutation_research_philosophy.md`
- EXIT_GATE: MutationResearch is Aether-owned, the new config/builder and
  placeholder surfaces exist, and the focused test ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the migration reveals a
  deeper runtime dependency that prevents a clean Aether-owned root.

## Scope Boundaries
- In scope:
  - Aether-owned `MutationResearch`
  - MutationResearch singleton/configuration pattern
  - placeholder `MutationConduit`
  - placeholder `MutationFrame`
  - affected tests
- Out of scope:
  - full MutationConduit implementation
  - full MutationFrame implementation
  - MutationContract runtime enablement

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested starting the move now with
  no backward-compat shim layer.

## Steps / Checklist
- [ ] Move MutationResearch ownership to `Aether`.
- [ ] Add `MutationResearchConfiguration`.
- [ ] Add `MutationResearchConfigurationBuilder`.
- [ ] Add placeholder `MutationConduit`.
- [ ] Add placeholder `MutationFrame`.
- [ ] Update the affected Aether/conduit/mutation tests.
- [ ] Run focused validation.

## Deliverables
- Aether-owned `MutationResearch`
- mutation-research configuration/builder
- placeholder runtime surfaces
- green focused tests

## Files / Paths Impacted
- src/melder/mutation_research/**
- src/melder/aether/aether.py
- src/melder/aether/aetheric_frame.py
- src/melder/aether/conduit/conduit.py
- focused tests under `tests/unit/melder/aether/**`,
  `tests/integration/melder/aether/**`,
  `tests/unit/melder/aether/conduit/**`,
  and `tests/unit/component melder/spellbook/mutations/**` as needed

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: current tests and helper paths still assume frame-owned mutation
  research.
  Rollback: update those tests directly to the new Aether-owned contract
  instead of leaving adapter shims behind.

## Applicable Anti-Patterns
- [ ] No backward-compat shim layer.
- [ ] No widening into full MutationConduit/MutationFrame behavior.
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
- DATETIME: 2026-05-10T23:04:37Z
  TYPE: PLAN
  CLAIM: The move is now an implementation tranche, not just design. The
    focused goal is to make `MutationResearch` follow the same private-root
    pattern as `Nexus` and `Crystallizer`, while keeping the new runtime
    surfaces deliberately skeletal. The safe default config posture from the
    philosophy is `restricted_module_mutations=True` and
    `unrestricted_module_mutations=False`.
  EVIDENCE:
  - user_instruction: "go ahead and move the object up"
  - user_instruction: "we do want Mutation Research to become a singleton just like nexus or crystallizer"
  - codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md:159-199
  IMPACT: The next patch can stay tight: ownership move, config/builder, and
    placeholders only, with no compatibility shims.
  NEXT: patch the Aether-owned root and the new mutation-research files, then
    update the affected tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T23:17:36Z
  TYPE: MEASURE
  CLAIM: The Aether move and scaffold pass is landed and green. `MutationResearch`
    is now an Aether-owned singleton root in `src/melder/mutation_research/`,
    `Aether` hosts and cleans it alongside Nexus/Crystallizer, `AethericFrame`
    no longer constructs or owns it, `Conduit.get_mutation_research()` now
    delegates to the Aether-owned root directly, and the new
    `MutationResearchConfiguration`, `MutationResearchConfigurationBuilder`,
    placeholder `MutationConduit`, and placeholder `MutationFrame` classes now
    exist. The focused unit/integration ring for the affected Aether,
    AethericFrame, conduit, and mutation-research surfaces is green.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1-430
  - src/melder/mutation_research/mutation_configuration.py:1-262
  - src/melder/mutation_research/mutation_configuration_builder.py:1-175
  - src/melder/mutation_research/mutation_conduit.py:1-145
  - src/melder/mutation_research/mutation_frame.py:1-140
  - src/melder/aether/aether.py:1-200
  - src/melder/aether/aether.py:1953-1968
  - src/melder/aether/aetheric_frame.py:1-120
  - src/melder/aether/conduit/conduit.py:3971-4005
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:1-130
  - validation_result:
    `python -m py_compile src/melder/mutation_research/mutation_research.py src/melder/mutation_research/mutation_configuration.py src/melder/mutation_research/mutation_configuration_builder.py src/melder/mutation_research/mutation_conduit.py src/melder/mutation_research/mutation_frame.py src/melder/aether/aether.py src/melder/aether/aetheric_frame.py src/melder/aether/conduit/conduit.py src/melder/utilities/interfaces/iconduit.py tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_aetheric_frame.py tests/unit/melder/aether/conduit/test_conduit_dynamic.py tests/integration/melder/conduit/test_conduit_integration_lifecycle.py tests/integration/melder/aether/test_aether_integration_frames.py tests/integration/melder/aether/test_aether_integration_registry_ops.py tests/integration/melder/aether/test_aether_integration_frame_cleanup.py tests/unit/melder/spellbook/mutations/test_mutation_research.py tests/component/melder/spellbook/mutations/test_research_component.py tests/unit/melder/mutation_research/test_mutation_research_root.py`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_aetheric_frame.py tests/unit/melder/aether/conduit/test_conduit_dynamic.py tests/integration/melder/conduit/test_conduit_integration_lifecycle.py tests/integration/melder/aether/test_aether_integration_frames.py tests/integration/melder/aether/test_aether_integration_registry_ops.py tests/integration/melder/aether/test_aether_integration_frame_cleanup.py tests/unit/melder/spellbook/mutations/test_mutation_research.py tests/component/melder/spellbook/mutations/test_research_component.py tests/unit/melder/mutation_research/test_mutation_research_root.py` -> `258 passed`
  IMPACT: The ownership move is done with no shim layer, and the first
    placeholder runtime surfaces and configuration objects now exist to support
    the next mutation-runtime tranche.
  NEXT: return the migration/scaffold slice for review, then decide whether the
    next implementation step is the spell-facing MutationContract API,
    MutationConduit wiring, or the Phase 4 gate removal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the actual Aether migration plus the first config/runtime-surface
scaffolding for `MutationResearch`.
