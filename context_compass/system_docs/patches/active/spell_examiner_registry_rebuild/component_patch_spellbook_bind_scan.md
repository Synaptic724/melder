# component_patch_spellbook_bind_scan

## Component purpose and boundary in current architecture
`Spellbook.bind(...)`, `Conduit.bind(...)`, `scan_bind`, `Scan.scan_module(...)`,
and `SpellBinder.finalize()` form the public binding-entry boundary above
`Bind`.

## Before/after behavior summary
- Before:
  - no public profile-choice argument exists on the bind/scan entrypoints
  - all public binding paths implicitly land on the default general-profile path
  - scan metadata does not preserve a profile-choice override
- After:
  - public binding entrypoints accept `profile` with default `general`
  - `Conduit.bind(...)` mirrors and forwards the profile choice
  - `scan_bind` metadata and `Scan.scan_module(...)` preserve the profile choice
  - `SpellBinder` forwards the profile choice through finalize

## Validation expectations
- `Spellbook.bind(...)` forwards `profile` into `Bind.bind(...)`
- `Conduit.bind(...)` forwards `profile` into `Spellbook.bind(...)`
- `scan_bind` defaults to `general` and preserves explicit overrides
- `Scan.scan_module(...)` forwards metadata profile choice into `Spellbook.bind(...)`
- `SpellBinder.finalize()` forwards profile choice into `Spellbook.bind(...)`
