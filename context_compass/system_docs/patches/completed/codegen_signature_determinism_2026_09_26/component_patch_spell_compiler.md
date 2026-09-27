# component_patch_spell_compiler

## Metadata
- Patch ID: codegen_signature_determinism_2026_09_26
- Component: SpellCompiler and Validation Pipeline (IR seams: signature path; phase-8 occurrence
  analyzer strategy) and the codegen creation system's shared-assets helper facade
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T10:42:09Z

## Component Purpose and Boundary
- Current boundary: two byte-identical helper surfaces own the signature path -
  `SharedCompilerExecutions` (phases/shared_compiler_executions.py:58-137, :397-424) and
  `CodegenCreationSchemaHelpers` (codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:
  23-158); four phase-11 consumers import the latter under the alias `SharedCompilerExecutions`
  (spell_codegen_creation_cache.py:54; the three generalized steps). Phase 8's strategy owns its own key
  path (spell_occurrence_graph_analyzer_strategy.py:118-372).
- Target boundary: one leaf module `spell_compiler/shared_assets/codegen_signature.py` (stdlib only)
  implements the three helpers; both facades delegate and keep their names; the phase-8 strategy keeps
  its key path but hashes the pool-invariant rows once per pass.

## Before/After Behavior Summary
- Before (serializer): typed one-byte tags for None/bool/int/float/str/bytes; `dict`/`tuple`/`list`/
  `set`/`frozenset` and any other object go to `pickle.dumps(protocol=5)` with a `repr` fallback
  (shared_compiler_executions.py:58-109). A raw `set` of strings pickles in hash-seed order.
- After (serializer): identical bytes for every primitive, tuple, list and dict input; `set`/`frozenset`
  parts are frozen (sorted) before pickling; all other objects unchanged (pickle, then `repr`).
- Before (freeze): primitives pass; dict -> sorted `(key, frozen)` tuples; list/tuple -> tuples; set ->
  repr-sorted tuples; anything else -> `repr(value)` (:397-424), which is process-local for default
  reprs. Reached by user SpellContract override payloads through the injection processor strategy
  (spell_injection_processor_strategy.py:190-230, :303-348) into step rows and the no-overrides
  signature row (codegen_creation_schema_helpers.py:357-500).
- After (freeze) - AMENDED 2026-09-26 to the implemented rule: primitives, dict, list/tuple and set
  exactly as before; `frozenset` joins the sorted set branch; functions, bound methods and builtin
  callables -> `("__callable__", module, qualname)`; instances whose type keeps `object.__repr__` ->
  `("__object__", module, qualname of the type)`; every other value (classes, enum members,
  dataclasses, custom `repr`s) -> `repr(value)` byte-for-byte as before. Only values whose old
  rendering carried an address change bytes, so no previously deterministic signature moves and no
  cache generation bump is needed (`shared_assets/codegen_signature.py:181-291`).
- Cache-path LIMIT (found at task 2 U3, unchanged by this patch): the frozen payload values in the
  persisted step rows are executed on a cache hit - `_hydrate_steps_from_rows` rebuilds
  `contract_payload` from `row["contract_payload_items"]` and the manifest compiler binds those
  values as constructor keywords - while the in-process path compiles from the live plan's raw
  values. A non-value payload therefore constructs differently after a cache hit (before: the `repr`
  string; now: the marker tuple), and dict/list/enum payload values thaw as tuples / `repr` strings
  on that path today. RULED: owner option B, implemented by the emission gate below.
- Before (cache emission): `Spellbook._emit_spell_cache` packages every constructed spell at conjure
  end through `manifest_creation_cache.build_package` (manifest-first families) or
  `spell_codegen_creation_cache.build_package` (legacy both-lane package); neither looks at the payload
  values, so a plan with an object, callable, dict, list, set or enum payload value is persisted with
  its frozen projection and hydrates that projection into the constructor on the next process.
- After (cache emission, task 4): both builders ask
  `CodegenCreationSchemaHelpers.plan_contract_payloads_are_replayable(plan)` for each lane plan and
  return `None` when a payload value is not `None`/`bool`/`int`/`float`/`str` or a tuple of those;
  `_emit_spell_cache` treats `None` as "nothing staged" (info log, returns False), so the spell is
  absent from the bundle and the next process classifies the conduit `mixed` and recompiles that
  spell's phases 8-11. Spells with replayable payloads are unaffected. CORRECTED 2026-09-26: the
  in-process recompile of a manifest-first family still binds the frozen row projection (its lazy doors
  hydrate from the manifest), so the gate removes the persisted copy of a lossy plan but does not make
  the hot path lossless; that half is an open owner decision (fail fast, or raw-value side table).
