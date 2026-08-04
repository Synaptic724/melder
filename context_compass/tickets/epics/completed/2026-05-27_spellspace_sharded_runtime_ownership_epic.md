# Epic: SpellSpace-Sharded Runtime Ownership Investigation
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Epic ID: EPIC-2026-05-27-spellspace-sharded-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p0
- Created: 2026-05-27T21:56:19Z
- Updated: 2026-05-30T15:06:13Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder runtime performance optimization

## Problem / Opportunity
The current spellspace runtime is conduit-centered:
- `Conduit` owns one `Creations`
- `Conduit` owns one `Meld`
- `SpellSpace` is only a scope handle that delegates into conduit-owned state

That means spellspace-scoped work still:
- probes active spellspace state through conduit-owned storage
- shares conduit-owned miss/create coordination
- keeps spellspace ownership subordinate to the broader conduit runtime even
  though spellspaces are already pooled and explicit

The opportunity is to determine whether spellspaces should become real runtime
shards with:
- their own `Creations`
- their own spellspace-specialized execution lane
- clearer ownership and lower contention

## MRP Alignment (Most Reasonable Product)
The MRP here is not “invent more runtime surfaces.”
It is a trustworthy understanding of where sharding would actually help and
where it would just move complexity.

The foundational question is:
- should spellspace remain a bucket key inside conduit-owned state
- or should it become a first-class runtime owner for spellspace-only storage
  and execution?

That has implications across:
- `SpellSpace`
- `Creations`
- `Meld`
- `CreationContext`
- generated Phase 12 runtime lanes
- ownership transfer
- pooling and cleanup

This epic exists so that design pressure is evaluated coherently instead of as
one-off chat arguments.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an epic-level umbrella for
  investigating spellspace-owned runtime state and its implications across the
  component stack.
- EXECUTION_BOUNDARY: investigation and design work around spellspace-owned
  `Creations`, spellspace-specialized execution lanes, ownership shifts,
  contention shifts, transfer implications, pooling implications, and runtime
  contract implications.
- DEPENDENCIES:
  - `tickets/tasks/2026-05-27_investigate_spellspace_owned_creations_and_meld_lane_task.md`
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
  - `tickets/tasks/2026-05-26_implement_plain_ref_creation_storage_for_non_disposable_entries_task.md`
  - `tickets/tasks/2026-05-27_investigate_creations_guard_and_lock_need_task.md`
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - `system_docs/readable_src_graph.json`
- EXIT_GATE: ownership, runtime-lane, transfer, pooling, and contention
  implications are explicit enough to support a bounded implementation plan or
  a bounded rejection of the idea.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation uncovers a
  semantic break that cannot be resolved without broader public API or runtime
  contract changes.

## Goals (Outcomes)
- Determine whether spellspace-owned `Creations` is architecturally coherent.
- Determine whether spellspace-specialized execution should be:
  - a second `Meld` lane
  - or a narrower injected storage path inside the current runtime lane
- Determine what contention actually moves or disappears.
- Determine which components would have to change if spellspace becomes a
  first-class runtime shard.
- End with one bounded recommendation:
  - pursue
  - reject
  - or defer

## Non-Goals (Explicit Exclusions)
- No implementation in this epic by default.
- No scheduler redesign.
- No transaction-mediator redesign.
- No broad conduit-pooling redesign unrelated to spellspace ownership.

## Scope Boundaries
- In scope:
  - spellspace ownership model
  - spellspace storage model
  - spellspace execution-lane model
  - contention and lock implications
  - transfer / pooling / cleanup implications
- Out of scope:
  - unrelated conduit or dev-ops cleanup
  - broad compiler architecture rewrite
  - public API expansion unless proven necessary

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested one top-level epic for
  investigating spellspace-owned runtime ideas and their cross-component
  implications.

## Success Metrics
- The current conduit-centered ownership model is mapped with direct evidence.
- The sharded spellspace alternative is mapped with explicit component changes.
- The contention story is concrete, not speculative.
- The recommendation is bounded and implementation-ready if accepted.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify every component that assumes conduit-owned spellspace state
  - identify whether spellspace specialization changes semantics or only
    ownership
  - identify transfer/pooling/cleanup impact
- Non-functional:
  - no handwaving about contention
  - no assuming sharding helps without proving where the current contention
    actually is
  - keep the investigation compaction-safe

