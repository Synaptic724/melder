# Architecture patch: managed_settings_spell_id_2026_10_17

## Metadata
- Patch ID: managed_settings_spell_id_2026_10_17
- Status: archived at the story's closure (2026-10-18T11:45:58Z): part A landed at 0.2.8254 and was promoted to the
  system documents and the graph; part B was not built - superseded by EPIC-2026-10-18-spell_identity_is_the_code
  (one object, one spell)
- Owner: user (ruling, chat 2026-10-17); melder_0 (synaptic_python_developer) (patch)
- Created: 2026-10-18T00:10:00Z
- Updated: 2026-10-18T11:45:58Z
- Ticket: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (S6 of
  EPIC-2026-10-17-correctness_defects)

## Patch Scope and Non-Goals
- Objective: the owner's ruling - "the bind call itself shouldn't impact the actual SHA256 thats absurd", a bug, and
  "you gotta notch the version for the cache". A managed binding's four settings (mode, limit, queue timeout, reset
  names) leave its spell_id, so one class bound at one address is one spell with one pool whatever its settings; a
  rebind under the same spell_id gives its pool the new settings; the notch and a cache generation retire every
  bundle written before. With one pool per class and address, a release can no longer strand one version's count in
  another version's pool (S6).
- Non-goals:
  - The other bind inputs stay in the spell_id: the address (spellframe and binding_name - one class under two
    names is two spells, and a `unique` keys its one object by spell_id), existence, the resolved disposal names and
    resolvable (each shapes the plan the creation cache keeps under the spell_id; a full hit is decided by spell ids
    and the world stamp). Taking any of them out is a separate lane that re-keys the cache and the stores first.
  - No identity tracking of leased objects (owner, 2026-10-14); `ReleaseManagedSpell`'s routing is unchanged.
  - No change to emitted plans, the record's format (RecordVersion stays 4.2.0) or non-managed spell ids.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Binding Pipeline: `Bind.sha256_profile`, `Bind.spell_id_inspector`, `Bind._bind_logic` | modify | the managed part leaves the fingerprint; `_managed_fingerprint_part` retires | none |
| Managed Spell Pools: `ManagedSpellQuantity._rebind_spell` | modify | a same-id rebind may carry new settings; the pool takes them | Binding Pipeline |
| Creations: `ensure_managed_quantity` | modify | the rebind runs after the store lock, so the store lock stays a leaf | Managed Spell Pools |
| CachingSystem | modify | generation 22 records the retirement the notch performs | Binding Pipeline |
| Docstrings that say the settings are hashed: ManagedSpellMode, SpellCrystal (part A); Spell, RestoreEngine (with part B, files held by melder_1's fix #1) | modify | they would state the old rule | Binding Pipeline |
| Spellbook: `bind_inactive`, `_apply_add_to_index` and the collision error (part B) | modify | one class staged in one index at another address or disposal list still keeps two pools; refuse it | melder_1's release of spellbook.py |

## Interface and Boundary Deltas
- Public behaviour: every managed spell_id moves once (non-managed ids are byte-identical). Two managed bindings of
  one class at one address and disposal list share a spell_id: re-staging one with only other settings is refused as
  the same spell ("Spell ID collision detected"), and changing settings is `cleanup_spell` then `bind`, which keeps
  the spell_id and the pool. **Breaking change** for code that staged settings-only versions or relied on two frames
  binding one managed class at one address under process-wide ids (now a duplicate, as for any other spell).
- Internal: `Bind.sha256_profile` loses its four `managed_spell_*` keywords; `Bind._managed_fingerprint_part` is
  removed; `Bind.spell_id_inspector` keeps its keywords (it still validates them as bind does) and no longer passes
  them to the fingerprint. `ManagedSpellQuantity._rebind_spell` re-composes; `CachingSystem.CURRENT_VERSION` is 22.
- Part B (public): `bind_inactive` and `add_to_spell_index` refuse a managed version whose class already backs another
  managed version of the target index (RuntimeError naming both spell_ids and the remedy, as the seams refuse).

## Cross-Component Invariants
1. A managed spell_id is the fingerprint of the class, its address, existence, disposal names and resolvable - never
   of its managed settings. Every other spell's fingerprint input is unchanged.
2. One pool per (root store, spell_id), as before; a rebind under the spell_id meets that pool and the pool's policy
   is the current Spell's settings. Objects alive stay alive and counted; nothing is destroyed by a rebind.
3. Emitted plans read no managed setting (only the pool and the record do), so no plan changes; the cache admits only
   bundles of the running release, so the notch makes every older bundle cold, and generation 22 says why.
4. Locks: the store lock stays a leaf (the rebind is called after it is released); the pool lock stays a leaf, taken
   under the Spell lock as owner stamping takes it; no user code runs under either.
5. Part B: no index holds two managed versions of one class object, so each managed class has at most one pool per
   index per root.

## Migration and Rollout Order
1. This patch and the component and code-description patches; the owner's approval; mapping note in S6.
2. Wait for melder_1's 0.2.8253 landing and its NOTICE M1-26 (it holds __version__, the release note and the system
   documents until then; spellbook.py, spell.py, restore_engine.py and fix #1's other files until the owner closes it,
   M1-25).
