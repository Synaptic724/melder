# Architecture Patch: spell-index graft lane

- Patch ID: spell_index_graft_2026_07_12
- Ticket: STORY-2026-07-12-spell-index-graft
- Status: active

## Objective
Restore grain finer than a conduit slice: ONE spell_index (all members,
custody, selection) captured as a versioned dict and re-integrated into
a LIVE host book through the normal verbs only (bind creates the fresh
index; bind_inactive parks members onto it). Conservative overlap rule:
resident members refuse by default / skip with shortfall under
skip_resident - existing indexes are NEVER mutated (general_0's
add/remove seams untouched).

## Interface Deltas (additive)
- Spellbook.conduit property (public accessor for the conjured root
  conduit; retires the _conduit seam for borrowers).
- PersistenceProfile.capture_index_graft(index_id) + PersistenceSystem
  passthrough: versioned graft record (index twin payload + per-member
  custody payloads + custody_state).
- crystal_loader_system/graft_runner.py - GraftRunner (single-use):
  version gate -> host readiness (conjured book) -> per-member residence
  check (frame.find_index_for_spell) -> hydrate via the normal import
  lane -> selected member binds ACTIVE (fresh index) -> parked members
  bind_inactive onto it -> detached report with recorded->live identity.
  No LoadGate (grafts are user-verb activity, not world replays).
  Hydration v1 = import lane only; retained-text rebuild for graft
  members is a flagged follow-up.
- Crystallizer.capture_index_graft(index_id) /
  graft_index(record, host_spellbook, skip_resident=False) facades
  (activation-gated; live-object facade per create_spell_crystal
  precedent).

## Rollback
All additive: delete runner + capture + facades + the conduit property.