- Before (phase 8 key path): per root, `_build_root_blueprint_rows` twice, then a fast key holding the
  raw pool-wide rows and an input signature hashing them again (strategy :267-372); the skip check
  compares key and signature before testing `_occurrence_graph_analysis is not None` (:213-219), which
  phase 5's attach nulls every pass (compiler_phase_5.py:182-216).
- After (phase 8 key path): `analyze` returns to the build path immediately when the analysis slot is
  None (no compare); the pool-invariant rows are hashed once per pass into
  `analysis_pass_cache["phase8_pool_digest"]` (benign last-writer-wins like `phase8_spell_walk` and
  `phase8_graph_shape_rows`); root rows are built once; key = `(root_spell_id, ordered_node_ids,
  id(path_registry), blueprint_socket_rows, pool_digest)`; signature = `hash(...same parts...)`. Without a
  pass cache the digest is computed per root (same cost as today).

## Interface Deltas
- Inputs: unchanged for all three helpers and for `analyze`.
- Outputs: `freeze_phase11_schema_value` returns the two marker tuples above for callables and
  default-`repr` instances instead of `repr`; every other output unchanged; `hash_codegen_signature`
  bytes unchanged for previously deterministic inputs (proved by the reference oracle); the phase-8
  fast key becomes smaller (a digest string replaces the pool-wide rows) once task 3 lands.
- Error semantics: unchanged; no new exceptions. The plan-time refusal alternative was not chosen
  (owner option B, 2026-09-26): a refused emission is a silent, logged skip, never an error.
- Outputs (task 4): `manifest_creation_cache.build_package` and `spell_codegen_creation_cache.build_package`
  return `Optional[Dict[str, Any]]` - `None` means "not cacheable"; every existing caller is the
  emission call site or a test that asserts on a package.

## State and Lifecycle Deltas
- Owned state changes: one new pass-cache slot (`phase8_pool_digest`), dying with the pass units as the
  existing two do; no new artifact slots.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none. A refused emission is not a failure: the spell stays on the compile path.
- Removed failure mode: process-local executor signatures for object-valued contract payloads (cache
  miss every process; false hit only on identical reprs); silent divergence of the two serializer copies.
- Changed failure mode: a signature-algorithm drift would now be caught by the corpus and determinism
  tests instead of surfacing as stale full-hit caches.

## Dependency and Ordering Constraints
1. The shipped helper bodies are frozen verbatim in `tests/mocks/spellbook/codegen_signature_reference.py`
   and compared against live parts on every run (replaces the planned captured corpus fixture).
2. Land the leaf module and both facade delegations before the phase-8 hoist (the hoist uses the hash).
   LANDED 2026-09-26 (commit 6fc9af345); owner-run suites pending.
3. Sequence edits to `shared_compiler_executions.py` after melder_0's missing_dependency_sockets hunks
   land; re-verify with `git diff -w` before each patch.
4. Phase-8 edit confined to the key path; NOTICE to updater_1 and melder_0 precedes it.
5. Promotion into `src_components.md` (IR seams block) and index regeneration in the same pass, at
   story closure.

## Validation Expectations
- Test/validation item 1: unit tests for tags, freeze cases, set handling, delegation identity
  (`SharedCompilerExecutions.hash_codegen_signature is`/delegates to the leaf function).
- Test/validation item 2: two-process determinism test (different `PYTHONHASHSEED`) on a plain book
  and on a contract-payload book whose payload is an object (the proof case); both executor lanes
  where the family publishes them (`tests/component/melder/spellbook/test_codegen_signature_determinism.py`).
- Test/validation item 3: corpus byte-compatibility test - reference digest vs leaf digest for every
  facade `hash_codegen_signature` call over the plain book (same file).
- Test/validation item 4: phase-8 digest tests (built once per pass; None-first; equality across passes;
  change on topology change).
- Evidence target 1: owner-run pytest over `tests/unit/melder/spellbook/spell_crafter` and
  `tests/component/melder/spellbook`; breakdown harness before/after. "Not run." until reported.

## Unknowns and Open Decisions
- RESOLVED: manifest consumers DO read frozen payload values beyond equality - the cache-load path
  executes them (see the cache-path LIMIT above).
- DECISION (owner, 2026-09-26): option B; task 4 implements the emission gate on the live plan's raw
  payload values (rows unchanged).

## Context / Handoff Summary
- What changed: signature path landed (commit 6fc9af345): leaf module, both facades delegating,
  reference oracle, unit and component tests. Phase-8 key path unchanged so far (task 3).
- Remaining risks: owner-run suites not yet reported; the cache-path payload limit awaits a ruling;
  phase-8 file received melder_1's FORWARDREF commit (disjoint hunks; task 3 rebases on it).
- Next entrypoint: task 4 G2 (the two helpers), then G3 (the gates and the call site).
