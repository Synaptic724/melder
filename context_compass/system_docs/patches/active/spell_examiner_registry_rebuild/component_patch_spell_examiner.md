# component_patch_spell_examiner

## Component purpose and boundary in current architecture
`SpellExaminer` should become the registry-driven profile factory for spell and
object examination.

## Before/after behavior summary
- Before:
  Registry-driven middle state with:
  - explicit `threading.RLock`
  - default names `binding`, `resolution`, `ai`
  - private helper creators for each of those names
- After:
  One registry-driven `create_profile(...)` entrypoint with only:
  - `general`
  - `detailed`
  No explicit registry lock and no helper creator methods on the class surface.
  The profile objects themselves own the two-step build/complete lifecycle.

## Validation expectations
- default builders are registered at construction
- default builder names are only `general` and `detailed`
- `create_profile(...)` owns the target/profile guards directly
- no `_create_binding_profile`, `_create_resolution_profile`, or
  `_create_ai_profile` methods remain on the class
- no explicit `threading.RLock` remains on `SpellExaminer`
- no separate general/detailed strategy layer remains
