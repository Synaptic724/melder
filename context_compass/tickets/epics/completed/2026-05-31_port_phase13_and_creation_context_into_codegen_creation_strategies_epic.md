# Epic: Port Phase 13 And CreationContext Into Codegen Creation Strategies

## Metadata
- Epic ID: EPIC-2026-05-31-port-phase13-and-creation-context-into-codegen-creation-strategies
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-05-31T21:14:33Z
- Updated: 2026-06-01T11:05:49Z
- Target Window: 2026-Q2
- Related Program/Initiative: Add codegen creation discovery and strategy

## Problem / Opportunity
The current codegen creation layer does not actually mirror the planner seam.

Current state:
- planner is a real facade:
  - discovery reads `SpellCodegenModel`
  - builder resolves the selected strategy
  - strategy populates `SpellCodegenPlan`
- codegen creation is only a scaffold:
  - discovery returns one generic `generalized_codegen_creation`
  - builder resolves one placeholder strategy
  - that strategy only writes metadata into `SpellCodegenCreation`
- the real runtime responsibilities we need are still split across old
  Phase 13 emitters and `CreationContext` / `CreationContextBuilder`

That means the codegen creation system still does not own the thing it is
supposed to own:
- building the runtime-ready creation artifacts from:
  - `SpellCodegenModel`
  - `SpellCodegenPlan`

The opportunity is to mirror the planner pattern properly:
- keep `CodegenCreationSystem` as the facade
- keep `CodegenCreationDiscoverySystem` as the selector
- keep `SpellCodegenStrategyBuilder` as the registry owner
- replace the one fake generic strategy with the concrete creation strategies
  implied by the current runtime:
  - generalized no-overrides codegen creation
  - generalized overrides codegen creation
  - generalized mutation-overrides codegen creation

## MRP Alignment (Most Reasonable Product)
The MRP is not "rewrite all of Phase 13 and delete CreationContext."

It is:
- keep `CreationContext` as the runtime binder/dispatcher
- move the spell-static compiler-ish packaging work into codegen creation
- let discovery choose which creation strategies to run
- output one `SpellCodegenCreation` artifact that contains the runtime-ready
  pieces `CreationContextBuilder` needs

