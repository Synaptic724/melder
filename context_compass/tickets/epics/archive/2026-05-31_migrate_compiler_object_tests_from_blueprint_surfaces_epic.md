# Epic: Migrate Compiler Object Tests From Blueprint Surfaces

## Metadata
- Epic ID: EPIC-2026-05-31-migrate-compiler-object-tests-from-blueprint-surfaces
- Status: in_progress
- Owner: codex
- Agent Name: tester_0
- Priority: p1
- Created: 2026-05-31T21:51:49Z
- Updated: 2026-05-31T21:51:49Z
- Target Window: 2026-Q2
- Related Program/Initiative: Compiler ownership reorganization

## Problem / Opportunity
The compiler test surface still leans heavily on the old blueprint/phase
objects:
- occurrence-plan tests live mostly through Phase 8 seams
- injection-plan tests live mostly through Phase 9 seams
- patch-map tests live mostly through Phase 10 seams
- execution-plan tests live mostly through Phase 11 seams
- direct object coverage is thin for the new:
  - `spell_analyzer/`
  - `artifact_processor/`
  - `codegen_planner/`

Those old objects are being reorganized into analyzer, processor, planner,
their builders, strategies, and data objects. If we do not migrate the tests
now, we will keep proving obsolete surfaces while deleting the actual objects
that should become the new contract.

## MRP Alignment (Most Reasonable Product)
The MRP is not "keep every old phase test forever."

It is:
- move test intent from old phase/bluprint shells onto the new object
  contracts
- preserve behavioral proof while object ownership is shifting
- create direct unit/component surfaces for the new facades, builders,
  strategies, and data models
