# architecture_patch

## Metadata
- Patch ID: override_site_plan_2026_09_26
- Status: draft (S1 detailed; S2-S6 outlined and detailed in their own lanes before code)
- Owner: user (implementation: melder_0)
- Created: 2026-09-26T11:28:08Z
- Updated: 2026-09-26T18:08:38Z

## Patch Scope and Non-Goals
- Objective: implement the owner-approved override design (design v2): a site graph per root, one plan per
  override key set, and one lowering for normal and override melds, so supplied dependencies are never
  constructed and override melds run close to normal speed.
- This lane's first step (S1) adds the site graph (Phase 9) and a pure override-key resolver with a
  differential oracle against today's targeting. S1 changes no runtime behavior: nothing reads the new
  section yet.
- Non-goals for S1: any executor, emitter, dispatch, cache-format or Phase-5 change; value validation of
  supplied objects (owner decision: none, ever).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler and Validation Pipeline (Phase 9 artifact processor) | add | New `site_graph_shape` section: sites keyed by instance key, full parameter tables from the Phase-3 topology, a parameter-name index and logical path counts | Phase-9 instance and injection sections |
| SpellCompiler and Validation Pipeline (override key resolution) | add | Pure resolver from a key tuple to winning operands per (site, parameter), with today's grammar, ranks and error texts, P1 cuts and E1 conflict detection | `site_graph_shape` |
| Meld Resolution Runtime | none in S1 | S3 replaces the override executors with the key-set dispatcher | S2, S3 |
| Creations and SpellSpace | none | Slot guards are reused unchanged in S2/S3 | - |
| SpellCompiler and Validation Pipeline (PathRegistry, Phases 5 and 8) | fix | Collection members get their own child paths so their many dependencies are built per member (owner ruling 2026-09-26); cache generation 13 | Phase-5 overlay, Phase-8 occurrence graph |
| SpellCompiler and Validation Pipeline (Phase-5 blueprint builder) | remove | S5: the per-path socket overlay is retired; blueprints carry no SocketRefs and Phase 8 mints the path ids; conjure stops scaling with logical paths | Phase-8 path minting |

## Interface and Boundary Deltas
- Boundary delta 1 (S1): `SpellCodegenModel` gains the processor-owned section `site_graph_shape`
  (`SpellSiteGraphAnalysis`) and it is listed in `section_names()`. Processor strategy order gains
  `spell_site_graph_processor` directly after `spell_injection_processor`.
- Interface delta 1 (S1): new internal `OverrideKeyResolver.resolve(site_graph, keys, positional_arity)`
  returning `OverrideKeyResolution` (winners, positional placements, equal-rank conflicts, inactive keys).
  It raises `RuntimeError` with today's messages; callers keep today's `MeldExecutionError("Failed to apply
  overrides.")` wrapping. No public API changes.
- Later deltas (outline): S2 shared lowering for the empty key set; S3 key-set plans and dispatcher replace
  `execute_with_overrides` and the override emitters; S4 unresolved inputs decided in the plan; S5 Phase-5
  path overlay retired. Cache generation 12 is taken (melder_1, complete_bundle_restage); the collection
  fix takes 13; S2 or S3 takes 14, whichever first changes emitted code.
- Interface delta 2 (collection fix): `PathRegistry.extend_path(parent, name, *, member=None)`; see
  component_patch_collection_member_paths.md.

## Cross-Component Invariants
- Invariant 1: operands are a function of the key set only (owner decision P3). No step reads store state
  to choose a value.
- Invariant 2: a PATH rule whose walk crosses a parameter that another key already supplies is inactive
  (P1); every key is still validated against the graph, including under cut ancestors.
- Invariant 3: UNIQUE counts logical root paths through `path_counts`, so "matched N sockets" keeps today's
  N without listing paths.
- Invariant 4: supplied values are never inspected; the only per-call value check allowed is the E1
  equal-rank conflict guard (identity, then `==` for plain scalars).
- Invariant 5 (S1): adding the section changes no executor, emitted source, cache payload or meld result.

## Migration and Rollout Order
1. S1: `site_graph_shape` + `OverrideKeyResolver` + differential oracle (this lane's first patch). Done.
1b. Collection fix: member-specific child paths in Phases 5 and 8; cache generation 13.
2. S2: shared lowering for normal melds (empty key set), parity gate, cache generation 14.
3. S3: key-set plans and dispatcher for all families; retire the override emitters and the targeting
   runtime.
4. S4: unresolved inputs decided in the plan; retire `UnresolvedInputError.from_failed_construction`.
5. S5: retire the Phase-5 per-path socket overlay after its readers are resolved.
   S5a stops the walk; retiring the dead targeting surface it fed waits for the owner (with S2b-3).
6. S6: canonical docs, graph descriptors, assets, release note.

## Rollback Strategy
- Rollback trigger (S1): conjure regression or suite failure attributable to the new processor strategy.
- Rollback steps: remove the strategy registration and the model slot; the new modules are then unused.
- Post-rollback verification: registered strategy order and section names match the pre-patch tests.

## Validation Expectations and Evidence Plan
- S1 unit tests: site construction (many, shared, collection fan-out, plain/default, unresolved,
  override-required, contract), topological order, path counts, name index, cleanup.
- S1 resolver tests: each key form, rank order, P1 cuts (including the Codex leak case), E1 conflicts,
  positional arity, and today's three error texts.
- S1 differential oracle (component): for a corpus of conjured graphs and keys, the resolver's raw targets
  projected to (spell id, parameter) and their logical counts equal today's targeting results, and both
  raise the same messages for invalid keys.
- Existing processor tests updated for the new strategy order and section name.
- Evidence source: ticket notes of TASK-2026-09-26-build-site-graph-and-override-key-resolver.

## Ticket Coverage Map
- Epic: EPIC-2026-09-24-override-execution-performance
- Story: STORY-2026-09-26-implement-override-site-plan-lowering
- Tasks: TASK-2026-09-26-build-site-graph-and-override-key-resolver (S1, done);
  TASK-2026-09-26-fix-collection-member-many-sharing (1b); S2-S6 tasks open in sequence.

## Unknowns and Decision Requests
- UNKNOWN: whether a PATH through a collection is covered by any existing test (decides how B7 is
  qualified in S3).
- RESOLVED (S5, 2026-09-26T18:08:38Z): Phase-6 socket_ref_sanity_strategy, the Phase-8 occurrence analyzer and
  shared_compiler_executions do not need logical paths (source read; exploratory run: only tests pinning the
  overlay's output fail). See component_patch_spellcompiler_validation_pipeline.md, S5 section.
- DECISION_REQUEST: none open for S1 (Q1-Q5 approved 2026-09-26T11:26Z).

## Context / Handoff Summary
- What changed: lane opened; S1 contracts defined.
- What remains: S1 implementation and validation; S2-S6 lanes.
- Next entrypoint: component_patch_spellcompiler_validation_pipeline.md, then
  code_description_patch_override_key_resolver.md.
