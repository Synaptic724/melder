# Phase 12 Precompute Audit (MeldRuntime/MeldEngine)

## Metadata
- Status: in_progress
- Owner: codex
- Created: 2026-01-29
- Updated: 2026-01-29
- Related story: STORY-2026-01-29-phase12-precompute-meld-runtime
- Related task: TASK-2026-01-29-phase12-precompute-meld-runtime

## Objective
Identify which remaining MeldEngine/MeldRuntime computations can be moved into Phase 12 precomputed artifacts, leaving a minimal runtime assembly/execution loop that is override-capable.

## Direction updates (user guidance)
- Prefer optimistic object references so real object refs are available for execution when possible.
- Precompute spell-id match routing ahead of time so runtime uses direct lookups.
- Include an explicit "available" param contract that identifies which creations container applies based on spell type.
- Support multiple Phase 12 execution plans with fast-path selection when overrides are absent.
- Phase 12 should be the final stage in the meld engine flow: it should return the final object instance and delegate creations placement without runtime re-planning in the engine.

## Evidence anchors (current runtime/engine)
- MeldRuntime.execute: src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- MeldEngine.run: src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- MeldEngine.run_execution_plan: src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- Creations selection/reuse/registration: src/melder/aether/conduit/meld/meld_engine/meld_engine.py (_select_creations_for_spell, _get_existing_creation, _register_spell)
- Instance planning helpers: src/melder/aether/conduit/meld/meld_engine/meld_engine.py (_instance_key_for_occurrence, _build_instance_override_map, _build_kwargs_for_instance)

## Inventory: Runtime computations still in MeldEngine
### A) Execution flow + gating (per call)
- Cancel/cancellation checks and error wrapping.
- Root spell eligibility gates (hooks, validation, etc. are already in MeldRuntime).
- Instance result storage and fallback root construction.

### B) Instance planning / routing
- Instance key resolution for shared vs. per-path instances.
- Per-instance override map derivation (socket overrides -> param overrides).
- Contract override payload selection per instance.
- Dependency kwargs assembly (including list aggregation and override merging).

### C) Creations selection + existence semantics
- Creations container selection by existence policy (caller/owner/spellspace).
- Lock strategy selection for shared existences.
- Reuse lookup, registration, and override rejection when instance already exists.

### D) Creations resolution + locking (engine-specific today)
- `_should_use_spell_lock` chooses between spell lock vs. creations lock based on existence and caller lock state.
- `_resolve_spell_instance` encodes the full reuse/construct/register flow and lock ordering for each existence type.
- `_select_creations_for_spell` selects caller vs. owner creations containers with fallbacks.
- `_get_existing_creation` performs existence-specific lookups across Creations and LesserCreations (including SpellSpace rules).
- `_register_spell` registers constructed instances into the appropriate container and handles disposal metadata.

## Precompute candidates (Phase 12)
### 1) Execution routing plan for instances (artifact)
Precompute and store:
- Instance keys per step (already in Phase 8/11, but Phase 12 can carry per-step routing summaries).
- Shared/per-path existence flags for each step.
- Canonical occurrence per spell id (Phase 8).
- Override target mapping per spell id (Phase 10 patch-map output baked into plan-specific routing indices).
- Contract override routing lookups by occurrence/spell id (already in Phase 8/11).
- Dependency keys per step (Phase 9 injection plan).

### 2) Creations targeting metadata
Precompute and store:
- Creations target kind for each step (caller/owner/spellspace) derived from existence policy.
- Flags for whether a spell is shared vs. per-path (for override gating).
- Whether a step is eligible for reuse vs. must construct (existence + disposal).
- Locking policy hints (spell lock vs. creations lock) to remove lock-choice logic from the engine.
- Container lookup requirements (e.g., needs active SpellSpace, caller vs owner fallback).

### 3) Optimistic object refs + availability contract
Precompute and store:
- Object ref handles keyed by spell id to enable optimistic execution path when creations already exist.
- Spell-id match tables for direct lookup (spell id -> plan step / instance key).
- An explicit "available" param that indicates which creations container applies based on spell type.

