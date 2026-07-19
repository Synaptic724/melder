# Story: Phase 10 Solo And Many-Only Discovery

## Metadata
- Story ID: STORY-2026-06-06-phase10-solo-and-many-only-discovery
- Epic: EPIC-2026-05-30-right-size-execution-strategy-compiler-outputs
- Status: in_progress
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-07T00:14:08Z
- Updated: 2026-06-07T09:08:51Z

## User Narrative
As a compiler architect, I want phase 10 to classify `solo` and `many_only`
graphs explicitly, so that phase 11 can choose simpler creation families
without widening the runtime seam.

## Value / MRP Alignment
This story strengthens the core compiler layering:
- phase 8 produces raw existence/disposal truth
- phase 9 exposes that truth on the model
- phase 10 selects plan families from that model truth
- phase 11 later chooses the matching creation family

That is the smallest coherent way to add `solo` and `many_only` without
collapsing discovery back into runtime or forcing phase 10 to reopen live
spell surfaces.

## Ticket Contract
- ENTRY_GATE: the phase-11 generalized family migration is landed and the
  phase-8/9 existence-occurrence section exists on `SpellCodegenModel`.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `tests/unit/melder/spellbook/spell_compiler/`
  - `tests/component/melder/spellbook/spell_compiler/`
  - `codex/context_compass/tickets/stories/2026-06-06_phase10_solo_and_many_only_discovery_story.md`
  - `codex/context_compass/tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
- EXIT_GATE:
  - phase 10 discovery emits `solo` and `many_only`
  - matching planner strategy ids exist
  - planner/creation discovery tests prove the new category selection order
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the category rules require
  widening the phase-11/runtime seam instead of staying model-only.

## Requirements (Functional)
- Add a dedicated `solo` discovery strategy.
- Add a dedicated `many_only` discovery strategy.
- `solo` wins whenever the visible spell set size is exactly `1`.
- `many_only` applies only when the visible spell set size is greater than `1`
  and every visible spell has `Existence.many`.
- Emit the category through:
  - `selected_strategy_id`
  - `plan_family_id`
  - `candidate_codegen_style_ids`
- Keep the current generalized fallback path.

## Requirements (Non-Functional)
- Do not widen the `SpellCodegenCreation -> CreationContext` seam.
- Do not reopen live spellbook/runtime surfaces in phase 10 discovery.
- Consume only model-owned facts from phase 9.
- Preserve deterministic discovery order and stable strategy ids.

## Scope Boundaries
- In scope:
  - phase-10 discovery strategy ordering
  - phase-10 planner strategy ids for `solo` and `many_only`
  - model-driven category selection from `existence_occurrence_shape`
- Out of scope:
  - phase-11 family implementation for `solo` and `many_only`
  - runtime emitter changes
  - broader generalized planner refactor

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the next bounded slice to
  adding `solo` and `many_only` as phase-10 categories.

## Dependencies / Related Work
- `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
- `src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py`
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_existence_occurrence_processor_strategy.py`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-06-06-decompose-phase10-phase11-strategy-groups - add `solo` and `many_only` discovery selectors.
- [ ] Task: TASK-2026-06-06-decompose-phase10-phase11-strategy-groups - add matching planner strategy ids.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `solo` discovery wins first when visible spell count is exactly `1`.
- `many_only` discovery wins when visible spell count is greater than `1` and
  all visible spells are `Existence.many`.
- `generalized` remains the fallback.
- Focused phase-10/phase-11 discovery and planner tests are green.

## Validation / Test Plan
- `pytest -q`
  - `tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py`
  - `tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py`
  - `tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py`

## UX / API / Data Notes
- This story changes planner discovery categories only.
- `solo` and `many_only` are category labels, not runtime surface changes.
- Phase 10 should read:
  - `model.existence_occurrence_shape`
  - `model.root_dependency_count`

## Risks / Mitigations
- Risk: phase 10 discovery starts recomputing spell/runtime truth.
  - Mitigation: use only model-owned phase-9 sections.
- Risk: `solo` and `many_only` rules overlap ambiguously.
  - Mitigation: `solo` wins first, `many_only` only when count > 1.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether `many_only` should later split by disposal posture into distinct
  candidate style ids.

## Decision Log
- `solo` is defined by visible spell count, not by existence.
- `many_only` is defined by the whole visible spell set, not the root spell
  alone.
- Phase 10 consumes model truth; it does not reopen the spellbook.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: true
- CONTEXT_IDS:
  - CTX-2026-06-07-phase10-solo-and-many-only-discovery
- CONTEXT_TOPICS:
  - phase-8 existence-occurrence production
  - phase-9 model exposure
  - phase-10 `solo` and `many_only` discovery
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-07T00:14:08Z
  TYPE: PLAN
  CLAIM: This story isolates the first phase-10 category expansion: `solo`
    and `many_only`. Phase 8/9 now already publish the raw and aggregate
    existence/disposal truth needed for those selectors, so the next move is
    discovery and planner categorization only.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py:1-30
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_existence_occurrence_processor_strategy.py:1-55
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:1-26
  IMPACT: The compiler can now add the 2 phase-10 categories without widening
    the phase-11/runtime seam or forcing discovery to reopen live spell
    objects.
  NEXT: implement the 2 discovery strategies and matching planner strategy ids.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T08:40:54Z
  TYPE: FACT
  CLAIM: The `solo` and `many_only` phase-10 slice now has a clearer upstream
    dependency boundary. These selectors are not just reading phase-8/9
    existence rows; they sit on top of the full compiler foundation where
    phases 4-7 establish structural validity, rooted blueprints, system
    validation, and change-control wiring before analyzer, processor, planner,
    and phase-11 creation packaging take over.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:56-145
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:458-615
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:109-473
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:55-231
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:20-100
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:16-74
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:16-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-87
  IMPACT: Later phase-11 `solo` and `many_only` families should be designed as
    consumers of a much richer compiler stack than the story originally
    spelled out. That reduces the risk of building category-specific families
    that accidentally ignore rooted-system or validity contracts.
  NEXT: extend the linked context artifact so later implementation rereads the
    phase-4-to-11 compiler seams and the current runtime handoff before phase-11
    family code starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:03:36Z
  TYPE: FACT
  CLAIM: The story is not done at category detection alone. The current `solo`
    and `many_only` planner strategies still build their lanes through the same
    generalized lane builder, so the phase-10 output categories are real but
    the phase-10 lane families are not yet distinct.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py:19-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py:19-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:19-69
  IMPACT: The next bounded step is still phase 10, not phase 11. We need real
    dedicated lane builders so phase 11 receives genuine solo and many-only
    plan families instead of renamed generalized output.
  NEXT: implement dedicated solo and many-only lane builders and rewire the
    category strategies to use them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:07:29Z
  TYPE: FACT
  CLAIM: The story has now crossed the category-only line. The `solo` and
    `many_only` planner strategies are rewired to dedicated builder surfaces,
    and those builders now enforce their own family preconditions instead of
    acting as direct generalized-builder aliases.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1011-1314
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py:19-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py:19-61
  IMPACT: The phase-10 story is now genuinely close to closure. What remains is
    validation, not more planner-family scaffolding.
  NEXT: validate the focused planner/discovery ring and then reassess whether
    phase 11 is now the correct next active slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:08:51Z
  TYPE: MEASURE
  CLAIM: The focused phase-10 planner/discovery ring is green after the lane
    builder split. The story now has all three required pieces for this
    milestone: category detection, emitted plan-family/style metadata, and
    dedicated solo/many-only lane-builder surfaces.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py:1-49
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py:1-60
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1011-1314
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py:1-241
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-300
  IMPACT: The story is ready to hand off to phase 11. What remains is not more
    phase-10 family work; it is real phase-11 consumption of the new plan
    families.
  NEXT: start phase-11 `solo` and `many_only` creation-family discovery and
    strategy work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the first phase-10 category expansion. The phase-8/9 existence
section is already present, so the next bounded implementation move is phase-10
discovery and planner categorization for `solo` and `many_only`.
