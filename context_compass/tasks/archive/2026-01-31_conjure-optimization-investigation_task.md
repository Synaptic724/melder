# Task: Investigate conjure optimization options and map to existing tickets

## Metadata
- Task ID: TASK-2026-01-31-conjure-optimization-investigation
- Story:
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Produce an evidence-backed investigation summary that maps the user-provided
optimization ideas and profiling notes to existing tickets, identifies gaps,
and proposes a recommended sequencing without creating new tickets or changing
code.

## Scope Boundaries
- In scope:
  - Consolidate user-provided profile/tracemalloc observations (mark as user-provided).
  - Map each optimization idea to existing tickets in `context_compass/tasks/`.
  - Identify gaps where no current ticket exists (do not create new tickets).
  - Provide a priority/impact/risk sequencing recommendation.
- Out of scope:
  - Code changes, tests, benchmarks, or edits outside this ticket.
  - Creating additional tickets beyond this single investigation task.

## Evidence Inputs (User-Provided, User-Confirmed 2026-01-31, Not Verified)
- Conjure build profile shows large time in Phase 5 root blueprints
  (`_overlay_sockets_and_index`, `build_blueprint_for_spell_id`).
- Phase 11 plan builds show repeated `_build_execution_plan_variant` calls.
- Phase 6 system validation hotspot in `SocketRefSanityStrategy.run`.
- Tracemalloc top allocs from path tuple concatenation in occurrence planning.

User-confirmed performance snapshot (2026-01-31, not reproduced in-repo):
- profile_conjure_build_direct: build-only direct phases avg=322.770ms.
- cProfile target: 0.308s total; Phase 5 root blueprints dominates:
  - run_phase_root_blueprints cumtime ~0.172s
  - _overlay_sockets_and_index cumtime ~0.135s
  - build_blueprint_for_spell_id cumtime ~0.118s
- Phase 11 plan build cost:
  - run_phase_execution_plan cumtime ~0.054s
  - _build_execution_plan_variant cumtime ~0.054s (3 variants)
  - ExecutionPlan.build cumtime ~0.053s
- Phase 6 system validation:
  - run_phase_system_validation cumtime ~0.044s
  - SocketRefSanityStrategy.run cumtime ~0.032s
- Phase 8 occurrence plan:
  - run_phase_occurrence_plan cumtime ~0.013s
  - OccurrencePlan.build cumtime ~0.013s
- Benchmarks/testing_other_di:
  - Conjure total (ms): 163.632
  - Phase breakdown (ms): requirements 15.142, symbolic_graph 10.180,
    local_frame 11.495, validation 11.530, root_blueprints 10.043,
    system_validation 10.929, change_control 10.193, occurrence_plan 16.552,
    injection_plan 10.761, patch_maps 10.957, execution_plan 12.500.
  - Conjure (cprofile target) (ms): 218.646
  - Tracemalloc top allocations include `socket_path = path + (...)` and
    `child_occurrence = (target_id, path + (...))`.

NOTE: The above are user-provided logs, confirmed by the user on 2026-01-31,
but must still be treated as unverified until reproduced in-repo.

## Code Evidence (Verified)
- Phase 5 uses the live spell_id_pool and builds per-spell blueprints:
  `src/melder/spellbook/spell_crafter/spell_crafter.py:SpellCrafter.run_phase_root_blueprints`
  (uses `spellbook._spell_id_pool.keys()` and iterates all spells, calling
  `build_blueprint_for_spell_id` when missing).
- Phase 11 builds three variants per spell and passes spell_id_pool directly:
  `src/melder/spellbook/spell_crafter/spell_crafter.py:SpellCrafter.run_phase_execution_plan`.
- Circular DFS uses in-place path mutation:
  `src/melder/spellbook/spell_crafter/validation/strategies/circular_dependency_strategy.py:
  CircularDependencyStrategy.validate` (path append/pop).
- Occurrence plan uses tuple path concatenation for child occurrences:
  `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py` (multiple
  `path + (param_name,)` sites).
- Root blueprint socket overlay builds tuple socket paths:
  `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:
  SpellSystemRootBlueprintBuilder._overlay_sockets_and_index` (`socket_path = path + (...)`).
