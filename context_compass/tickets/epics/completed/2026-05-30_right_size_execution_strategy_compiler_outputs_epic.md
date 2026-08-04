Completed: 2026-06-20T15:28:05Z
Summary: Umbrella for right-sizing compiler outputs via a strategy-selection
  phase. Locked contract landed: phase 9 truth-only (SpellCodegenModel), phase 10
  discovery + plan families, phase 11 discovery selects one concrete codegen
  style, SpellCodegenCreation kept narrow (no_overrides_executor +
  overrides_executor), direct CreationContext hot path restored. Child lanes
  (port_phase13, reorganize_phase8_11, group_codegen_creation) all landed. Two
  execution-strategy design artifacts retained as reference. Closed per user
  direction.

# Epic: Right-Size Execution Strategy Compiler Outputs

## Metadata
- Epic ID: EPIC-2026-05-30-right-size-execution-strategy-compiler-outputs
- Status: in_progress
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T14:58:15Z
- Updated: 2026-06-07T08:40:54Z
  Updated (effective): 2026-06-07T08:40:54Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder runtime performance optimization

## Problem / Opportunity
The current `phase 10 -> 12 -> CreationContext` compiler/runtime seam is
already better than a generic interpreter-style runtime, but it is still too
middle-of-the-road.

Today:
- Phase 10 builds patch targeting truth.
- Phase 11 builds raw execution-plan truth and some shape/metric outputs.
- Current Phase 13 compiles the no-overrides lane and leaves significant
  strategy/customization pressure to later layers.
- `CreationContext` still acts partly like a runtime binder and partly like a
  late strategy/customizer surface.

That means the final emitted code still carries too much generic branch logic:
- existence handling
- reuse vs create
- lock strategy
- registration strategy
- contract payload merge behavior
- override target count handling
- generic helper dispatch where more exact emission should be possible

The opportunity is to introduce a real compiler-owned execution strategy stage
between raw plan truth and final executor emission, so the compiler chooses the
best executor family earlier and `CreationContext` becomes thinner.

## MRP Alignment (Most Reasonable Product)
The MRP here is not a whole compiler rewrite.

It is:
- keep the existing compiler phases and artifacts that already work
- add one explicit strategy-selection/right-sizing layer
- move compiler-owned output data to compiler-owned artifacts
- make final executor emission consume an explicit strategy artifact instead of
  rediscovering shape ad hoc

That yields a better output compiler without destabilizing the whole runtime.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a new epic for the strategy-driven
  compiler direction after the existing spellspace/conduit runtime lane, and
  the active board is cleaned so this epic becomes the next clean umbrella.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/phases/`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/`
  - `src/melder/aether/conduit/meld/creation_context/`
  - `src/melder/aether/spellbook/spell.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - direction artifacts and tickets under `codex/context_compass/`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
  - `tickets/tasks/2026-05-30_move_execution_plan_metrics_to_spell_compiler_artifact_task.md`
  - `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
- EXIT_GATE:
  - one explicit strategy-phase design exists between current Phase 11 and
    current Phase 13
  - compiler-owned shape/strategy outputs are mapped to artifact ownership
  - the target role of new Phase 12, current Phase 13, and `CreationContext`
    is explicit
  - a bounded implementation order exists
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the right-sizing direction
  requires abandoning the current plan system instead of extending it.

## Goals (Outcomes)
- Define one explicit compiler-owned strategy-selection/right-sizing phase.
- Keep raw execution-plan truth separate from strategy-family selection.
- Make final executor emission a narrower, more deterministic backend phase.
- Thin `CreationContext` from late strategy surface into a runtime binder of
  chosen outputs.
- Create an extensible architecture where new compiler strategies can be added
  deliberately instead of leaking into generic runtime code.

## Non-Goals (Explicit Exclusions)
- No full compiler rewrite from scratch.
- No scheduler redesign.
- No spellspace runtime ownership redesign in this epic.
- No broad public API redesign.
- No immediate source implementation in this epic by default.