3. Part A: red tests (GIL off and on) -> `src/` (bind.py, managed_spell_quantity.py, creations.py, caching_system.py,
   the docstrings) -> green -> the 13 integration tests that built a second version from one class's settings move to
   versions of two classes -> whole tree -> notch (the number above melder_1's) and the release-note section ->
   system documents, indexes and graph -> rebuild last, both checks OK.
4. Part B after melder_1 releases spellbook.py (with the Spell and RestoreEngine docstrings): its own red/green,
   notch, docs and rebuild.

## Rollback Strategy
- Rollback trigger: a regression in managed leasing, releasing, transfer or restore that the suites or probes show.
- Rollback steps: revert part A's files with its notch's tests; spell_ids return to the settings-hashed form; bundles
  go cold once more (the release changes).
- Post-rollback verification: the managed suites and probes Q1-Q6 as on 0.2.8253.

## Validation Expectations and Evidence Plan
- Unit: the fingerprint ignores the settings (one id for every variant; non-managed golden ids byte-identical);
  `spell_id_inspector` parity and refusals; `_rebind_spell` re-composition per mode change, the unchanged-settings
  no-op, waiters woken; `ensure_managed_quantity` calling it outside the store lock; generation 22.
- Integration: R1 (settings change by `cleanup_spell` + `bind`: same spell_id and pool, counts true after a release),
  R2 (settings-only re-stage refused, nothing registered), R3 (mode change with idle objects above the new limit);
  restore and graft of worlds made with the new rule; the moved integration tests.
- Probes: probe_settings_rebind (R1-R3), probe_same_id_staging (S1-S2), probe_managed_release_routing (Q1-Q6, updated
  to the renamed lookup), each with the GIL off and on.

## Ticket Coverage Map
- Epic: EPIC-2026-10-17-correctness_defects
- Story: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (S6)
- Tasks: none; S6 carries parts A and B.

## Unknowns and Decision Requests
- ANSWERED (owner, chat 2026-10-18): the scope - only the four managed settings leave the spell_id; the rest stays.
- DECISION_REQUEST (owner): a record made by 0.2.8242-0.2.8253 holding two settings-only versions of one managed class
  in one index cannot rebuild both (they are one spell now). Recommended: the restore refuses it whole, as any other
  replay failure does (no restore code changes); the alternative is a shortfall naming the dropped version.
- UNKNOWN: none in the code paths read (bind.py, managed_spell_quantity.py, creations.py, caching_system.py,
  spellbook_creation_system.py's cache classification).

## Context / Handoff Summary
- What changed: nothing in `src/` yet; a prototype in a scratch mirror proved parts of A (S6's MEASURE note).
- What remains: part A (the owner's go and scope answer, 2026-10-18; melder_1's landing met, M1-26); part B and
  the legacy record after the talk that follows part A.
- Next entrypoint: component_patch_binding_fingerprint.md, then component_patch_managed_pool_rebind.md.