## Constraints / Assumptions
- `SpellSpace` is already pooled and explicit.
- `unique_per_spell_space` is already a separate existence route in runtime.
- The current generated runtime already has spellspace-specific branches.
- The current conduit-centered model is still the source of truth until changed.

## Dependencies / External References
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- `src/melder/aether/conduit/conduit.py`

## Required Merge Order
The path is now explicit and should be executed in this order:

1. Fix storage ownership truth.
   - `src/melder/aether/conduit/conduit.py`
     - owner conduit must construct `ConduitCreations`
   - `src/melder/aether/conduit/spell_space/spell_space.py`
     - spellspace must own its own base `Creations`
   - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
     - pool must create spellspaces with spellspace-owned `Creations`
   - `src/melder/aether/conduit/creations/conduit_creations.py`
     - keep conduit/root helpers
     - only host spellspace delegation shims when generated/runtime callers still require them

2. Fix meld front doors.
   - `src/melder/aether/conduit/meld/meld.py`
     - `meld(...)` is conduit-only and must reject `requires_spellspace_request`
       in all target-resolution branches, including direct spell-id string paths
     - `spellspace_meld(...)` is spellspace-capable and must accept the
       spellspace context it actually needs
     - route by `Existence`:
       - `unique_per_spell_space` -> spellspace-owned `Creations`
       - `unique_per_conduit` -> owner-conduit `ConduitCreations`
       - `unique`, `unique_per_conduit_cluster`, `unique_per_conduit_lineage`
         -> `spell._owner_creations`

3. Fix spellspace probe/reuse paths.
   - `src/melder/aether/conduit/meld/meld.py`
     - `meld_existing_spell(...)`
     - `has_live_creation(...)`
     - `describe_live_creation_status(...)`
     - `_describe_spell_live_creation_status(...)`
   - these must stop assuming conduit-owned spellspace storage when the caller
     is the spellspace front door

4. Fix creation-context runtime assumptions.
   - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
   - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
   - current compiled doors still run spellspace through:
     - `caller_creations.get_active_spellspace()`
     - `caller_creations.get_spellspace_creation(...)`
   - either preserve that through explicit delegation on `ConduitCreations`
     or rewrite the spellspace route to take direct spellspace-owned storage

5. Fix Phase 12 executor assumptions.
   - `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py`
   - `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py`
   - current generated/runtime helpers still treat SPELLSPACE as a CALLER-style
     creations target and still call:
     - `get_active_spellspace()`
     - `get_spellspace_creation(...)`
     - `register_spellspace_creation(...)`
   - this is the main lower-layer blast radius beyond the `Meld` front door

6. Fix spell ownership / factory coherence.
   - `src/melder/aether/spellbook/spell.py`
   - `spell._owner_creations`
   - `spell._creation_context`
   - `spell._creation_context_factory`
   - the spell-owned runtime cache/factory layer must remain coherent when a
     spell is built from spellspace but still targets owner-conduit or
     root-owner storage for broader scopes

7. Fix transfer / rollback semantics.
   - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
   - current move/rollback logic is conduit-creations-centric and depends on:
     - `extract_spell_creations(...)`
     - `restore_spell_creations(...)`
   - we must explicitly decide whether spellspace-owned live state:
     - is non-transferable
     - is torn down on transfer
     - or gets a separate spellspace-aware move path

8. Fix pooling / cleanup semantics.
   - `src/melder/aether/conduit/conduit_pool.py`
   - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
   - `src/melder/aether/conduit/spell_space/spell_space.py`
   - `src/melder/aether/conduit/conduit.py`
   - reset/destroy/reuse flows must preserve the new ownership split without
     silently routing spellspace-owned state back into conduit-owned stores

9. Rewire external callers that currently assume conduit-only meld access.
   - `src/melder/nexus/rift/command_system/capability_command_system.py`
     - currently calls `conduit.meld(...)`
   - `src/melder/nexus/rift/command_system/command_system.py`
     - currently exposes `get_active_spellspace(...)` by delegating into
       conduit spellspace state
   - any caller using conduit-only spell activation or spellspace inspection
     must be reviewed once the front-door split is stable

## Target End State
The best outcome from the completed read is:

- `ConduitCreations`
  - owns conduit-local state
  - owns transfer / rollback / contract-invalidation helpers
  - does not own spellspace buckets as primary storage
- base `Creations`
  - owns spellspace-local state
  - one instance per spellspace
  - no spellspace-id bucket indirection