- Phase 6 currently copies spell_id_pool into a new dict:
  `src/melder/spellbook/spell_crafter/spell_crafter.py:SpellCrafter.run_phase_system_validation`
  (builds `spell_lookup` via loop).

## GPT Pro Claim Check (Verified vs UNKNOWN)
- Phase 5 uses live `spellbook._spell_id_pool` (no scanner/dict rebuild):
  VERIFIED by `SpellCrafter.run_phase_root_blueprints` (see Code Evidence).
- Phase 11 passes `spellbook._spell_id_pool` into ExecutionPlanBuilder:
  VERIFIED by `SpellCrafter.run_phase_execution_plan`.
- Circular DFS now uses `path.append()/pop()` (not `path + [...]`):
  VERIFIED by `CircularDependencyStrategy.validate`.
- Phase 5 builds per-spell deep blueprints (non-root spells):
  VERIFIED by `SpellCrafter.run_phase_root_blueprints`.
- Phase 11 always builds three plan variants per spell:
  VERIFIED by `SpellCrafter.run_phase_execution_plan`.
- SpellSystemAdjacencySnapshot allows `all_spell_ids` to be a live view:
  VERIFIED by `SpellSystemAdjacencySnapshot.all_spell_ids` docstring.
- Spellbook keeps contracted spell IDs in `_spell_id_pool`:
  VERIFIED by `Spellbook._register_contracted_spell_id` /
  `_update_contracted_spell_id` / `_unregister_contracted_spell_id` adding/removing
  from `_spell_id_pool`.
- Path tuple churn in occurrence planning is a top allocator in profiles:
  UNKNOWN (performance claim not reproduced), but tuple concat sites are
  VERIFIED in `occurrence_plan.py` (see Code Evidence).
- RootResolutionBlueprint is a "dumb container" with DAG + ordered ids +
  socket refs + dag index:
  VERIFIED by `src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py:
  RootResolutionBlueprint` docstring and slots.
- Phase 8 topological ordering avoids list pop(0) by walking with an index:
  VERIFIED by `OccurrencePlanBuilder._build_execution_order`
  (`queue_idx` traversal) in `occurrence_plan.py`.
- Phase 8–11 phase factories create a UnitOfWork per spell:
  VERIFIED by `Spellbook._phase_occurrence_plan_factory`,
  `_phase_injection_plan_factory`, `_phase_patch_maps_factory`,
  `_phase_execution_plan_factory` in `src/melder/spellbook/spellbook.py`.
- Spell-level validation strategies rebuild global views per spell:
  VERIFIED for multiple strategies that iterate `spellbook._spell_id_pool`
  (e.g., CircularDependencyStrategy, DuplicateSpellNameStrategy,
  BindingResolutionCycleStrategy).

## GPT Pro Claims Investigation Summary (Evidence Anchors)
- Claim: Phase 5 uses live spell_id_pool (no scanner + dict rebuild).
  Evidence: `src/melder/spellbook/spell_crafter/spell_crafter.py:
  SpellCrafter.run_phase_root_blueprints` (uses `spellbook._spell_id_pool.keys()` and
  `spellbook._spell_id_pool[...]` directly).
- Claim: Phase 11 uses live spell_id_pool for plan building.
  Evidence: `src/melder/spellbook/spell_crafter/spell_crafter.py:
  SpellCrafter.run_phase_execution_plan` (passes `spell_lookup=self._spell._spellbook._spell_id_pool`).
- Claim: Circular DFS now uses in-place path mutation.
  Evidence: `src/melder/spellbook/spell_crafter/validation/strategies/circular_dependency_strategy.py:
  CircularDependencyStrategy.validate` (path append/pop).
- Claim: Phase 5 per-spell blueprint compilation occurs for non-root spells.
  Evidence: `src/melder/spellbook/spell_crafter/spell_crafter.py:
  SpellCrafter.run_phase_root_blueprints` (calls `build_blueprint_for_spell_id` when
  blueprint missing for a spell_id).
- Claim: Phase 11 builds three variants per spell.
  Evidence: `src/melder/spellbook/spell_crafter/spell_crafter.py:
  SpellCrafter.run_phase_execution_plan` (NO_OVERRIDES_FAST, OVERRIDES,
  OVERRIDES_WITH_MUTATIONS).