That gives us the missing ownership seam without forcing a whole runtime
rewrite in one pass.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to mirror the planner/discovery pattern
  in the codegen creation system and to start from the current Phase 13 /
  `CreationContext` responsibilities rather than inventing new semantics.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-31_add_codegen_creation_discovery_and_strategy_epic.md`
  - `tickets/epics/2026-05-31_reorganize_phase8_to_phase11_compiler_ownership_epic.md`
- EXIT_GATE:
  - the codegen creation seam mirrors planner ownership clearly
  - discovery selection and strategy execution are explicit
  - the first bounded implementation order is explicit
  - `SpellCodegenCreation` is identified as the compiler-owned handoff artifact
    to `CreationContextBuilder`
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current runtime split
  proves we need a different lane decomposition than
  no-overrides / overrides / mutation-overrides.

## Goals (Outcomes)
- Make codegen creation mirror the planner pattern honestly.
- Replace the single placeholder generalized strategy with the concrete
  strategy surfaces that match the current runtime.
- Treat `SpellCodegenCreation` as the artifact-owned handoff object that
  `CreationContextBuilder` should consume.
- Move spell-static creation packaging responsibility out of
  `CreationContextBuilder` and `CreationContext` over time.

## Non-Goals (Explicit Exclusions)
- No planner contract rewrite in this epic.
- No analyzer or processor redesign in this epic.
- No full `CreationContext` deletion in this epic.
- No broad runtime cutover in the same first slice.
- No discovery ranking experiments beyond the simple default selection rule.

## Scope Boundaries
- In scope:
  - codegen creation discovery result shape
  - codegen creation strategy registry shape
  - concrete generalized strategy naming
  - mapping old Phase 13 / `CreationContext` responsibilities into strategies
  - `SpellCodegenCreation` as the artifact-owned creation handoff
- Out of scope:
  - deleting old Phase 13 files in this planning slice
  - deep runtime dispatch redesign
  - changing override semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to start from the current
  planner/discovery objects and build the next codegen creation umbrella around
  the real Phase 13 / `CreationContext` responsibilities.

## Architecture Decision
### Planner
- planner chooses execution semantics
- planner outputs `SpellCodegenPlan`

### Codegen Creation
- codegen creation chooses which creation strategies to execute
- codegen creation consumes:
  - `SpellCodegenModel`
  - `SpellCodegenPlan`
- codegen creation outputs:
  - `SpellCodegenCreation`

### CreationContext
- `CreationContext` should remain the runtime binder/dispatcher
- it should not remain the owner of broad spell-static codegen packaging logic
- it may still keep tiny per-call runtime specialization behavior where that
  is genuinely call-shape-dependent

## Current Runtime Seam We Need To Port
### Compiler-owned today
- Phase 13 no-overrides executor compilation
- artifact-held `_phase13_no_overrides_executor`
- artifact-held `_phase13_no_overrides_executor_signature`

### CreationContext-owned today
- override route config assembly
- mutation override route config assembly
- override patch-map handoff
- override specialization cache
- override emitted-source cache
- override code-object cache
- override prefilter metadata cache
- last-shape / last-executor hot reuse
- lazy override specialization compilation

This is the split we need to reorganize.

## Desired Discovery Contract
The current codegen creation discovery result is too narrow because it only
returns one selected strategy id.

We need discovery to choose the strategy chain to execute.

Recommended direction:
- `CodegenCreationDiscovery`
  - `selected_strategy_ids: Tuple[str, ...]`
  - `discovery_reason: str`

Initial default rule:
- when planner selected `generalized_codegen_plan`
- codegen creation discovery selects:
  - `generalized_creation_context_setup_codegen_creation`
  - `generalized_no_overrides_codegen_creation`
  - `generalized_overrides_codegen_creation`
  - `generalized_mutation_overrides_codegen_creation`

This keeps the selection model simple while still mirroring the real lane split.

## Desired Strategy Names
Do not keep one vague generic `generalized_codegen_creation` strategy.

Use names that match the real current runtime responsibilities:
- `generalized_creation_context_setup_codegen_creation`
- `generalized_no_overrides_codegen_creation`
- `generalized_overrides_codegen_creation`
- `generalized_mutation_overrides_codegen_creation`

Those names tell the truth about what each strategy packages.

## Required Strategy Set
Current recommendation: **4 strategies** for the first honest port.

### 1. `generalized_creation_context_setup_codegen_creation`
Purpose:
- port the shared spell-static builder inputs that are currently assembled in
  `CreationContextBuilder` before lane payloads are attached

Outputs:
- `resolve_route_key`
- `fast_transient_no_overrides_enabled`

Current source seam:
- `CreationContextBuilder._resolve_route_key(...)`
- `CreationContextBuilder._resolve_fast_transient_no_overrides_enabled(...)`
- `CreationContextBuilder._coerce_fast_transient_route_eligibility(...)`

Why this is separate:
- these values are top-level creation-context inputs shared by all lanes
- they are not specifically no-overrides / overrides / mutation payloads

### 2. `generalized_no_overrides_codegen_creation`
Purpose:
- port the current compiler-owned no-overrides Phase 13 packaging into the
  codegen-creation layer

Outputs:
- `no_overrides_creation`
  - compiled no-overrides executor
  - executor signature / compile provenance

Current source seam:
- `CompilerPhase13.compile_no_overrides_executor(...)`
- `CompilerPhase13.compile_no_overrides_executor_from_plan(...)`
- `CompilerPhase13.compile_no_overrides_executor_from_payload(...)`
- `phase13_no_overrides_executor.py`

Why this remains one strategy:
- transient-unrolled versus step-emitted compile is still one lane and should
  stay one strategy body for now

### 3. `generalized_overrides_codegen_creation`
Purpose:
- port the non-mutation override packaging that is currently assembled in
  `CreationContextBuilder` and then consumed by `CreationContext`

Outputs:
- `overrides_creation`
  - `override_patch_map_phase10`
  - non-mutation `OverrideRouteConfig`
  - optional baseline override executor when we decide to prebuild it

Current source seam:
- `CreationContextBuilder._resolve_override_patch_map_phase10(...)`
- `CreationContextBuilder._build_override_route_config(..., execution_ir_key=\"overrides\")`
- the spell-static route-config fields already consumed by `CreationContext`

Why this is one strategy:
- this is the "same graph, patched inputs" lane
- spell-static packaging is coherent even if some runtime-shape specialization
  stays inside `CreationContext` initially

### 4. `generalized_mutation_overrides_codegen_creation`
Purpose:
- port the mutation-aware override packaging into the codegen-creation layer

Outputs:
- `mutation_overrides_creation`
  - mutation-lane `OverrideRouteConfig`
  - optional mutation-lane baseline override executor when we decide to
    prebuild it

Current source seam:
- `CreationContextBuilder._build_mutation_override_route_config(...)`
- `CreationContextBuilder._build_override_route_config(..., execution_ir_key=\"overrides_with_mutations\")`

Why this is separate:
- mutation overrides are graph-rewrite semantics, not plain socket-value
  substitution
- they should stay distinct from the non-mutation override lane in strategy
  and payload naming

## Not In The First Strategy Count
These are real concerns, but they should **not** become first-pass strategies
yet:
- emitted override-source caching
- emitted override code-object caching
- last-shape hot reuse
- per-call override socket-shape specialization

Reason:
- those are runtime specialization details
- they may stay partly inside `CreationContext`
- port them only after the main spell-static creation contract is stable

## Desired `SpellCodegenCreation` Contract
`SpellCodegenCreation` should become the compiler-owned runtime handoff object.

Recommended top-level fields:
- `selected_strategy_ids`
- `discovery_reason`
- `resolve_route_key`
- `fast_transient_no_overrides_enabled`
- `no_overrides_creation`
- `overrides_creation`
- `mutation_overrides_creation`
- `metadata`

### Why these top-level fields exist
- `resolve_route_key`
  - `CreationContextBuilder` currently derives this directly from spell
    existence and passes it into `CreationContext` as the route selector.
- `fast_transient_no_overrides_enabled`
  - `CreationContextBuilder` currently computes this from spell/static plan
    state to decide whether the no-overrides door may use the fast transient
    lane.
- `selected_strategy_ids` / `discovery_reason`
  - mirror planner provenance, but now for the creation layer.

### Current spell-static inputs `CreationContextBuilder` assembles today
These are the real outputs we need to formalize because they are already the
spell-static handoff contract in code:
- `no_overrides_executor`
- `override_patch_map_phase10`
- `override_route_config_no_mutation`
- `override_route_config_mutation`

That is the actual seam to port, not a guessed future abstraction.

### Concrete lane payload expectations

#### No-Overrides Creation
- compiled no-overrides executor
- executor signature / compile provenance

This mirrors the current compiler-owned Phase 13 output:
- `artifact._phase13_no_overrides_executor`
- `artifact._phase13_no_overrides_executor_signature`

#### Overrides Creation
- Phase 10 override patch map artifact
- override route config for the non-mutation lane
- optional baseline override executor for empty override payloads

Current route-config fields already proved by `OverrideRouteConfig`:
- `plan_signature`
- `path_registry`
- `plan_rows`
- `root_spell_id`
- `spell_lookup`
- `empty_shape_key`
- `baseline_executor`

#### Mutation-Overrides Creation
- mutation-lane override route config
- optional mutation-lane baseline executor

Current route-config shape is the same object family as the plain override
lane, but sourced from the mutation-aware execution IR.

### What should remain in `CreationContext`
`CreationContext` should remain the runtime binder/dispatcher, not the broad
spell-static packaging owner.

Keep here:
- dynamic environment / creation gate ownership
- `caller_creations` / `owner_creations` runtime handling
- choosing which already-built lane to dispatch for one call
- splitting root positional override args from targeted override payload
- tiny runtime-only hot cache / last-shape reuse if we still want it

Do not keep here long-term:
- no-overrides executor compilation
- override route-config assembly
- mutation route-config assembly
- broad spell-static codegen packaging policy

## Proposed Implementation Order
1. Update `CodegenCreationDiscovery` to support selected strategy chains
   rather than one placeholder strategy id.
2. Update `CodegenCreationSystem` to resolve and execute an ordered strategy
   chain.
3. Replace `SpellGeneralizedCodegenCreationStrategy` with the four explicit
   generalized creation strategies:
   - creation-context setup
   - no-overrides
   - overrides
   - mutation-overrides
4. Port current `CreationContextBuilder` setup fields into
   `generalized_creation_context_setup_codegen_creation`.
5. Port current Phase 13 no-overrides compile packaging into the
   generalized no-overrides codegen creation strategy.
6. Port current `CreationContextBuilder._build_override_route_config(...)`
   packaging into the generalized overrides codegen creation strategy.
7. Port current mutation override route packaging into the generalized
   mutation-overrides codegen creation strategy.
8. Refactor `CreationContextBuilder` to consume `artifact._spell_codegen_creation`
   first, while leaving compatibility fallback reads in place until the new
   handoff is trusted.

## Milestones
- [ ] Milestone 1: discovery supports ordered codegen strategy execution
- [ ] Milestone 2: generalized lane strategies replace the placeholder
- [ ] Milestone 3: creation-context setup payload is compiler-owned
- [ ] Milestone 4: no-overrides creation payload is compiler-owned
- [ ] Milestone 5: override and mutation route packaging are compiler-owned
- [ ] Milestone 6: `CreationContextBuilder` reads `SpellCodegenCreation`

## Stories (Required To Complete)
- [ ] Story: redefine codegen creation discovery result shape
- [ ] Story: make codegen creation system execute selected strategy chains
- [ ] Story: add generalized creation-context setup codegen creation strategy
- [ ] Story: add generalized no-overrides codegen creation strategy
- [ ] Story: add generalized overrides codegen creation strategy
- [ ] Story: add generalized mutation-overrides codegen creation strategy
- [ ] Story: point `CreationContextBuilder` at `SpellCodegenCreation`

## Tasks (Cross-Cutting Or Epic-Level)
- [ ] Task: preserve current override semantics while ownership moves
- [ ] Task: keep `CreationContext` thin and runtime-focused
- [ ] Task: avoid overfitting codegen creation back into one giant placeholder
- [ ] Task: keep the first implementation slice bounded to discovery + naming
- [ ] Task: do not split runtime-only specialization details into extra
      strategies before the spell-static creation contract is stable

## Acceptance Criteria (Epic Done)
- The codegen creation layer mirrors the planner discovery/builder/strategy
  seam honestly.
- Strategy names reflect the real runtime lane responsibilities.
- `SpellCodegenCreation` is the explicit compiler-owned handoff object.
- `CreationContextBuilder` can consume the new creation artifact instead of
  owning broad spell-static packaging logic.

## Risks / Mitigations
- Risk: we just move `CreationContext` complexity into one generic codegen
  creation strategy.
  - Mitigation: split by the real runtime lanes from the start.
- Risk: discovery is still too coarse.
  - Mitigation: start with ordered strategy ids and keep ranking simple.
- Risk: we over-move runtime-shape-specific logic that really belongs at call
  time.
  - Mitigation: keep tiny per-call specialization behavior in
    `CreationContext` when it is genuinely runtime-only.

## Applicable Anti-Patterns
- [ ] No single fake generic codegen creation strategy that hides all lanes.
- [ ] No planner re-deciding code emission here.
- [ ] No `CreationContext` runtime binder owning broad compiler packaging logic forever.
- [ ] No broad runtime cutover in the same first slice.

## Validation / Test Approach
- Planning only in this epic.
- The first implementation slice should stop at:
  - discovery contract
  - builder execution contract
  - strategy naming / registration
- Not run.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-01T10:30:01Z
  TYPE: FACT
  CLAIM: The live codegen-creation surface is now phase13-clean. Active `src/`
    and touched tests no longer expose `phase13` helper names, emitted symbol
    names, or runtime/docstring wording on the overrides/no-overrides executor
    compile path. The only remaining `Phase 13` references are in historical
    system-doc patch artifacts that describe earlier migration slices.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/generalized_overrides_codegen_creation_compiler.py:1-2550
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1700
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:720-840
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:110-1320
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:430-820
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:1-1280
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:800-1410
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:1-30
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1570-1598
  IMPACT: Future reads of the live compiler/runtime path should no longer
    mistake codegen-creation executor compilation for a separate Phase 13. Any
    remaining `Phase 13` hits now point to historical patch notes, not active
    runtime ownership.
  NEXT: keep any further cleanup focused on true behavior drift or historical
    patch-doc archival, not on live-code naming repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:25:34Z
  TYPE: FACT
  CLAIM: The object-shape cleanup is now in. `SpellCodegenCreation` directly
    owns the spell-static creation fields instead of delegating to extra lane
    payload classes, the non-strategy helper modules are back at package root,
    only the actual strategy implementations remain under
    `codegen_creation/strategies/`, and `CompilerPhase12` now runs
    `CodegenCreationSystem` so the live new path actually produces
    `artifact._spell_codegen_creation` before `CreationContextBuilder` is
    asked to consume it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_creation.py:1-142
  - src/melder/aether/spellbook/spell_compiler/codegen_creation:directory_listing
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies:directory_listing
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-132
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-90
  IMPACT: The new creation seam is now structurally coherent and live-wired.
    The next migration should target the remaining old compiler-path fields and
    callers rather than more creation-package reshaping.
  NEXT: identify and remove the remaining direct legacy compiler-path users of
    `_execution_plan_phase11*`, `_phase13_no_overrides_executor*`, and old
    Phase 10 compatibility fields.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:18:16Z
  TYPE: PLAN
  CLAIM: The next correction slice is object-shape cleanup, not more behavior.
    `SpellCodegenCreation` should directly own the spell-static creation fields
    instead of delegating to extra lane payload data objects, and only actual
    strategies should live under `codegen_creation/strategies/`. This slice
    will flatten the lane payloads into `SpellCodegenCreation`, move the
    compiler helper modules back out of `strategies/`, and repoint the current
    strategies plus `CreationContextBuilder` to that flattened contract.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation:directory_listing
  IMPACT: The codegen-creation package shape will match the planner pattern
    more honestly: one artifact object, one facade/discovery/builder seam, and
    strategies only in the strategy folder.
  NEXT: flatten `SpellCodegenCreation`, remove the extra lane payload classes,
    relocate non-strategy helpers, and stop after imports are clean.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:14:03Z
  TYPE: FACT
  CLAIM: The current `codegen_creation/` layout drifted. The package root should
    stay focused on the facade/discovery/builder/contracts plus the final
    `SpellCodegenCreation` artifact. The lane-specific modules added during the
    Phase 13 port (`generalized_*_compiler.py` and the per-lane creation
    payload classes) should not stay at package root; they should move under
    `codegen_creation/strategies/` so the package shape matches the planner
    rebuild intent more honestly.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation:directory_listing
  IMPACT: The next patch should be structural cleanup only: move the lane-
    specific creation modules under `strategies/` and repoint imports without
    changing behavior.
  NEXT: move the lane-specific creation/payload/compiler modules into
    `codegen_creation/strategies/`, then stop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:12:03Z
  TYPE: FACT
  CLAIM: The new system is now off the old Phase 13 blueprint-module imports.
    The Phase 13 helper code has been ported into
    `codegen_creation/generalized_no_overrides_codegen_creation_compiler.py`
    and `codegen_creation/generalized_overrides_codegen_creation_compiler.py`,
    and the new-system imports now point there. In the same slice,
    `CreationContextBuilder` was cut over to consume
    `artifact._spell_codegen_creation`, and the overrides creation payload now
    carries a compiler-owned `SpellOverrideTargetingCodegenCreation` bridge
    instead of the old runtime `OverridePatchMap`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/generalized_no_overrides_codegen_creation_compiler.py:1-1755
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/generalized_overrides_codegen_creation_compiler.py:1-2869
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:1-135
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_overrides_codegen_creation_strategy.py:1-194
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-132
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1360
  IMPACT: The remaining legacy surfaces are now the old compiler-path fields
    and callers, not the new codegen-creation / creation-context seam.
  NEXT: remove or isolate the remaining direct compiler-path dependencies on
    `_phase13_no_overrides_executor`, `_phase13_no_overrides_executor_signature`,
    and old Phase 10/11 artifact fields now that the new runtime seam no
    longer consumes them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:10:38Z
  TYPE: PLAN
  CLAIM: The next bounded migration seam is ownership of the actual Phase 13
    helper modules themselves. The new codegen-creation strategies and
    `CreationContext` seam are still importing old blueprint helpers directly,
    so the next step is to port the no-overrides and overrides Phase 13 helper
    modules into the codegen-creation package and repoint the new-system
    imports there. The old blueprint files can stay for the old compiler path
    until substitution, but the new system should stop importing them.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:1-135
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:16-27
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py:1-1755
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py:1-2869
  IMPACT: This gets the new system off the old blueprint module imports before
    we worry about deleting the old compiler path.
  NEXT: port the two Phase 13 helper modules into `codegen_creation/`, repoint
    the new-system imports, and stop without deleting the old compiler-facing
    files yet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:03:52Z
  TYPE: FACT
  CLAIM: The Phase 10 bridge and `CreationContextBuilder` cutover are now in.
    The overrides creation strategy builds a new
    `SpellOverrideTargetingCodegenCreation` artifact from
    `model.override_targeting_shape`, and `CreationContextBuilder` no longer
    reads `_phase13_no_overrides_executor`, `_override_patch_map_phase10`, or
    old exported execution IR from the compiler artifact. It now consumes
    `artifact._spell_codegen_creation` as the spell-static creation handoff.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_override_targeting_codegen_creation.py:1-314
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_overrides_codegen_creation_strategy.py:1-194
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-132
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-1346
  IMPACT: The runtime builder seam is now on the new creation artifact. The
    next legacy deletion work is no longer blocked on `CreationContextBuilder`;
    it is blocked on the remaining old compiler-phase artifact fields and any
    still-live direct callers of those old outputs.
  NEXT: identify and remove the remaining direct runtime/compiler dependencies
    on `_phase13_no_overrides_executor`, `_phase13_no_overrides_executor_signature`,
    and old Phase 10/11 compatibility artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T21:47:40Z
  TYPE: FACT
  CLAIM: The full Phase 13-side generalized creation chain is now landed.
    `CodegenCreationDiscoverySystem` returns an ordered strategy chain, the
    creation system executes that chain, and all 4 generalized strategies now
    exist:
    setup, no-overrides, overrides, and mutation-overrides. The no-overrides
    strategy compiles directly from the generalized lane plan, and the
    overrides / mutation-overrides strategies now build spell-static
    `OverrideRouteConfig` payloads and baseline empty-shape override
    executors directly from the generalized lane plans instead of old exported
    IR. The remaining seam is the Phase 10 patch-map bridge plus
    `CreationContextBuilder` cutover.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-71
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-99
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_strategy_builder.py:1-91
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:1-92
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:1-135
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_overrides_codegen_creation_strategy.py:1-194
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_mutation_overrides_codegen_creation_strategy.py:1-186
  IMPACT: Codegen creation now mirrors the planner seam on the Phase 13 side.
    The next migration no longer needs to invent strategy structure; it needs
    to decide whether to cut `CreationContextBuilder` over first or port the
    remaining Phase 10 patch-map bridge first.
  NEXT: choose the next bounded seam: `CreationContextBuilder` cutover to
    `artifact._spell_codegen_creation`, or direct port of the Phase 10
    patch-map bridge into the new creation artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T21:39:59Z
  TYPE: FACT
  CLAIM: The first bounded codegen-creation port slice is landed. The creation
    artifact contract is now formalized around
    `selected_strategy_ids`, `discovery_reason`, `resolve_route_key`,
    `fast_transient_no_overrides_enabled`, and the 3 lane homes
    (`no_overrides_creation`, `overrides_creation`,
    `mutation_overrides_creation`). Codegen creation discovery now returns an
    ordered strategy chain, the creation system executes that chain, and the
    first 2 generalized strategies are real:
    `generalized_creation_context_setup_codegen_creation` and
    `generalized_no_overrides_codegen_creation`. The no-overrides strategy now
    compiles the runtime callable directly from the generalized lane plan using
    the old Phase 13 no-overrides compiler, without lifting a legacy
    `ExecutionPlan`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_creation.py:1-100
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_no_overrides_codegen_creation.py:1-65
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_overrides_codegen_creation.py:1-66
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_mutation_overrides_codegen_creation.py:1-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-71
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-99
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_strategy_builder.py:1-87
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:1-92
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:1-135
  IMPACT: The codegen-creation layer now has a real artifact contract plus a
    real Phase 13-first migration seam. The remaining work is the override and
    mutation lanes, then `CreationContextBuilder` cutover.
  NEXT: choose whether the next bounded slice ports the non-mutation override
    lane or the mutation-override lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T21:34:14Z
  TYPE: PLAN
  CLAIM: The first implementation cut under this epic should do 3 things only:
    formalize the `SpellCodegenCreation` object contract, keep that explicit
    slot on `SpellCompilerArtifact`, and start the real Phase 13 migration on
    the safest lane first: `generalized_no_overrides_codegen_creation`.
    `CreationContextBuilder` should remain untouched in this cut except for
    future-facing contract comments if needed.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-05-31_port_phase13_and_creation_context_into_codegen_creation_strategies_epic.md:150-244
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:22-244
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:33-112
  IMPACT: We get one real compiler-owned creation lane without widening into
    the more complex override and mutation packaging seams too early.
  NEXT: patch the creation object + artifact slot contract, then implement the
    no-overrides creation strategy and stop there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T21:18:50Z
  TYPE: PLAN
  CLAIM: The first honest port needs 4 codegen-creation strategies, not 1 and
    not an explosion of micro-strategies. One setup strategy ports the shared
    `CreationContextBuilder` inputs (`resolve_route_key`,
    `fast_transient_no_overrides_enabled`), and then 3 lane strategies port the
    actual no-overrides / overrides / mutation-overrides creation payloads.
    Runtime-only specialization details like last-shape hot reuse and lazy
    override code-object/source caching should stay out of the first strategy
    count.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:33-112
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:176-251
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:22-244
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:585-1346
  IMPACT: We now have a bounded strategy count and an implementation order that
    ports the real spell-static creation seams without prematurely exploding the
    runtime-only specialization logic into extra creation strategies.
  NEXT: iterate on this 4-strategy decomposition with the user, then implement
    the discovery result shape and strategy registration first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T21:18:50Z
  TYPE: FACT
  CLAIM: The concrete `SpellCodegenCreation` handoff is now source-backed.
    `CreationContextBuilder` currently assembles four spell-static inputs:
    `no_overrides_executor`, `override_patch_map_phase10`,
    `override_route_config_no_mutation`, and
    `override_route_config_mutation`. Those are the real outputs we need to
    port under the codegen-creation layer. The additional top-level
    `resolve_route_key` and `fast_transient_no_overrides_enabled` values are
    also part of the current handoff because `CreationContext` consumes them at
    construction time.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:33-112
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:176-251
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:22-244
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:180-356
  IMPACT: The next implementation slice can work from the real handoff
    contract instead of a guessed future object model.
  NEXT: keep the first codegen-creation implementation slice focused on
    discovery result shape plus strategy registration around these concrete
    outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T21:14:33Z
  TYPE: FACT
  CLAIM: The current planner seam is already the right pattern to mirror:
    discovery selects, builder resolves, strategy populates the artifact-owned
    plan container. The creation layer does not yet do that honestly because
    it still exposes one placeholder `generalized_codegen_creation` strategy
    while the real runtime responsibilities are already split between
    Phase 13 no-overrides compilation and `CreationContext` override /
    mutation-override packaging.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py:1-43
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-117
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:1-109
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-43
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-91
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/spell_codegen_strategy_builder.py:1-66
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py:57-533
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-251
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-1346
  IMPACT: The next real codegen-creation work should mirror the planner
    contract and split strategies by the actual runtime lanes instead of
    widening the placeholder scaffold.
  NEXT: route this epic on the board and keep the first implementation slice
    at discovery contract + strategy naming only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic exists because the next codegen-creation step is no longer "invent a
placeholder." The planner seam is already correct: discovery chooses, builder
resolves, strategy populates the artifact-owned result. Codegen creation must
mirror that, but it needs multiple generalized strategies because the real
runtime seam is already split across:
- no-overrides executor creation
- overrides creation packaging
- mutation-overrides creation packaging

The first bounded implementation slice under this epic should stop at the
discovery result shape, codegen-creation system chain execution, and strategy
naming / registration. It should not widen into emitted-code behavior yet.