- `Meld`
  - remains the conduit-safe base class
  - owns shared heavy logic:
    - spell resolution
    - override normalization
    - structural / resolution / contract gating
    - compiler-system access
    - lookup caches
- `SpellSpaceMeld`
  - is a specialized hot path above the same heavy shared logic
  - owns spellspace front-door semantics and storage routing
  - does not inherit conduit-only external behavior by accident
- `CreationContext`
  - stays shared initially
  - but the compiled runtime lanes must distinguish conduit-caller and
    spellspace-caller execution inputs explicitly

### Ownership Matrix By Existence
- `unique_per_spell_space`
  - caller: `SpellSpaceMeld`
  - storage owner: spellspace-owned `Creations`
- `unique_per_conduit`
  - caller: `Meld` or `SpellSpaceMeld`
  - storage owner: owner-conduit `ConduitCreations`
- `unique`
  - caller: `Meld` or `SpellSpaceMeld`
  - storage owner: `spell._owner_creations`
- `unique_per_conduit_cluster`
  - caller: `Meld` or `SpellSpaceMeld`
  - storage owner: `spell._owner_creations`
- `unique_per_conduit_lineage`
  - caller: `Meld` or `SpellSpaceMeld`
  - storage owner: `spell._owner_creations`
- `many`
  - caller: `Meld` or `SpellSpaceMeld`
  - recommended storage owner:
    - conduit call -> conduit creations
    - spellspace call -> spellspace creations when disposal tracking is needed
    - otherwise no retained storage

### Front-Door Legality Rules
- `Conduit.meld(...)`
  - must reject any request where `target_spell.requires_spellspace_request`
    is true
  - this reject must happen regardless of whether resolution started from
    spell-id string or logical key lookup
- `SpellSpace.meld(...)`
  - must delegate to `SpellSpaceMeld`
  - is the only legal front door for spellspace-required requests

## Detailed Migration Phases

### Phase A: Restore Clean Runtime Contracts
Goal:
- remove broken intermediate states before deeper optimization

Required changes:
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/aether/conduit/spell_space/spell_space_pool.py`
- `src/melder/aether/conduit/conduit.py`

Deliverable:
- live code parses and every constructor surface tells the truth about storage
  ownership again

### Phase B: Finalize Storage Ownership
Goal:
- spellspace owns spellspace-local storage directly
- conduit owns conduit-local storage directly

Required changes:
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/conduit_creations.py`
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/aether/conduit/conduit.py`

Rules:
- spellspace-specific state must stop being modeled as a bucket inside conduit
  storage
- any remaining spellspace delegation methods on `ConduitCreations` are
  temporary compatibility seams only

### Phase C: Split Meld Hot Paths Properly
Goal:
- keep shared heavy logic once
- create a specialized spellspace hot path with its own front door

Required changes:
- `src/melder/aether/conduit/meld/meld.py`
- new `src/melder/aether/conduit/meld/spellspace_meld.py`

Implementation shape:
- `Meld`
  - conduit-safe base
  - shared heavy helpers stay here
- `SpellSpaceMeld(Meld)`
  - overrides:
    - `meld(...)`
    - `meld_existing_spell(...)`
    - `has_live_creation(...)`
    - `describe_live_creation_status(...)`
    - `_describe_spell_live_creation_status(...)`

Reason:
- the completed read shows the divergence is larger than one front door
- probe/reuse/status behavior is also caller-shape dependent

### Phase D: Rewire SpellSpace / Pool To The Specialized Hot Path
Goal:
- `SpellSpace` owns a real spellspace-specific meld object

Required changes:
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/aether/conduit/spell_space/spell_space_pool.py`
- `src/melder/aether/conduit/conduit.py`

Rules:
- `SpellSpace` must keep:
  - spellspace-owned `Creations`
  - owner conduit id
  - owner conduit creations reference
  - specialized meld surface

### Phase E: Rework CreationContext Runtime Inputs
Goal:
- stop forcing spellspace through generic caller-creations assumptions

