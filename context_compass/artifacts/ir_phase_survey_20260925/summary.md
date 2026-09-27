# Survey summary: the structural snapshot basis (D1-D6)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 3, step S11).
Status: COMPLETE. Consolidates nine source-backed records in this directory: driver.md,
phase_01.md .. phase_07.md, structural_driver.md, resolution_driver.md, cache_seam.md,
invalidation.md. Every claim below cites the record that carries the `path:start-end` evidence;
this file adds no new source reads. Scope ruled by the owner (epic Decision Log 2026-09-26): the
basis for a STRUCTURAL SNAPSHOT - a full creation-cache hit skips phases 1-7 the way it skips
8-11, by hydrating value rows - plus the determinism-test task. Phases 8-11 are surveyed only as
far as the full-hit load path reads phase 1-7 objects.

## The one-paragraph result
Phases 1-7 already compute value-shaped results; the objects that carry them are transient. Phases
1-4 run per spell and their artifacts are RESET after every resolution pass (structural_driver.md);
what survives is registry state (`SpellSystemStates`: dependencies, topologies, structural validity)
plus two Spell fields. Phases 5-7 run once per conjure on the lead spell, read registry state only,
and produce blueprints, a system index, per-conduit validity rows and change-control wiring. A full
cache hit today still runs 1-7 and skips only 8-11; the cached executors' hydration reads exactly
two live things from 1-7: the Spell pool and the phase-5 blueprint's path registry
(resolution_driver.md). So the snapshot hydrates REGISTRY ROWS for 1-4, a BLUEPRINT (path registry
included) plus registry rows for 5-7, and re-registers one closure; nothing else in 1-7 needs to
become an object again. Two things bound the design: phase 3's identity matching (a custom-`__eq__`
frame) and index ULIDs inside phase-5 rows.

## D1 - object-bound points across phases 1-7, with verdicts
| phase | what is held live | verdict | record |
| --- | --- | --- | --- |
| 1 | annotation / element annotation type objects; `spellframe` type or str | VALUE-EXPRESSIBLE as (module, qualname) type refs or strings; identity use decided in phase 3 | phase_01.md |
| 1 | the EXACT default object of every defaulted parameter, PLAIN included | VALUE for PLAIN (phase 2 drops it, phase 3 never reads it; the constructor applies its own default); SpellMap/SpellContract descriptors are value-shaped keys | phase_01.md, phase_02.md, phase_03.md |
| 1-2 | one `RLock` per requirements/graph object and per row | RUNTIME-ONLY baggage of the carrier, not of the data | phase_01.md, phase_02.md |
| 2 | `target_annotation` (live type), `spellmap_default` (descriptor) | VALUE-EXPRESSIBLE; `contract_key` already `(frame_key, binding_key)` | phase_02.md |
| 3 | DAG node payloads = live Spells; candidate index keyed on `id()` | VALUE-EXPRESSIBLE as id/edge rows with Spell lookup by id at hydration; the index is pass-scoped | phase_03.md |
| 3 | matching: strings/ForwardRefs BY NAME, objects BY IDENTITY (`is`, `==` fallback on frames) | a canonical (module, qualname) ref reproduces the identity match except for a frame with a custom `__eq__` - IDENTITY-BEARING, owner ruling needed | phase_03.md |
| 4 | result/issue objects; pass caches `contract_provider_map`, `binding_resolution_graph` | VALUE (codes, keys, ids); caches are value graphs already | phase_04.md |
| 5 | blueprint DAG (payload None), `SpellSystemIndex`, adjacency snapshot, `PathRegistry` | VALUE rows (sorted, deterministic); registry = `(id, parent_id, segment)` rows in insertion order | phase_05.md, resolution_driver.md |
| 5 / 7 | the revalidator closure over `(spellbook, conduit_id)` | RUNTIME-ONLY; reconstructible from those two values | phase_05.md, phase_07.md |
| 6 | `SpellSystemValidationState`, `SystemDiagnostic` objects shared onto every artifact | VALUE rows; the objects are nulled by the post-pass reset anyway | phase_06.md |
| 7 | CCM component-of map | VALUE (`Dict[node_id, Set[root_id]]`), derivable from blueprint rows | phase_07.md |
| 5-6 | `lineage_id` = index ULID inside `SpellSystemNode` and `phase5_root_lineage_id` | VALUE but PROCESS-LOCAL: restore re-mints ULIDs; rows must reference lineages by binding key or translate at hydration | phase_05.md, invalidation.md |
Reflection points: phase 1 only (`inspect.signature`, `get_annotations(eval_str=True)` in the user
module namespace); Python-callback points in-phase: none in 1-7 (the phase-7 closure and the
RiskManager callbacks are Melder code); world reads: phase 1-2 none; phase 3 one query over
`_spell_id_pool`; phase 4 the pool plus posture plus `_contracted_spells`; phases 5-7 registry
private fields, the pool, owned ids, frame name, CCM (records above).

