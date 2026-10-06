# Code description patch: the generic construction's dict literal (S8)

- Patch id: lazy_instance_results_2026_10_03
- File: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py`
- Owner: fable_0
- Created: 2026-10-03T18:51:39Z

<!-- BEGIN ENTRY: "Generic construction: control flow" -->
## Control flow
1. `render`: `self._direct` is computed as today; `_dict_mode` is gone; no `instance_results = {}` line.
2. `_place`: for each shared site, `needed` collects the providers of EVERY member placed inside it (direct or
   generic) and of the site itself, minus the members inside; the result is the miss's outer `v` parameters.
3. `_emit_context`: builds each child (shared hit or many), no store line.
4. `_emit_construct(index, step, direct, supplied, indent, lines)`, generic branch: take `masked` (when supplied)
   or `step`; `keys = [key for _, keys in masked_or_step.dependency_resolution_order for key in keys]`; map each
   key to `index_by_key[key]` (raise RuntimeError when absent - cannot happen after `_place`); bind
   `key{p}` constants; emit `{indent}instance_results = {{{key_a}: v{a}, ...}}` (or `= {}`); then the
   construct line exactly as today.
5. `_miss_arguments`: `args` for the root with `__args__`, then the outer values; no dict.
<!-- END ENTRY: "Generic construction: control flow" -->

<!-- BEGIN ENTRY: "Generic construction: edge and error semantics" -->
## Edge and error semantics
- A step whose order lists one key twice (two parameters fed by one provider) gets one literal entry; dict
  literals keep the last duplicate, same value.
- A collection parameter with n keys contributes n entries; `_build_kwargs_no_overrides` reads each.
- The supplied-values path builds the literal from the masked step, so supplied parameters contribute no
  entry - the helper never reads them (it never did: `masked` dropped them from the order).
- Failure in the constructor: unchanged (`_raise_meld_construction_error`); a missing key cannot occur.

## Invariants / idempotency
- The literal is rebuilt per construction (a miss runs once per cold build; a generic many step once per
  creation); no shared mutable dict is held in the namespace.

## Explicit non-goals
- No change to `_construct_spell_instance` / `_build_kwargs_no_overrides`; no change to direct steps; no
  change to the manifest compiler's lowering.
<!-- END ENTRY: "Generic construction: edge and error semantics" -->
