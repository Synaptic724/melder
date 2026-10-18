# Architecture patch: find_spell_by_spell_id_2026_10_17

## Objective and non-goals
- Objective: a lookup by spell_id returns the spell that owns that spell_id, or nothing. The owner's rule
  (2026-10-17): a spell_id (the SHA `bind` and `bind_inactive` return) and a SpellIndex (its ULID) are separate
  things - sharing an index follows whatever spell the index has active, sharing a spell by spell_id is exactly
  that spell - and a spell_id lookup never answers with the spell the index has active.
  `Spellbook.find_spell_by_id` breaks the rule: it finds a parked spell under its spell_id in `_inactive_spells`,
  then returns `_spells[that spell's index]`. Renamed `find_spell_by_spell_id` (the owner's name) and made exact;
  `Conduit.get_spell_by_id`, renamed `get_spell_by_spell_id` (owner, 2026-10-17: "yeah use
  get_spell_by_spell_id"), and `Conduit.get_spell_permissions` answer through it. The Rift room command of the
  same name is renamed `get_spell_by_spell_id` too, and the room lookups that turned a spell_id, or a source id
  naming one, into its index and answered with the spell the index has active, or with any record of that index,
  answer exactly that spell (owner, 2026-10-17: "update it all bro if its there and misunderstood then update it").
- Callers that used the lookup to reach the spell an index has active keep that answer by asking the index
  explicitly: the spell_id names a member, and its index is asked for its active spell. Their behaviour does not
  change in this patch.
- Non-goals: the other five places that swap a spell_id for its index's active spell or copy
  (`Spellbook._find_contracted_spell_by_id`, the contract row `Detail`, `ConduitWard._get_spell_in_contracts`,
  `ConduitWard._get_all_spells_in_contracts`, `ConduitWard._validate_contracts_and_define`) wait for the owner;
  so does `Meld._current_in_pool` and the three places that file a borrowed copy under
  `spell_index.selected_spell_id`. The internal `Spellbook._get_spell_by_id_via_aether` and the static room's
  `describe_spell_status_by_id` keep their names (not asked). No decision on what a transfer or a dependency grant
  should do with a parked spell_id (open with the owner; kept as today). A version in an index minted by
  `remove_from_spell_index` is missing from the frame registry, so the Conduit lookup still raises for it before
  the Book is asked (pre-existing; STORY-2026-10-17-minted_index_missing_from_frame_registry).

## Changed components
- Spellbook: `find_spell_by_id` -> `find_spell_by_spell_id`; `_get_spell_by_id_via_aether` calls it.
- Conduit: `get_spell_by_id` -> `get_spell_by_spell_id` (exact through the lookup); `get_spell_permissions`
  (exact through the lookup); `_resolve_transfer_spell` (explicit index step); the notch target's error message;
  the notch and index-move docstrings that cite the old answer.
- ConduitWard: the grant check (renamed call); the two dependency walks and `_transfer_spell_ownership` (explicit
  index step); the outbound half of `_get_spells_in_contract_by_conduit` (exact through the lookup).
- TransferOfOwnership: `_resolve_spell`, `_deps_resolvable_on_target`, `_transfer_owned_dependencies` (explicit
  index step); `_dirty_dependencies` (renamed call).
- Rift command surfaces: `CommandSystem.get_spell_by_id` -> `get_spell_by_spell_id` (its action name, raw-access
  label and advertised name with it); `CommandSystem.get_spell_by_source_id` exact through the new
  `_get_spell_by_record_locked`; `StaticCommandSystem.get_spell_by_id` -> `get_spell_by_spell_id` and
  `get_spell_by_source_id` exact through the new `_meld_live_spell_from_records_locked`, which the index path
  shares.
- Renamed call only: AmbiguousProviderStrategy, GraftRunner, RestoreEngine.
- Docstrings only: `SpellIndex.update`, `SpellIndex.has_spell`, `Spell._spell_index_unless_cleaned`.

## Invariants
- I1. `Spellbook.find_spell_by_spell_id(spell_id)` returns the Spell whose `spell_id` is the argument - the active
  version from `_spells_by_id`, else the parked version from `_inactive_spells` - or None. Never another version.
- I2. `Conduit.get_spell_by_spell_id(spell_id)` returns what the owning Book's `find_spell_by_spell_id` returns; a
  spell_id no conduit in the frame claims still raises ValueError.
- I3. The index path is explicit: a caller that needs the spell an index has active finds the spell by spell_id,
  then asks the index for its active spell (the owner's Book, or the source conduit for a transfer). That is what
  the old lookup returned for every id of an owned spell, so a transfer, a dependency grant and its preflight, and
  the transfer's dependency checks answer as before.
- I4. Locks: the lookup stays lock-free (single-key reads of two dicts). Each explicit index step takes one Book
  lock alone (`_find_spell`, `get_spell_by_index_id`, or `_spells` under that lock), at a call site that holds no
  other lock; no lock-order edge is added.
- I5. Nothing persisted or emitted reads the lookups: no cache generation, record version or codegen change.
- I6. A Rift room lookup by spell_id, or by a source id that names one, answers that spell - the Spell (capability
  and codegen rooms) or its live object (static rooms) - or raises; only a lookup by spell index id answers with
  what the index has active.

## Interface deltas
- Removed (public): `Spellbook.find_spell_by_id` and `Conduit.get_spell_by_id`. No alias - the owner's
  no-fallback rule; Breaking, with the upgrade in the release note.
- Added (public): `Spellbook.find_spell_by_spell_id(spell_id: str) -> Optional[Spell]` and
  `Conduit.get_spell_by_spell_id(spell_id: str, aetheric_frame_name: str = "default") -> Optional[Spell]` (the old
  signature).
- `Conduit.get_spell_by_spell_id`: a parked spell_id returns the parked spell; `get_spell_by_id` returned the spell
  its index has active. Breaking.
- `Conduit.get_spell_permissions` (public, signature unchanged): a parked spell_id returns that version's own
  permissions; before, the active version's. Breaking.
- Removed (public): `CommandSystem.get_spell_by_id`, `StaticCommandSystem.get_spell_by_id` and the room command
  name "get_spell_by_id"; added `get_spell_by_spell_id(spell_id, *, frame_name=None)` on both, the same signature,
  no alias. Breaking.
- `get_spell_by_source_id` (both rooms) answers the spell its source id names; before, the spell the record's index
  has active (capability and codegen rooms) or the live object of any record of that index (static rooms).
  Static-room refusals on the spell_id and source-id paths name what was asked.
- `Conduit.add_spell_to_contract(spell_id=<parked>)` and `remove_spell_from_contract(spell_id=<parked>)` resolve the
  parked spell and proceed (a grant parks the copy on the borrower, as a grant of the Spell object does); before,
  RuntimeError "Provided spell_id '<parked>' does not match inspected ID '<active>'.".

## Migration order
1. Patch docs, linked from the ticket. 2. Red tests against 0.2.8251: the exact answers, and guards that the
transfer and the dependency grant keep their answers. 3. The lookups and the explicit index steps in one change,
so no state of the tree hands a parked Spell to a transfer or a dependency grant. 4. The renamed calls and
docstrings, the Rift room lookups; the tests' renamed calls (scripted) and the tests that asserted the old answer;
the UX examples' renamed calls, experts 17 and 26 corrected to the exact answer they now get. 5. Suites, GIL off
and on, and the UX example harness. 6. System docs and indexes, graph, release note, the notch (the next number
at landing, above melder_0's 0.2.8252, M0-183), NOTICE to melder_0.

## Rollback
- Revert the change set. Nothing is persisted or cached under either method's name.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md (Notes 2026-10-17T19:41:06Z, 19:49:27Z, 20:00:43Z, 20:22:39Z, 20:53:48Z, 21:24:30Z) |

## Code description patch
- Not required: no new control flow, error semantics, rollback path or lock.