## D2 - hydrate obligations (every runtime write of phases 1-7)
| writer (record) | target | value shape | ordering | replayable from rows |
| --- | --- | --- | --- | --- |
| phase 1 (phase_01.md) | artifact `_requirements` (borrowed from the bind profile or fresh) | rows | first | yes, and reset after the pass: hydrate is optional |
| phase 2 (phase_02.md) | artifact `_symbolic_graph` | rows | after 1 | yes; reset after the pass |
| phase 3 (phase_03.md) | `SpellSystemStates.update_dependencies` (direct deps, reverse edges, gated `dependencies_changed`, dirty) | id sets | per spell, between barriers | YES |
| phase 3 | `register_local_topology` (topology + collection/contract reverse indexes) | descriptor rows | same | YES |
| phase 3 | `Spell._add_build_details`: `dependency_graph` (DAG object), `dependencies` (ids); creation context invalidated | ids; DAG object | same | ids YES; DAG object UNKNOWN reader |
| phase 3 | Nexus publication when enabled | - | same | side effect, re-run |
| phase 4 (phase_04.md) | lineage validity: `invalid` / `clear_dirty(ts)` + `valid` / `gated contract_unvalidated` | enum + ts | after the phase-3 barrier | YES (ts is metadata) |
| driver (structural_driver.md) | reset of phase 1-4 (+6) artifacts after every resolution pass | - | pass end | n/a: confirms rows, not objects, are the durable form |
| phase 5 (phase_05.md) | per owned spell: index + blueprint + `requires_spellspace_request`; invalidates 8-11 state and the creation context | objects from rows | once per conjure, lead spell | YES: rebuild blueprint (+ path registry) and index from rows |
| phase 5 / 7 | `rebuild_component_of`, `set_revalidator` (once per conduit) | map; closure | after 5 | map YES; closure re-registered from `(spellbook, conduit_id)` |
| phase 6 (phase_06.md) | per-conduit `ConduitResolutionState`: spell/root validity maps, diagnostics, `clear_conduit_dirty(ts)`; RiskManager fan-out; verdict object on every artifact | enums, rows, ts | after 5 | YES (registry); the object is nulled by the reset |
| load path (resolution_driver.md) | `spell.resolution_complete/required`, `_door_epoch`; lazy `CreationContext` | flags | after ownership wiring | YES (already cache-driven) |

## D3 - snapshot key composition (cache_seam.md)
- Per-spell tier (phases 1-3): the spell id. It hashes the constructor signature text, annotation
  names, sorted bases/MRO/method names, `spell_name`, `str(spellframe)`, `binding_name`,
  existence, disposal order and the resolvable domain; the sorted VISIBLE id set therefore fixes
  phase 3's pool projection under name matching. RISK: a type that moves module while keeping its
  rendered name keeps the id (module fingerprint decision for the design story).
- Per-conduit tier (phases 4-7): sorted visible resolvable ids, sorted OWNED ids, frame posture
  (`system_state`), sorted contracted keys, plus per-spell `_is_broken`; runtime ids (frame name,
  conduit id) are not key material. Configuration flags read on this path:
  `generalized_singleton_specialization_enabled` (hydration); phase 8-11 flags deferred.
- Envelope level (already enforced): format generation, Melder release, Python cache tag, frame
  name, conduit name.
- The dormant phase 2-5 signature is a per-spell CONTENT digest of outputs (verification stamp),
  not a lookup key; its rows define the 2-5 row schema; driver.md's hash hazards do not reach it.

## D4 - `.melc` mechanics (cache_seam.md)
One marshal envelope per (frame, conduit name) with four exact-match stamps and per-spell
nested-marshal bytes; admission at construction is wholesale (cold reset on any mismatch); emit is
temp-file plus atomic replace preserving the accepted release. Placement decision for the owner:
a structural section inside the envelope (generation bump 10 -> 11, one cold reset everywhere) or
a sidecar with its own four stamps. Classification keys on the live id set only; posture is echoed,
not used.

