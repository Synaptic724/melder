# component_patch_spellcompiler_validation_pipeline

## Metadata
- Patch ID: override_site_plan_2026_09_26
- Component: SpellCompiler and Validation Pipeline (Phase 9 artifact processor; override key resolution)
- Status: draft (S1; S5 section added)
- Owner: user (implementation: melder_0)
- Created: 2026-09-26T11:28:08Z
- Updated: 2026-09-26T18:08:38Z

## Component Purpose and Boundary
- Current boundary: Phase 9 fits instance, injection, contract, order, runtime and override-targeting
  sections. Override targeting is keyed by logical path strings built from the Phase-5 socket overlay
  (one ref per socket per logical path).
- Target boundary (S1): Phase 9 also fits `site_graph_shape`, a physical view keyed by instance key with no
  path enumeration. A pure resolver turns a key tuple into winning operands over that view. The existing
  targeting section stays and keeps serving today's runtime until S3.

## Before/After Behavior Summary
- Before: the only override structure is `override_targeting_shape` (size proportional to logical paths).
- After (S1): additionally `site_graph_shape` with
  - `sites`: one `SpellSite` per instance key reachable from the root, parents first. Fields: `index`,
    `instance_key`, `spell_id` (selected id), `shared` (instance key has no path), `params`.
  - `params`: one `SpellSiteParam` per Phase-3 topology socket in position order. Fields: `name`,
    `position`, `parameter_kind`, `socket_kind_value`, `is_collection`, `is_optional`, `source_kind`
    (`dependency`, `unresolved_input`, `override_required`, `contract`, `plain`) and `dependency_sites`
    (site indexes; several for a collection, in injection order).
  - `root_site_index`, `site_index_by_instance_key`, `param_index` (parameter name -> (site, name) pairs in
    site order) and `path_counts` (logical root paths per site; root = 1).
  All fields are values (str, int, bool, tuples), so S2/S3 can persist them in the manifest.
- `OverrideKeyResolver.resolve(site_graph, keys, positional_arity)` returns `OverrideKeyResolution`:
  `targets` (raw targets per key before cuts), `winners` ((site, param) -> winning key), `positional`
  (root param -> `__args__` index), `conflicts` ((site, param, first key, other key)) and `inactive_keys`.

## Interface Deltas
- Inputs: `SpellCodegenModel.instance_shape`, `injection_shape`, and Phase-3 local topologies via
  `spell._spellbook._spell_system_states.get_local_topology_by_id` (the source the injection processor
  already reads).
- Outputs: `model.site_graph_shape`; `section_names()` gains `"site_graph_shape"`.
- Error semantics: the resolver raises `RuntimeError` with today's texts:
  "No sockets found for override path '<a>b>'.", "No sockets found for unique override '*n'.",
  "Unique override '*n' matched N sockets; expected exactly one.", "No sockets found for broadcast
  override '**n'.". `TargetSpec.parse` errors (`ValueError`) pass through unchanged.

## State and Lifecycle Deltas
- Owned state changes: `SpellCodegenModel` owns `site_graph_shape` and cleans it like the other
  processor-owned sections; the strategy cleans a superseded section on refit (same pattern as today).
- Lifecycle/cleanup changes: `SpellSiteGraphAnalysis.cleanup()` clears its dicts and deletes its fields.
  The resolver holds no state.

## Failure Mode Deltas
- New failure mode: a missing injection spec or topology for a reachable instance key raises
  `RuntimeError` during Phase 9 (same posture as the injection processor). Existing-creation spells and
  topologies that are absent produce sites with no parameters, as the injection processor does.
- Removed failure mode: none in S1.
- Changed failure mode: none in S1 (no runtime consumer).

## Dependency and Ordering Constraints
1. `spell_site_graph_processor` runs after `spell_injection_processor` (it maps dependency instance keys
   from injection sources) and before `spell_override_targeting_processor`.
2. Sites are ordered parents first by a DFS post-order reversal from the root; `path_counts` is computed in
   that order.
