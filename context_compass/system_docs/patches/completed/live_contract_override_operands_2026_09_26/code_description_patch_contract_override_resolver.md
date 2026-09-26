# code_description_patch_contract_override_resolver

## Metadata
- Patch ID: live_contract_override_operands_2026_09_26
- Component: compiler leaf (`CodegenSignature`) and codegen creation system shared assets
  (`CodegenCreationSchemaHelpers`)
- Status: implemented (owner-run suites pending)
- Owner: fable_0 (cowork)
- Created: 2026-09-26T11:57:20Z
- Updated: 2026-09-26T12:42:22Z

## Control Flow
1. `build_contract_override_ref(consumer_spell_id, param_name, key)` (phase 9): returns the tuple
   `("__contract_override__", consumer_spell_id, param_name, key)`; `key` is a `str` kwarg name or an
   `int` positional index.
2. `CodegenSignature.project_contract_payload_entry(param, value, refs)` (leaf, stdlib only): return
   `value` when `is_replayable_contract_payload_value(value)` (None, exact bool/int/float/str, exact
   tuples of those - freeze fixed points, so the bytes equal the previous frozen rows), else
   `refs[param]` (missing -> `RuntimeError`); for `"__args__"`: `None` -> `None`, a list/tuple ->
   `tuple(item if replayable else refs["__args__"][index])`, a replayable scalar -> itself, anything
   else -> `RuntimeError`. Row builders (`build_phase11_step_ir_row`,
   `build_no_overrides_codegen_creation_step_signature_row`, the many_only helpers' two builders and
   `_build_many_only_no_overrides_row`) call it for every payload entry and for the positional payload.
3. `is_contract_override_ref(value)`: `type(value) is tuple and len(value) == 4 and value[0] ==
   "__contract_override__"`.
4. `resolve_contract_override_ref(ref, spell_lookup, descriptor_cache)`: `spell = spell_lookup[consumer]`
   (missing -> `RuntimeError`); `descriptor = descriptor_cache.get((consumer, param))` else read
   `inspect.signature(spell.spell, annotation_format=Format.FORWARDREF).parameters[param].default`
   (missing parameter, empty default, or a default that is neither `SpellContract` nor `SpellMap` ->
   `RuntimeError`), store it; `payload = descriptor.override`; `dict` payload: `payload[key]` for a
   `str` key, `payload["__args__"][key]` for an `int` key; `list`/`tuple` payload: `payload[key]`;
   a missing key -> `RuntimeError`.
5. `resolve_contract_payload_row_values(row, spell_lookup, descriptor_cache)`: returns
   `(payload_items, positional)` with every ref replaced by its value (tuples walked element by element);
   scalars pass through untouched; the row is not mutated.
6. `contract_payload_refs_from_row(row)`: rebuilds the refs map a hydrated adapter carries (keyword refs;
   `__args__` -> tuple with the ref at each referenced index and `None` elsewhere); `None` when the row
   carries no ref.
7. `generalized_manifest_no_overrides_compiler.resolve_contract_payload_rows(rows, spell_lookup)`:
   shallow-copies every row that carries a payload or a positional override with (5) applied; other rows
   pass through as the same object; called once at the top of `hydrate_no_overrides_executor` and
   `build_specialized_no_overrides_executor`.

## Edge / Error Semantics
- A ref never appears in generated source: values ride the bindings (`step_contract_values`,
  `step_positional_args`) or the hydrated step adapters.
- The descriptor cache is a plain dict owned by the hydration call; nothing module-level.
- `Format.FORWARDREF` avoids NameError on TYPE_CHECKING-only annotations (2026-09-26 invariant).

## Invariants / Idempotency
- Resolution is pure over (row, live descriptor); repeated hydration yields the same objects while the
  descriptor is unchanged.

## Explicit Non-Goals
- No caching of resolved values across contexts; no validation of the value; no override-lane changes.
