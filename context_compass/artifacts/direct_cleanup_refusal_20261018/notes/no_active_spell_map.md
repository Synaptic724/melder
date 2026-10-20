# No active spell in a SpellIndex - the map

STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions (S9). melder_1 (synaptic_python_developer),
2026-10-18, on 0.2.8255. Read-only: no src edit.

The owner's rule (the story's DECISION notes, 2026-10-18): cleaning up an index's active version marks it invalid
and removes it; the index keeps its parked versions with nothing active; no version is promoted or selected in its
place; whatever resolves through the index meets a hole whose error says the index has no active spell; only an
index left without members is destroyed; `cleanup_spell` no longer refuses.

## 1. The state to reach

English (active) is removed from an index that still holds French (parked). Afterwards:

- the index is alive, its members are {French}, and nothing is active (`has_active_spell` is False);
- the Book's active map (`Spellbook._spells`) has no entry for it - as for the index `remove_from_spell_index`
  mints today; a notch into it already works, because `_apply_notch` finds the outgoing version in `_spells`
  (none here) and only promotes (spellbook.py:3911-4066);
- SpellSystemStates holds no lineage for it: English's is unregistered and its verdicts retired; parked versions
  are never registered;
- the frame's registry keeps it, so French stays findable by spell_id (today the removal drops it from the
  registry; the minted index never enters it - the S4 symptom);
- the record keeps it: its index crystal is re-emitted with members {French} and no selection; English's custody
  leaves the record as today;
- English's address lookup and frame claim are released, so the address is free and a new bind can fill the hole;
- Nexus drops English's record; French was never published (only active versions are);
- index-link borrowers lose their copy of English (the member-removed emission) and keep their parked French;
- English's dependents are marked through `unregister_index`'s impact closure; their next meld finds no
  provider - the hole.

## 2. Who reads the pointer

`selected_spell_id` appears 143 times in 52 files outside spell_index.py and the build assets; 23 are prose.

- About 70 read it through an active spell (`spell.spell_index.selected_spell_id`): the compiler phases,
  codegen, the manifests, the validation strategies, Meld gating, RiskManager, UnresolvedInputError. An index
  with nothing active has no active spell pointing at it, so none of these meets it, whatever the representation.
- The readers below take an index directly; these are the ones that can meet "no active spell".