## Scope Boundaries
- In scope:
  - strategy-phase insertion after current Phase 11
  - current Phase 13 backend role and future Phase 12 insertion
  - strategy artifact design
  - no-overrides vs overrides family design
  - `CreationContextBuilder` and `CreationContext` consequence analysis
  - exact compiler-owned output ownership
- Out of scope:
  - transaction/dev-ops redesign
  - unrelated conduit pooling work
  - spellspace ownership lane except where it constrains strategy design

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new umbrella epic for the
  execution-strategy compiler direction.

## Success Metrics
- We have an explicit answer for what new Phase 12 does.
- We have an explicit answer for what current Phase 13 does.
- We have an explicit answer for how `CreationContext` changes.
- We have an explicit strategy-artifact design and initial strategy families.
- The direction is concrete enough to split into bounded implementation tasks.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify the current producer/consumer chain for execution-plan metrics
  - define the new strategy artifact
  - define strategy-selection inputs
  - define final emitter inputs/outputs
  - define `CreationContext` post-strategy role
- Non-functional:
  - no handwaving about performance wins
  - no pretending the current compiler is fully generic trash
  - no pretending the current compiler is already maximally specialized
  - keep the design extensible so new strategies are easy to add later

## Constraints / Assumptions
- Current Phase 11 remains the raw execution-plan builder.
- Current Phase 13 is the current no-overrides backend compiler surface.
- `CreationContext` currently binds no-overrides executors, patch maps, and
  override specialization machinery.
- `execution_plan_dispatch_route` is still a live runtime consumer on `Spell`
  for now.
- Compiler-owned output metrics should live on `SpellCompilerArtifact`.

## Dependencies / External References
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py`
- `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py`
- `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- `src/melder/aether/spellbook/spell.py`
- `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`

## Proposed Target Model
### Phase 10
- Keep as patch-map targeting truth.

### Phase 11
- Keep as raw execution-plan builder and plan-truth producer.
- Also produce shape inputs on `SpellCompilerArtifact`.

### New Phase 12
- Strategy-selection / right-sizing phase.
- Consume:
  - plan truth
  - patch-map truth
  - artifact-owned shape metrics
  - route/override/contract/lock/registration shape data
- Produce:
  - strategy family selection
  - emitter family selection
  - strategy artifact rows/hints for final emission

### Concrete Phase 12 Shape
Phase 12 should not be a vague selector. It should be a compiler-owned system
with explicit class roles:

- `SpellExaminationBuilder`
  - builds the examination inputs and any normalized intermediate views needed
    by the examination system from current artifact truth
- `SpellExaminationStrategy`
  - one examination strategy rule/family matcher
  - consumes the current spell/compiler truth
  - contributes or selects the best codegen candidates
- `SpellExaminationSystem`
  - the Phase 12 orchestrator
  - runs the examination strategies over the spell/compiler inputs
  - owns the ordered evaluation flow and conflict/priority handling
- `SpellCodegenPlanStrategyBuilder`
  - lowers accepted examination results into compile-ready codegen plan
    structures
- `SpellCodegenPlanStrategy`
  - one plan-shaping strategy that turns examination outcomes into concrete
    codegen-ready families/hints/rows

The key point:
- the examination layer and the codegen-plan shaping layer both belong inside
  Phase 12
- they are not separate phases
- Phase 12 is the full right-sizing pipeline

### Phase 12 Output Contract
Phase 12 should output a fully formed compiler-owned codegen strategy plan,
not just loose metrics or labels.

That output should be complete enough that:
- current Phase 13 can consume it directly
- `CreationContext` can bind the results cleanly
- no later layer has to rediscover what the compiler already knew

Working-name output artifact:
- `SpellCodegenPlan`

That artifact should eventually carry things like:
- selected no-overrides strategy family
- selected overrides strategy family
- later selected mutation strategy family
- lowered step strategy rows
- lock/register/override/call-mode compile hints
- emitter-family identity
- fallback reason when a generic path is required

### Current Phase 13
- Final executor emission/compile phase.
- Consume the strategy artifact.
- Emit the exact chosen no-overrides / overrides backend.

