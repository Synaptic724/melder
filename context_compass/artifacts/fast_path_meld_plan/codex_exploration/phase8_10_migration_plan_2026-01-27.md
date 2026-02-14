# Phase 8-10 Migration Plan (Runtime to Phases) - 2026-01-27

## Purpose
Plan how to migrate meld runtime planning work into conjure phases 8-10, so
meld becomes a thin executor that reads precompiled artifacts. This document
is intended as a durable handoff for context compaction.

## Evidence Anchors (Current Behavior)
### Spell and SpellCrafter phase model
- `src/melder/spellbook/spell.py:run_structural_phases`
- `src/melder/spellbook/spell.py:run_all_phases`
- `src/melder/spellbook/spell_crafter/spell_crafter.py` (phase artifacts + cleanup)

### Meld runtime gating and orchestration
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute`
  - Gating: system validity, change-control dirty root, broken/validated checks
  - Applies GraphMutator and SpellOverrider when blueprint exists
  - Builds ResolutionFrame and runs MeldEngine

### Meld engine per-call planning
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_occurrence_graph`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_extend_occurrence_graph_with_ordered_nodes`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_execution_order`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_plan`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_apply_mutation_overrides_to_dependencies`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_record_contract_override`

## Current Runtime Responsibilities (to migrate)
From `MeldEngine.run`, the per-call work that should move to phases:
- Build occurrence graph (path-aware expansion).
- Extend occurrence graph with ordered nodes from blueprint.
- Build execution order (topo + fallback ordering).
- Build instance plan (instance keys + canonical occurrences).
- Resolve contract overrides during occurrence expansion.
- Apply mutation overrides to dependencies (rewiring during occurrence expansion).
- Build kwargs per instance by walking occurrences and instance results.

From `MeldRuntime.execute`:
- Apply GraphMutator (mutation overrides).
- Apply SpellOverrider (override maps).
- Build ResolutionFrame overrides.

These responsibilities should be split into phases 8-10, with meld runtime
only orchestrating gating and executing a precompiled plan.

## Migration Goal State (Phases 8-10)
### Phase 8 (OccurrencePlan)
Move from runtime to Phase 8:
- occurrence_graph
- execution_order
- instance plan (instance_keys_by_spell_id, canonical_occurrences_by_spell_id,
  root_instance_key, shared_spell_ids)

Evidence for outputs: `MeldEngine.run` and `_build_instance_plan`.

Phase 8 should be compiled from:
- RootResolutionBlueprint DAG and ordered_node_ids
- Local topology (SpellSystemStates)
- DAG node dependencies and socket kinds
- Spell lookup for contract sockets and existence
- DagIndex for mutation targeting

### Phase 9 (InjectionPlan)
Move from runtime to Phase 9:
- argument wiring for each instance key
- contract override payload selection rules
- positional override handling

Evidence for behavior: `_build_kwargs_for_instance`, `_build_instance_override_map`,
`_get_contract_override_payload_for_instance`.

### Phase 10 (PatchMaps)
Move from runtime to Phase 10:
- override targeting (socket refs, TargetSpec, precedence)
- mutation override rewiring when possible
- mapping for patchable overrides without graph rebuild

Evidence for current runtime behavior:
- `GraphMutator.apply` in `meld_runtime.py` (mutation override application)
- `SpellOverrider.apply` in `meld_runtime.py` (override map creation)

UNKNOWN: exact patchable subset and how much of GraphMutator is precomputable
without dynamic inputs.

## Where Phases 8-10 Should Live
Observed pattern (phases 1-7):
- Spell owns phase facades that call SpellCrafter.
  Evidence: `Spell.run_structural_phases`, `Spell.run_all_phases`.
- SpellCrafter owns phase artifacts and cleanup logic.
  Evidence: `SpellCrafter` fields and `cleanup_phase_artifacts`.

Proposed pattern for phases 8-10:
- Add Spell facades:
  - `Spell.run_phase_occurrence_plan`
  - `Spell.run_phase_injection_plan`
  - `Spell.run_phase_patch_maps`
  - Optional: `Spell.run_all_phases` extends to 8-10 when requested.
- Add SpellCrafter phase methods that produce and store artifacts:
  - `SpellCrafter.run_phase_occurrence_plan`
  - `SpellCrafter.run_phase_injection_plan`
  - `SpellCrafter.run_phase_patch_maps`
- SpellCrafter stores phase 8-10 artifacts similar to Phase 5 fields.

This matches the existing phase model and allows re-running phases via
Spell methods with conduit_id and cancellation params.

## Phase 8 Migration (OccurrencePlan)
### Inputs (evidence-based)
- RootResolutionBlueprint DAG and ordered_node_ids:
  - `MeldEngine.run` uses `blueprint.dag` and `blueprint.ordered_node_ids`.
- Local topology from SpellSystemStates:
  - `_collect_occurrence_dependencies` uses `get_local_topology_by_id`.
- DAG node dependency data and socket kinds:
  - `_collect_occurrence_dependencies` uses `dag.get_node` and `dag._socket_kinds`.
- Spell lookup:
  - `_apply_spell_contract_dependencies` and `_build_instance_plan`.
- DagIndex for mutation override targeting:
  - `_apply_mutation_overrides_to_dependencies`.

### Outputs (evidence-based)
- occurrence_graph
- execution_order
- instance_keys_by_spell_id
- canonical_occurrences_by_spell_id
- root_instance_key
- shared_spell_ids

Evidence: `_build_occurrence_graph`, `_build_execution_order`, `_build_instance_plan`.

### Migration steps
1) Create OccurrencePlan artifact in SpellCrafter (Phase 8).
2) Compile it during conjure using the same inputs as `MeldEngine.run`.
3) Store on SpellCrafter (or blueprint) and expose via Spell facade.
4) In meld runtime, use the OccurrencePlan directly and skip runtime planning.
5) If missing/stale, fall back to current runtime planning.

### Rerun conditions
Candidate triggers (must be confirmed):
- Root blueprint changes (Phase 5).
- Local topology changes (Phase 3).
- Change-control dirty root.
- Contract or mutation wiring changes.

## Phase 9 Migration (InjectionPlan)
### Inputs (evidence-based)
- occurrence_graph and canonical occurrences (Phase 8 outputs).
- instance results (runtime values at execution time).
- override map and contract override payloads:
  - `_build_instance_override_map`
  - `_get_contract_override_payload_for_instance`

### Outputs (draft)
- per-instance argument wiring plan
- positional override rules
- per-socket injection rules

Evidence: `_build_kwargs_for_instance` logic.

### Migration steps
1) Define InjectionPlan artifact in SpellCrafter (Phase 9).
2) Compile with occurrence graph and spell metadata.
3) At runtime, execute plan to build kwargs without walking graph.

UNKNOWN: how much of override behavior remains dynamic vs precompiled.

## Phase 10 Migration (Patch Maps)
### Inputs (evidence-based)
- RootResolutionBlueprint and DagIndex for target selection.
- Override and mutation inputs (TargetSpec).
- Contract wiring and socket refs.

Evidence: `GraphMutator.apply` and `SpellOverrider.apply` in `MeldRuntime.execute`.

### Outputs (draft)
- override patch map keyed by socket ref and target path
- mutation patch map keyed by socket and replacement target

### Migration steps
1) Define patch map artifacts in SpellCrafter (Phase 10).
2) Compile patch maps from blueprint + dag index + socket refs.
3) At runtime, apply patch maps when overrides exist.
4) If unsupported override/mutation case, fall back to slow path.

UNKNOWN: exact supported subset for patching without rebuilding the DAG.

## Meld Runtime After Migration
Target runtime responsibilities:
- Gate eligibility (validity, dirty root, hooks, overrides).
- Load Phase 8-10 artifacts from SpellCrafter (or blueprint).
- Execute compiled plan (fast path).
- Fallback to current runtime path if any gate fails.

Evidence for current gating entrypoint: `MeldRuntime.execute`.

## Migration Map (Runtime -> Phase)
| Current runtime responsibility | Evidence | Move to | Notes |
| --- | --- | --- | --- |
| Build occurrence graph | `MeldEngine._build_occurrence_graph` | Phase 8 | Precompute once per root blueprint |
| Extend with ordered nodes | `MeldEngine._extend_occurrence_graph_with_ordered_nodes` | Phase 8 | Plan should include all ordered nodes |
| Build execution order | `MeldEngine._build_execution_order` | Phase 8 | Store in OccurrencePlan |
| Build instance plan | `MeldEngine._build_instance_plan` | Phase 8 | Store instance keys + canonical occurrences |
| Build kwargs per instance | `MeldEngine._build_kwargs_for_instance` | Phase 9 | InjectionPlan executes at runtime |
| Contract override payload selection | `_get_contract_override_payload_for_instance` | Phase 9 or 10 | Decide whether it belongs to injection or patch maps |
| Override targeting (TargetSpec -> SocketRef) | `SpellOverrider.apply` | Phase 10 | Pre-resolve sockets, preserve specificity |
| Mutation DAG rewiring | `GraphMutator.apply` | Phase 10 (subset) | Precompute patchable rewires; fallback for complex cases |

## Phase 11 (Optional, Max Enhancement)
Phase 11 is an optional speed layer that can further reduce runtime work once
Phases 8-10 are stable. Not all paths will support Phase 11.

Candidate Phase 11 features:
- Codegen executor for OccurrencePlan + InjectionPlan (tight loop).
- Pre-baked callable invocation payloads (arg arrays or kwargs structs).
- Specialized fast path for best-case (no overrides, no mutations).
- Optional C-extension or Cython executor if profiling warrants it.
- Pre-flattened instance order (single pass array of steps: construct/register).
- Pre-resolved creation targets (owner vs caller vs spellspace) per step.
- Pre-built object pools for hot-path lists (avoid per-call allocations).
- Vectorized dispatch for same spell types (batch constructions).
- “No-overrides” fast lane with zero dict merges (pure positional or direct deps).
- Optional bytecode-level prebinding (store bound callables or descriptors).

Phase 11 constraints:
- Only valid for strict best-case routes (no overrides, no hooks, no mutations).
- Must fall back to Phase 8-10 executor when gates fail.

## Phase 11 Integration Notes
- Phase 11 should consume Phase 8/9/10 artifacts as inputs, not replace them.
- It should be enabled behind a gate so correctness falls back to the Phase 8-10
  executor on any mismatch or missing artifact.
- If Phase 11 is not viable for a root, Phase 8-10 remain sufficient.

## Phase 11 Feasibility Gates (Draft)
- No overrides, no mutations, no hooks.
- Validity is valid and root is not dirty.
- Plan signature matches (Phase 8/9/10 artifacts in sync).
- No spellspace scope required (or spellspace pre-validated).
- No contract override payloads.

## Open Questions (Explicit UNKNOWNs)
- Where to store Phase 8-10 artifacts (SpellCrafter vs Blueprint vs Conduit).
- Exact invalidation signature inputs for each phase.
- Patchable override/mutation subset for Phase 10.
- Whether contract override payloads are Phase 8 or Phase 10 responsibilities.
 - Which best-case routes are eligible for Phase 11 execution.

## Iteration Plan (Branch: no backward-compat constraints)
Goal: migrate planning out of runtime in controlled passes, keeping a clean
"stop line" per iteration so we do not mix phases and runtime logic.

### Iteration 1: Phase 8 structural plan only (best-case path)
Migrate to Phase 8:
- occurrence_graph (path-aware expansion)
- ordered-node expansion
- execution_order
- instance plan (instance keys + canonical occurrences + shared ids)

Stop line (leave in runtime for now):
- Override handling (SpellOverrider, override maps)
- Mutation overrides (GraphMutator, mutation rewiring)
- Contract override payload selection
- Kwarg construction (_build_kwargs_for_instance) and override merging

Runtime gating for Phase 8 path (best-case):
- No overrides
- No mutation overrides
- No hooks
- Validity OK + not dirty

### Iteration 2: Phase 9 injection plan (override-free)
Migrate to Phase 9:
- Per-instance argument wiring based on occurrence graph + instance plan
- Contract sockets (no override payloads)
- Positional args support only when static (no runtime override)

Stop line:
- Any override payloads (root or socket)
- Mutation overrides
- Patch maps (Phase 10)

Runtime gating for Phase 9 path:
- Same as Iteration 1 plus "no override payloads"

### Iteration 3: Phase 10 patch maps (limited override support)
Migrate to Phase 10:
- Precomputed override targets and patch slots for supported cases
- Patch maps for mutation overrides only when safe (subset)

Stop line:
- Dynamic graph mutation for unsupported cases
- Complex TargetSpec cases that require runtime DAG rebuild

Fallback:
- Any unsupported override/mutation -> slow path

## Migration Boundary Summary (Phase 8 only)
If we stop at Phase 8:
- Runtime still builds kwargs and applies overrides.
- Runtime still executes GraphMutator/SpellOverrider when overrides exist.
- Fast path only covers the "no overrides/no mutations" best-case lane.

## Immediate Next Steps
1) Finalize Phase 8/9/10 storage + invalidation rules (choose artifact location).
2) Define fast-path gating checklist for Phase 8/9/10 (no overrides, no hooks, etc.).
3) Decide Phase 11 feasibility criteria and profiling gates.