Required changes:
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`

Conclusion from full read:
- `CreationContext` can remain one class
- but the compiled doors need explicit spellspace-caller vs conduit-caller
  variants
- keeping a single `caller_creations` input and pretending SPELLSPACE is just
  CALLER keeps the old design alive

### Phase F: Rework Phase 12 Executors
Goal:
- remove the lower-level conduit-owned spellspace assumption

Required changes:
- `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py`
- `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py`

Conclusion from full read:
- both files currently treat `ExecutionPlanTargetKind.SPELLSPACE` as a
  caller-creations route
- that is the main lower-layer performance and design bottleneck

Required end-state:
- SPELLSPACE route uses explicit spellspace-owned storage
- OWNER route stays owner-root
- CONDUIT route stays conduit-owned

### Phase G: Preserve Spell-Owned Runtime Cache Truth
Goal:
- keep `Spell` cache/factory state coherent while storage ownership diverges

Required changes:
- `src/melder/aether/spellbook/spell.py`

Specific surfaces:
- `_creation_context`
- `_creation_context_factory`
- `_owner_creations`
- `requires_spellspace_request`

### Phase H: Decide Transfer Semantics Explicitly
Goal:
- remove ambiguity about spellspace-owned live state during transfer

Required changes:
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`

Recommended decision:
- spellspace-owned live state should be non-transferable and destroyed on
  ownership transfer

Reason:
- spellspace is owner-conduit-local and narrower-lived
- moving that state across owners adds complexity with weak payoff

### Phase I: Revalidate Pooling / Cleanup
Goal:
- make cleanup and reuse obey the new ownership split

Required changes:
- `src/melder/aether/conduit/conduit_pool.py`
- `src/melder/aether/conduit/spell_space/spell_space_pool.py`
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `src/melder/aether/conduit/conduit.py`

### Phase J: Rewire External Callers
Goal:
- make external entry surfaces align with the new front-door rules

Required changes:
- `src/melder/nexus/rift/command_system/capability_command_system.py`
- `src/melder/nexus/rift/command_system/command_system.py`

Rules:
- callers that need spellspace-required requests must go through spellspace
  surfaces
- conduit-only command paths must not accidentally build spellspace-only
  requests

## Milestones (Track Progress)
- [ ] Milestone 1: Current Ownership Map
  - Current conduit-centered spellspace ownership and route assumptions are
    explicit with direct source evidence.
- [ ] Milestone 2: Sharded Alternative Map
  - Spellspace-owned `Creations` and spellspace-lane options are mapped with
    concrete component implications.
- [ ] Milestone 3: Recommendation
  - One bounded implementation recommendation or bounded rejection is written.

## Stories (Required to Complete)
- [ ] Story: Split storage ownership so spellspace-owned live state uses base `Creations` and conduit-owned state uses `ConduitCreations`.
- [ ] Story: Rewire conduit construction so owner-conduit and spellspace storage are both available at runtime without mixed spellspace buckets in conduit storage.
- [ ] Story: Upgrade `Meld` to expose two front doors:
  - `meld(...)` for conduit-only requests
  - `spellspace_meld(...)` for spellspace-capable requests
- [ ] Story: Rewire `SpellSpace` and `SpellSpacePool` to use spellspace-owned `Creations` plus owner-conduit context.
- [ ] Story: Rework `CreationContext` / generated executor spellspace routes so `unique_per_spell_space` uses spellspace-owned storage while broader scopes stay conduit/root owned.
- [ ] Story: Rework transfer / rollback / contract invalidation semantics so spellspace-owned live state is either explicitly non-transferable or handled through a separate spellspace-aware path.
- [ ] Story: Revalidate pooling and cleanup so spellspace reset, conduit reset, and ownership teardown all match the new storage split.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete task `TASK-2026-05-27-investigate-spellspace-owned-creations-and-meld-lane`.
- [ ] Task: Complete task `TASK-2026-05-30-move-creation-extract-restore-contract-to-base`.
- [ ] Task: Replace the current broken intermediate spellspace runtime seam in:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/spell_space/spell_space.py`
  - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
  - `src/melder/aether/conduit/meld/meld.py`
- [ ] Task: Rework generated/runtime spellspace routes in:
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py`
- [ ] Task: Rework transfer/pooling cleanup surfaces in:
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  - `src/melder/aether/conduit/conduit_cluster.py`
  - `src/melder/aether/conduit/conduit_pool.py`
  - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Final Recommendation
The completed read supports one clear recommendation:

- pursue the spellspace optimization path
- do it as a **real runtime split**, not as more conduit-owned spellspace
  delegation