### Output Simplification Direction
The older transition shape implicitly carried 3 top-level runtime families:
- no-overrides
- overrides
- mutation-overrides

The cleaner target is 2:
- `no_overrides_creation`
- `override_creation`

Mutation-aware behavior still matters, but once mutation-capable sockets are
treated as late-bound holes, mutation should affect upstream build selection
rather than require a permanent third top-level emitted family.

### Migration Model
The current scaffold should not become a permanent adapter above the old
planning pipeline.

The intended migration is:
- extend the new processor/planner stack until it becomes authoritative
- treat current Phases `8-11` as temporary migration oracles and parity
  references
- allow the new processor to spend meaningful compiler work deriving a better
  model from earlier compiler truth when that yields stronger plan selection
- replace the old `8-11` planning path once the new model and planner can
  stand on their own
- then remake the current Phase 13 surface as a pure backend emitter over the
  chosen `SpellCodegenPlan`

This means the long-term target is not "Phase 12 consumes old plans forever."
It is "Phase 12 becomes the replacement planning architecture."

### Concrete Phase 13 Shape
Phase 13 is not another selector. It is the backend-emitter layer.

Current design direction:
- `SpellCodegenStrategy`
  - one backend emission strategy family
- `SpellCodegenBuilder`
  - binds/builds the concrete backend-emitter inputs for one selected plan
- `SpellCodegenCreatorSystem`
  - orchestrates backend creation/compile from the Phase 12 codegen plan

The key rule:
- Phase 13 should not be re-deciding graph family or runtime shape
- it should just take the Phase 12 codegen plan and emit the final backend
- if Phase 13 still needs to guess broadly, Phase 12 did not do enough

### CreationContext
- Stop behaving like a late customizer.
- Bind the chosen compiler outputs.
- Keep runtime cache/binding responsibility only.

## Strategy Direction
The new strategy phase should support a growing registry of compile-time
families rather than one generic backend.

Likely family dimensions:
- no-overrides vs overrides
- transient-unrolled vs step-plan
- caller singleton vs shared singleton vs spellspace singleton
- small-plan vs large-plan
- lockless vs creations-lock vs spell-lock+creations-lock
- contract-heavy vs contract-light
- override target count `0 / 1 / 2 / many`
- root positional override present / absent
- `CALLN` fallback
- generic fallback

The best part of this direction is extensibility:
- when new strategy ideas show up later, add them to the strategy phase
- benchmark them
- keep or kill them
- do not pollute generic runtime code paths with every new idea

### Strategy Layering Rule
There are two distinct strategy layers, both necessary:

1. Phase 12 examination + plan-shaping strategies
- decide what kind of spell/runtime graph this is
- decide what codegen plan family fits it best

2. Phase 13 backend emission strategies
- take the already-chosen codegen plan
- emit/compile the correct backend for that family

This prevents the main failure mode:
- Phase 12 collapsing into another generic Phase 11
- or Phase 13 having to rediscover shape and strategy too late

## Milestones (Track Progress)
- [ ] Milestone 1: Producer/consumer ownership cleanup
  - compiler-owned output fields live on compiler artifacts
- [ ] Milestone 2: Strategy artifact definition
  - one explicit artifact and strategy-phase contract exists
- [ ] Milestone 3: Phase 12 class scaffold
  - `SpellExaminationBuilder`, `SpellExaminationSystem`,
    `SpellExaminationStrategy`, `SpellCodegenPlanStrategyBuilder`, and
    `SpellCodegenPlanStrategy` are explicit in role and data flow
- [ ] Milestone 4: Strategy family design
  - initial no-overrides and overrides strategy families are explicit
- [ ] Milestone 4: `CreationContext` consequence map
  - runtime binder role is explicit enough for implementation slicing

## Stories (Required to Complete)
- [ ] Story: STORY-2026-06-06-phase10-solo-and-many-only-discovery
  Add `solo` and `many_only` as explicit phase-10 categories using the new
  phase-8/9 existence-occurrence model section.