### 3) Minimal runtime assembly loop
Runtime should only:
- Bind live creations containers (caller/owner/spellspace) to precomputed target kinds.
- Apply per-call override payload values to precomputed override routing maps.
- Execute cancellation checks and invoke callables.

## Runtime-only (cannot precompute)
- Actual creations container references and their locks (per-call context).
- Override payload values from the meld context (per-call data).
- Cancellation events and error handling / tracing.
- Actual object instantiation (callables and potential exceptions).

## Proposed Phase 12 artifact sketch
**Phase12ExecutionAssemblyPlan** (new artifact):
- root_spell_id
- steps[]:
  - spell_id
  - instance_key
  - occurrence
  - existence_policy
  - creations_target_kind (caller/owner/spellspace)
  - shared_instance (bool)
  - dependency_keys (from injection plan)
  - override_target_keys (pre-resolved socket refs or param names)
  - contract_override_key (or payload ref)
- contract_overrides_by_occurrence / by_spell_id
- canonical_occurrences_by_spell_id
- shared_spell_ids
- override_patch_map signature / plan snapshot
- spell_id_step_index (spell id -> step index)
- optimistic_object_refs_by_spell_id
- available_param_by_spell_id
- plan_variant (no_overrides_fast | overrides | overrides_with_mutations)

## Minimal runtime execution flow (target)
1) Validate context/spell; select Phase 12 plan variant (gate by plan snapshot + override payload presence + mutation overrides + hooks).
2) Bind creations containers to plan targets (caller/owner/spellspace).
3) For each step in plan order:
   - Resolve instance reuse or construct based on existence + creations target.
   - Build kwargs from dependency results + override payload values + contract payloads using precomputed routing.
   - Register instance if required.
4) Return root instance; perform cleanup.

## Plan variants (selection intent)
- no_overrides_fast: fastest plan when there are no overrides or mutations.
- overrides: plan variant that supports contract/override payloads (no mutations).
- overrides_with_mutations: plan variant that supports contract/override payloads and mutation overrides.

## Options under consideration (Phase 12 design)
### Option A: New Phase 12 artifact (ExecutionAssemblyPlan)
- Create a new Phase 12 artifact dedicated to execution assembly (creations routing + lock hints + override routing).
- Pros: clean separation from Phase 11; explicit terminal execution contract; easier cleanup boundaries.
- Cons: additional artifact lifecycle + wiring; more migration surface.

### Option B: Extend Phase 11 ExecutionPlan into Phase 12
- Extend Phase 11 ExecutionPlan to include creations routing/lock hints + optimistic refs, and treat Phase 12 as a thin wrapper.
- Pros: fewer new types; leverage existing plan selection/gating.
- Cons: Phase 11 becomes overloaded; harder to keep "terminal" semantics clear.

### Option C: Hybrid (Phase 11 plan + Phase 12 execution addendum)
- Keep Phase 11 plan for ordering/routing; add a Phase 12 addendum artifact focused on creations delegation and locks.
- Pros: minimal new data; clearer boundary between routing and creations/locks.
- Cons: coordinating two artifacts; risk of mismatch if not tightly versioned.

### Option D: Creations delegation contract
- **Routing table approach**: explicit per-step creations target kind + lock hints.
  - Pros: runtime has no branching logic; deterministic execution.
  - Cons: needs careful coverage of SpellSpace + disposal edge cases.
- **Declarative policy approach**: encode existence policy + minimal hints, runtime computes lock/target.
  - Pros: smaller artifacts; fewer stale-policy risks.
  - Cons: leaves more runtime logic, weaker Phase 12 goals.

### Option E: Optimistic object refs
- **Pre-resolved ref snapshot** keyed by spell id (best-effort lookup during Phase 12 build).
  - Pros: enables fast-path reuse when creations already exist.
  - Cons: staleness risk; must be validated at runtime.
