# Command-Level Meld Helpers Architecture Patch

## Objective
Add shared command-level spell activation helpers over the existing conduit
meld seams.

## Non-Goals
- No codegen command work.
- No broader spell getter redesign.
- No viewer changes.

## Changed Components
- `CommandSystem`
- `StaticCommandSystem`
- `interfaces.py` (`ICommandSystem`)

## Boundary Contract
- existing spell-object getters keep returning `ISpell` metadata/runtime spell
  objects
- new helpers provide explicit activation semantics:
  - `meld(...)` for create/reuse
  - `meld_existing_spell(...)` for reuse-only
- static denies the create-path helper
- capability and dynamic inherit the shared activation helpers

## Migration Order
1. add shared command-level meld helpers to `CommandSystem`
2. deny `meld(...)` in `StaticCommandSystem`
3. update `ICommandSystem` and supported-method introspection
4. add focused capability/static tests
