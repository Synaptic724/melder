# Component patch: owner stamps through an ownership transfer (managed_spell_quantity_2026_10_15, S6)

Components: TransferOfOwnership (the flip's stamp, `_migrate_inactive_members`, the rollbacks of both) and Creations
(`discard_managed_quantity`). Story: STORY-2026-10-15-managed_ownership_transfer. Control flow, the rollback order
and edge semantics: the code-description patch beside this.

## Before / after
- Before (0.2.8245): rows move right - `_move_creations` carries every member's rows (a managed version's pool
  among them) to the target, `_teardown_creations` takes the active member's rows out, rollback puts rows back (S3,
  S4) - but the owner stamp does not follow them. A stamp is what `Spell._add_owned_conduit` writes: the owner id,
  name and store (`_owner_creations`), a fresh CreationContextFactory and the caching posture; for a managed version
  it also composes the version's pool in that store (`ensure_managed_quantity`). The flip stamps the active member
  onto the target and nothing stamps it back on rollback; parked members are moved without a stamp
  (`_owner_conduit_id` only); a notch never stamps (U9). The S6 probe on 0.2.8245:
  - B: a parked managed version, moved and notched in on the target, raises the missing-pool error.
  - D: a failed moving transfer leaves the active member on the target's store: the owner's meld raises missing-pool.
  - E: a failed no-move transfer leaves an empty registered pool in the target and the member on the target's store:
    the owner melds into the target's pool and a release by class raises "Session is managed by 2 pools".
  - F: `unique` after a failed transfer builds a second object into the target's store.
  - G: a parked `unique` version, moved and notched in on the target, stores its object in the source's store.
- After:
  - The flip stamps the active member through `_restamp(spell)`: it registers the rollback that stamps the member
    back onto the source root, stamps it onto the target, then - for a managed version whose pool the stamp composed
    (the target store held none under the id before) - registers the rollback that discards that pool.
  - `_migrate_inactive_members` moves the parked members' maps as before, then calls `_restamp` for every moved
    member that carries a stamp (`_owner_creations` is set). A member never stamped - a version staged with
    `bind_inactive` before conjure - is moved as before: maps and `_owner_conduit_id` only.
  - A stamp is the one conjure, bind and the flip already write (`_stamp_owner(spell, root, book)`):
    `spell._add_owned_conduit(root._id, root._name, root._creations, dynamic_environment=root.__dynamic_environment__,
    creation_gate_controller=root._creation_gate_controller, caching_enabled=book._resolve_system_caching_enabled())`.
  - `_discard_composed_pool(store, spell_id, pool)`: `store.discard_managed_quantity(spell_id, pool)` removes the pool
    only while it is still the store's pool under the id, and unregisters it; the transfer then cleans it. It is
    empty: the lineage is disabled for the whole transfer, so nothing leased from it.
  - Rows, which rows each mode takes, and the row rollbacks are unchanged.
- Outcomes. Move: a parked managed version's pool and its stamp both end in the target, so a notch there leases from
  the moved pool and releases reach it. No move: the target composes fresh pools for the active and the stamped
  parked versions; the source keeps the parked versions' old pools, as no-move keeps their other rows. Failure: every
  stamp names the store it named before, the pools are where they were and the registry lists them as before.

## Interface deltas
- Internal, new: `Creations.discard_managed_quantity(spell_id, pool) -> bool`; TransferOfOwnership `_stamp_owner`,
  `_restamp`, `_discard_composed_pool`.
- Internal, unchanged: `_rollback_spellbook_move`, `_rollback_inactive_members`, `_move_creations`,
  `_teardown_creations`, `_rollback_creations_move`, `extract_spell_creations`, `restore_spell_creations`.
- Public: none. Persisted: none. No cache generation, record version or spell id moves.

## State / failure deltas
- A transfer still disposes nothing: the only pool it cleans is one it composed and discards, and no object was ever
  in it.
- After a no-move transfer a stamped parked managed version has a pool in each root: the source's old one (its idle
  objects disposed when the source tears down, like the parked version's other rows) and the target's fresh one.
  Once that version is notched in, a release by class meets two pools of the selected version and raises the
  documented ambiguity ("<Type> is managed by <k> pools: ... Pass spell_id=... or conduit=... to pick one.");
  `ManagedSpellLease.release()` and a release with `conduit=` are unaffected.
- Recorded for review, not changed: a lineage that comes back, by a moving transfer, to a root still holding such a
  parked pool replaces it, and `restore_spell_creations` cleans the replaced pool (S4), disposing its idle objects.
- Rollback stays best-effort (`_rollback` runs every action and swallows its failure; the incident is recorded): a
  stamp-back that raises leaves that member's stamp as the failed step left it, and the next action still runs.
- Unchanged: a release racing a transfer meets the gap between extract and restore and raises ValueError (not
  managed) for that call.

## Dependency / ordering
- S3: `ensure_managed_quantity` at stamping and the `managed` row; S4: register and unregister follow the stores.
- Rollback runs in reverse registration order: row rollbacks, then each re-stamped parked member (its discard, then
  its stamp-back), the parked maps, then the active member (its discard, then its stamp-back),
  `_rollback_spellbook_move`, the registry flip, the force-unshare pre-clean, the disable.
- The epic's B8 line "parked members move as rows; they are not re-stamped" becomes "they are re-stamped".
- Raised to the owner, outside this story: conjure stamps only the Book's active spells, so a version staged before
  conjure is never stamped and notching it in fails for every existence.

## Validation expectations
- Unit, both GIL modes, beside test_transfer_of_ownership.py on its fakes: the flip registers the stamp-back before
  stamping; a managed active member with no target pool registers the discard, one with a held pool does not;
  migrate re-stamps stamped parked members and skips unstamped ones; each rollback stamps back onto the source and
  discards only the composed pool; the reverse order; a stamp that raises still leaves its stamp-back registered.
- Unit, both GIL modes: `Creations.discard_managed_quantity` - identity, unregister, a cleaned store, other maps
  untouched, a second discard, concurrent discards (exactly one wins).
- Integration, both GIL modes: the probe's B, D, E, F and G as tests with the fixed outcome, A and C kept, releases
  and registry entries after each.
- The existing transfer suites (unit, component, integration) and the whole tree green in both modes.