- aim for:
  - spellspace-owned `Creations`
  - owner-conduit `ConduitCreations`
  - root-owned `spell._owner_creations`
  - a specialized `SpellSpaceMeld(Meld)` hot path
  - shared heavy validation/compiler logic where that logic is truly common
  - explicit lower-layer executor rewrites so SPELLSPACE stops being modeled as
    a CALLER-style creations target

### Why this is the best code outcome
- It makes storage ownership truthful.
- It removes the fake “spellspace is just a bucket inside conduit” model.
- It gives spellspace its own hot path where the divergence is actually real:
  - front door
  - reuse/probe/status
  - storage target selection
- It keeps the deep validation/compiler machinery shared where the read proved
  the logic is still common.
- It avoids the worst long-term outcome: one enormous conduit-centered meld
  object with endless spellspace special cases.

## Acceptance Criteria (Epic Done)
- We can answer, from files rather than instinct:
  - whether spellspace-owned `Creations` is coherent
  - whether a separate spellspace execution lane is justified
  - what contention would actually improve
  - what component blast radius the idea has
- The result is one bounded recommendation with explicit tradeoffs.

## Risks / Mitigations
- Risk: The idea looks good locally but explodes transfer/pooling semantics.
  - Mitigation: keep transfer, pooling, and cleanup as first-class investigation
    surfaces instead of an afterthought.
- Risk: We mistake ownership clarity for actual runtime speed.
  - Mitigation: keep contention claims evidence-backed and tied to current lock
    sites.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Investigation only by default.
- If later implementation is approved, validation should include:
  - direct spellspace/creations unit rings
  - direct meld/creation-context rings
  - transfer/pooling integration surfaces

## Rollout / Adoption Plan
- Investigate current ownership first.
- Investigate sharded alternative second.
- Decide implementation direction only after transfer/pooling implications are
  explicit.

## Open Questions
- Should spellspace sharding only affect `unique_per_spell_space`, or should it
  also change how other existences are routed when called from a spellspace?
- Is a second specialized meld lane better than extending the current one with
  injected storage ownership?
- Does transfer semantics become simpler or harder if spellspace-owned state is
  no longer embedded inside conduit-owned `Creations`?

## Decision Log
- The current runtime is conduit-centered.
- The sharded spellspace idea is worth investigation because pooled spellspaces
  already exist and the runtime already has spellspace-specific branches.
- No implementation is implied by opening this epic.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: after the investigation direction is accepted and split into
  child stories/tasks

