Completed: 2026-06-20T15:28:05Z
Summary: Investigation epic. Mojo migration dropped per user; surviving
  conclusion captured: an override-disabled / no-overrides compiler-build lane
  gated by an effective per-spell overrides_enabled flag rather than removing
  override support. Actionable follow-on routed to the separate
  add_overrides_enabled_configuration_and_spell_gate epic. Closed per user
  direction.

# Epic: Investigate AOT, CreationContext, Override Disable, and No-Overrides Compiler Path

## Metadata
- Epic ID: EPIC-2026-05-11-investigate-aot-creation-context-override-disable-and-no-overrides-compiler-path
- Status: in_progress
- Owner: codex
- Agent Name: mojo_0
- Priority: p0
- Created: 2026-05-11T10:34:17Z
- Updated: 2026-05-15T10:42:00Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder runtime execution and override-free compiler path

## Problem / Opportunity
The runtime already has multiple compiled execution and override-related
surfaces spread across `SpellCrafter`, `CreationContext`, `Meld`,
Phase 12 executors, contract descriptors, and the room-owned codegen engine.
The user wants a direct source-backed answer to three linked questions:

- can overrides and mutation-override structures be made optional behind one
  configuration flag
- can the runtime remove those override structures cleanly when disabled
- can we carve out a dedicated compiler/build path that avoids
  override-specific planning and executor work when a spell has overrides
  disabled

This is not a narrow single-file question. It spans architecture, ownership,
compiled execution lanes, validation gates, contract descriptors, and the
current AOT/codegen path.

## MRP Alignment (Most Reasonable Product)
The MRP is not "rewrite the whole compiler now" or "rip out overrides fast."
The MRP is:

- a source-backed map of the current AOT/codegen and runtime execution seams
- a bounded assessment of whether override-disable can be configuration-owned
  without tearing through unrelated runtime contracts
- a bounded assessment of where a no-overrides compiler/build lane can branch
  off to reduce unnecessary override-specific build work

That gives us the right foundation for later design or implementation work
without bluffing over structural constraints.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for an epic, a sprawl-level
  investigation, and an assessment focused on AOT/compiler, `CreationContext`,
  override-disable feasibility, and a no-overrides compiler/build path.
- EXECUTION_BOUNDARY: investigation and architecture assessment only; no code
  edits to runtime behavior in this epic.
- DEPENDENCIES:
  - `context_compass/system_docs/src_architecture.md`
  - `context_compass/system_docs/src_components.md`
  - `context_compass/system_docs/readable_src_graph.json`
  - `src/melder/spellbook/spell_crafter/spell_crafter.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - `src/melder/aether/nexus/rift/codegen_system/codegen_system.py`
  - override and contract descriptor surfaces under
    `src/melder/aether/conduit/meld/contracts/`
- EXIT_GATE: the epic produces a source-backed assessment with clear answers,
  constraints, and likely implementation boundaries for both override-disable
  and a no-overrides compiler/build path.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation proves the
  ask depends on deeper subsystem expansion than the user likely intends.

## Goals (Outcomes)
- Map the current AOT/compiler surfaces that exist today.
- Map how `CreationContext` and compiled Phase 12 execution are split between
  no-overrides, overrides, and mutation-aware paths.
- Decide whether a configuration-owned override-disable mode is structurally
  plausible.
- Decide where a no-overrides compiler/build lane can split from the current
  override-aware planning and executor pipeline.
- Reduce the sprawl into a bounded epic/story/task follow-on shape.

## Non-Goals (Explicit Exclusions)
- Implementing the override-disable flag in this epic.
- Implementing the new compiler/build path in this epic.
- Rewriting ticket or policy systems.
- Making speculative performance claims without source support.

## Scope Boundaries
- In scope:
  - AOT/codegen engine shape in AR/runtime surfaces
  - `SpellCrafter` execution-plan and compiled-executor generation
  - `CreationContext` execution dispatch
  - `Meld` runtime gates and call entry semantics
  - Spell override and mutation override structures
  - Contract descriptor and validation surfaces tied to overrides
  - feasibility boundaries for a no-overrides compiler/build lane
- Out of scope:
  - broad unrelated AR feature work
  - unrelated mutation research philosophy work
  - implementation of a new compiler backend

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new epic and asked for a
  sprawl-level investigation across these runtime/compiler surfaces.

## Success Metrics
- The current AOT/runtime execution seams are mapped with specific source
  anchors.
- Override-disable feasibility is answered with concrete blockers and likely
  control points.
- A no-overrides compiler/build path is answered with concrete phase and
  ownership boundaries.
- Follow-on work can be reduced into narrower tickets without redoing the
  same discovery pass.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify current AOT/compiler surfaces in runtime and AR codegen
  - identify all major override and mutation-override entrypoints
  - identify where override structures are compiled, cached, and executed
  - identify which override-specific artifacts can be skipped or replaced when
    overrides are disabled
  - produce an assessment, not just raw notes
- Non-functional:
  - evidence-backed only
  - no handwaving about build-time gains
  - explicit unknowns where source is not enough
  - no code edits outside ticket and board routing state

## Constraints / Assumptions
- `src_graph.json` remains unread by user instruction; graph context comes from
  `readable_src_graph.json`.
- The investigation may sprawl across many files; that is intentional and
  explicitly user-approved here.
- The assessment must distinguish codegen-room AOT from runtime Phase 12
  compiled execution; they are not assumed to be the same subsystem.

## Dependencies / External References
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`
- `codex/context_compass/system_docs/readable_src_graph.json`

