# Component patch: SitePlanRuntimeHelpers - the missing-pool message

## Metadata
- Patch ID: parked_versions_wired_at_conjure_2026_10_16
- Component: `SitePlanRuntimeHelpers.raise_missing_managed_pool`
  (src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py)
- Writer: melder_0 (synaptic_python_developer)
- Created: 2026-10-16T09:42:54Z
- Status: built as written; promoted at landing (0.2.8248) and archived 2026-10-16T11:41:08Z

## Before (0.2.8247)
- The one missing-pool MeldExecutionError, raised by a per-creation pool read in an emitted plan and by
  `Conduit.managed_spell_meld`: "Managed spell '<name>' has no pool to lease from: its owner root was torn down, or
  this version was never given one (a version staged with bind_inactive before conjure and notched in after it). Meld
  it through a live root, or stage the version after conjure."

## After
- "Managed spell '<name>' has no pool to lease from: its owner root was torn down, or its owner store holds no pool
  for this version. Meld it through a live root that owns it." The pre-conjure staging cause no longer exists once
  conjure stamps parked versions, and "stage the version after conjure" is no longer a remedy. The first clause is
  kept, so text quoting it (the release note) stays true.
- The docstring keeps both read failures (AttributeError: no owner store or a torn-down one; KeyError: no pool under
  the id) and names the one remaining way a version is never stamped: a stamp that raised and was logged.

## Interface deltas
- None; the exception type, its fields and the call sites are unchanged.

## Validation expectations
- tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py: its two assertions on
  the old text match the new text (red until the message changes).
