# Architecture patch: staged_signature_claims_2026_10_19

Patch id: staged_signature_claims_2026_10_19. Story: STORY-2026-10-17-staged_version_releases_active_signature
(S1 of EPIC-2026-10-17-correctness_defects). Author: melder_1 (synaptic_python_developer), 2026-10-19.

## Objective
Destroying an index a parked version left empty must not touch another spell's binding signature. Today
`Spellbook._destroy_spell_index` pops the Book's address route and releases the frame claim by the departing
member's binding key, whoever holds them, so staging a version keyed like the active one (every `bind_inactive`
folds off a throwaway index), moving a parked version back, or disposing a lone parked version takes the active
version's claim and route - in this Book or another Book of the frame.

## Non-goals
- The notch's own signature handling (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only, S2).
- Refusing a staging under a key another spell holds: staging stays open to any key (the owner, 2026-10-17).
- Restore and graft code: they stage through `bind_inactive` and inherit the fix.

## Changed components
- Spellbook Core: `_destroy_spell_index` and the arguments its two callers pass (`_apply_add_to_index`,
  `_dispose_spell`).

## Invariants
- A route `_lookup_spells[key]` is dropped by a destroy only when it routes the key to the destroyed index.
- A frame claim is released by a destroy only when the departing member holds it (by spell_id); a parked version
  claims no signature, so in a sound world the release is a no-op.
- Every other spell's claim and route, in any Book of the frame, survive staging, index moves and parked disposal.

## Interface deltas
- Internal only: `_destroy_spell_index` takes `spell_id=` (the departing member). No public signature changes.

## Locks
- No new lock or lock-order edge: the route check stays under the Book lock the pop already took; the release is
  the frame container's leaf call it already made, by spell_id instead of by key.

## Migration order and rollback
- One src change (spellbook.py), its regression tests, the system documents, one notch. Rollback: revert the seam.

## Ticket coverage
| requirement | change | validation |
| --- | --- | --- |
| claim kept on staging (C1, C2) | release by spell_id | test_bind_inactive_keeps_..., ..._before_conjure_... |
| claim kept on a move back (C3) | route check, release by spell_id | test_index_move_back_keeps_... |
| claim kept on a lone parked cleanup (C4) | same | test_cleanup_of_a_lone_parked_version_keeps_... |
| another Book's claim kept (C6) | release by spell_id | test_staging_does_not_release_another_books_... |