3. S1 must not change any emitted source or cache payload (Invariant 5 in the architecture patch).

## Validation Expectations
- Unit: analysis construction and cleanup; strategy over hand-built model sections (many, shared diamond,
  collection, plain default, unresolved input, override-required, contract).
- Unit: resolver key forms, ranks, cuts, conflicts, positional arity, error texts.
- Component: differential oracle against `SpellOverrideTargetingCodegenCreation` on conjured graphs.
- Existing: `test_spell_artifact_processor_core.py` strategy order and section names updated.
- Evidence target: 3.14t and GIL runs of the touched unit/component files plus the full unit suite.

## Unknowns and Open Decisions
- UNKNOWN: collection coverage in today's tests (the oracle records today's last-member behavior as a known
  difference instead of asserting equality for PATH through a collection).
- DECISION_REQUEST: none.

## S5: Phase-5 Path Overlay Retired
- Before: Phase 5's `SpellSystemRootBlueprintBuilder._overlay_sockets_and_index` walked every (node, path) pair
  below a blueprint's root, minted a path id per parameter chain in the blueprint's `PathRegistry` and recorded one
  `SocketRef` per socket per path, for shared and many nodes alike. Phase 5 builds a blueprint per spell, so the
  walk cost followed logical paths (binary chain of 15 sites: 65,504 refs, 56% of conjure; its readers took most
  of the rest). Readers: Phase-6 `SocketRefSanityStrategy` (duplicate refs; its index checks need a built
  `DagIndex`, which only the unreferenced `SpellOverrider` builds), the Phase-8 analysis-reuse key (socket rows,
  artifact-local and redundant with the pool topology rows), the dormant phase2-5 capture. None needs paths.
- After: `_install_fresh_index(blueprint)` gives each blueprint a fresh `DagIndex` and `PathRegistry` and records no
  `SocketRef`. Phase 8 mints every path id it uses into that registry, as it already did for paths the walk had
  not minted. Blueprint DAG, `ordered_node_ids`, `requires_spellspace_request` and the reachability memo are
  unchanged.
- Interface deltas (private only): `_overlay_sockets_and_index(blueprint, topologies)` becomes
  `_install_fresh_index(blueprint)`; `build_root_blueprints` and `build_blueprint_for_spell_id` no longer read
  `snapshot.topologies`, so their "Missing topologies in SpellSystemAdjacencySnapshot" RuntimeError goes.
- State and failure deltas: compiled blueprints' `socket_refs` are empty; `SocketRefSanityStrategy` finds nothing to
  report on them; `ensure_dag_index_built` builds an empty index. Path ids in phase-11 rows (instance keys,
  `override_match_prefix`) may be numbered in Phase-8 order: values only, same shape. No cache generation:
  hydration treats persisted path ids as labels (`resolve_path_registry` has no caller since S3), and the version
  notch already cold-resets older bundles.
- Unchanged: every meld result, constructor count and emitted executor shape; Phase-8 occurrences.
- Validation: tests that pinned the per-path output are rewritten to this contract (DAG and order kept; sanity
  tests inject hand-built refs; targeting tests over compiled blueprints removed, the engine keeps its hand-built
  unit tests); full suites on 3.14t and GIL; s5_overlay_cost.py before and after (binary chain at 13 and 15
  sites, shared and many lattices).
- Deferred to the owner's retirement decision (with S2b-3): `SpellOverrider`, `DagTargetingEngine` and the
  `DagIndex` socket maps, `SocketRefSanityStrategy`, the blueprint socket API, `resolve_path_registry`, the Phase-8
  key's socket rows and the phase2-5 socket rows (fable_0's seam, M0-37).

## Context / Handoff Summary
- What changed: S1 contracts for the new section and resolver.
- Remaining risks: conjure cost of one more processor pass (expected linear; measured in S1 validation).
- Next entrypoint: code_description_patch_override_key_resolver.md.
