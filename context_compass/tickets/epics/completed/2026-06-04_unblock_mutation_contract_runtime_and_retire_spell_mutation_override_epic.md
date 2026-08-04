Completed: 2026-06-06T18:18:17Z
Summary: Closed after the mutation contract / spell mutation override cleanup lane converged: MutationContract was stripped out of the compiler/runtime path, mutation override became a spell-local overlay consumed through the normal override path, and the phase 9-11 / CreationContext seam was cleaned and hot-path-restored.

# Epic: Unblock MutationContract Runtime And Retire Spell Mutation Override

## Metadata
- Epic ID: EPIC-2026-06-04-unblock-mutation-contract-runtime-and-retire-spell-mutation-override
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-05T00:05:03Z
- Updated: 2026-06-06T18:18:17Z
- Updated: 2026-06-05T22:52:54Z
- Target Window: 2026-Q2
- Related Program/Initiative: runtime contract correction for mutation-capable dependency holes

## Problem / Opportunity
Current mutation behavior is split across two different mental models:

- `SpellContract`
  - late-bound dependency hole
  - build/conjure is allowed in dynamic mode
  - meld fails when the hole cannot be resolved
  - once resolution is possible, meld forces revalidation and proceeds

- `MutationContract` plus `Spell.mutation_override`
  - the socket is currently blocked by Phase 4 with
    `MUTATION_CONTRACT_DISABLED`
  - when that gate is bypassed, the spell can still baseline-meld and the
    constructor receives the raw `MutationContract` object
  - a later spell-owned `mutation_override` can rewire the path if a mutation
    socket exists

That split is too inconsistent.

The desired model is:
- `MutationContract` should live in the same semantic space as `SpellContract`
  as a late-bound runtime hole
- the difference is that mutation bindings are expected to change over time and
  revalidation should make those changes visible on later melds
- a spell should not successfully meld while its mutation-capable socket is
  still unresolved
- the current spell-owned `mutation_override` overlay model should be retired
  rather than remain the long-term contract surface

## Context
We now have direct experimental proof of the current mismatch:

- post-conjure `mutation_override` works when a `MutationContract` socket
  exists and rewires the later meld path
- without a `MutationContract` socket, the same post-conjure
  `mutation_override` fails at runtime with `No mutation sockets found...`
- before any override is applied, a baseline meld on the mutation-capable host
  still succeeds and hands the raw `MutationContract` object into the
  constructor

That baseline behavior is the part that no longer fits the desired model.

## MRP Alignment (Most Reasonable Product)
The MRP is:
- unblock `MutationContract` from the current Phase 4 blanket disable path
- make unresolved `MutationContract` sockets behave like `SpellContract`
  holes at meld time
- drive mutation changes through revalidation and normal runtime resolution
- retire the spell-owned `mutation_override` overlay API as the primary model

The MRP is not:
- full mutation research rollout
- speculative optimizer work
- broad redesign of all override systems at once

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a new epic to record that
  `MutationContract` should be unblocked and should behave more like
  `SpellContract`, while the current spell-owned `mutation_override` model
  should be stripped out.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell.py`
  - `src/melder/aether/conduit/meld/contracts/mutation_contract.py`
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/meld/overrides/graph_mutator.py`
  - `src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/`
  - `tests/experimentation/test_mutation_override_requires_mutation_contract_experiment.py`
  - `tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-10_implement_mutation_contract_runtime_socket_management_epic.md`
  - `tickets/epics/2026-05-10_design_mutation_research_runtime_surfaces_epic.md`
  - `tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md`
- EXIT_GATE:
  - the semantic mismatch between `SpellContract` and `MutationContract` is
    documented clearly
  - the target runtime behavior is explicit
  - the retirement direction for spell-owned `mutation_override` is explicit
  - follow-on work can start without guessing at the intended contract
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the user wants to keep the
  spell-owned `mutation_override` overlay as a permanent public surface.

## Goals (Outcomes)
- Unblock `MutationContract` from the current blanket disabled posture.
- Make unresolved mutation sockets fail at meld time the same way unresolved
  contract holes do.
- Allow mutation-capable bindings to be changed later through revalidation
  instead of through a special persistent spell-owned overlay model.
- Remove the semantic split where a mutation-capable spell can baseline-meld
  with a raw `MutationContract` object still sitting in the constructor slot.

## Non-Goals (Explicit Exclusions)
- No full mutation research implementation in this epic.
- No broad Rust/performance work in this epic.
- No unrelated `SpellContract` semantics change in this epic.
- No broad override-system redesign unless needed by the mutation contract fix.

## Scope Boundaries
- In scope:
  - `MutationContract` validation posture
  - meld-time unresolved-hole behavior
  - mutation-specific revalidation semantics
  - the contract-level retirement plan for spell-owned `mutation_override`