| reader | today | with None | with a "no_active_spell" id |
| --- | --- | --- | --- |
| `SpellSystemStates.register_index`, `update_dependencies`, `mark_structural_change`, `register_local_topology` | raise "selected_spell_id is unavailable" when it is None | refuse clearly, as written | register or mark a lineage under the fake id |
| `SpellSystemStates.unregister_index`, `get_local_topology` | skip on a falsy id / return None | as written | look the fake id up (a miss) |
| `Meld._gated_validation_required`, `_force_resolution_revalidation`, `_get_resolution_validity` | raise / answer unknown on None | as written | gate the fake id |
| `ContractProviderPresenceStrategy.validate` | falls back to the copy's own id on None | as written | names the fake id as provider |
| `RestoreEngine._enforce_selections`, `_live_index_for` | skip a None selection | as written | try to translate and notch the fake id (a shortfall) |
| `SpellIndexCrystal` | `selected_spell_id: Optional[str]` | as written | records the fake id as a spell |
| `Conduit.notch_spell` | fans out to borrowers only when `outgoing_id is not None and != incoming` | skips the fan-out: must change | flows through (the fake id parks nothing) |
| `Spellbook._apply_add_to_index` | proves ownership by `selected_spell_id in _spell_ids` | refuses: must change | refuses: must change |
| `ConduitWard._add_index_to_contract` | needs an active spell, refuses otherwise | refuses, clearly | refuses |
| `IndexDetail` (the index-link head) | `selected_spell_id: str` | head becomes Optional | holds the fake id |
| `GraftRunner.run` (fresh index) | needs a selected member, ValueError otherwise | refuses, clearly (S5's lane) | ValueError |
| `MutationResearch._locate_live_membership` | equality | reports parked | reports parked |
| `TransferOfOwnership._enumerate_borrowers`, `_migrate_inactive_members` | equality / skip the selected | unaffected (a transfer starts from an active spell) | unaffected |
| `Spellbook._add_contracted_spell`, `_clear_contracted_spells_for_conduit`, `_destroy_detached_link_contract` | file a borrowed copy under its lender index's selection | a stale copy is filed under None | under the fake id |

Nine of these already guard for None - raise, skip or fall back - though no index can hold None today: the code
was written expecting "no selection" to be None.

## 3. The four ideas

- None, with a flag (`SpellIndex.has_active_spell`): the value the code already guards for, and the record's type.
  The readers that cannot meet the state stay as they are; the ones that can are the table above. Recommended.
- A reserved `no_active_spell` id with a flag: the type stays a str, but the id is truthy and not None, so it
  slips past every guard above and gets registered, gated and recorded as if it were a spell; restore and graft
  would chase it. The flag would have to be checked everywhere the None guards already stand.
- A hole object in the active slot: it would sit in `_spells` and the spell pool, so the phases, melds, Nexus,
  transfers and teardown would all treat it as a spell. It breaks everything.
- A "broken" mark with the old pointer left: every reader that does not check the mark uses the removed spell's
  id. The same breakage, harder to see.

## 4. What the fix touches (a sketch for the patch)

- `SpellIndex`: `selected_spell_id` becomes `Optional[str]`; `has_active_spell`, the flag; one method that clears
  the selection when it names a given spell, under the index lock.
- The removal (`cleanup_and_remove_spell`, reached from all three doors): invalidate; unregister the lineage and
  retire its verdicts while the selection still names the spell (`unregister_index` reads it); remove the member
  and clear the selection; if members remain, keep the index in the frame registry, re-emit its crystal and skip
  the index's removal record and cleanup; if none remain, destroy it as today.
- `cleanup_spell`: the refusal goes; `Conduit.cleanup_spell` sends index-link borrowers the member-removed
  emission when the index survives, and the index destroy when it does not.
- `Conduit.notch_spell`: a notch into an index with nothing active activates the incoming version on borrowers
  and moves index-link heads.
- `_apply_add_to_index`: ownership proven through a member, not the selection.
- `IndexDetail`: head Optional; the contract crystal records None.
- The hole's message: a meld by address or by index id, and UnresolvedInputError, say the index has no active
  spell and name its parked versions (built on the error path only).

## 5. Open, for the owner

- The index `remove_from_spell_index` mints selects its parked member today (S10, ruled fine). With a real
  "no active spell" state it should probably say none too - one state, not two. Its record and graft side is
  S5's, which waits for the identity epic.
- A direct `Spell.cleanup()` or `cleanup_and_remove_spell` has no conduit, so index-link borrowers are not told
  (pre-existing); `cleanup_spell` is the door that tells them.
- `cleanup_spell` invalidates an active spell first, and `Spell.invalidate_spell` raises unless the owner conduit
  is dynamic (`Conduit.__dynamic_environment__`), so disposing an active version through `cleanup_spell` is
  dynamic-only today; the direct doors work in either posture.
- Until S5 lands, a restore drops an index with nothing active, with a shortfall - as it drops a minted index
  today.

## Evidence

- src/melder/aether/spellbook/bind/spell_index.py:83-116 (one selected id from birth)
- src/melder/aether/spellbook/bind/spell_index.py:143-205 (`selected_spell_id`, `update`)
- src/melder/aether/spellbook/bind/spell_index.py:241-275 (`remove_member` leaves the selection)
- src/melder/aether/spellbook/spellbook.py:3911-4066 (`_apply_notch`: outgoing from `_spells`)
- src/melder/aether/spellbook/spellbook.py:4155-4167 (`_apply_add_to_index` ownership check)
- src/melder/aether/spellbook/spellbook.py:4427-4568 (`_dispose_spell`: refusal, invalidate, removal)
- src/melder/aether/spellbook/spellbook.py:602-748 (`cleanup_and_remove_spell`)
- src/melder/aether/spellbook/spell.py:1597-1663 (`invalidate_spell`)
- src/melder/aether/conduit/conduit.py:295-295 (`__dynamic_environment__`)
- src/melder/aether/conduit/conduit.py:5735-5787 (`notch_spell` fan-out gate)
- src/melder/aether/conduit/conduit_ward/conduit_ward.py:2093-2219 (`_add_index_to_contract`)
- src/melder/aether/conduit/conduit_ward/conduit_ward.py:2322-2387 (`_emit_index_notch`)
- src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589 (`_emit_index_member_removed`)
- src/melder/aether/conduit/conduit_ward/contract/details.py:323-404 (`IndexDetail`)
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:437-441
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:784-790
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:845-851
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1193-1199
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1813-1819
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1863-1867
- src/melder/aether/conduit/meld/meld.py:1243-1248
- src/melder/aether/conduit/meld/meld.py:1682-1687
- src/melder/aether/conduit/meld/meld.py:1719-1723
- src/melder/aether/conduit/meld/meld.py:2188-2236 (`_resolve_spell_by_lookup_key`: the miss)
- src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:120-154
- src/melder/crystallizer/crystals/spell_index_crystal.py:79-106
- src/melder/crystallizer/crystal_loader_system/restore_engine.py:2271-2321
- src/melder/crystallizer/crystal_loader_system/restore_engine.py:2400-2440
- src/melder/crystallizer/crystal_loader_system/graft_runner.py:230-310
- src/melder/mutation_research/mutation_research.py:1485-1525
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1655-1675
- context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:397-428 (A3: the minted index)
- context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:725-752 (A12: its selection)
