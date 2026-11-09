# component_patch_compiler_phase_3

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: SpellCompiler Phase 3 (`CompilerPhase3`) and its socket record (`SpellSocketDescriptor`, topology)
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Component Purpose and Boundary
- Current boundary: Phase 3 resolves each socket and records the per-spell topology; a class lookup reaches only a
  spell bound bare (`_answers_class_lookup`, 0.2.8278).
- Target boundary: unchanged for resolution. Phase 3 also records, on a class-lookup miss, the spells of that class a
  class lookup does not reach ("hidden candidates"), for Phase 4, Phase 6 and the watch index.

## Before/After Behavior Summary
- Before (0.2.8280): a miss records UNRESOLVED_INPUT (single) or a NORMAL collection socket with no target, whatever
  is bound elsewhere; `_resolve_spellmap_default` raises RuntimeError on every miss.
  EVIDENCE: src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1279-1292 (miss branch), :982-987
  (SpellMap raise), :548-601 (index), :1047-1141 (`_build_local_topology`).
- After:
  1. `_hidden_type_key(spell_obj) -> Optional[str]` (static): None when `_answers_class_lookup(spell_obj)` or
     `_spell_definition_key(spell_obj) is not None` (a Protocol's own definition never counts, D5); else
     `_spell_type_key(spell_obj)`.
  2. `_build_candidate_index` adds a fifth bucket `by_hidden_type` (type key -> entries): every spell whose
     `_hidden_type_key` is not None, appended once in the same loop. `_index_buckets_for` and every resolver are
     unchanged (resolution never reads this bucket).
  3. `_hidden_class_candidates(spellbook, annotation, *, candidate_index, collection) -> (ids, frame_keys)`:
     - () and () when `_annotation_kind(annotation)` is CONTRACT, or NAME with `collection=True` (a label lookup);
     - key = `_annotation_key(annotation)`; entries = `by_hidden_type[key]` (index path) or the scan
       `_iter_all_spells` filtered by `_hidden_type_key(s) == key` (scan path) - one predicate, equal membership;
     - single socket: drop METHOD, METHOD_WITH_BINDING_NAME, LAMBDA_METHOD_WITH_BINDING_NAME; keep non-resolvable
       (D5). Collection: keep resolvable only (D5);
     - ids: one `spell_index.selected_spell_id` per SpellIndex, sorted; frame_keys: the distinct `spell_obj.key[0]`
       (address frame key) of the kept spells, sorted.
  4. `_build_local_frame_dag`, miss branch (`if not resolved:`), annotation normalized by
     `_normalize_annotation_for_matching(dep.target_annotation)`:
     - SINGLE_BY_ANNOTATION: `socket_unresolved.add(key)` as today; hidden = `_hidden_class_candidates(...,
       collection=False)`; when ids: `socket_hidden[key] = (ids, frame_keys)`. `Optional[Class]` without a default
       takes this path (D5).
     - COLLECTION_BY_ANNOTATION with `not dep.is_optional`: hidden = `(..., collection=True)`; when ids:
       `socket_hidden[key] = (ids, ())` (no watch keys: the valid consumer injects `[]` or is refused at Phase 6).
     - SPELLMAP_DEFAULT: `_resolve_spellmap_default(..., hidden_out=found)`; when it returns {} with `found`:
       `socket_unresolved.add(key)`; `socket_hidden[key] = (ids, frame_keys)` of `found`.
  5. `_resolve_spellmap_default(spell, spellbook, dep, *, hidden_out: Optional[list] = None)`: the explicit-spell
     branch without a spellframe, on no candidate, takes hidden = the pool spells whose `.spell is spellmap.spell`
     (every registration of X, since none was reached). With hidden and `hidden_out` given: extend it, return {}.
     With hidden and no `hidden_out` (direct callers): raise the old RuntimeError with one sentence appended (below).
     With no hidden (X bound nowhere), a frame-named or frame-only miss, or several candidates: raise as today (D4).
  6. `_build_local_topology(..., socket_hidden=None)` writes `hidden_spell_ids` and `hidden_frame_keys` on the
     descriptor of each key in `socket_hidden`; every other descriptor keeps ().
  7. `SpellSocketDescriptor` gains two trailing fields with defaults: `hidden_spell_ids: Tuple[str, ...] = ()` and
     `hidden_frame_keys: Tuple[str, ...] = ()`; docstring: descriptive only - never traversed, planned or published.

## Interface Deltas
- Inputs: `_resolve_spellmap_default` keyword `hidden_out`; `_build_local_topology` keyword `socket_hidden`.
- Outputs: the two descriptor fields; the fifth index bucket; a SPELLMAP_DEFAULT socket may now be UNRESOLVED_INPUT
  (only with hidden ids; its `dependency_key` is the SpellMap's `canonical_key`, e.g. ("english", "__default__")).
- Error semantics: a `SpellMap(Class)` miss with Class registered elsewhere no longer raises inside Phase 3 (Phase 4
  refuses it). Direct callers without `hidden_out` get the old text plus: "English is bound only where this class
  lookup does not reach: English at (spellframe='Greeter', binding_name='english') - use
  SpellMap(spellframe=Greeter, binding_name='english')." (entries rendered by `HiddenProviderReport`).

## State and Lifecycle Deltas
- Owned state changes: none. The bucket lives in the pass-scoped `resolution_pass_cache` with the other four
  (benign build race unchanged); the descriptor stays frozen; no lock is added.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none raised here; Phase 4 turns the record into HIDDEN_PROVIDER.
- Removed failure mode: the Phase 3 RuntimeError for a `SpellMap(Class)` whose Class is registered elsewhere (it
  surfaced as PhaseExecutionError at conjure and as a bare RuntimeError at a late bind, leaving the spell without a
  topology).
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The scan path and the index path get the predicate in the same change (invariant 2).
2. The descriptor fields land with the snapshot row change (component_patch_structural_snapshot_and_cache.md) - a
   valid dynamic spell's empty `list[Class]` socket can carry hidden ids, so rows must carry them.
3. Phase 4's strategy lands in the same change: a recorded socket without its strategy would leave the consumer
   valid with a socket that names candidates nobody reports.

## Validation Expectations
- tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py, added: hidden ids and frame keys equal
  on the scan and the index path for a placement matrix (Protocol, Protocol + name, category, category + name, bare +
  name, two frames, an existing object); empty for a bare class (control), a Protocol annotation, a string
  collection, a Protocol definition under a frame; method spells excluded on single sockets; non-resolvable spells
  excluded on collections only; the `by_hidden_type` bucket; descriptors carry the ids on UNRESOLVED_INPUT, SPELLMAP
  and empty required collection sockets and nowhere else; resolution unchanged for every control.
- Same file, rewritten (measured flips): the 5 cases of
  `test_resolve_spellmap_default_explicit_spell_without_a_spellframe_refuses_an_address_it_does_not_name` - with
  `hidden_out` they return {} and fill it; without it they raise the extended text. Updated by design: the index
  key-set asserts in `test_indexed_candidates_equal_the_scan_for_every_kind` and
  `test_indexed_candidates_equal_the_scan_for_an_existing_object` (add "by_hidden_type").
- Evidence target 1: the unit file the GIL off and on; the probe matrix re-run (sockets: UNRESOLVED_INPUT with ids).

## Unknowns and Open Decisions
- UNKNOWN: none for this component.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: a caller of `_resolve_spellmap_default` outside Phase 3 relying on the raise - none in src; the
  direct callers are the unit tests in test_compiler_phase_3.py (other "could not be resolved" matches in the suite
  are unrelated messages: the cluster leader, contract overrides).
- Next entrypoint: `CompilerPhase3._hidden_type_key`, then `_build_local_frame_dag`.