- keep phase tests only as temporary migration or integration seams, not as the
  long-term primary contract

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an epic and explicitly redirected
  the lane away from phase-centric tests toward the specific new objects and
  the blueprint-derived strategy/data surfaces they replace.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation/`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/`
  - `tests/unit/melder/spellbook/spell_compiler/`
  - `tests/component/melder/spellbook/`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/tickets/stories/`
  - `codex/context_compass/tickets/tasks/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-31_reorganize_phase8_to_phase11_compiler_ownership_epic.md`
  - `tickets/tasks/2026-05-30_define_execution_strategy_phase12_task.md`
  - direct source under the 3 target object folders
  - current compiler tests under `tests/unit/melder/spellbook/spell_compiler/`
- EXIT_GATE:
  - direct unit coverage exists for analyzer / processor / planner facades and
    builders
  - strategy/data coverage exists for the migrated blueprint-derived seams
  - component coverage exists where the new object surfaces now form real
    integration slices
  - stale blueprint/phase-only tests are either ported, reduced to temporary
    migration seams, or explicitly retired
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a proposed test slice still
  depends primarily on phase naming instead of object contracts.

## Goals (Outcomes)
- Make `spell_analyzer`, `artifact_processor`, and `codegen_planner` the
  primary test targets.
- Mirror old occurrence/injection/patch/execution intent onto the new object
  and strategy surfaces.
- Add missing tests for facades, builders, strategies, and core data objects.
- Create direct component coverage only where the new object seams form real
  integration slices.

## Non-Goals (Explicit Exclusions)
- No renaming or widening of production code in this epic unless a test
  migration reveals a real contract bug.
- No phase-name preservation just to keep old tests comfortable.
- No broad compiler redesign under the cover of test migration.

## Scope Boundaries
- In scope:
  - direct object and strategy/data test migration
  - blueprint-to-object intent mapping
  - unit/component test creation for the new object surfaces
- Out of scope:
  - production implementation rewrites unrelated to testability
  - keeping old phase tests as the long-term primary proof surface

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a focused epic for object
  and strategy/data test migration and explicitly rejected phase-centric drift.

## Success Metrics
- analyzer / processor / planner each have direct unit coverage
- builder registries are directly covered
- blueprint-derived strategy/data seams have direct proof
- new component coverage exists only where it maps to a real object boundary

## Requirements (Functional + Non-Functional)
- Preserve old test intent while moving it to the new object contracts.
- Prefer object-level tests over phase-name tests.
- Keep tests deterministic and contract-driven.
- Report validation truthfully.

## Constraints / Assumptions
- The old blueprint objects are source-side truth for migration intent, not the
  new long-term test target.
- `tests/component/melder/spellbook/spell_compiler/` does not currently exist;
  any component slice there should be created intentionally rather than assumed.
- Some current direct coverage already exists for analyzer; processor/planner
  are still mostly covered indirectly.

## Dependencies / External References
- `tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_8.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_9.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_10.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_11.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py`

## Milestones (Track Progress)
- [ ] Milestone 1: direct unit tests exist for analyzer / processor / planner
- [ ] Milestone 2: blueprint-derived strategy/data intent is mirrored onto new
      object tests
- [ ] Milestone 3: component coverage exists for the real new object seams
- [ ] Milestone 4: stale phase-only tests are reduced to temporary migration
      seams or retired

## Stories (Required to Complete)
- [ ] Story: direct unit migration for analyzer / processor / planner facades
- [ ] Story: strategy and builder migration for occurrence/injection/patch/codegen planning
- [ ] Story: component coverage for real compiler object seams
- [ ] Story: stale phase-centric test reduction after direct object coverage lands

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: inventory which old tests map to which new object/strategy/data surfaces
- [ ] Task: keep the lane object-centric and reject phase-centric drift
- [ ] Task: verify no old test intent is silently dropped during migration
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The primary proof surface for these compiler lanes is the new object stack,
  not the old phase names.
- Direct tests exist for facades, builders, and key strategy/data objects.
- Component tests exist where the new objects form real integration seams.
- Old phase-only tests are no longer the main contract for these lanes.

## Risks / Mitigations
- Risk: we keep porting tests mechanically and preserve phase-centric drift.
  - Mitigation: every task must name the target object surface explicitly.
- Risk: component coverage is invented where no real component seam exists.
  - Mitigation: only add component tests for real multi-object object seams.
- Risk: broad test churn hides contract bugs.
  - Mitigation: migrate in small slices and keep source intent explicit in ticket notes.

## Validation / Test Approach
- start with direct unit tests for facades and builders
- migrate blueprint-derived intent into strategy/data unit tests next
- add focused component slices only after the direct object contract is clear

## Rollout / Adoption Plan
- land the first direct unit slice
- use it as the pattern for later object and strategy/data migration

## Open Questions
- which existing phase-only assertions should remain as temporary migration
  proof and which should move entirely

## Decision Log
- object and strategy/data surfaces are the primary migration target
- phases are temporary migration seams only

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-31T21:51:49Z
  TYPE: FACT
  CLAIM: The existing test surface is skewed. Analyzer already has one direct
    unit file, but processor and planner are still mostly proved indirectly
    through Phase 12 and the old phase 8-11 test files. There is also no
    direct `tests/component/melder/spellbook/spell_compiler/` subtree yet, so
    any component migration there has to be intentionally created rather than
    discovered.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-103
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_8.py:1-336
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_9.py:1-102
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_10.py:1-158
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_11.py:1-614
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:1-256
  - tests/component/melder/spellbook:1-1
  IMPACT: We should start with direct object tests immediately, then widen to
    strategy/data and component coverage from there.
  NEXT: create the first story/task for direct analyzer / processor / planner
    unit migration and land the first test slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:33:58Z
  TYPE: FACT
  CLAIM: The migration scope has now widened to include
    `src/melder/aether/spellbook/spell_compiler/codegen_creation/` directly.
    That is necessary because the new planner output does not stop at
    `SpellCodegenPlan`; the real replacement object stack continues into
    `CodegenCreationDiscoverySystem`, `CodegenCreationSystem`,
    `SpellCodegenCreation`, `SpellCodegenStrategyBuilder`, and the generalized
    creation strategies. The first direct `codegen_creation` unit slice is now
    landed and green.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-66
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-120
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_creation.py:1-164
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_strategy_builder.py:1-111
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-346
  IMPACT: The compiler object migration epic now explicitly spans the
    post-planner creation layer too, instead of stopping prematurely at planner
    outputs.
  NEXT: keep migrating remaining `codegen_creation` strategy/compiler intent
    alongside the unfinished processor/planner seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when target object boundaries or migration scope changes.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists to move proof from old blueprint/phase-centric compiler tests
onto the new analyzer / processor / planner object stack and the strategy/data
objects those lanes now own.
