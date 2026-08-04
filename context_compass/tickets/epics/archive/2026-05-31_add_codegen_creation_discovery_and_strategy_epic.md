# Epic: Add Codegen Creation Discovery And Strategy

## Metadata
- Epic ID: EPIC-2026-05-31-add-codegen-creation-discovery-and-strategy
- Status: in_progress
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-05-31T19:32:19Z
- Updated: 2026-05-31T19:36:07Z
- Target Window: 2026-Q2
- Related Program/Initiative: Reorganize Phase 8 To Phase 11 Compiler Ownership

## Problem / Opportunity
The current compiler reorganization now has:
- analyzer-owned graph truth
- processor-owned occurrence / injection / patch-targeting model sections
- planner-owned generalized lane plans built from the model

But the pipeline still compresses two different decisions together:
- execution strategy selection
- code emission strategy selection

That leaves Phase 13 with no explicit discovery/strategy system of its own,
which means we lose a clean place to:
- try different code emission approaches for the same chosen execution plan
- rank those approaches
- tune compile-time specialization versus runtime speed
- carry plan-level hints forward into codegen without forcing the plan to
  choose every emission detail too early

The opportunity is to add a distinct codegen-creation layer after planning:
- `CodegenCreationDiscoverySystem`
- `SpellCodegenStrategyBuilder`
- `SpellCodegenStrategy`
- `CodegenCreationSystem`

That layer should consume:
- `SpellCodegenModel`
- `SpellCodegenPlan`

and decide the best emitted code shape for the already-chosen execution
semantics.

## MRP Alignment (Most Reasonable Product)
The MRP is not a full Phase 13 rewrite in one pass.

It is:
- keep the current generalized planner lane working
- add an explicit discovery/strategy seam for code emission
- start with one generalized codegen creation strategy
- keep specialized codegen experimentation additive
- preserve the ability to compare old and new emitted forms while the runtime
  converges

That gives us a real optimization surface without breaking the current
execution-semantics work.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for this design to be documented as the
  next-step epic after discussing planner versus codegen responsibilities.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py`
  - `src/melder/aether/conduit/meld/creation_context/`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-31_reorganize_phase8_to_phase11_compiler_ownership_epic.md`
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
- EXIT_GATE:
  - codegen creation discovery, strategy, and creation-system roles are explicit
  - planner versus codegen responsibilities are non-overlapping
  - one bounded implementation order exists for the first codegen creation cut
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first codegen creation
  cut reveals that plan objects are still missing essential forward hints that
  codegen needs.

## Goals (Outcomes)
- Define a distinct codegen creation discovery layer after planning.
- Preserve `SpellCodegenPlan` as execution-strategy output, not final code.
- Let codegen reconsume both the model and the chosen plan.
- Create room for multiple code emission strategies for the same plan.
- Keep `CreationContext` as the final binder/cache holder for emitted artifacts.

## Non-Goals (Explicit Exclusions)
- No planner ownership rewrite in this epic.
- No analyzer or processor lane redesign here.
- No promise that one generalized codegen strategy is the final best strategy.
- No runtime consumer deletion in the same planning-only epic.

## Scope Boundaries
- In scope:
  - codegen discovery architecture
  - codegen strategy architecture
  - codegen creation system role
  - plan-level forward-hint expectations
- Out of scope:
  - deleting old Phase 13 emitter files in this epic
  - broad runtime consumer cutover in this epic
  - unrelated compiler phase ownership work already covered by the current epic

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the next architectural question after the planner/model
  work is the missing codegen discovery/strategy seam, and the user asked for
  that next-step direction to be documented explicitly.

## Success Metrics
- We have an explicit answer for what codegen discovery does.
- We have an explicit answer for what codegen strategies do.
- We have an explicit answer for what `CodegenCreationSystem` does.
- We have an explicit answer for what plan-level hints should survive into
  codegen.

## Requirements (Functional + Non-Functional)
- Functional:
  - define `CodegenCreationDiscoverySystem`
  - define `SpellCodegenStrategyBuilder`
  - define `SpellCodegenStrategy`
  - define `CodegenCreationSystem`
  - define how `SpellCodegenModel` and `SpellCodegenPlan` are both consumed
- Non-functional:
  - no handwavy “Phase 13 just optimizes stuff” claims
  - no collapsing execution strategy and code emission strategy back together
  - no overfitting the codegen layer to one generalized emitted form forever

## Constraints / Assumptions
- Planner chooses execution semantics first.
- Codegen chooses emitted code shape second.
- The same chosen plan may still have multiple viable code emission forms.
- Plan objects should carry enough facts/hints forward that codegen does not
  need to rediscover execution semantics.