- **Lookup-first** using spell-id -> instance key map only.
  - Pros: avoids stale refs; simpler correctness story.
  - Cons: less fast-path benefit.

## Selected options (user direction)
- Artifact strategy: **Option A** (new Phase 12 ExecutionAssemblyPlan).
- Creations delegation: **Option D1** (routing table approach with explicit target kind + lock hints).
- Optimistic object refs: **Option E1** (pre-resolved ref snapshot), relying on validation system for staleness checks.

## Implementation research (Phase 12 target extraction)
### Method-by-method extraction map
**MeldEngine.run / run_execution_plan**
- Keep in runtime: cancellation checks, error wrapping, final return wiring.
- Precompute: plan selection inputs, routing tables, and per-step data so engine doesn't branch.

**_instance_key_for_occurrence**
- Precompute instance keys per step (already in Phase 8/11); Phase 12 should store final instance keys + spell-id lookup table.

**_build_instance_override_map**
- Precompute override routing tables per step (socket -> param mapping) and keep payload values runtime-bound.

**_build_kwargs_for_instance**
- Precompute dependency key ordering + aggregation rules.
- Runtime only merges dependency results + override payload values + contract payload for the step.

**_select_creations_for_spell**
- Precompute creations_target_kind (caller/owner/spellspace) and fallback rules.
- Runtime binds actual containers by target kind without re-planning.

**_should_use_spell_lock**
- Precompute lock_hint per step (spell lock vs creations lock) based on existence policy + shared instance.

**_get_existing_creation**
- Precompute container lookup requirements (SpellSpace required, owner conduit validation).
- Runtime performs lookup using precomputed target kind and validates optimistic refs.

**_register_spell**
- Precompute registration behavior (must_register + disposal metadata).
- Runtime registers against the precomputed target container.

### Optimistic ref validation (Option E1)
- Store optimistic refs keyed by spell id in the Phase 12 plan.
- Runtime must validate optimistic refs against the container + instance key before reuse.
- If validation fails, fallback to standard lookup/construct path for that step.

### Phase 12 plan payload (delta vs current sketch)
- Add `lock_hint` to each step (spell_lock | creations_lock).
- Add `requires_spellspace` + `owner_conduit_required` flags to each step for lookup validation.
- Add `must_register` + `disposal_policy` metadata per step.

## Phase 12 execution handoff intent
- Phase 12 is the final execution stage for meld: it should return the root instance directly and delegate creations placement based on precomputed targets.
- The meld engine should not re-plan during execution; remaining work is only binding live creations containers and applying per-call override values.
- The runtime should encapsulate the execution assembly so engine logic is minimized (or becomes a thin wrapper).
- Creations selection/registration logic currently in MeldEngine should move into Phase 12 artifacts + runtime assembly: engine should only perform bounded lookups/locks with precomputed targets.

## Implementation note (Phase 11 precursor)
- Phase 11 plan variants are now being selected based on override and mutation presence to exercise the variant-switching logic that Phase 12 will formalize.
- MeldRuntime now precomputes override targets and override-presence flags for Phase 11 fast-path execution to remove duplicated override detection in MeldEngine.

## Open questions
- What is the expected shape of the “root creations flap map”? Determine if it maps spell id -> creations target or includes instance-key routing.
- Which portions of reuse/lock logic can be encoded declaratively without losing correctness (e.g., shared-instance override rejection)?
- What is the minimal object-ref contract needed for optimistic execution without risking stale refs?
- What is the minimal "creations delegation" contract needed so Phase 12 can select targets without engine intervention?
- How should Phase 12 encode SpellSpace requirements (active spellspace + owner conduit validation) to keep runtime checks minimal?

## Next steps
- Update Phase 12 artifact sketch with lock_hint, registration metadata, and SpellSpace requirement flags.
- Draft the Phase 12 builder wiring (where it will live in SpellCrafter and cleanup rules).
- Draft runtime execution loop changes and the engine call-site adjustments.
- Propose follow-up implementation tasks once the plan schema is agreed.
