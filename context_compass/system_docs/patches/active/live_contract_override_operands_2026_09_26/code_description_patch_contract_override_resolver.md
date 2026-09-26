# code_description_patch_contract_override_resolver

## Metadata
- Patch ID: live_contract_override_operands_2026_09_26
- Component: Codegen creation system shared assets (`CodegenCreationSchemaHelpers`)
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T11:57:20Z
- Updated: 2026-09-26T11:57:20Z

## Control Flow
1. `build_contract_override_ref(consumer_spell_id, param_name, key)` (phase 9): returns the tuple
   `("__contract_override__", consumer_spell_id, param_name, key)`; `key` is a `str` kwarg name or an
   `int` positional index.
2. Row builders (`build_phase11_step_ir_row`, `build_no_overrides_codegen_creation_step_signature_row`,
   and the many_only twins): for each `(param, value)` of `step.contract_payload`, emit
   `(param, freeze(value))` when `is_replayable_contract_payload_value(value)` else
   `(param, step.contract_payload_refs[param])`; for `__args__` / `contract_positional_override`, apply
   the rule per element with the positional ref for that index.
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
   `(payload_items, positional)` with every ref replaced by its value; scalars pass through untouched.

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