## Dependencies / External References
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py`
- `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`

## Milestones (Track Progress)
- [ ] Milestone 1: discovery/strategy/creation-system roles are explicit
- [ ] Milestone 2: generalized codegen creation strategy contract is explicit
- [ ] Milestone 3: plan-level forward hints are explicit enough for codegen work

## Stories (Required to Complete)
- [ ] Story: define `CodegenCreationDiscoverySystem`
- [ ] Story: define `SpellCodegenStrategyBuilder` and `SpellCodegenStrategy`
- [ ] Story: define `CodegenCreationSystem`
- [ ] Story: define the first generalized codegen creation strategy
- [ ] Story: define specialized codegen strategy candidates and ranking dimensions

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: keep planner output generic and strategy-owned
- [ ] Task: keep Phase 13/codegen from re-deciding execution semantics
- [ ] Task: preserve `CreationContext` as final binder/cache holder
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The codegen creation layer has a concrete discovery/strategy/system design.
- The separation between plan strategy and codegen strategy is explicit.
- The next implementation slice can start without re-arguing the architecture.

## Risks / Mitigations
- Risk: planner and codegen drift back into one merged phase.
  - Mitigation: keep the discovery/system objects separate and document their
    boundaries explicitly.
- Risk: plan objects carry too little information for codegen.
  - Mitigation: document plan-level forward hints as an explicit work item.
- Risk: codegen over-optimizes one emitted form and becomes brittle.
  - Mitigation: treat generalized codegen as the stable baseline and add
    specialized strategies experimentally.

## Applicable Anti-Patterns
- [ ] No collapsing execution strategy and code emission strategy into one layer again.
- [ ] No planner re-deciding code emission details too early.
- [ ] No codegen re-deciding execution semantics.

## Validation / Test Approach
- Planning only in this epic by default.
- Future implementation slices can add narrow syntax validation or focused rings
  when the user asks for them.

## Rollout / Adoption Plan
- First: keep the current generalized planner strategy intact.
- Second: define the codegen creation discovery/strategy/system seam.
- Third: land one generalized codegen creation strategy.
- Fourth: add specialized codegen strategies and ranking logic experimentally.
- Fifth: cut runtime consumers over once the emitted artifact seam stabilizes.

## Open Questions
- Which plan-level hints should be explicit fields versus metadata?
- Should codegen strategy discovery rank per lane or per whole-plan family?
- How much compile-time cost are we willing to trade for runtime speed?

- DATETIME: 2026-06-05T00:14:04Z
  TYPE: DECISION
  CLAIM: The long-term top-level codegen-creation runtime surface should
    converge toward only 2 output families: `no_overrides_creation` and
    `override_creation`. Mutation-aware behavior still exists, but the newer
    semantic direction is that mutation affects upstream contract/revalidation
    and build selection rather than remaining a permanent third top-level
    output family.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md:1-320
  - codex/context_compass/tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md:1-260
  IMPACT: Future discovery/strategy work under this umbrella should avoid
    overfitting the API to 3 permanent top-level runtime families.
  NEXT: keep creation-discovery and strategy planning aligned to the 2-output
    target and let mutation semantics live in the upstream contract lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Decision Log
- Decision: planner chooses execution semantics; codegen chooses emitted code
  shape.
- Decision: `SpellCodegenPlan` remains the execution-strategy output, not the
  final emitted code artifact.
- Decision: codegen should reconsume both the model and the plan.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: not applicable

## Notes
- DATETIME: 2026-05-31T21:12:49Z
  TYPE: FACT
  CLAIM: The current codegen-creation scaffold only mirrors the planner
    superficially. Planner discovery selects one plan strategy family, but the
    real Phase 13 / `CreationContext` seam is already split across multiple
    codegen-creation responsibilities: no-overrides executor creation, override
    creation packaging, and mutation-override creation packaging. That means
    the next umbrella should capture a multi-strategy creation surface instead
    of one generic `generalized_codegen_creation` placeholder.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py:1-43
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-117
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-43
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-91
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py:57-533
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py:22-3031
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-1346
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-251
  IMPACT: We need a focused follow-on epic that ports current Phase 13 and
    `CreationContext` creation responsibilities into named codegen-creation
    strategies instead of widening the current placeholder strategy.
  NEXT: create the follow-on epic, route it on the board, and keep the first
    implementation slice at discovery + strategy naming only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T20:41:00Z
  TYPE: PLAN
  CLAIM: The next bounded implementation slice is naming and artifact-contract
    cleanup only. The generic `SpellCodegenCreation` / `_spell_codegen_creation`
    wording is too vague for the intended runtime handoff, so this slice will
    rename that surface to `SpellCodegenCreation` /
    `artifact._spell_codegen_creation` while intentionally leaving the current
    placeholder codegen-creation behavior unchanged.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_creation.py:1-57
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-91
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:201-203
  IMPACT: The post-plan codegen layer will use a runtime-facing creation name
    that fits the future `CreationContext` handoff instead of a vague generic
    output label.
  NEXT: rename the container class/file and artifact slot, then stop without
    changing emitted-code behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T19:32:19Z
  TYPE: FACT
  CLAIM: The planner/model discussion clarified that Phase 13 still has real
    optimization room even after planning chooses the execution shape. The
    missing layer is a codegen creation discovery/strategy/system seam that can
    reconsume both `SpellCodegenModel` and `SpellCodegenPlan`.
  EVIDENCE:
  - user_instruction
  IMPACT: This epic now captures the next architectural umbrella instead of
    letting the codegen layer drift back into chat-only context.
  NEXT: review this epic and choose the first bounded implementation slice when
    you want to start the codegen creation work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T19:36:07Z
  TYPE: PLAN
  CLAIM: The first bounded implementation slice under this epic is scaffold
    only. The exact cut is: add one new `codegen_creation/` package with a
    discovery system, strategy contract, strategy builder, placeholder
    generalized strategy, and creation system, then add one generic
    `SpellCodegenCreation` container and park it on `SpellCompilerArtifact`.
    This slice intentionally does not implement Phase 13 emission logic yet.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py:1-54
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-119
  IMPACT: This gives the post-plan codegen layer a real home and keeps future
    emission work from being invented ad hoc inside planner or runtime code.
  NEXT: patch the scaffold objects and artifact slot, then stop without
    implementing emitted-code behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T19:36:07Z
  TYPE: FACT
  CLAIM: The first codegen creation scaffold is now landed. A new
    `codegen_creation/` layer exists with `CodegenCreationDiscoverySystem`,
    `SpellCodegenStrategy`, `SpellCodegenStrategyBuilder`, one placeholder
    `SpellGeneralizedCodegenCreationStrategy`, and `CodegenCreationSystem`.
    The generic artifact-owned `SpellCodegenCreation` container is also added and
    parked on `SpellCompilerArtifact` as `_spell_codegen_creation`. The scaffold
    consumes both `artifact._spell_codegen_model` and
    `artifact._spell_codegen_plan`, but intentionally stops short of Phase 13
    emitted-code behavior.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_creation.py:1-57
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-53
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_strategy.py:1-47
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_strategy_builder.py:1-78
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_codegen_creation_strategy.py:1-67
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-100
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:1-562
  IMPACT: The post-plan codegen layer now has a real architectural home, so
    future emitted-code work can target this layer directly instead of
    overloading planner or runtime binder surfaces.
  NEXT: choose the first real emitted-code implementation slice when you want
    to start codegen behavior work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T20:10:10Z
  TYPE: PLAN
  CLAIM: The next implementation order for this epic is now explicit. First,
    replace the placeholder generalized codegen creation strategy with a real
    emitted-code strategy for the no-overrides lane that consumes the
    generalized lane plan and produces concrete codegen output payloads.
    Second, cut the current Phase 13 no-overrides executor consumers over to
    `artifact._spell_codegen_creation`. Third, add the real overrides and
    mutation-overrides emitted-code strategies. Fourth, add discovery ranking
    logic once the generalized emitted forms are real enough to compare against
    specialized alternatives.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_codegen_creation_strategy.py:1-67
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-100
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py:1-1755
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py:1-2869
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1253
  IMPACT: Post-compaction work can start from one concrete sequence instead of
    reopening the architecture discussion about where codegen discovery,
    emitted-code strategies, and runtime cutover should happen.
  NEXT: when work resumes, take the no-overrides emitted-code strategy as the
    first bounded implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic captures the next architectural umbrella after the current compiler
ownership reorganization: a distinct codegen creation discovery/strategy/system
layer that consumes both `SpellCodegenModel` and `SpellCodegenPlan` so Phase 13
style optimization has a clean home. The immediate next slice is no-overrides
emitted-code behavior in the generalized codegen creation strategy, followed by
Phase 13/runtime consumer cutover to `artifact._spell_codegen_creation`, then the
real overrides and mutation-overrides emitted-code strategies, and only after
that discovery ranking or specialized alternatives.