## Notes
- DATETIME: 2026-05-27T21:56:19Z
  TYPE: PLAN
  CLAIM: This epic exists to keep the spellspace-sharded runtime idea coherent
    across all affected components instead of leaving it as a one-file or
    one-argument discussion. The first child work is the current
    spellspace-owned `Creations` / meld-lane investigation task.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-05-27_investigate_spellspace_owned_creations_and_meld_lane_task.md
  IMPACT: Later design or implementation slices can hang off one canonical
    umbrella instead of rebuilding the context from chat.
  NEXT: continue the active task and use this epic as the durable umbrella for
    any follow-up stories/tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T09:09:41Z
  TYPE: DECISION
  CLAIM: The target path is now explicit: the migration is not just `Meld`.
    The full change set spans storage ownership, conduit construction,
    spellspace entry, dual meld front doors, generated CreationContext /
    phase12 spellspace routes, and transfer/pooling semantics. The correct
    runtime model is:
    - spellspace-owned `Creations` for `unique_per_spell_space`
    - owner-conduit `ConduitCreations` for `unique_per_conduit`
    - root/owner creations for `unique`, `unique_per_conduit_cluster`, and
      `unique_per_conduit_lineage`
    - conduit `meld(...)` must reject spellspace-required requests
    - spellspace `meld(...)` must allow them
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:256-300
  - src/melder/aether/conduit/spell_space/spell_space.py:19-189
  - src/melder/aether/conduit/meld/meld.py:259-564
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:567-580
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:751-798
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1370-1380
  IMPACT: Future work should stop pretending this is a one-file refactor. The
    epic now reflects the real blast radius and the sequence needed to land the
    design cleanly.
  NEXT: use this epic as the canonical migration order and cut story/task
    slices in the order listed above instead of arguing piecemeal in chat.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T09:09:41Z
  TYPE: FACT
  CLAIM: The full runtime chain is now explicit. The front-door split point is
    `Meld`, but the lower runtime layers still treat SPELLSPACE as a CALLER-style
    creations target. The current conduit/spellspace runtime still has these
    exact assumptions:
    1. `Conduit` constructs owner-conduit `ConduitCreations` and gives that to `Meld`.
    2. `SpellSpace` now owns its own base `Creations`, but still delegates into
       `Meld.spellspace_meld(...)`.
    3. `Meld.meld(...)` is the correct conduit-only front door and
       `Meld.spellspace_meld(...)` is the correct spellspace-only front door,
       but `spellspace_meld(...)` is still unfinished and its signature does not
       yet fully match the caller.
    4. `CreationContext.execute(...)` and `execute_no_hooks(...)` are still
       generic and only receive `caller_creations`, so the spellspace path
       below `Meld` still depends on caller-creations spellspace delegation.
    5. `creation_context_codegen.py` emits spellspace source that still calls:
       - `caller_creations.get_active_spellspace()`
       - `caller_creations.get_spellspace_creation(...)`
    6. `phase12_no_overrides_executor.py` still treats
       `ExecutionPlanTargetKind.SPELLSPACE` as a caller-creations route and
       still calls:
       - `get_active_spellspace()`
       - `get_spellspace_creation(...)`
       - `register_spellspace_creation(...)`
    7. `phase12_overrides_executor.py` still emits the same spellspace-as-caller
       assumption in its shape-specialized override source.
    8. `Spell` still owns `_creation_context`, `_owner_creations`, and the
       `CreationContextFactory`, so the spell-owned runtime cache layer must
       remain coherent while storage ownership diverges by `Existence`.
    9. transfer/rollback is still conduit-creations-centric through
       `extract_spell_creations(...)` / `restore_spell_creations(...)`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:256-300
  - src/melder/aether/conduit/spell_space/spell_space.py:80-188
  - src/melder/aether/conduit/meld/meld.py:259-603
  - src/melder/aether/conduit/meld/meld.py:717-753
  - src/melder/aether/conduit/meld/meld.py:1001-1118
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:433-557
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:567-580
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:751-798
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1116-1127
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1370-1380
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1459-1469
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:1897-1900
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:2297-2305
  - src/melder/aether/spellbook/spell.py:672-697
  - src/melder/aether/spellbook/spell.py:1047-1054
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:958-991
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1428-1464
  IMPACT: The migration is now concrete instead of vague. The key design
    decision is not whether spellspace should be first-class; it already is on
    the front door. The real remaining work is whether we preserve the current
    caller-creations delegation at the `CreationContext` / Phase 12 layer or
    fully rewrite those lower layers to take explicit spellspace-owned storage
    surfaces.
  NEXT: cut the next child task specifically on the `Meld` front-door contract
    so `spellspace_meld(...)` and the probe/existing-object spellspace paths are
    finished before we touch generated executor code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T09:09:41Z
  TYPE: MEASURE
  CLAIM: The long runtime files have now been read line by line in capped
    chunks, including the full `CreationContext` file and both large Phase 12
    executor files. The completed read confirms three additional things that
    matter for the merge path:
    1. `CreationContext` itself is still caller-creations-generic and does not
       distinguish a spellspace-owned store directly; that distinction still
       lives in the route key and the emitted executor bodies.
    2. both Phase 12 executor modules treat
       `ExecutionPlanTargetKind.SPELLSPACE` as a CALLER-style creations target,
       and the spellspace route remains expressed through:
       - `get_active_spellspace()`
       - `get_spellspace_creation(...)`
       - `register_spellspace_creation(...)`
    3. external caller blast radius exists above conduit:
       `CapabilityCommandSystem` currently calls `conduit.meld(...)` directly,
       and `CommandSystem` exposes `get_active_spellspace(...)` by delegating
       into conduit spellspace state.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:433-746
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:533-613
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:673-868
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:714-727
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:999-1022
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1116-1127
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1370-1469
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:1897-1900
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:2297-2305
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:2407-2408
  - src/melder/nexus/rift/command_system/capability_command_system.py:1006-1029
  - src/melder/nexus/rift/command_system/command_system.py:435-476
  IMPACT: The epic now reflects the full lower-layer and caller-layer blast
    radius from completed reads, not from partial runtime sampling.
  NEXT: execute the merge path in the documented order, starting with fixing
    the `Meld` front-door contract and only then touching the generated
    executor layers.
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
This epic is the umbrella for investigating whether spellspace should become a
first-class runtime shard with its own storage and execution lane, and what that
would imply across ownership, contention, transfer, pooling, and cleanup.