- [ ] Story: Define the new strategy-phase contract and artifact surface.
- [ ] Story: Scaffold Phase 12 around `SpellExaminationBuilder`,
      `SpellExaminationSystem`, and `SpellExaminationStrategy`.
- [ ] Story: Scaffold Phase 12 codegen-plan shaping around
      `SpellCodegenPlanStrategyBuilder` and `SpellCodegenPlanStrategy`.
- [ ] Story: Define no-overrides right-sizing families and emitter choices.
- [ ] Story: Define overrides right-sizing families and specialization flow.
- [ ] Story: Thin `CreationContext` and `CreationContextBuilder` to the new binder role.
- [ ] Story: Introduce the new strategy phase between current Phase 11 and current Phase 13.
- [ ] Story: Keep current Phase 13 narrow as the backend emitter role.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Keep execution-plan metric ownership on compiler artifact surfaces.
- [ ] Task: Document the strategy artifact fields and producer/consumer surfaces.
- [ ] Task: Document the first 10-20 strategy families and selection dimensions.
- [ ] Task: Define a benchmark plan to compare old outputs against right-sized outputs.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The strategy phase has a concrete role and artifact definition.
- Current Phase 11, new Phase 12, current Phase 13, and `CreationContext` have
  non-overlapping responsibilities.
- The direction is detailed enough to start bounded implementation slices.

## Risks / Mitigations
- Risk: strategy explosion creates unreadable compiler code.
  - Mitigation: use explicit strategy families with a single selector surface.
- Risk: expected speed gains are overstated.
  - Mitigation: define benchmark-backed validation before claiming large wins.
- Risk: `CreationContext` stays half-strategist, half-binder.
  - Mitigation: make the post-strategy role explicit before implementation.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No compiler-rewrite claims without source-backed producer/consumer mapping.
- [ ] No closure while the strategy artifact and implementation order are still vague.

## Validation / Test Approach
- Investigation/design only by default.
- Future implementation should compare:
  - old output code shape
  - new strategy-selected output code shape
  - runtime performance on hot no-overrides and hot overrides families

## Rollout / Adoption Plan
- First: clean old spellspace/conduit lane routing.
- Second: finish ownership cleanup for compiler outputs.
- Third: define the strategy artifact.
- Fourth: define and land the strategy-selection phase.
- Fifth: keep current Phase 13 narrow while the new Phase 12 is introduced above it.

## Open Questions
- Which shape fields belong directly on the strategy artifact versus the raw plan artifact?
- How many strategy families are worth the first implementation cut?
- Should no-overrides and overrides use one shared strategy artifact or two sibling artifacts?
- Should Phase 12 emit one unified `SpellCodegenPlan` or lane-specific sibling
  plan artifacts that still roll up under one compiler-owned top-level result?

## Decision Log
- Decision: do not throw away the current compiler.
- Decision: add a strategy/right-sizing phase rather than stuffing more logic
  into current Phase 13 or `CreationContext`.
- Decision: keep the design extensible so new strategy ideas are additive.
- Decision: Phase 12 owns both examination and codegen-plan shaping; those are
  not separate phases.
- Decision: Phase 13 is the backend-emitter layer and may have its own backend
  strategies, but it should not re-decide runtime shape.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
  - `artifacts/2026-05-30_phase12_north_star_runtime_model.md`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: user-directed after direction acceptance