- Out of scope:
  - mutation research branch/history tooling
  - crystallizer rollout
  - public benchmark positioning

## Requirements
- `MutationContract` sockets must no longer be treated as "disabled forever"
  by default.
- A spell with unresolved mutation-capable sockets may build/conjure in
  dynamic mode, but must not successfully meld until the hole is satisfied.
- Changing the mutation binding later must remain possible and should drive
  revalidation rather than mutate live instances silently.
- The current spell-owned `mutation_override` overlay model must be treated as
  transitional and scheduled for removal.

## Acceptance Criteria
- The repo has a durable epic describing the target semantics clearly.
- The difference between current and desired mutation behavior is source-backed
  and explicit.
- The experiment proof is referenced as evidence for the current mismatch.
- The board routes active work to this epic.

## Risks / Mitigations
- Risk: removing the current spell-owned overlay model may require changes
  across analyzer, planner, and codegen creation.
  - Mitigation: keep this epic semantic-first and decompose implementation
    later.
- Risk: unblocking `MutationContract` may surface deeper runtime assumptions.
  - Mitigation: use the existing experimentation proof and add focused runtime
    tests before widening the rollout.

## Validation Plan
- Not run for this ticket creation slice.
- Existing experimentation proof:
  - `tests/experimentation/test_mutation_override_requires_mutation_contract_experiment.py`

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new epic to record that
  mutation-capable sockets should behave more like spell-contract late-bound
  holes and that the current spell-owned `mutation_override` model should be
  retired.

## Architecture Decision
### Current `SpellContract` model
- allowed to build/conjure in dynamic mode
- unresolved hole fails at meld
- successful resolution forces revalidation and proceeds

### Current `MutationContract` model
- blocked by `MUTATION_CONTRACT_DISABLED`
- when bypassed experimentally:
  - post-conjure mutation rewiring works if a mutation socket exists
  - no mutation socket fails at meld with `No mutation sockets found...`
  - baseline meld still injects the raw `MutationContract` object, which is
    not the desired end-state semantics

### Target model
- `MutationContract` should be a late-bound hole like `SpellContract`
- no successful meld while unresolved
- changing the mutation binding later is allowed and should trigger
  revalidation
- spell-owned `mutation_override` should not remain the long-term public model
- once that contract is corrected, phase 11 should not need a permanent third
  top-level `mutation_overrides_creation` output family; it should build the
  correct `override_creation` for the current spell state

## Initial Implementation Order
1. Remove the Phase 4 blanket disabled posture for `MutationContract`.
2. Decide the exact unresolved-hole meld error semantics for mutation sockets.
3. Add direct runtime/component tests for unresolved mutation-hole behavior.
4. Replace the current spell-owned mutation overlay model with the intended
   late-bound runtime path.
5. Reconcile planner/codegen creation outputs with that corrected mutation
   contract model.

## Applicable Anti-Patterns
- [ ] Do not leave `MutationContract` both "disabled" and "runtime-capable" at once.
- [ ] Do not keep the raw `MutationContract` object flowing into user
      constructors as a long-term accepted runtime behavior.
- [ ] Do not redesign mutation research and runtime semantics in one step.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Noting Behavior
- Epic notes should capture:
  - current-vs-target mutation contract semantics
  - proof surfaces
  - implementation sequencing only