- Claim: Path tuple churn in occurrence planning + root overlay.
  Evidence: `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
  (multiple `path + (param_name,)`) and
  `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:
  SpellSystemRootBlueprintBuilder._overlay_sockets_and_index` (`socket_path = path + (...)`).
- Claim: SpellSystemAdjacencySnapshot allows live `all_spell_ids` view.
  Evidence: `src/melder/spellbook/spell_crafter/system/spell_system_adjacency_snapshot.py:
  SpellSystemAdjacencySnapshot.all_spell_ids` docstring.
- Claim: spell_id_pool includes contracted spell IDs.
  Evidence: `src/melder/spellbook/spellbook.py:Spellbook._register_contracted_spell_id`,
  `_update_contracted_spell_id`, `_unregister_contracted_spell_id` mutating
  `_spell_id_pool`.
- Claim: RootResolutionBlueprint is intentionally a dumb container for DAG +
  order + socket metadata.
  Evidence: `src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py:
  RootResolutionBlueprint` docstring and slots.
- Claim: Phase 8 topological sort uses queue index traversal (no pop(0)).
  Evidence: `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:
  OccurrencePlanBuilder._build_execution_order` (`queue_idx` loop).
- Claim: Phase 8–11 factories build a UnitOfWork per spell.
  Evidence: `src/melder/spellbook/spellbook.py` phase factories listed above.
- Claim: Spell-level validation strategies rescan the world per spell.
  Evidence: `circular_dependency_strategy.py`, `duplicate_spell_name_strategy.py`,
  `binding_resolution_cycle_strategy.py` iterate `spellbook._spell_id_pool` during
  `validate()`.

## GPT Pro Claims Requiring Runtime Repro (Still UNKNOWN)
- Any timing/cProfile/tracemalloc ranking or absolute numbers.
- Any “largest phase” or “top allocator” assertions beyond the code sites noted above.

## Existing Tickets to Map Against
- `context_compass/tasks/2026-01-31_root_blueprint_overlay_cost_task.md`
- `context_compass/tasks/2026-01-31_execution_plan_build_overhead_task.md`
- `context_compass/tasks/2026-01-31_conjure-occurrence-plan-hotspots_task.md`
- `context_compass/tasks/2026-01-31_phase6_socket_ref_sanity_hotspot_task.md`
- `context_compass/tasks/2026-01-31_conjure-phase-churn_task.md`
- `context_compass/tasks/2026-01-31_phase8-11_spell-id-pool_task.md`

## Ideas to Evaluate (from user notes)
- Phase 5: reduce per-spell blueprint compilation
  - Lazy non-root blueprints at meld time
  - Global blueprint + view-based blueprints
  - Memoize build_blueprint_for_spell_id
- Phase 11: reduce plan variant construction overhead
  - Build only default plan, lazy-build other variants
  - Config-driven variant selection
  - Build base once, specialize variants
- Phase 8/10/11: reduce path tuple/alloc churn (path interning)
- Phase 6: reduce validation repeated work via shared caches
- Scheduler: avoid per-spell UoW when no-op or existing creation
- Phase 6/validation: use spell_id_pool directly (avoid copies)
- Misc: micro-optimizations in snapshot filtering
- Optional: "fast conjure" mode (skip some validation)
- Optional: free-threaded parallelism in conjure phases

## Mapping (Idea -> Existing Ticket -> Notes)
- Phase 5 root blueprint overlay cost:
  -> `2026-01-31_root_blueprint_overlay_cost_task.md`
  -> Aligns with hotspot `_overlay_sockets_and_index`; code evidence confirms
     tuple path creation in overlay.
- Phase 5 per-spell blueprint compilation (lazy / global view / memoize):
  -> PARTIAL fit to `2026-01-31_root_blueprint_overlay_cost_task.md`
  -> Gap: lazy/global/memoize is not explicitly scoped; likely needs extension
     or new task if we choose any of these structural changes.
- Phase 11 plan build overhead (micro-optimizations, reduce redundant work):
  -> `2026-01-31_execution_plan_build_overhead_task.md`
  -> Fits if we keep three variants and optimize within build.
- Phase 11 lazy variants / config-driven variants / base-plan specialization:
  -> GAP (explicitly outside current execution-plan task non-goals).
- Phase 8/10/11 path tuple churn (path interning):
  -> PARTIAL fit to `2026-01-31_conjure-occurrence-plan-hotspots_task.md`
  -> Gap: interning is larger than current scope; current task focuses on
     queue/keys/DFS allocations, not interning.
- Phase 6 hotspot in `SocketRefSanityStrategy`:
  -> `2026-01-31_phase6_socket_ref_sanity_hotspot_task.md`
  -> Direct match; code evidence verifies strategy location.
- Validation shared caches (reduce repeated work across strategies):
  -> GAP (no existing ticket).
- Scheduler: avoid per-spell UoW when no-op / existing-creation:
  -> PARTIAL fit to `2026-01-31_conjure-phase-churn_task.md`
  -> Gap: current ticket focuses on phases 5-7 scheduling; UoW filtering for
     later phases not explicitly covered.
- Phase 6 use spell_id_pool directly (avoid copies):
  -> GAP (current `2026-01-31_phase8-11_spell-id-pool_task.md` is Phase 8/11 only).
- Micro-opts in `_filter_snapshot_to_visible_spells`:
  -> GAP (not covered by existing tickets).
- "Fast conjure" mode (skip validation):
  -> GAP (behavior/API change; not covered).
- Free-threaded parallelism:
  -> GAP (no existing ticket).

## Gaps (Ideas Without Coverage)
All gaps below remain UNKNOWN until a dedicated ticket is approved:
- Lazy non-root blueprints / global blueprint view / memoize build_blueprint_for_spell_id.
- Lazy or config-driven Phase 11 plan variants; base-plan specialization.
- Path interning for occurrence/param/socket paths.
- Shared validation caches across strategies.
- Phase factory prefiltering for existing-creation / no-op phases beyond 5-7.
- Phase 6 spell_id_pool direct use (remove dict copies).
- `_filter_snapshot_to_visible_spells` micro-optimizations.
- "Fast conjure" mode (validation skipping).
- Free-threaded parallelism for conjure phases.

## Sequencing Recommendation (Low Risk -> High Risk)
1) Finish/validate existing targeted hotspots:
   - `phase6_socket_ref_sanity_hotspot` (local algorithm change).
   - `root_blueprint_overlay_cost` (Phase 5 overlay/indexing).
   - `execution_plan_build_overhead` (Phase 11 build micro-opts).
   - `conjure-occurrence-plan-hotspots` (Phase 8 queue/alloc fixes).
2) Small-scope low-risk gaps:
   - Phase 6 spell_id_pool direct use (avoid copies).
   - `_filter_snapshot_to_visible_spells` micro-opts.
3) Medium-risk structural changes:
   - Lazy/non-root blueprint strategies or memoization.
   - Phase 11 lazy/config variants.
4) High-risk / architectural changes:
   - Path interning across occurrence/param/socket paths.
   - Shared validation caches across strategies.
   - Fast-conjure validation mode.
   - Free-threaded phase parallelism.

## Steps / Checklist
- [x] Re-read the user-provided profile/tracemalloc notes and capture the exact
      functions and phases mentioned (verbatim references).
- [x] Map each idea to one or more existing tickets (or mark as gap).
- [x] For each mapped idea, list expected impact, risk, and evidence needed.
- [x] Identify gaps (ideas without a ticket) and label as UNKNOWN.
- [x] Produce a ranked sequencing recommendation (low-risk -> high-risk).
- [ ] Share the investigation summary with the user and get direction.

## Deliverables
- Investigation summary with a mapping table (idea -> existing ticket).
- Gap list (ideas without coverage) marked UNKNOWN.
- Recommended sequencing and risk notes.

## Files / Paths Impacted
- `context_compass/tasks/2026-01-31_conjure-optimization-investigation_task.md`

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: relying on unverified performance data leads to incorrect priorities.
  Mitigation: require an in-repo repro before implementation work.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Mapped the GPT Pro claims to verified code evidence, aligned ideas to existing
tickets, and listed gaps (UNKNOWN) that require dedicated approval. Recommended
sequencing prioritizes existing hotspot tickets before higher-risk structural
changes (lazy blueprints/variants, path interning, validation caches).
