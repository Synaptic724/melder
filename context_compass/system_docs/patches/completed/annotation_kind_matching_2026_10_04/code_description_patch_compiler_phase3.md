# code_description_patch_compiler_phase3

## Metadata
- Patch ID: annotation_kind_matching_2026_10_04
- Status: active
- Owner: user (agent fable_1)
- Created: 2026-10-04T01:20:00Z
- Updated: 2026-10-04T01:20:00Z

<!-- BEGIN ENTRY: "Phase 3 predicate and index: control flow" -->
## Control Flow
1. `_normalize_annotation_for_matching` (unchanged) strips Optional/Union and turns a ForwardRef into its name.
2. `_annotation_kind`: `inspect.isclass(a)` and `is_protocol_type(a)` -> contract; `inspect.isclass(a)` ->
   type; else name. `_annotation_key` lowercases as before.
3. `_matches_annotation(annotation, binding_name, spell, *, require_class_spell, collection)`:
   METHOD/LAMBDA exclusion first (singles); then one comparison chosen by (kind, collection):
   - single/type: key == type_key(spell); single/contract: key == contract_key(spell);
     single/name: key == type_key(spell) or key == contract_key(spell);
   - collection/type: key == type_key; collection/contract: key == contract_key; collection/name:
     key == label_key(spell).
   Then the binding-name filter as before.
4. `_build_candidate_index`: one pass over the pool copy appending `(position, index, spell)` to
   `by_type[type_key]`, `by_label[label_key]`, and `by_contract[contract_key]` when present.
5. `_indexed_annotation_candidates(index, annotation, *, require_class_spell, collection)`: picks the bucket(s)
   the same (kind, collection) table names - two buckets for single/name, merged by position - and replays
   the scan's dict semantics (first position, last spell object) exactly as today.
6. The resolvers only pass `collection=` through; their ambiguity / empty / resolvable logic is unchanged.

## Edge and Error Semantics
- A spell bound bare has label_key == type_key == its own class name; it is reachable by `x: Cls`,
  `x: "Cls"`, `list[Cls]` and `list["cls"]`, as before.
- A spell under a string category is reachable by `x: Cls` / `x: "Cls"` (its type) and `list["label"]`
  (its label); not by `x: "label"`.
- A spell under a Protocol is reachable by `x: Cls`, `x: Proto`, `x: "Proto"`, `list[Proto]`, `list["proto"]`
  and `list[Cls]`; never by a different class's name.
- An existing object's type_key is its instance's class name (`spell_name` at bind), unchanged.
- Two spells of one type in the pool are still an ambiguity for a single annotation; none is UNRESOLVED_INPUT.

## Invariants / Idempotency
- The predicate is pure over (annotation, spell) and the index is pass-scoped, rebuilt per resolution pass as
  before; scan and index agree on membership and order for every (kind, collection) pair - tested.
- No lock, no hot-path (meld) change; Phase 3 cost stays O(candidates) per socket.

## Explicit Non-Goals
- `_dependency_key_for_dep` (watcher key) and `BindingResolutionCycleStrategy` keep keying annotations by name;
  their approximation for type matches across frames predates this patch and is recorded as a known gap.
<!-- END ENTRY: "Phase 3 predicate and index: control flow" -->
