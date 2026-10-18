# Component patch: Binding Pipeline - the managed settings leave the fingerprint (managed_settings_spell_id_2026_10_17)

## Metadata
- Patch ID: managed_settings_spell_id_2026_10_17
- Component: Binding Pipeline (Bind, Spell, SpellIndex) - `Bind.sha256_profile`, `Bind.spell_id_inspector`,
  `Bind._bind_logic`, `Bind._managed_fingerprint_part`; docstrings of ManagedSpellMode, Spell, SpellCrystal and
  RestoreEngine that state the old rule
- Status: approved (owner, chat 2026-10-18: "just do the 4")
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T00:10:00Z
- Updated: 2026-10-18T00:42:22Z

## Component Purpose and Boundary
- Current boundary: `sha256_profile` hashes the binding profile, spell_name, spellframe, binding_name, existence, the
  resolved disposal names, resolvable (the hash domain) and - only when `managed_spell_mode` is given - one last part
  `managed:<mode>:<limit>:<timeout>:<reset names>` (`_managed_fingerprint_part`; S2 of the managed epic, 0.2.8242).
- Target boundary: the same inputs without the managed part. `_normalize_managed_options` still validates and
  normalizes the four settings once, before the fingerprint, and the Spell still keeps them; nothing else hashes them.

## Before/After Behavior Summary
- Before: Worker bound managed with limit 1 and Worker with limit 2 at one address are two spell_ids, so a settings
  change (`cleanup_spell` then `bind`, or `bind_inactive` on the index) makes a second version with its own pool.
- After: both are one spell_id - the id the managed binding had at 0.2.8241, before the part existed. Re-staging it is
  the existing duplicate refusal; a rebind after `cleanup_spell` keeps the spell_id (its pool takes the new settings,
  component_patch_managed_pool_rebind.md). Non-managed ids are byte-identical (the part was never added for them).

## Interface Deltas
- Inputs: `sha256_profile(profile, *, spellframe, spell_name, binding_name, existence, disposal_method_names,
  resolvable)` - the four `managed_spell_*` keywords are removed (internal API). `spell_id_inspector` keeps its four
  keywords: it normalizes them with `_normalize_managed_options` exactly as bind does, so it refuses what bind
  refuses, and hashes without them. `_bind_logic` passes no setting to the fingerprint.
- Outputs: a managed spell_id equals the hash of the same inputs without the managed part.
- Error semantics: unchanged - every refusal of `_normalize_managed_options` stays, before any registry change.

## State and Lifecycle Deltas
- Owned state changes: none (the Spell's four fields are unchanged).
- Lifecycle/cleanup changes: none.
- `_managed_fingerprint_part` is removed: its only caller was the fingerprint.
- Docstrings and comments that say the settings are hashed are corrected: `_bind_logic`'s contract and its comment
  above the normalization, `sha256_profile`'s contract, `spell_id_inspector`'s contract, `ManagedSpellMode`'s class
  docstring ("identity data"), the Spell's field comment, `SpellCrystal.managed_bind_options` and
  `RestoreEngine._bind_one_active` ("gets its own spell id back"). spell.py and restore_engine.py are in melder_1's
  fix #1 until the owner closes it (M1-25), so those two corrections ride with part B.

## Failure Mode Deltas
- New failure mode: `bind_inactive` of a settings-only version onto an index that holds the spell raises the existing
  RuntimeError "Spell ID collision detected. ..." with nothing registered (it was accepted as a second version).
- New failure mode: under process-wide spell ids, a second frame binding the same managed class at the same address
  and disposal list is refused by bind's cross-frame duplicate check, as for any spell (it was a second spell_id when
  its settings differed).
- Removed failure mode: none. Changed failure mode: none.

## Dependency and Ordering Constraints
1. Lands with component_patch_managed_pool_rebind.md in one notch: without the pool's re-composition a settings change
   by rebind would keep the old settings.
2. Lands after melder_1's 0.2.8253 and its NOTICE M1-26 (it frees __version__, the release note and the system
   documents).

## Validation Expectations
- Unit (test_bind_managed_spell_options.py, moved to the new rule): every settings variant of the golden managed
  binding hashes to one id, the managed id without a part (`GOLDEN_MANAGED_WITHOUT_PART`); the twelve existing
  golden ids, the frame/name/disposal id and the callable and instance ids stay byte-identical; `spell_id_inspector`
  equals bind's fingerprint for a managed class and still refuses an option on another existence.
- Integration (a real Spellbook): a settings-only `bind_inactive` is refused and leaves the Book as it was; `bind`
  after `cleanup_spell` with other settings returns the same spell_id; a restore of a world recorded under this rule
  rebinds every managed spell with its recorded settings and the same spell_id.
- Probes: probe_same_id_staging S1 (refused), S2 (same id).

## Unknowns and Open Decisions
- ANSWERED (owner, chat 2026-10-18): only the four settings leave the fingerprint (architecture patch).
- UNKNOWN: none.

## Context / Handoff Summary
- What changed: nothing yet; the prototype dropped the part and the unit suites showed exactly the two tests that pin
  the part's form failing (S6's MEASURE note).
- Remaining risks: records with two settings-only versions in one index (architecture patch, decision request).
- Next entrypoint: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile`.