## Milestones (Track Progress)
- [ ] Milestone 1: route the investigation and capture the first source-backed
      system map
- [ ] Milestone 2: read the runtime execution files and map override ownership
- [ ] Milestone 3: produce the override-disable feasibility assessment
- [ ] Milestone 4: produce the no-overrides compiler/build-path assessment

## Stories (Required to Complete)
- [ ] Story: map AOT/codegen and runtime compiled-executor surfaces
- [ ] Story: map `CreationContext`, `Meld`, and override dispatch ownership
- [ ] Story: assess configuration-owned override-disable feasibility
- [ ] Story: assess the no-overrides compiler/build path for meld and compiled
      systems

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: read the direct source files for runtime compiled execution
- [ ] Task: log each meaningful finding in `## Notes` before widening further
- [ ] Task: synthesize the findings into a bounded assessment
- [ ] Task: reduce follow-on work into narrower tickets if needed

## Acceptance Criteria (Epic Done)
- We can point to the exact files that own AOT/codegen and compiled runtime
  execution today.
- We can explain whether override-disable can be optional and what it would
  have to cut through.
- We can explain whether a no-overrides compiler/build path is credible,
  partial, or blocked, and why.
- The answer is concrete enough to guide future design or implementation work.

## Risks / Mitigations
- Risk: "AOT compiler" is overloaded between AR codegen and Phase 12 executor
  compilation.
  Mitigation: keep those lanes separated explicitly in notes and findings.
- Risk: override surfaces sprawl into more files than expected.
  Mitigation: log the expansion with evidence and keep synthesis grouped by
  ownership boundary.
- Risk: "new compiler" gets treated like a whole-backend rewrite instead of a
  narrower override-free build lane.
  Mitigation: anchor the assessment to actual current phase ownership and
  override-specific artifact boundaries.

## Applicable Anti-Patterns
- [ ] No architecture claims without source evidence.
- [ ] No collapsing AR codegen and runtime compiled execution into one vague
      "compiler" story.
- [ ] No compiler-path claims that ignore current phase ownership and artifact
      boundaries.

## Validation / Test Approach
- Investigation only in this epic.
- Validation is source-backed coherence across docs, graph surface, and direct
  code reads.
- Runtime tests are out of scope unless a later story opens an implementation
  lane.

## Rollout / Adoption Plan
- First complete the sprawl-level investigation in this epic.
- Then reduce the answer into narrower design or implementation tickets.
- Only after that decide which override-disable and no-overrides compiler slice
  deserves the next implementation tranche.

## Open Questions
- Does "AOT compiler system" primarily mean the room-owned codegen engine, the
  Phase 12 compiled executors, or both?
- Are override and mutation-override structures separable enough to disable
  together cleanly?
- Which late compile/runtime artifacts can be skipped entirely when
  `overrides_enabled` is false?

