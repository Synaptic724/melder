Completed: 2026-06-06T18:18:17Z
Summary: Investigation completed and retained as historical context. The later overlay-first direction and MutationContract retirement path superseded this original runtime-socket investigation lane.

# Task: Investigate MutationContract Runtime Socket Feature

## Metadata
- Task ID: TASK-2026-05-10-investigate-mutation-contract-runtime-socket-feature
- Story:
- Epic: EPIC-2026-05-10-implement-mutation-contract-runtime-socket-management
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T19:02:12Z
- Updated: 2026-06-06T18:18:17Z

## Objective
Investigate the exact runtime seams needed to make `MutationContract` into a
real spell-facing mutable socket feature.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a new epic and an investigation
  before implementation.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/contracts/mutation_contract.py`
  - `src/melder/spellbook/spell.py`
  - `src/melder/spellbook/spell_crafter/**`
  - mutation override / graph mutator seams when needed as evidence
- DEPENDENCIES:
  - the new MutationContract epic
- EXIT_GATE: the exact runtime feature shape is clear enough to patch
  deliberately instead of guessing.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the socket metadata is too
  weak and the first feature needs a deeper contract redesign.

## Scope Boundaries
- In scope:
  - mutation socket metadata path
  - current spell-level invalidation behavior
  - graph-mutation relation to MutationContract sockets
- Out of scope:
  - implementation itself
  - full MutationResearch redesign
  - conduit-lineage semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user asked to investigate the feature before
  implementation.

## Steps / Checklist
- [ ] Re-read `mutation_contract.py`.
- [ ] Re-read the SpellCrafter socket metadata path.
- [ ] Re-read the spell mutation-override invalidation path.
- [ ] Record the smallest viable feature shape.

## Deliverables
- evidence-backed first feature shape for MutationContract runtime sockets

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_mutation_contract_runtime_socket_feature_task.md
- codex/context_compass/attention_board.md

## Validation
- Investigation only.

## Risks / Rollback Notes
- Risk: we overstate how much runtime support already exists.
  Rollback: keep the feature description tied directly to the current source
  seams only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No pretending MutationContract already resolves live objects.

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
- DATETIME: 2026-05-10T19:02:12Z
  TYPE: PLAN
  CLAIM: The first investigation has to answer one narrow question: what exact
    runtime state do we already have that could support a spell-facing
    “enumerate mutation sockets / retarget one / mark dirty / re-evaluate”
    feature without redesigning the whole mutation system.
  EVIDENCE:
  - user_instruction: "make an epic and lets invsetigate this and then implement it"
  - recent source read: mutation contract classification + mutation_override invalidation path
  IMPACT: This keeps the first feature slice honest and bounded.
  NEXT: inspect the socket metadata and spell invalidation seams directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T19:28:49Z
  TYPE: FACT
  CLAIM: `mutation_override` is already a real spell-owned mechanism, but it
    is separate from `MutationContract`. The only source-defined write surface
    for it today is `Spell.apply_mutation_override(...)` /
    `Spell.clear_mutation_override(...)` plus the matching `ISpell` contract.
    Those methods clear the spell-owned `CreationContext` and call
    `SpellSystemStates.mark_structural_change(...)`, which gates the index and
    adds it to the dirty-index set. They do **not** check dynamic mode,
    spellframe eligibility, or MutationContract enablement before accepting the
    overlay. The active runtime use is downstream instead: Phase 2/3 still
    treat `MutationContract` sockets as metadata-only, Phase 4 still hard-blocks
    declared `MutationContract` defaults with `MUTATION_CONTRACT_DISABLED`, and
    the occurrence-plan override path later filters and rewires only
    `SocketKind.MUTATION_CONTRACT` sockets when `spell.mutation_override` is
    present.
  EVIDENCE:
  - src/melder/spellbook/spell.py:1574-1646
  - src/melder/utilities/interfaces/ispell.py:196-258
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:476-510
  - src/melder/aether/dev_ops/spell_system_states/spell_system_state.py:449-475
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:1044-1104
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3175-3193
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3440-3465
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3498-3523
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3696-3710
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:97-124
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1393-1545
  - src/melder/spellbook/spell_crafter/dag/socket_kind.py:3-23
  - source_scan: `rg -n "apply_mutation_override\\(|clear_mutation_override\\(" src/melder tests`
  IMPACT: The first real MutationContract feature does not need to replace the
    mutation-override system, but it does need a new runtime path that turns
    declared mutation sockets into a supported spell-facing retargetable
    surface instead of leaving that responsibility to raw overlay dictionaries.
  NEXT: inspect whether the existing public spell artifacts (`symbolic_graph`,
    `resolution_frame`, or local-topology structures) already expose enough
    mutation-socket metadata to build a thin spell-facing enumeration API.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T19:29:52Z
  TYPE: FACT
  CLAIM: The existing runtime already stores enough metadata to enumerate
    MutationContract sockets, but that metadata is not surfaced through a
    dedicated spell-facing API yet. Phase 2 `SpellSymbolicDependency` records
    keep `di_shape`, `contract_key`, and `contract_late_binding`; Phase 3
    `SpellSocketDescriptor` and `SpellLocalTopology` keep `socket_kind`,
    `contract_key`, `contract_late_binding`, and any resolved targets; and
    `SpellSystemStates` publishes that topology by spell index or spell id.
    `Spell` itself publicly exposes `requirements`, `symbolic_graph`, and
    `resolution_frame`, but not local topology or a mutation-socket iterator.
    So the first feature can likely be a thin spell-facing wrapper over
    existing symbolic/topology state rather than a new deep storage seam.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/symbolic_graph/spell_symbolic_dependency.py:12-64
  - src/melder/spellbook/spell_crafter/symbolic_graph/spell_symbolic_dependency.py:94-127
  - src/melder/spellbook/spell_crafter/symbolic_graph/spell_symbolic_dependency.py:238-258
  - src/melder/spellbook/spell_crafter/symbolic_graph/spell_symbolic_graph.py:7-33
  - src/melder/spellbook/spell_crafter/symbolic_graph/spell_symbolic_graph.py:114-133
  - src/melder/spellbook/spell_crafter/topology/spell_local_topology.py:9-75
  - src/melder/spellbook/spell_crafter/topology/spell_local_topology.py:78-190
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:1175-1268
  - src/melder/spellbook/spell.py:871-888
  - src/melder/utilities/interfaces/ispell.py:394-420
  IMPACT: The smallest honest MutationContract runtime feature is probably a
    spell method that reads existing symbolic/topology state and exposes only
    the mutation-socket subset, rather than inventing a second mutation-socket
    registry.
  NEXT: decide whether the first enumeration path should read from
    `symbolic_graph.dependencies`, `SpellSystemStates.get_local_topology(...)`,
    or both.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T19:32:09Z
  TYPE: FACT
  CLAIM: The current mode boundary is split. `MutationResearch` itself is
    explicitly dynamic-only at the conduit surface: normal conduit plus dynamic
    environment are required before `get_mutation_research()` returns anything.
    `mutation_override`, however, is not mode-gated at the `Spell` write
    surface. `Spell.apply_mutation_override(...)` and
    `Spell.clear_mutation_override(...)` accept the overlay, clear creation
    context, and dirty/gate the index without checking system state or
    spellframe posture. The occurrence-plan mutation-override machinery also
    does not add a dynamic-only gate around `_resolve_mutation_override_targets`
    itself; it only insists that the targeted sockets are
    `SocketKind.MUTATION_CONTRACT`. So today the write path is broader than the
    intended mutation-research access path.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3971-4005
  - src/melder/spellbook/spell.py:1574-1646
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:476-510
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1191-1199
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1201-1228
  IMPACT: If we want MutationContract to become a real supported feature, we
    need to choose whether its spell-facing socket mutation path should follow
    the current broad `mutation_override` setter semantics or be tightened to
    the same dynamic-only posture used by conduit-level MutationResearch.
  NEXT: answer the user's mode question clearly, then continue investigating
    whether the first supported MutationContract API should enforce dynamic-mode
    at the spell-facing entrypoint.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T19:52:14Z
  TYPE: FACT
  CLAIM: The spell-level runtime mode flag is not set during bind itself. A
    new `Spell` starts with `_dynamic_environment = False` in its constructor.
    The real mode stamp happens later when the spellbook already has a conjured
    conduit and calls `Spell._add_owned_conduit(...)`; that path forwards
    `self._conduit.__dynamic_environment__` into
    `_configure_creation_context_factory(...)`, which stores the bool on the
    spell. The conduit derives its own `__dynamic_environment__` from
    configuration flags and the explicit `automatic` argument during conduit
    construction.
  EVIDENCE:
  - src/melder/spellbook/spell.py:317-370
  - src/melder/spellbook/spell.py:470-509
  - src/melder/spellbook/spell.py:960-990
  - src/melder/spellbook/spellbook.py:2745-2760
  - src/melder/aether/conduit/conduit.py:162-209
  IMPACT: If a future MutationContract spell-facing API needs strict dynamic-only
    behavior, it should not assume bind-time state is enough; it needs to rely
    on the later conduit-ownership/runtime-mode stamp or consult spellbook
    configuration directly.
  NEXT: answer the user’s mode-stamping question and keep the MutationContract
    investigation focused on the spell-facing API boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T20:00:03Z
  TYPE: FACT
  CLAIM: A `MutationContract` definitely changes the spell's dependency
    surface, but it does not universally imply a new host-spell SHA. Phase 1
    classifies it ahead of normal DI and later phases preserve it as a
    mutation socket with `contract_key` and `contract_late_binding`, so it is
    part of the spell's constructor/dependency shape. But the bind-time
    `spell_id` SHA comes from `Bind.sha256_profile(...)`, which fingerprints
    only the binding profile. For normal class spells that uses
    `ClassBindingProfile`, and that profile does not include constructor
    default objects or Phase 1 requirement metadata. So mutating a
    `MutationContract` on a class constructor does not by itself imply a new
    `spell_id`; the observable change is in requirements/topology after the
    relevant phases are rerun. The main exception is directly bound callables,
    where `CallableBindingProfile` fingerprints parameter `default_repr`, so a
    recomputed callable profile could change if the contract object's repr
    changes.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:1044-1104
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3440-3465
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3498-3523
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3696-3710
  - src/melder/spellbook/bind/bind.py:245-257
  - src/melder/spellbook/bind/bind.py:355-423
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/binding_profile.py:58-149
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/binding_profile.py:187-317
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/binding_profile_strategy.py:62-153
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:167-206
  IMPACT: The first MutationContract feature should think in terms of
    revalidation/rebuild of spell requirements/topology, not automatic host
    `spell_id` rotation. If we ever want host-spell SHA to track contract
    mutation for class spells, that is a separate fingerprint-policy change.
  NEXT: answer the user's binding-signature/SHA question with the class-vs-callable
    distinction and keep the implementation discussion centered on revalidation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T20:04:28Z
  TYPE: FACT
  CLAIM: There is already one simple normalized binding-signature helper path
    we can reuse for `SpellMap` and `SpellContract`. The canonical key shape is
    `(frame_key, binding_key)` built through `SpellInputUtils`:
    `normalize_binding_name(...)`, `make_spell_key_from_parts(...)`, and
    `normalize_spell_key(...)`. `SpellMap.canonical_key` and
    `SpellContract.canonical_key` already delegate to that helper, and
    Spellbook lookup identity uses the same family of helpers for runtime
    binding keys. So if we want the host bind SHA to include contract/map
    signature, we can add an explicit normalized signature extraction based on
    those canonical keys and deliberately omit `MutationContract` from that
    extraction.
  EVIDENCE:
  - src/melder/utilities/helpers/general_helpers.py:178-290
  - src/melder/aether/conduit/meld/contracts/spell_map.py:183-229
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:185-228
  - src/melder/spellbook/spellbook.py:1295-1313
  - src/melder/spellbook/bind/bind.py:355-423
  IMPACT: The "include SpellMap and SpellContract, exclude MutationContract"
    split is feasible without inventing a new naming scheme; the missing piece
    is only where to splice that normalized signature into the bind-time
    fingerprint path.
  NEXT: tell the user the existing canonical-key template is reusable and that
    the remaining design choice is whether to inject it into
    `Bind.sha256_profile(...)` directly or into a higher-level host-signature
    extraction step before hashing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T20:18:16Z
  TYPE: DECISION
  CLAIM: The investigation lane is sufficiently grounded to carve out one
    bounded implementation task before continuing the larger MutationContract
    design. The immediate user request is to make the spell mutation-override
    setters require dynamic mode, which is a smaller runtime-contract fix than
    full MutationContract enablement.
  EVIDENCE:
  - user_instruction: "before you do anything else go ahead and inside spell, upgrade the methods so that mutation_override requires dynamic mode"
  - src/melder/spellbook/spell.py:1574-1646
  - src/melder/aether/conduit/conduit.py:3971-4005
  IMPACT: Active routing can switch to a narrow implementation task while this
    investigation remains open for the larger MutationContract runtime feature.
  NEXT: patch the spell-side dynamic-mode guard in the new implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T21:29:58Z
  TYPE: PLAN
  CLAIM: The next investigation slice is now a direct runtime experiment under
    `tests/experimentation/`: bind a simple class whose constructor default is
    a `MutationContract`, recover the live contract reference from the bound
    spell, mutate that reference in memory, then re-read through the same spell
    path to see whether the updated contract state sticks. This is the fastest
    way to prove what object we are actually mutating before wider API work.
  EVIDENCE:
  - user_instruction: "make a test in test/experiments"
  - user_instruction: "create a simple class with a mutation contract in its init, and then bind it to a spell"
  - user_instruction: "experiment on changing that contract and then re-referencing that reference to see if it stuck"
  IMPACT: The next step is experiment-first verification of live declaration
    object identity and persistence, not another speculative API pass.
  NEXT: add and run one focused MutationContract bind/reference experiment
    under `tests/experimentation`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T21:31:53Z
  TYPE: MEASURE
  CLAIM: The focused bind/reference experiment is green and gives a direct
    answer. After binding a class whose `__init__` default is one
    `MutationContract` instance, the bound spell's Phase 1 requirement path
    returns that same live object reference, and the callable signature default
    still points at that same object too. Updating the recovered contract in
    memory via `update_contract(...)` changes the later re-read result through
    both the spell requirement path and the class signature path. So the live
    mutation surface is the in-memory declaration object itself, not a copied
    file-backed value.
  EVIDENCE:
  - tests/experimentation/mutation_contract_bind_reference_testbench.py:1-210
  - validation_result:
    `python tests/experimentation/mutation_contract_bind_reference_testbench.py` -> `START_MUTATION_CONTRACT_BIND_REFERENCE`, `OK_MUTATION_CONTRACT_REFERENCE_SHARED`, `OK_MUTATION_CONTRACT_UPDATE_STUCK`, `DONE_MUTATION_CONTRACT_BIND_REFERENCE`
  - validation_result:
    `python -m py_compile tests/experimentation/mutation_contract_bind_reference_testbench.py`
  IMPACT: This proves the world-first model we were discussing is real: a
    spell-facing MutationContract API can operate on the live declaration
    object in memory without touching the file, and updates can stick when the
    same reference is re-read later.
  NEXT: use this result when deciding whether the first spell-facing API should
    return those live contract objects directly or wrap them in a narrower
    mutation-socket facade.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first investigation pass for the MutationContract runtime
socket feature.
