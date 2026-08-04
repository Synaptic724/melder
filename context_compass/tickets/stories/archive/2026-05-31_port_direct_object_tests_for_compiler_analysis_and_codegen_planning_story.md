# Story: Port direct object tests for compiler analysis and codegen planning

## Metadata
- Story ID: STORY-2026-05-31-port-direct-object-tests-for-compiler-analysis-and-codegen-planning
- Epic: EPIC-2026-05-31-migrate-compiler-object-tests-from-blueprint-surfaces
- Status: in_progress
- Owner: codex
- Agent Name: tester_0
- Priority: p1
- Created: 2026-05-31T21:51:49Z
- Updated: 2026-05-31T21:51:49Z

## User Narrative
As a maintainer removing the old blueprint/phase-centric objects, I want direct
tests on the new analyzer / processor / planner stack, so that deleting the old
objects does not delete the real proof surface with them.

## Value / MRP Alignment
This story strengthens the compiler core by making the new object boundaries the
thing we actually prove, instead of preserving indirect proof through phase
names that are already expected to drift.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the lane to object-centric test
  migration and away from phase-centric drift.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation/`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/`
  - `tests/unit/melder/spellbook/spell_compiler/`
  - `codex/context_compass/tickets/stories/`
  - `codex/context_compass/tickets/tasks/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-31_migrate_compiler_object_tests_from_blueprint_surfaces_epic.md`
  - current direct source under the 3 target object folders
- EXIT_GATE:
  - first direct unit slice lands for analyzer / processor / planner
  - stale or indirect test intent moved onto those object contracts
  - next strategy/data slice is explicit
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a test intent cannot be mapped
  cleanly from blueprint/phase source to a real new object boundary.

## Requirements (Functional)
- add direct unit coverage for analyzer / processor / planner facades
- add direct coverage for the builder/discovery helpers that make those facades
  deterministic
- keep phase names out of the new primary assertions

## Requirements (Non-Functional)
- tests stay deterministic
- assertions stay contract-level and reviewable
- no low-value private-shape assertions without real contract reason

## Scope Boundaries
- In scope:
  - direct object unit migration
  - first builder/discovery tests
- Out of scope:
  - broader component migration
  - large phase test rewrites in this first slice

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the direct object unit slice is the right first bounded
  migration seam.

## Dependencies / Related Work
- `tickets/tasks/2026-05-31_start_unit_tests_for_spell_analyzer_artifact_processor_and_codegen_planner_task.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-05-31-start-unit-tests-for-spell-analyzer-artifact-processor-and-codegen-planner - land the first direct unit slice
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- analyzer facade coverage exists directly
- artifact processor facade/builder/model shell coverage exists directly
- planner facade/builder/discovery/plan shell coverage exists directly
- next migration slice is defined in notes

## Validation / Test Plan
- run focused pytest on the new direct unit files only

## UX / API / Data Notes
- object contracts are the target, not the old phase names

## Risks / Mitigations
- Risk: new tests accidentally restate the old phase API.
  - Mitigation: each new assertion should name the current object contract.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- which old phase-only tests should remain temporary migration proofs after the
  first direct object slice lands

## Decision Log
- first slice is direct unit coverage for facades/builders/discovery helpers

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-31T21:51:49Z
  TYPE: PLAN
  CLAIM: The first bounded migration slice should target the direct unit
    surfaces for analyzer / processor / planner facades and their helper
    registries. That lets us land meaningful proof immediately without
    re-litigating all of the old phase assertions in one pass.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-122
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-156
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-117
  IMPACT: We can get real object-centric coverage started now and use it as the
    pattern for later strategy/data and component slices.
  NEXT: create and execute the first task for direct unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T22:33:58Z
  TYPE: FACT
  CLAIM: The story scope now includes `codegen_creation/` directly because the
    replacement object layer continues past planner into the creation facade,
    creation container, strategy builder, and generalized creation strategies.
    A first direct `codegen_creation` unit slice is already landed, so future
    work should keep extending that layer instead of treating it as out of
    scope.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-66
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-120
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-346
  IMPACT: Future slices under this story should include remaining
    `codegen_creation` strategy/compiler migration work, not just analyzer /
    processor / planner objects.
  NEXT: extend direct coverage to the remaining `codegen_creation`
    strategy/compiler seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes or migration boundaries sharpen.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story is the first direct object migration slice under the compiler test
epic: analyzer / processor / planner facades and their helper registries first,
wider strategy/data migration next.
