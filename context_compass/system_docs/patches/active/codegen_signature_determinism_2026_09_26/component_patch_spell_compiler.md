# component_patch_spell_compiler

## Metadata
- Patch ID: codegen_signature_determinism_2026_09_26
- Component: SpellCompiler and Validation Pipeline (IR seams: signature path; phase-8 occurrence
  analyzer strategy) and the codegen creation system's shared-assets helper facade
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T09:05:00Z

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
- After (freeze): primitives, dict, list/tuple, set exactly as before; classes and functions ->
  `"<module>:<qualname>"`; enum members -> `"<module>:<qualname>:<name>"`; any other object ->
  `("__unhashable_object__", "<module>:<qualname of type(value)>")`. Objects whose `repr` was already
  stable (dataclasses, enums via `repr`) change bytes ONLY if they are enums (now canonical) - the
  corpus test decides whether the gauntlet book carries any; expected none.
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
- Outputs: `freeze_phase11_schema_value` returns canonical strings/markers for the object cases above
  instead of `repr`; `hash_codegen_signature` bytes unchanged for previously deterministic inputs; the
  phase-8 fast key is smaller (a digest string replaces the pool-wide rows).
- Error semantics: unchanged; no new exceptions. (Alternative the owner may choose: raise
  `MeldExecutionError` at plan time for an unhashable payload object instead of marking it.)

## State and Lifecycle Deltas
- Owned state changes: one new pass-cache slot (`phase8_pool_digest`), dying with the pass units as the
  existing two do; no new artifact slots.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: process-local executor signatures for object-valued contract payloads (cache
  miss every process; false hit only on identical reprs); silent divergence of the two serializer copies.
- Changed failure mode: a signature-algorithm drift would now be caught by the corpus and determinism
  tests instead of surfacing as stale full-hit caches.

## Dependency and Ordering Constraints
1. Capture the corpus fixture with the shipped code before any edit (task 2, step U3 prerequisite).
2. Land the leaf module and both facade delegations before the phase-8 hoist (the hoist uses the hash).
3. Sequence edits to `shared_compiler_executions.py` after melder_0's missing_dependency_sockets hunks
   land; re-verify with `git diff -w` before each patch.
4. Phase-8 edit confined to the key path; NOTICE to updater_1 and melder_0 precedes it.
5. Promotion into `src_components.md` (IR seams block) and index regeneration in the same pass, at
   story closure.

## Validation Expectations
- Test/validation item 1: unit tests for tags, freeze cases, set handling, delegation identity
  (`SharedCompilerExecutions.hash_codegen_signature is`/delegates to the leaf function).
- Test/validation item 2: two-process determinism test on the gauntlet book (different
  `PYTHONHASHSEED`); both executor lanes.
- Test/validation item 3: corpus byte-compatibility test (before-fixture vs after).
- Test/validation item 4: phase-8 digest tests (built once per pass; None-first; equality across passes;
  change on topology change).
- Evidence target 1: owner-run pytest over `tests/unit/melder/spellbook/spell_crafter` and
  `tests/component/melder/spellbook`; breakdown harness before/after. "Not run." until reported.

## Unknowns and Open Decisions
- UNKNOWN: whether any manifest consumer reads a frozen payload value for anything but equality
  (grep at task 2 start).
- DECISION_REQUEST: none now; the marker-vs-raise choice for unhashable payload objects defaults to the
  marker and stays open to the owner during task 2's Propose -> Confirm.

## Context / Handoff Summary
- What changed: contract only; no code yet.
- Remaining risks: byte drift for a previously deterministic input (caught by the corpus test);
  concurrent edits by melder_0 and updater_1 (NOTICEs sent).
- Next entrypoint: task 2 U1 (Propose -> Confirm with exact files and symbols).