## D5 - invalidation surface (invalidation.md)
Every structural-validity write funnels through `SpellSystemState.set_validity` and the registry
helpers; writers: bind/rebind, post-conjure bind and the commit-side dirty marker (collection and
contract dependents), notch, index destroy and spell cleanup (impact closure), link/unlink and
contract add/remove, transfer (the only production per-conduit dirty). Cluster and leader
transactions write nothing into the registry. Posture is frozen (key input, not event). Restore
re-mints index ULIDs. Rule: capture only from a pass that ended valid and clean; hydrate by
replaying the registry writes; key tier 2 on (visible ids, owned ids, posture, contracted keys).
No new invalidation hook is needed.

## D6 - what a full hit consumes from phase 1-7 objects (resolution_driver.md)
Phases 5-7 still run on a full hit; only 8-11 skip. The lazy cache load performs zero phase 1-7
reads at conjure; first-meld hydration reads `spellbook._spell_id_pool` and
`artifact._root_blueprint_phase5.path_registry` (path ids are embedded in manifest rows as ints, so
the registry must reproduce the build's sequential assignment). Nothing reads phase 1-4 artifacts,
the phase-5 index, the phase-6 verdict objects or change-control state. Meld-time gating reads both
registry validity tiers, so a hydrate must restore the rows or the first meld reruns the phases.

## CONFLICT list (source vs documents; all candidates for owner-authorized corrections)
1. `src_architecture.md` Spellbook init step 3 says it "initializes ... SpellValidationSystem";
   the validator is per-run inside `SpellCompilerSystem` (structural_driver.md). STALE.
2. `src_architecture.md:485-486`, `:768-773`, `:1132`: the change-control dirty-root loop is
   described as live; the meld gate is armed only by `notify_spell_changed`, which no shipped path
   calls (phase_07.md). Owner ruling: public DevOps API (document fine) or dead wiring.
3. The epic's premise "the plan is not an artifact / nothing to record": a signed value-only phase
   2-5 export and consumed phase-11 step rows exist; the working representation is objects
   (driver.md). Wording, not behaviour.
4. Phase 7 duplicates phase 5's change-control writes; maps list it as the change-control phase
   (phase_07.md). Behaviour is correct; the design can fold 7 into the 5 hydrate.
Docstring residue (`SpellCrafter`, facade parameters that do not exist, "phase-2-5 cache" in
`run_local`) is listed per record and is not a behaviour conflict.

## Remaining UNKNOWNs (with where to look)
- Owner ruling: frames with a custom `__eq__` (identity-bearing match) - phase_03.md.
- `Spell.dependency_graph` runtime readers (DAG object vs ids): grep under `conduit/meld/` and
  `spell_compiler/` (phase_03.md).
- `init_signature` / `default_repr` rendering of object defaults (process-local ids?):
  `spell_examiner/profiles/general_profile.py`, `binding_profile.py:238-265` (cache_seam.md).
- Whether `bind_inactive` runs phases 1-4 for parked members: `spellbook.py` (invalidation.md).
- Cluster / leader-election effect on resolution rows: `conduit/conduit_cluster.py`.
- RiskManager reaction to hydrated validity bursts: `dev_ops/risk_manager/risk_manager.py`.
- Phase 4's eleven unread strategies and phase 6's twenty-two: read when the row set is designed.
- `DagIndex` / `SocketRef` exact fields: `dag/dag_index.py:279-520` (phase_05.md).
- Phase 8-11 configuration flags and the deferred exhaustive survey (schema story).

## Implementation entry (epic: I-0, I-1) - what this survey hands over
- I-0 signature-determinism test plus one serializer: hazards live on the phase-11 executor
  signature path (driver.md: set iteration order; `repr` fallback; duplicated serializer), not on
  the phase 2-5 digest. Small, compiler-side, protects today's cache.
- I-1 structural snapshot, behind patch docs: architecture_patch (two-tier key, envelope vs
  sidecar, capture-on-valid rule, no raw index ULIDs), component_patch for the SpellCompiler
  component (row schemas from `capture_phase2_5_codegen_ir`; hydrate = registry replay + blueprint
  rebuild + one revalidator registration), code_description_patch for the hydrator control flow
  (order: rows -> registry -> blueprint/index attach -> component-of -> revalidator -> Spell flags;
   then the existing 8-11 cache load). Gauntlet-gated tasks: capture on miss, hydrate on hit,
   invalidation parity (the D5 table as the test list), restore parity (fresh index ULIDs).
- Owner decisions the design needs before I-1: custom-`__eq__` frames; envelope vs sidecar;
  module-fingerprint in the per-spell key; whether the CCM dirty-root loop is public API.
