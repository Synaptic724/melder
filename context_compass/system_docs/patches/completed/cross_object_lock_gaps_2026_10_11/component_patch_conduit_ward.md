# Component patch: ConduitWard and Contracts (cross_object_lock_gaps_2026_10_11)

## Before / after
- `_emit_index_notch`, `_emit_index_destroy`, `_emit_index_member_added`, `_emit_index_member_removed`: walked
  `self._contracts.values()` with no lock, after the owner's transaction had ended (notch, add/remove index, bind
  inactive) or with no transaction (cleanup_spell); a link or sever admitted in that window resized the dict, the
  emission raised "dictionary changed size during iteration" after the owner's change had committed, and the borrowers
  not yet visited stayed out of step (a destroyed index still subscribed; a borrower left with no active copy). After:
  each walk runs under `with self._lock:` (no copy); contract records are emitted after the lock, as before.
- `_contract_member_spell`: `Contract._add` ran with no lock; after: under the contract lock, as
  `_uncontract_member_spell` already removes under it.
- `_get_spell_in_contracts` (public `Conduit.get_spell_in_contracts`): walked a contract's detail maps holding only
  the caller's ward lock. After: under that contract's lock, trying the detail keyed by the id first (O(1)); the
  lineage walk runs only for another version of a contracted lineage, and both paths resolve the same index. The
  contracted-spell resolution through this conduit's Book runs after the contract lock is released.
- `_get_spells_in_contract_by_conduit` (public `get_spells_in_contract_by_conduit` and the by-name variant): walked the
  two detail maps with no contract lock and resolved inbound ids through `Conduit.find_contracted_spell` - which takes
  the conduit lock while this method holds the ward lock, the reverse of link and sever (conduit lock, then ward
  locks): a lister and a sever on the same conduit deadlocked. After: both maps are walked under the contract lock and
  every id is resolved by key through the Book, taking no conduit lock: inbound through
  `Spellbook._find_contracted_spell_by_id(sid, peer_id)`, outbound through `Spellbook.find_spell_by_id(sid)` (the
  Book's id maps; the old outbound route through `Conduit.get_spell_by_id` swallowed its exceptions).
- Dependency, Spellbook Core: `_find_contracted_spell_by_id` answers by key before its 0.2.8230 snapshot walk - the
  active borrowed copy from `_contracted_spells_by_id[conduit_id][spell_id]`, a parked copy through its index
  (`Spell._spell_index_unless_cleaned`, the parked spell's own lock) keying the lineage's active copy in
  `_contracted_spells`. Only a version this Book holds no copy of falls back to the walk.

## Interface deltas
No signature changes. The listing no longer calls the Conduit lookups.

## State / failure deltas
The races' RuntimeErrors (and the cleaned-Detail and missing-field errors of a borrower inspection) no longer occur,
and the listing no longer hangs against link or sever. A link or sever of the owner waits for an in-flight emission;
an owner's member write waits for an in-flight borrower read. The emission bodies call no user code.

## Dependency / ordering
ward -> contract (as sever) and ward -> Book (as link); the contract reads take Book, spell, Detail and SpellIndex
locks under the contract lock, none of which ever wait for a contract or ward lock (spellbook.py and the contract
methods take neither).

## Validation expectations
Forced interleavings: cleanup_spell and notch_spell mid-emission against owner.link(C); get_spell_in_contracts
mid-walk against a member stage; the listing under the ward lock against borrower.sever_link(owner) (red: both threads
blocked). The listing unit test answers outbound from the Book without calling the Conduit lookup. The ward, contract,
index-link and transfer suites stay green.