## Notes
- DATETIME: 2026-06-05T00:05:03Z
  TYPE: FACT
  CLAIM: Current mutation behavior is internally inconsistent with the current
    `SpellContract` late-bound hole model. The experimentation proof shows
    that post-conjure mutation rewiring works when a mutation-capable socket
    exists and fails when no mutation socket exists, but baseline meld can
    still inject the raw `MutationContract` object when no override has been
    applied. That baseline behavior is the semantic mismatch.
  EVIDENCE:
  - tests/experimentation/test_mutation_override_requires_mutation_contract_experiment.py:1-437
  - src/melder/aether/spellbook/spell.py:1146-1231
  - src/melder/aether/conduit/meld/meld.py:766-858
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:29-129
  IMPACT: Mutation-capable sockets need a clear target contract before phase
    11 and mutation runtime work can converge cleanly.
  NEXT: define the exact unresolved-hole runtime contract and the retirement
    path for spell-owned `mutation_override`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T00:14:04Z
  TYPE: DECISION
  CLAIM: Once `MutationContract` is corrected to behave like a late-bound
    hole, mutation is no longer a reason to keep a permanent third top-level
    phase-11 runtime output family. Mutation-aware rebuilding still matters,
    but it should select/build the correct `override_creation` for the current
    spell state instead of forcing `mutation_overrides_creation` to remain
    first-class forever.
  EVIDENCE:
  - tests/experimentation/test_mutation_override_requires_mutation_contract_experiment.py:1-437
  - codex/context_compass/tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md:1-320
  IMPACT: This runtime contract correction directly simplifies the target
    phase-11 output surface.
  NEXT: keep the mutation contract fix and the phase-11 output convergence work
    explicitly linked.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T22:52:54Z
  TYPE: FACT
  CLAIM: The live compiler/runtime seam is now very explicit. Phases 1-7 are
    still the foundational structural/system pipeline, but phases 8-11 are no
    longer old occurrence/injection/patch/execution-plan builders in practice.
    They are thin wrappers over:
    - phase 8 `SpellAnalyzer`
    - phase 9 `SpellArtifactProcessor`
    - phase 10 `SpellCodegenPlanner`
    - phase 11 `CodegenCreationSystem`
    Then `CreationContextBuilder` rehydrates the flattened
    `_spell_codegen_creation` handoff into route-specific runtime config, and
    generic `Meld` now mainly owns spell resolution, structural/resolution
    gating, SpellContract-triggered revalidation, and dispatch into the
    spell-bound `CreationContext`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:20-20
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:16-16
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:16-16
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-17
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:399-399
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:741-741
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:794-794
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:15-15
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:38-38
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-123
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:446-446
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:607-607
  - src/melder/aether/conduit/meld/meld.py:42-42
  - src/melder/aether/conduit/meld/meld.py:466-466
  - src/melder/aether/conduit/meld/meld.py:532-532
  - src/melder/aether/conduit/meld/meld.py:704-704
  - src/melder/aether/conduit/meld/meld.py:764-764
  IMPACT: The mutation contract cleanup should target the real current seam,
    not the old blueprint mental model. If mutation becomes a late-bound hole
    like SpellContract, the meaningful place to simplify is the phase-11
    handoff and the CreationContext route model, because that is where runtime
    behavior is actually packaged now.
  NEXT: compare the current SpellContract revalidation path in `Meld` against
    the current MutationContract + mutation overlay path, then decide what has
    to move upstream into validation/build versus what should stay in the
    phase-11/runtime handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T23:01:12Z
  TYPE: FACT
  CLAIM: The current mutation model is split across four separate live seams,
    which is exactly why the behavior feels incoherent. Right now mutation is
    represented as:
    - spell-owned persistent overlay state on `Spell`
    - a Phase-4 hard disable for `MutationContract`
    - analyzer-time mutation dependency rewriting in the occurrence graph
    - a separate mutation-specific phase-11 runtime handoff lane
    That means the system is simultaneously saying "mutation is blocked",
    "mutation is spell-owned overlay state", and "mutation gets its own
    downstream compiler/runtime packaging."
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1106-1229
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:125-128
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:718-718
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1218-1235
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:12-12
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:47-53
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:122-136
  IMPACT: The mutation epic is not just about changing one contract class. It
    has to collapse duplicated semantics across validation, analyzer,
    codegen-planning, phase-11 output, and runtime binders.
  NEXT: read the mutation-contract, spell-contract, graph-mutator, and
    analyzer mutation override paths directly to decide which part should
    become the real late-bound-hole source of truth.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T23:21:22Z
  TYPE: FACT
  CLAIM: The current planner and phase-11 creation packaging still treat
    mutation as a first-class always-available third lane. The generalized
    planner always builds `no_overrides`, `overrides`, and
    `mutation_overrides`, and the current codegen-creation discovery chain
    always includes the mutation-overrides strategy when the generalized plan
    is selected. That means the downstream compiler/runtime still assumes the
    mutation lane exists structurally, even before we decide whether mutation
    should really collapse into the normal override lane after late-bound-hole
    resolution.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:43-60
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:12-26
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system.py:41-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:52-86
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_mutation_overrides_codegen_creation_strategy.py:49-108
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:47-53
  IMPACT: Retiring spell-owned `mutation_override` is not enough by itself.
    We also need to collapse planner/discovery/creation packaging assumptions
    so mutation stops being baked in as a permanent third output family.
  NEXT: compare this unconditional planner/runtime mutation lane against the
    actual MutationContract late-bound-hole semantics and decide where the
    collapse point should be: analyzer, planner, or phase-11 creation
    packaging.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T23:29:45Z
  TYPE: DECISION
  CLAIM: The target semantic correction is narrower than "remove mutation
    override." The actual goal is to treat `MutationContract` as a special
    late-bound dependency hole that agents can satisfy with any spell binding,
    while keeping it modifiable over time. In other words:
    - unresolved mutation socket: spell may exist structurally, but meld must throw
    - resolved mutation socket: meld may proceed
    - later mutation rebinding: mark the spell dirty, clear runtime shape, and
      force revalidation again
    This differs from `SpellContract` mainly in mutability policy, not in the
    fact that an unresolved hole must block successful meld.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:764-917
  - src/melder/aether/spellbook/spell.py:1146-1229
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:47-128
  IMPACT: The first implementation target is to make unresolved
    `MutationContract` sockets fail like unresolved `SpellContract` holes at
    meld time. API removal or replacement decisions are secondary and should
    not be confused with the semantic contract.
  NEXT: inspect how `SpellContract` late-bound failure and revalidation work,
    then mirror that runtime contract for mutation sockets while preserving the
    ability to rebind them later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T09:05:33Z
  TYPE: FACT
  CLAIM: The current `SpellContract` lifecycle is now explicit enough to use
    as the direct mirror target.
    1. Phase 1 classifies `SpellContract` defaults as a dedicated DI shape.
    2. Phase 2/3 keep them as metadata-only sockets in the symbolic graph and
       local topology instead of resolving them into normal DAG edges.
    3. Phase 4 allows missing providers only in dynamic mode and marks the
       lineage `gated` with `contract_unvalidated`.
    4. The occurrence/analyzer and artifact-processor layers can resolve
       contracted providers and thread those results into downstream graph/model
       state.
    5. At runtime, `Meld._check_contracts_and_force_revalidation(...)` inspects
       the live contract defaults again, fails meld if the contract still has
       no provider, and when a provider exists it gates conduit-local
       resolution so phases 5-11 rerun.
    6. Contract-link changes dirty only the affected consumer lineages through
       `SpellSystemStates.mark_contract_dependents_dirty(...)`, and
       `ConduitWard` also clears cached creations for those impacted consumers.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1049-1073
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:806-919
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:220-387
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:143-201
  - src/melder/aether/conduit/meld/meld.py:764-917
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1110-1189
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1830-1878
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:780-794
  IMPACT: The mutation fix can be implemented as a mirror of a known working
    contract path instead of inventing a new runtime model. The key delta is
    mutability: mutation bindings are allowed to change later, but unresolved
    sockets still must not meld.
  NEXT: align `MutationContract` to the same phase/runtime lifecycle, but swap
    the contract-link source of truth for the mutation-binding source of truth
    and keep `invalidate_spell(...)` as the direct spell-local dirty/reset hook
    when mutation rebinding occurs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T10:24:45Z
  TYPE: FACT
  CLAIM: Phase 9 already computes enough mutation truth for phase 10 to select
    the right baseline strategy, but phase 10 is not using that truth yet.
    Current processor/model surfaces already expose:
    - `graph_shape.mutation_override_dependency_count`
    - `mutation_targeting_shape`
    - `spell_runtime_shape` with live runtime spell records
    So a planner strategy can already tell whether mutation is active for the
    current graph. The current issue is that phase 10 discovery/strategy still
    unconditionally builds a permanent third `mutation_overrides_plan` family
    instead of selecting which strategy fills the stable
    `no_overrides_plan` / `overrides_plan` outputs.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:64-88
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_mutation_targeting_processor_strategy.py:58-122
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:51-100
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py:24-40
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:43-60
  IMPACT: Phase 9 does not require a mandatory redesign before the next step.
    The real downstream work is phase 10 strategy selection and output shape.
    An explicit processor-owned mutation-baseline flag may still be useful for
    cleanliness, but it is optional, not required.
  NEXT: change phase 10 so it uses current processor/model truth to select the
    correct baseline strategy into `no_overrides_plan` and keep `overrides_plan`
    as the secondary runtime override path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T17:35:40Z
  TYPE: FACT
  CLAIM: The downstream convergence is now materially landed. The compiler no
    longer carries mutation as a first-class lane through phases 9-11, and the
    generalized phase-11 chain is now extended with
    `general_creation_context_codegen_creation` as a finalizer that converts
    the earlier generalized phase-11 strategy outputs into the real runtime
    handoff shape:
    - `no_overrides_executor`
    - `overrides_executor`
    `CreationContext` has been slimmed down to a thin runtime dispatcher, and
    meld front doors now call its public `execute(...)` / `execute_no_hooks(...)`
    surface instead of reaching into internal compiled-door fields.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-55
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-370
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-62
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-138
  - src/melder/aether/conduit/meld/conduit_meld.py:229-279
  - src/melder/aether/conduit/meld/spellspace_meld.py:238-288
  IMPACT: The old mutation-specific downstream runtime family is gone on the
    compiler/creation-context seam, and the runtime now reflects the
    overlay-first mutation model directly.
  NEXT: decide whether to run broader sanity validation or start closing the
    mutation convergence lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic records the desired semantic correction: `MutationContract` should
behave more like `SpellContract` as a late-bound runtime hole, except mutation
bindings are expected to change over time and drive revalidation. The current
spell-owned `mutation_override` model is treated as transitional and should be
retired. That convergence is now materially in place on the compiler and
creation-context seam: phase 11 emits only the two final runtime doors
(`no_overrides_executor`, `overrides_executor`) and meld uses a thin
CreationContext dispatcher over them.
