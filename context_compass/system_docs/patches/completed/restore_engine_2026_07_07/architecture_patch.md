# Architecture Patch: Crystallizer Restore Engine (restore_engine_2026_07_07)

## Metadata
- Patch ID: restore_engine_2026_07_07
- Status: active
- Owner ticket: tickets/stories/2026-07-07_restore_engine_load_checkpoint_story.md
- Created: 2026-07-07T03:05:00Z

## Objective
Land the restore engine: `PersistenceSystem.load_checkpoint(checkpoint_id)`
unfolds a recorded world on a fresh boot by folding the checkpoint chain and
replaying it through the EXISTING public runtime verbs. No new public API on
runtime classes; the engine is a driver, not a new surface.

## Non-Goals
- Synthetic-module re-import (parent epic M3/M5): synthetic-rooted spells are
  REPORTED as shortfalls.
- Hook callable restoration (markers only, by design): REPORTED.
- Storage adapters (persistence epic, sequenced LAST).
- MutationResearch internals (separate agent; the recorded MR state switch is
  reported, not replayed, in this cut).

## Changed Components
1. `src/melder/crystallizer/persistence/restore_engine.py` (NEW)
   - `RestoreEngine` (Cleanable; cleanup() directly after __init__): single-use
     driver. Verbs: `restore(checkpoint_id)` -> `RestoreReport`.
   - `RestoreReport` (Cleanable, value-only fields + plain containers): built
     counts, shortfall entries (kind, key, reason), old->new identity map,
     replayed-window bounds. Exposed as detached `describe()` dict.
2. `src/melder/crystallizer/persistence/persistence_system.py`
   - `load_checkpoint` body: validate id (unchanged), construct RestoreEngine,
     delegate, return None (facade contract unchanged) while the report is
     retrievable via the engine-call return path on the crystallizer facade.
3. `src/melder/crystallizer/crystallizer.py`
   - `load_checkpoint` facade returns the detached report dict (was None +
     NotImplementedError passthrough).
4. `src/melder/crystallizer/persistence/crystals/spell_crystal.py` (+ the
   constructor read path) - CAPTURE GAP fixes:
   - `_disposal_method_names` (sorted list off `Spell.disposal_method_names`).
   - `_profile_family` ("detailed" when the live spell's attached profile is a
     SpellDetailedProfile, else "general"; derived WITHOUT importing examiner
     types at module scope - duck check on class name to avoid import pressure).
   - Both appear in `describe()`; cleanup dels extended.

## Invariants (must hold after patch)
- R-A covenant: crystallizer-off worlds byte-identical (engine only runs when
  explicitly invoked; capture-gap fields read existing spell state).
- Never-rehydrate-ULIDs: engine mints fresh identities; recorded ids live only
  in the translation map inside the report.
- Checkpoint-shaped replay, never raw map-merge.
- All-or-nothing: a replay failure tears down every unit the engine built
  (books/conduits cleaned in reverse build order) then re-raises.
- Re-emission during replay is INTENDED: the rebuilt world re-records itself
  into the active profile under fresh identities.

## Replay Order (canonical, data-driven from folded state)
1. Aether configuration (payload -> create_configuration/configure/activate;
   skip if the live Aether is already configured - report as skipped).
2. Frame postures (recorded frame twins define per-frame SpellbookConfiguration
   posture inputs).
3. Spellbook configs (payload -> set_property loop; lossy str-coerced values
   classified; hooks -> shortfall entries from hook_names).
4. Conjure (one root conduit per recorded book with a conduit twin:
   name/policy/dynamic from ConduitCrystal).
5. Binds by SpellbookCrystal.bind_order: hydratable actives -> Spellbook.bind
   (spellframe restored by NAME string - normalize_frame_key parity);
   staged members -> Conduit.bind_inactive onto the translated index anchor.
6. Notch to recorded SpellIndexCrystal selections.
7. Links from ConduitCrystal.link_targets (initiator side).
8. Clusters (create + add members via ConduitCloud; shares via cluster verbs;
   leader last).
9. Contracts LAST (details/index subscriptions re-granted through the public
   contract verbs inside link transaction windows).

## Migration Order / Rollback
- Capture-gap fields land first (additive; old cached checkpoints without the
  new keys restore with empty disposal names + "general" profile family and a
  shortfall entry noting the absence).
- Engine lands second; facade flip last. Rollback = revert facade body to the
  NotImplementedError (engine module is inert without the seat).

## Ticket Coverage Matrix
| Patch section | Implementation | Validation |
| --- | --- | --- |
| Capture-gap fields | spell_crystal.py fields+describe+cleanup | unit: describe carries both; old-item absence tolerated |
| Fold | RestoreEngine._fold_chain | unit: later-wins, tombstones, window bounds |
| Translate | RestoreEngine identity map | unit: no recorded ULID escapes into the live world |
| Replay 1-9 | RestoreEngine._replay_* stages | integration: seal->wipe->reload->restore round trip |
| Shortfalls | RestoreReport entries | unit: hooks/replay_required/synthetic/lossy-config classified |
| All-or-nothing | engine teardown path | integration: injected failure -> world absent |
