# Architecture patch: contracted_copy_removal_by_version_2026_10_16

## Objective and non-goals
- Objective: removing a borrowed version's contracted copy removes that version's copy and no other - the owner's
  rule (2026-10-16): "you remove that spell if its not active, you look in inactive, thats it". After a notch, an
  index unlink (`remove_index_from_contract`) then completes in either member order. Today it raises RuntimeError
  "Spell version <id> not found for conduit ID <lender>." and leaves a parked copy behind whenever the hash seed
  orders the parked member first (seeds 3, 4, 6, 8 and 9 of 0-9, on 0.2.8249 and 0.2.8250).
- Non-goals: no new state on the contract's per-version `Detail` rows (an open question for the owner); no change
  to the existence set `_contracted_spell_ids` (index-level by design, read only by `snapshot_state` and the
  per-conduit key checks); no change to the ward's callers, the add paths, the notch fan-out or transfers; no
  change to rule 2's marks.

## Changed components
- Spellbook, borrower side: `Spellbook._remove_contracted_spell`.

## Invariants
- A borrower Book holds each borrowed copy, by version id, in exactly one place: the active maps
  (`_contracted_spells`, `_lookup_contracted_spells`, `_contracted_spells_by_id`) or the parked map
  (`_inactive_contracted_spells`). A removal of version V touches only V's copy: the active entry whose copy's own
  `spell_id` is V, else V's parked entry; when the Book holds neither it raises RuntimeError and changes nothing.
- An active removal still marks the Book's SpellContract consumers of the copy's key (rule 2, 0.2.8250); a parked
  removal still marks nothing.
- Locks unchanged: the maps change under the Book lock; the mark, the staged-key refresh and the RiskManager call
  run after it is released.

## Interface deltas
- None public. Internal: `_remove_contracted_spell(spell_id, conduit_id)` no longer removes another version's
  active copy when asked for a member id of the same live index; asked for a version it holds no copy of, it
  raises instead.

## Migration order
1. Patch docs, linked from the ticket. 2. Red tests: unit (a parked removal beside another active version of the
index; a member id with no copy raises and keeps the active copy), integration (the unlink after a notch, each
member first). 3. The method. 4. The one component test that asserted the old match. 5. Suites, GIL off and on.
6. System docs, graph, release note, notch 0.2.8251. 7. Closure; the rebuild last.

## Rollback
- Restore the member-set match for live indexes; the unlink's order dependence returns.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md |