## Notes
- DATETIME: 2026-06-06T19:02:19Z
  TYPE: DECISION
  CLAIM: The formal phase 9-11 contract is now locked tighter than the older
    Phase 12 / Phase 13 design notes. The current intended split is:
    - phase 9 computes processor-owned truth only (`SpellCodegenModel`)
    - phase 10 discovery chooses the **plan family** from that truth and may
      also record the bounded set of candidate codegen styles the family allows
    - phase 11 discovery chooses the concrete **codegen style** for the chosen
      plan family and builds the final runtime handoff
    The critical boundary is that `SpellCodegenCreation` does **not** widen
    into a style-report object. Its real contract remains only:
    - `no_overrides_executor`
    - `overrides_executor`
    Any selected codegen style is provenance only and should live in metadata,
    not as a new top-level runtime contract field.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-274
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:1-25
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-84
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-119
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:1-22
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-70
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:1-114
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-69
  IMPACT: This finally separates structural planning from concrete emitter
    choice without polluting the runtime handoff. Future family expansion
    should attach to this split instead of reopening the runtime contract.
  NEXT: reorganize the current generalized phase 10 and phase 11 strategy
    bodies into smaller named groups behind this now-locked discovery/ownership
    contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T00:14:08Z
  TYPE: FACT
  CLAIM: The epic now has concrete implementation progress behind the earlier
    architecture notes. Up to this point we have:
    - landed the generalized phase-11 family migration with one family facade,
      one state object, ordered internal steps, and the wrapper layer removed
    - moved genuinely shared phase-11 helpers into
      `codegen_creation_system/shared_assets/`
    - added phase-8 `SpellExistenceOccurrenceAnalysis`
    - exposed that section in phase 9 as `model.existence_occurrence_shape`
    - started the bounded phase-10 expansion by defining a dedicated story for
      `solo` and `many_only`
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_codegen_creation_strategy.py:1-76
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:1-312
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py:1-30
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_existence_occurrence_processor_strategy.py:1-55
  - tickets/stories/2026-06-06_phase10_solo_and_many_only_discovery_story.md:1-118
  IMPACT: The epic now contains both the architectural target and the durable
    record of the concrete compiler normalization work already landed.
  NEXT: implement the new phase-10 `solo` and `many_only` category selectors
    under the linked story, then let phase 11 consume those families later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:02:19Z
  TYPE: FACT
  CLAIM: The hot-path restore is now part of the architectural guardrail for
    this epic. The earlier phase-11 finalizer had added wrapper closures and
    per-call `created` probes around the runtime doors. That shape was removed.
    The direct `CreationContext` hooks/no-hooks compiled doors are restored,
    while the heavy override specialization work stays spell-static and
    phase-11-owned. That means any future phase 10-11 refactor under this epic
    should preserve:
    - `CreationContext` as the direct runtime binder
    - `SpellCodegenCreation` as the spell-static executor handoff
    - no wrapper/probe rediscovery around the final runtime doors
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-283
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-117
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:4-1103
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-533
  - codex/context_compass/tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md:1148-1288
  IMPACT: The next decomposition work must stay behind the restored direct
    runtime seam. If later strategy regrouping widens the `CreationContext`
    hot path again, it is architectural regression, not neutral cleanup.
  NEXT: treat the current `CreationContext` handoff as fixed while we split the
    large generalized strategy bodies into smaller groups.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:51:58Z
  TYPE: DECISION
  CLAIM: The first concrete decomposition map is now locked. Phase 10 should
    be treated as 5 planner responsibilities:
    - plan family discovery
    - plan shell bootstrap
    - no-overrides lane build
    - overrides lane build
    - plan finalization/provenance
    Phase 11 should be treated as 6 creation responsibilities:
    - creation discovery
    - shared route/setup facts
    - no-overrides executor build
    - overrides static-input packaging
    - overrides runtime specialization build
    - final CreationContext handoff write
    Under the current live code, phase 10 already has discovery and shell
    bootstrap separated, but still collapses both lane builds into one
    generalized plan strategy. Phase 11 already has discovery plus setup,
    no-overrides, and overrides-static strategies, but still collapses the
    override-runtime build and final handoff write into the fat
    `general_creation_context_codegen_creation` finalizer.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:21-130
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:8-46
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:13-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-71
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:13-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:20-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:24-205
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:34-709
  IMPACT: The remodel now has a bounded extraction order instead of generic
    "break up the big files" language. We can split phase 10 first without
    touching the runtime handoff, then split the fat phase-11 finalizer once
    cleaner lane ownership is in place.
  NEXT: make the first bounded implementation slice the phase-10 breakup:
    extract one no-overrides lane-plan strategy, one overrides lane-plan
    strategy, and one small planner finalizer while keeping the existing
    discovery contract and `SpellCodegenPlan` shape fixed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:58:28Z
  TYPE: FACT
  CLAIM: The family-vs-style split is now documented directly in the phase
    discovery code, not just in tickets. Phase 10 discovery docs now say it
    chooses the planning family and bounded style allow-list. Phase 11
    discovery docs now say it chooses the concrete codegen style and ordered
    creation chain for that already-selected family. `SpellCodegenCreation`
    still keeps style as metadata provenance only and does not widen the
    top-level runtime handoff.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:6-30
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_strategy.py:12-48
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_system.py:13-64
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:8-39
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:6-23
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:6-26
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_strategy.py:15-47
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_system.py:16-61
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-39
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:6-23
  IMPACT: This reduces future architectural drift. The next refactor slices can
    decompose planner and creation strategy bodies without relitigating which
    phase owns family selection versus style selection.
  NEXT: keep the discovery object contracts fixed while splitting the big phase
    10 and phase 11 strategy bodies underneath them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:14:34Z
  TYPE: DECISION
  CLAIM: Phase 11 should now be normalized around **family packages**, not the
    current flat top-level strategy/helper mix. Discovery should select one
    family strategy for the already-chosen phase-10 plan family. That family
    strategy should then execute an explicit ordered batch of named internal
    steps over one explicit build-state object to produce the final
    `SpellCodegenCreation`. This means the current generalized helper/compiler
    modules are not the wrong functionality, but they are in the wrong
    structural place when they are family-specific. The intended generalized
    family shape is:
    - one `generalized` family folder
    - one family strategy
    - one build-state object
    - explicit named steps:
      - setup / route facts
      - no-overrides executor build
      - override targeting artifact build
      - override route-input packaging
      - override baseline executor build
      - override runtime specialization build
      - final output write
    The phase-11 root should keep only shared contracts, discovery, the system
    facade, and the final output artifact shape.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy.py:14-30
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:13-95
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:6-24
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-39
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:13-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:20-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:24-205
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:34-709
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_no_overrides_codegen_creation_compiler.py:1-176
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_overrides_codegen_creation_compiler.py:1-419
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_override_targeting_codegen_creation.py:1-252
  IMPACT: This changes the remodel target from "split the big finalizer" to
    "promote phase 11 into family-strategy packages with explicit internal
    steps and build state." That is the right normalization before adding more
    real families beyond `generalized`.
  NEXT: define the concrete generalized family folder layout and decide whether
    the existing `SpellCodegenStrategy` contract becomes the family-strategy
    contract or remains the inner step-level contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:24:02Z
  TYPE: DECISION
  CLAIM: The family-package split now has a root/shared/family boundary. The
    phase-11 root should keep only discovery contracts/systems/builders, the
    family-strategy interface, the creation-system facade, the final
    `SpellCodegenCreation` output object, and an optional
    `shared_strategy_assets/` area for truly cross-family helpers. The current
    helper compilers are not shared enough for the root:
    - `generalized_no_overrides_codegen_creation_compiler.py`
    - `generalized_overrides_codegen_creation_compiler.py`
    They should move under the `generalized` family package because they compile
    generalized-family executor shapes. The current
    `spell_override_targeting_codegen_creation.py` should also be treated as
    generalized-family-local unless a second family later proves it belongs in
    shared assets.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_no_overrides_codegen_creation_compiler.py:57-1875
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_overrides_codegen_creation_compiler.py:22-2979
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_override_targeting_codegen_creation.py:47-252
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  IMPACT: This prevents phase 11 from normalizing into a misleading
    "shared-by-default" root where generalized-family code still dominates the
    top-level directory under a generic name.
  NEXT: keep `shared_strategy_assets/` minimal and explicitly define the
    generalized family folder contents before moving code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T00:14:04Z
  TYPE: DECISION
  CLAIM: The right-sized phase-11 output target is simpler than the older
    3-family transition shape. The target should converge to only
    `no_overrides_creation` and `override_creation`, with mutation-aware
    behavior treated as an upstream contract/revalidation/build concern.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md:1-320
  - codex/context_compass/tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md:1-260
  IMPACT: This narrows the target output surface and should make later
    specialization work easier to benchmark and reason about.
  NEXT: keep future right-sizing work aligned to the 2-output target instead of
    designing around a permanent mutation-specific top-level runtime family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T08:06:23Z
  TYPE: MEASURE
  CLAIM: The current benchmark evidence shows that the existing late
    planning/backend stack is expensive enough to justify replacement rather
    than permanent extension. In the depth-9 hotpath benchmark, the current
    conjure path reported `51.567ms` total, with `root_blueprints` at
    `13.037ms`, `execution_plan` at `4.708ms`, and `executor_compile` at
    `18.246ms`. That does not make Phase 11 alone the single slowest named
    phase, but it does show that the old `8-11` planning plus current backend
    compile path is a major compiler cost center.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_hotpath_profiles.py:49-49
  - benchmarks/testing_other_di/test_melder_hotpath_profiles.py:134-147
  - benchmarks/testing_other_di/test_melder_hotpath_profiles.py:203-227
  - user_benchmark_output
  IMPACT: The epic should optimize toward replacing the old planning/backend
    path with the new processor/planner/emitter architecture instead of
    preserving the old plan builder indefinitely.
  NEXT: keep future model and strategy work focused on making the new planning
    stack authoritative.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T08:06:23Z
  TYPE: DECISION
  CLAIM: The current migration direction is now explicit: extend the new
    `artifact_processor` and `codegen_planner` properly, let them become the
    real planning architecture, then replace the old `8-11` planning phases
    and remake the current Phase 13 surface as a pure emitter over the chosen
    plan.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:45-524
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:37-240
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:35-243
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:595-880
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:80-94
  IMPACT: The epic now distinguishes between short-term compatibility and the
    real end-state. The new planning stack is not meant to sit permanently on
    top of the old one.
  NEXT: reflect this replacement model in the retained strategy artifacts so
    later work does not fall back into "consume old plans forever" thinking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T22:03:39Z
  TYPE: FACT
  CLAIM: The north-star runtime philosophy now has its own dedicated artifact.
    It captures the narrower end-state we are optimizing toward: Phase 12
    chooses the spell's runtime/codegen pattern, Phase 13 emits it, the
    spell-owned runtime binder holds the resulting pattern plus
    creations-owner surfaces, and `Meld` either takes a sealed fast path or
    jumps directly into the exact bound callable pack.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/artifacts/2026-05-30_phase12_north_star_runtime_model.md
  IMPACT: The epic now has both the broader compiler-direction artifact and a
    narrower runtime north-star artifact, so later work can reference the right
    level without overloading one document.
  NEXT: Keep future Phase 12 and Phase 13 work aligned to this runtime target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T22:03:39Z
  TYPE: DECISION
  CLAIM: The north-star runtime target is now explicit in the supporting
    direction artifact. The intended end state is that `Meld` either creates on
    a sealed fast path or jumps directly into a spell-owned bound runtime tool,
    while the spell-owned runtime binder holds the chosen codegen pattern and
    the concrete creations-owner surfaces for that pattern. Phase 12 chooses
    that pattern, Phase 13 emits it, and the runtime stops carrying generic
    late decision pressure.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/artifacts/2026-05-30_execution_strategy_compiler_direction.md
  IMPACT: The epic now has a stronger optimization target than "add more
    strategies." It has a concrete end-state runtime model to optimize toward.
  NEXT: Keep future Phase 12 and Phase 13 work aligned to this runtime shape
    instead of preserving generic `CreationContext` behavior by default.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:29:29Z
  TYPE: FACT
  CLAIM: The supporting spirit artifact now captures the concrete Phase 12 and
    Phase 13 class layout the user specified. Phase 12 is explicitly modeled
    around `SpellExaminationBuilder`, `SpellExaminationStrategy`,
    `SpellExaminationSystem`, `SpellCodegenPlanStrategyBuilder`, and
    `SpellCodegenPlanStrategy`, while Phase 13 is explicitly modeled around
    `SpellCodegenStrategy`, `SpellCodegenBuilder`, and
    `SpellCodegenCreatorSystem`.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/artifacts/2026-05-30_execution_strategy_compiler_direction.md
  IMPACT: The epic no longer depends on chat memory for the concrete class
    model and can now hand implementation slices off against the artifact.
  NEXT: start the Phase 12 scaffold against this documented contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T08:40:54Z
  TYPE: FACT
  CLAIM: The active compiler epics and artifacts now line up more tightly with
    the live code than the earlier umbrella notes captured. The top-down
    exploration epic and its strategy artifacts treat phases 1-7 as the heavy
    structural, rooted, validation, and change-control substrate; treat phases
    8-11 as the newer analyzer -> processor -> planner -> spell-static creation
    pipeline; and keep `_spell_codegen_creation` plus
    `CreationContextBuilder -> CreationContext` as the narrow runtime handoff.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md:20-57
  - codex/context_compass/artifacts/2026-06-02_topdown_compiler_exploration_strategy.md:18-133
  - codex/context_compass/artifacts/2026-05-30_execution_strategy_compiler_direction.md:15-139
  - codex/context_compass/artifacts/2026-05-30_phase12_north_star_runtime_model.md:11-89
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:12-123
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:22-313
  IMPACT: The epic now has an explicit bridge from the strategic compiler
    direction docs back down to the live runtime seam. Future family work
    under this umbrella should optimize spell-static packaging and strategy
    selection while preserving the thin `CreationContext` binder model.
  NEXT: keep the `solo` and `many_only` work nested under this stronger
    convergence framing, then use the same framing when phase-11 family
    implementations start.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T14:58:15Z
  TYPE: PLAN
  CLAIM: This epic exists to capture the compiler direction the user asked for:
    keep the current compiler, add a real strategy-selection/right-sizing phase,
    then let final emission compile from a chosen strategy artifact instead of
    relying on a middle-of-the-road generic output path.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:540-547
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:166-170
  IMPACT: Later work can route through one compiler-strategy umbrella instead
    of being rebuilt from chat context.
  NEXT: capture the spirit in one supporting artifact and then clean the older
    spellspace/conduit runtime-ownership lane out of active routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic is the umbrella for making the compiler outputs truly right-sized by
