# Component Patch: StaticCommandSystem

## Before
- Static command relied on `meld_existing_spell(...)` to reject unsupported
  existences indirectly.

## After
- Static command explicitly rejects:
  - `Existence.many`
  - `Existence.unique_per_spell_space`

## Contract
- Static direct spell fetches fail fast when the published spell existence is
  unsupported for static, even if some local runtime state exists elsewhere.
