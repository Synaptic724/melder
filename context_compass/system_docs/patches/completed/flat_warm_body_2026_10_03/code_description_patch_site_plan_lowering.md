# Code description patch: `SitePlanEmission._emit_shared_hit`

- Patch id: flat_warm_body_2026_10_03
- File: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py`
- Owner: fable_0
- Created: 2026-10-03T21:41:39Z

<!-- BEGIN ENTRY: "Owner-store constants: control flow and edge semantics" -->
## Control flow
1. `_emit_shared_hit(index, step, indent, lines)`: compute `store = f"c{index}"`, bind `sid{index}`.
2. If `step.existence is Existence.unique` and `not step.spell._dynamic_environment` and
   `step.spell._owner_creations is not None`: `self._bind(store, step.spell._owner_creations)` and skip the
   alias line; else append `f"{indent}{store} = {self._route(step.existence, spell_name)}"` as today.
3. The hit read, the pinned-override refusal, the miss call (`store` among its arguments) and `_emit_miss` are
   unchanged.

## Edge and error semantics
- `_dynamic_environment` is a Spell slot set by `_add_owned_conduit` (False before ownership). A borrowed or
  unowned provider therefore keeps the read; nothing new can raise at emission.
- Inside `_miss{i}` the parameter `c{i}` shadows the global of the same name (same object).

## Invariants / idempotency
- Emission is still a pure function of the steps; equal shapes in equal postures share one code object.

## Explicit non-goals
- Binding `spells[i]` itself (`s{i}`): the remaining readers of `spells[i]` are cold paths (errors, locks).
<!-- END ENTRY: "Owner-store constants: control flow and edge semantics" -->
