# Component Patch: Codegen ACL Profiles

## Objective
Extend the reusable codegen ACL profiles to carry import, builtin, and
meta-behavior posture through the existing ruleset model.

## Planned Shape
- keep frame/conduit/spell/capability ruleset families
- add validator-facing operations under the codegen capability family
- use rule `conditions` for import roots and builtin names

## Expected Operations
- `enable_imports`
- `import_modules`
- `builtin_names`
- existing:
  - `dynamic_access`
  - `mutation`
  - `contract_override`
  - `unsafe_reflection`
  - `dunder_access`

## Profile Intent
- `safe`: imports off, dangerous builtins denied, dunder/reflection denied
- `hybrid`: curated stdlib imports, dangerous builtins denied, dunder/reflection denied
- `permissive`: broad stdlib imports, broad Python posture, free-reign codegen mode
- `precision`: explicit import/builtin/meta posture through the same compiled path