## Decision Log
- 2026-05-11T10:34:17Z: Opened this epic to hold the broad investigation the
  user explicitly requested across AOT/codegen, `CreationContext`, override
  structures, and the follow-on compiler/build-time direction.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-11T10:34:17Z
  TYPE: PLAN
  CLAIM: The initial evidence-backed scope already spans four distinct but
    coupled lanes: the AR codegen engine, the meld/runtime compiled executor
    lane, `CreationContext` execution dispatch, and override/mutation-contract
    structures. The assessment cannot be honest unless those lanes are read
    together and then separated again by ownership boundary.
  EVIDENCE:
  - codex/context_compass/system_docs/src_components.md:731-731
  - codex/context_compass/system_docs/src_components.md:1120-1120
  - codex/context_compass/system_docs/src_components.md:1188-1188
  - codex/context_compass/system_docs/src_components.md:1580-1586
  - codex/context_compass/system_docs/src_architecture.md:581-612
  - codex/context_compass/system_docs/src_architecture.md:843-845
  - codex/context_compass/system_docs/src_architecture.md:783-783
  IMPACT: The next investigation step should read direct source for each lane
    before any configuration or migration conclusion is attempted.
  NEXT: read `spell_crafter.py`, `creation_context.py`, `meld.py`, both Phase
    12 executor modules, and the room-owned codegen engine.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-11T10:36:27Z
  TYPE: FACT
  CLAIM: The current "compiler" story is already split in code. The
    room-owned `CodegenSystem` is an AR/codegen request engine that validates,
    builds a namespace, compiles, and executes user-generated Python for one
    room transaction. Separately, `SpellCrafter` owns spell-scoped Phase 11
    plans plus a cached Phase 12 no-overrides executor, and `CreationContext`
    owns the hot-path runtime dispatch layer plus the override specialization
    caches/executors for meld calls. This means override-disable and Mojo
    migration cannot be assessed as one monolithic compiler switch.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:236-313
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:338-418
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:126-165
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:280-340
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:541-643
  - src/melder/spellbook/spell_crafter/spell_crafter.py:210-217
  - src/melder/spellbook/spell_crafter/spell_crafter.py:281-288
  - src/melder/spellbook/spell_crafter/spell_crafter.py:566-607
  - src/melder/spellbook/spell_crafter/spell_crafter.py:2738-2878
  IMPACT: The next pass has to answer two different questions: whether runtime
    override machinery can be disabled without breaking meld execution, and
    whether the spell-runtime compile/dispatch lane is more portable to Mojo
    than the AR codegen request engine.
  NEXT: read `meld.py`, the Phase 12 executor modules, and the mutation/override
    descriptor surfaces to map exactly where no-overrides, overrides, and
    mutation-aware variants diverge.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-11T10:37:12Z
  TYPE: FACT
  CLAIM: A true override-free runtime lane already exists, but it is not the
    whole override story. `SpellCrafter` caches a dedicated Phase 11
    no-overrides plan plus a dedicated Phase 12 no-overrides executor,
    `CreationContext` has separate no-overrides compiled doors, and `Meld`
    only normalizes override payloads when the caller actually supplies one.
    At the same time, spell-level mutation overlays remain a live API that
    clears the cached `CreationContext` and marks structural change, while
    `MutationContract` descriptors are already hard-disabled in Phase 4. That
    means an override-disable option looks structurally plausible, but it
    cannot be implemented as "skip one executor" because override and mutation
    state also exist at descriptor, spell, and cache-invalidation layers.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:554-607
  - src/melder/spellbook/spell_crafter/spell_crafter.py:2738-2878
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:146-165
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:280-340
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:422-537
  - src/melder/aether/conduit/meld/meld.py:224-331
  - src/melder/aether/conduit/meld/meld.py:1373-1438
  - src/melder/spellbook/spell.py:1574-1666
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:23-29
  - src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py:96-121
  IMPACT: The feasibility question is no longer "is there a no-overrides path?"
    Yes. The real question is where one config switch would cut: frontdoor
    payload admission, spell-level mutation overlay APIs, descriptor
    validation, patch-map planning, or all of them together.
  NEXT: inspect the Phase 12 executor generator modules more directly to judge
    how Python-specific the generated execution path is and whether that lane
    is a realistic Mojo migration candidate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-11T10:38:09Z
  TYPE: FACT
  CLAIM: The cleanest control point for a configuration-owned override-disable
    mode is not `Meld` itself. It is `CreationContextBuilder` plus the
    spell/factory rebuild path. The builder decides whether a context gets the
    no-overrides executor, the Phase 10 override patch map, the non-mutation
    override route config, and the mutation-route config. The mutation route is
    already conditional on `spell.has_mutation_override`, and the
    spell/factory lifecycle already rebuilds the context when mutation overlay
    state changes. That means a disable flag has a plausible assembly-time seam
    instead of needing to hack every hot path in place.
  EVIDENCE:
  - src/melder\aether\conduit\meld\creation_context\creation_context_factory.py:20-25
  - src/melder\aether\conduit\meld\creation_context\creation_context_factory.py:162-255
  - src/melder\aether\conduit\meld\creation_context\creation_context_builder.py:69-117
  - src/melder\aether\conduit\meld\creation_context\creation_context_builder.py:183-252
  - src/melder\spellbook\spell.py:1574-1666
  IMPACT: If we pursue an optional disable mode, the likely cut is:
    configuration -> builder/factory assembly -> spell mutation-overlay API ->
    meld frontdoor payload admission. That is much cleaner than trying to
    rip override behavior out of already-built `CreationContext` instances.
  NEXT: finish the Mojo feasibility pass by judging how much of the current
    runtime path is generated Python, dynamic namespace binding, or native-ready
    dispatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-11T10:38:27Z
  TYPE: FACT
  CLAIM: A full "move meld and its compiled systems into Mojo" is not the most
    credible first migration slice. Both runtime executor variants are still
    generated Python that rely on `compile(..., \"exec\")` and dynamic
    namespace binding, and the room-owned `CodegenSystem` is explicitly a
    generated-Python validation/namespace/compile/execute engine. The strongest
    native seam I found is narrower: the no-overrides Phase 12 path already has
    an optional native transient dispatcher behind
    `MELDER_ENABLE_NATIVE_TRANSIENT_DISPATCH`, which suggests the first realistic
    Mojo move is a dispatch/executor backend or transient-call kernel, not the
    whole `Meld` or AR codegen system.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:46-95
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:112-173
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:552-580
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1401-1450
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:19-80
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:119-177
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:392-424
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:236-313
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:338-418
  IMPACT: The migration recommendation is currently asymmetric: a partial native
    backend for the spell-runtime no-overrides hot path looks plausible; a full
    Mojo migration of `Meld`, `CreationContext`, override specialization, and
    the room-owned codegen engine would cross too much dynamic Python behavior
    to treat as one bounded first step.
  NEXT: synthesize the findings into a user-facing assessment covering
    override-disable feasibility, likely control points, and realistic vs
    unrealistic Mojo migration slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-11T10:48:12Z
  TYPE: FACT
  CLAIM: A spell-level effective override flag layered over a config default is
    a credible way to speed compile/build time without removing the normal
    compiler pipeline. The late per-spell compiler stages are already split so
    that the no-overrides lane can stand on its own: Phase 10 patch maps are
    a dedicated override/mutation compilation pass, Phase 11 already materializes
    separate no-overrides and override-aware variants, and `CreationContextBuilder`
    already assembles the runtime context from those spell-scoped artifacts.
    So an effective `overrides_enabled` flag could suppress override-specific
    artifact construction while still letting the spell reach the same
    no-overrides execution plan and final executor path.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4467-4538
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4618-4761
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:69-117
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:183-252
  - src/melder/aether/conduit/meld/meld.py:224-287
  IMPACT: The clean implementation shape is not "delete override support." It
    is "compute an effective flag early enough that late compile/runtime lanes
    simply do less work for override-disabled spells."
  NEXT: answer the user directly with the phase-level consequence of using a
    config default plus spell-level effective flag.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-15T10:42:00Z
  TYPE: DECISION
  CLAIM: Mojo migration is no longer part of this epic. The useful surviving
    conclusion from the earlier investigation is the phase-level one: the real
    follow-on is a dedicated no-overrides compiler/build lane that branches
    from the current override-aware planning and executor pipeline when
    `overrides_enabled` is false. The current separate no-overrides runtime
    path, `CreationContextBuilder` assembly seam, and late override-specific
    Phase 10/11/12 artifacts are the relevant implementation pressure now.
  EVIDENCE:
  - user_instruction: "remove mojo migration from the epic name"
  - user_instruction: "we won't be migrating to mojo"
  - user_instruction: "we'll need to create a new compiler where we do not use overrides to improve build times"
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4467-4538
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4618-4761
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:69-117
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:183-252
  IMPACT: This epic should now route only override-disable and override-free
    compiler/build-time work, not language/backend migration discussion.
  NEXT: use this epic to narrow the next compiler/build implementation slice
    around skipping override-specific artifact work when overrides are
    disabled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche
  order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
The epic is open and routed around override-disable and the no-overrides
compiler/build path. The key current conclusion is that the room-owned codegen
engine and the meld/runtime compiled executor lane still have to be read
together but kept separate in the final assessment, and the real follow-on is
phase-level override-free build pruning rather than backend/language migration.
