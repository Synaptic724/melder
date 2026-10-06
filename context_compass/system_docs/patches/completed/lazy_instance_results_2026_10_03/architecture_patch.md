# Architecture patch: lazy instance_results (S8)

- Patch id: lazy_instance_results_2026_10_03
- Status: active (entry gate for TASK-2026-10-03-implement-lazy-instance-results)
- Owner: fable_0
- Created: 2026-10-03T18:51:39Z

<!-- BEGIN ENTRY: "Lazy instance_results: objective and non-goals" -->
## Objective
A site plan in dict mode (at least one generic step) no longer allocates `instance_results` at its top nor
stores every step into it in every context; each generic construction receives a dict literal holding exactly
its dependency values, built where it runs from locals the plan already holds. Direct-mode plans are
byte-identical. Same objects, same errors.

## Non-goals
- Making generic steps direct (S12), existing-object constants (S2a), site constants (S9).
- The manifest compiler's own locals/dict lowering (other lanes); the store; the doors; the hydrators.
<!-- END ENTRY: "Lazy instance_results: objective and non-goals" -->

<!-- BEGIN ENTRY: "Lazy instance_results: changed components and invariants" -->
## Changed components
- SpellCompiler and Validation Pipeline, site-plan lowering (`src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py`): `render`, `_place`, `_miss_arguments`,
  `_emit_context`, `_emit_construct`, the class contract docstring.
- Utilities, caching system: `CachingSystem.CACHE_VERSION_HISTORY` gains generation 17
  (`lazy_instance_results`).

## Invariants (unchanged)
- A generic construction reads `instance_results` only through the (masked) step's
  `dependency_resolution_order` keys; the literal carries exactly those keys, so every read that succeeded
  before succeeds after and the same `MeldExecutionError` texts fire for a missing dependency (impossible by
  construction: `_place` raises at emission for a key with no kept step).
- Placement, build guards, P2 refusal, unresolved-input refusal, registration and the door-held root are
  untouched; providers precede consumers, so every provider of a generic step is a local in scope where the
  step is constructed (built in the same context, or passed in as an outer `v` parameter).
- Direct-mode plans emit the same source as today.

## Interface deltas
- Emitted plan source: the top `instance_results = {}`, the `instance_results[keyN] = vN` stores and the
  `instance_results` miss parameter disappear; a generic construction is preceded by
  `instance_results = {keyP: vP, ...}` (or `= {}`). Public API: none.
- `SitePlanLowering`: the private `_dict_mode` flag goes; `_miss_arguments` drops the dict; `_place` passes a
  generic member's outer providers as `v` params like a direct member's.
<!-- END ENTRY: "Lazy instance_results: changed components and invariants" -->

<!-- BEGIN ENTRY: "Lazy instance_results: migration, rollback, coverage" -->
## Migration order
1. Lowering edit (`_place`, `_emit_construct`, `_emit_context`, `_miss_arguments`, `render`, docstring).
2. Emitter unit tests re-pinned to the new source; differential and component tests added.
3. Generation 17 so executors emitted with the eager dict are retired on the next conjure.
4. Docs, graph, release note, notch, assets last (contribution guide).

## Rollback
Restore the eager emission; keep the generation bumped (old executors are re-emitted on the next conjure).

## Ticket coverage matrix
| patch section | ticket | validation |
| --- | --- | --- |
| lowering edit | TASK-2026-10-03-implement-lazy-instance-results | emitter unit tests, differential tests, component conjure |
| generation 17 | same | cache-history pin test |
| docs/graph/assets | same | index --check, graph walker, asset and bundle --check |
<!-- END ENTRY: "Lazy instance_results: migration, rollback, coverage" -->