inserting a dedicated strategy-selection phase between current Phase 11 and
current Phase 13, while keeping the renamed Phase 13 as the backend emitter
role.

Latest locked contract:
- phase 9 computes truth only and owns `SpellCodegenModel`
- phase 10 discovery chooses the plan family and may record candidate codegen
  styles on `SpellCodegenPlan`
- phase 11 discovery chooses one concrete codegen style for that plan family
  and emits the final runtime handoff
- `SpellCodegenCreation` remains intentionally narrow:
  - `no_overrides_executor`
  - `overrides_executor`
  Any selected codegen style is provenance in metadata only, not a widened
  runtime contract field.

Latest runtime guardrail:
- the direct `CreationContext` hot path is restored and treated as fixed
- no wrapper/probe layer should be reintroduced around the final runtime doors
- heavy override specialization remains spell-static and phase-11-owned, but
  the final binder/runtime dispatch should stay direct

Locked decomposition map:
- phase 10:
  - discovery
  - plan shell bootstrap
  - no-overrides lane build
  - overrides lane build
  - plan finalization/provenance
- phase 11:
  - discovery selects one family strategy
  - phase-11 root keeps only shared contracts/system/discovery/output surfaces
  - optional `shared_strategy_assets/` is allowed only for truly reused helpers
  - each family strategy owns:
    - explicit build-state object
    - explicit ordered internal step batch
  - current generalized family step targets:
    - shared route/setup facts
    - no-overrides executor build
    - overrides static-input packaging
    - overrides runtime specialization build
    - final CreationContext handoff write

Next refactor slice:
- do **not** widen the runtime contract
- split phase 10 first:
  - extract one no-overrides lane-plan strategy
  - extract one overrides lane-plan strategy
  - extract one small planner finalizer
- keep discovery responsible for family/style selection only, not helper-level
  decomposition
- after phase 10 lane ownership is clean, normalize phase 11 around one
  generalized family package with explicit internal steps and build state
