# Epic — Index-Link Contract (contract identified by index_id)

- Completed: 2026-07-11T18:50:00Z
- Summary: All 7 iteration steps landed in June/July (spellbook concrete
  target, IndexDetail maps, ward add/remove, conduit facades, emission
  fan-out, eager activate, tests). Closed on owner-directed general_0
  cleanup: the exit signal (owner 3.14t green) is supplied by the repeated
  full-tree greens since (9702 latest, 2026-07-11/12) exercising the landed
  model; the authored index-link unit/integration coverage rides the tree
  via the index-ops testing epic.
- Created: 2026-06-30
- Owner: general_0 (inherited + closed by melder_0)
- Status: closed (owner-directed cleanup 2026-07-12; landed + green-covered;
  residue, if any, surfaces as new work with fresh evidence)
- Related: index-ops build epic; index-ops integration-testing epic (O1).

## Framing (corrected)

Not "spells are the wrong abstraction." The fix is narrower: a contract should be
**identified by the index it follows (`index_id`, a stable ULID), not the version it
snapshotted (`spell_id`, which churns on every notch).** A spell stays the ergonomic
handle; the contract is keyed by and tracks the index. Transfer already uses the index
as its base unit, so this is consistency, not a new paradigm.

Receiving side is delta-driven and ALREADY built: the borrower consumes
`(conduit_id, spell_id)` updates via `_activate_contract_spell` / `_inactivate_contract_spell`
/ `_add_inactive_contracted_spell` / `_remove_contracted_spell`. The index_id is the
subscription key; the active `spell_id` is what actually melds.

## Responsibility split (mirror the spell-contract design)
- **Spellbook OWNS the concrete index target:** a single dict `index_id -> SpellIndex`.
- **ConduitWard MANAGES the linking factors:** the Contract index-detail maps + the
  add/remove linking logic (mirrors `_add_spell_to_contract`).
- **Conduit is a FACADE:** `add_index_contract` / `remove_index_contract` delegate to the ward.

## Objects / methods

### Spellbook (concrete target)
- `_contracted_indexes: Dict[str, SpellIndex]`  # index_id -> the contracted SpellIndex
- `_add_contracted_index(index: SpellIndex) -> None`  # track index.id -> index
- `_remove_contracted_index(index_id: str) -> None`  # untrack (idempotent)
- cleanup: clear + del in `_cleanup_components` (mirror `_contracted_spells`)
- (later) borrower payload per index = current active spell_id + member ids, applied via
  the existing `_activate/_inactivate_contract_spell` methods.

### Contract (ward-side, contract/contract.py + a detail type)
- New index-detail maps mirroring `_details_a/_details_b`:
  `_index_details_a/_index_details_b: Dict[str, IndexDetail]`  # index_id -> IndexDetail
- `IndexDetail` (contract/details.py sibling, model on `Detail`): holds `spell_index`,
  `permissions`, `contract_type=index_link`, current `selected_spell_id`, `sources`.
- `_add_index` / `_remove_index` / `_check_index_exists` / `_get_index_detail_map(ward)`
  mirroring the spell `_add/_remove/_check_if_exists/_get_detail_map`.
- cleanup: clear both index-detail maps in `_clean_up`.

### ConduitWard (linking factors)
- `_add_index_to_contract(*, index, conduit/conduit_id, permissions, ...)` — mirror
  `_add_spell_to_contract`: eligibility/ownership, create IndexDetail, then
  `peer._spellbook._add_contracted_index(index)`.
- `_remove_index_from_contract(*, index_id, conduit/conduit_id)` — remove detail +
  `peer._spellbook._remove_contracted_index(index_id)`.
- `_get_index_links(index_id)` helper — contracts covering this index (for emission).

### Conduit (facade)
- `add_index_contract(*, index, target_conduit, permissions=...)` -> ward (dynamic-gated).
- `remove_index_contract(*, index, target_conduit)` -> ward (dynamic-gated).

### Emission (reuses existing borrower methods)
- notch / add_to_index / remove_from_index / cleanup: after the local op, if the index
  has index-link contracts, emit the spell_id delta to each receiver (generalize the
  `_deactivate_borrowed_spell` fan-out). Conduit-side; spellbook stays link-agnostic.

## Iteration order (build one at a time, verify each)
1. **Spellbook concrete target** — `_contracted_indexes` slot/init/cleanup +
   `_add_contracted_index`/`_remove_contracted_index`. [THIS ITERATION]
2. `IndexDetail` + Contract index-detail maps + Contract cleanup.
3. Ward `_add_index_to_contract` / `_remove_index_from_contract` / `_get_index_links`.
4. Conduit facades `add_index_contract` / `remove_index_contract` (dynamic-gated).
5. Emission wiring in notch/add/remove/cleanup (gated on index-link contracts present).
6. Eager-vs-lazy activate decision (default eager) + the activate branch.
7. Integration tests (follow-on-notch, add/remove propagation, multi-borrower, cleanup).

## Guardrails
- Additive: version-anchored spell contracts keep working untouched.
- Don't leak conduit/ward types into the spellbook (it only sees index_id / SpellIndex).
- Emission runs under the same mediator seal as the owner op (cross-conduit).
- Update cleanup everywhere a new container is added (spellbook + Contract).

## Tracking
- [x] 1 spellbook _contracted_indexes (+ methods, cleanup) — DONE 2026-06-30
- [x] 2 IndexDetail + Contract maps — DONE 2026-06-30 (details.py IndexDetail; Contract _index_details_a/b + _get_index_detail_map/_add_index/_remove_index/_check_index_exists + cleanup)
- [x] 3 ward add/remove/get index links — DONE 2026-06-30 (_add_index_to_contract / _remove_index_from_contract / _get_index_links; import IndexDetail)
- [x] 4 conduit facades — DONE 2026-06-30 (add_index_contract / remove_index_contract; reuse ADD_SPELL_OR_INDEX_TO_CONTRACT txn, _qualify_contracts gate, delegate to ward)
- [x] 5 emission wiring — DONE 2026-06-30. NOTCH: ward `_emit_index_notch` (walk index-link contracts, IndexDetail.update_selected, park-old/eager-activate-new on receivers; wired in Conduit.notch_spell). DESTROY: ward `_emit_index_destroy` (untrack index on receivers via `_remove_contracted_index` + drop/clean the IndexDetail; wired in Conduit.cleanup_spell, gated on `is_sole_member` -> index destroyed). add_to_index/remove_from_index need NO emission (they move INACTIVE members; borrowers follow the active member which is unchanged, and a later notch handles activation). Also removed two impossible `_conduit_ward is not None` / `_conduit is None` guards on the live-notch
## Note — 2026-06-30 — facade naming + dispose walk-back

Renamed conduit facades to the spell convention: `add_index_to_contract` /
`remove_index_from_contract` (were add_index_contract / remove_index_contract). Setup
chain confirmed end to end: facade -> `_conduit_ward._add_index_to_contract` ->
`peer._spellbook._add_contracted_index(index)` -> `_contracted_indexes[index.id]=index`
(the required dict is created in Spellbook.__init__, populated on add, popped on remove).

Dispose walk-back (all new objects properly disposed):
- Spellbook `_contracted_indexes`: cleared + del in `_cleanup_components`. Holds BORROWED
  SpellIndex objects (owner-owned) -> drop refs only, do NOT cleanup them. Correct.
- Contract `_index_details_a/_b`: each IndexDetail `.cleanup()`'d + cleared in `_clean_up`,
  del'd in `cleanup`.
- IndexDetail.cleanup: dels spell_index/selected_spell_id/permissions/contract_type/reason/
  sources(clear+del)/_id; `_lock` intentionally retained (it guards its own cleanup), same
  as Detail.
- IndexDetail disposed at every removal site: `_remove_index_from_contract` (FIXED this pass
  -- previously dropped the map entry without cleaning the object) and `_emit_index_destroy`.
- IndexDetail holds a BORROWED spell_index -> `del` drops the ref, no cleanup of the borrowed
  index. Correct.

## Note — 2026-06-30 — per-member spell contracts (user's model)

Reworked from "poke the borrower's maps" to "issue a real, correctly-typed spell
contract for EVERY member, kept in sync, driven by IndexDetail.permissions":
- Spellbook `_get_owned_spell(spell_id)`: resolve an owned member (active or inactive).
- Ward `_contract_member_spell(contract, owner_ward, member_spell, permission, reason)`:
  create a per-member spell Detail (ContractTypes.received) on the owner side +
  populate the borrower's copy (active head -> `_add_contracted_spell`, else
  `_add_inactive_contracted_spell`). `_uncontract_member_spell(...)`: remove+clean the
  Detail + untrack the borrower (`_remove_contracted_spell`). owner_ward passed
  explicitly (link path runs on borrower ward, emission on owner ward).
- `_add_index_to_contract`: after the IndexDetail, maps ALL members via
  `_contract_member_spell` with the index permission.
- `_emit_index_member_added(index, member_id)` -> wired in Conduit.add_to_spell_index.
- `_emit_index_member_removed(index_id, member_id)` -> wired in Conduit.remove_from_spell_index.
- notch unchanged: members are pre-mapped (Detail + parked copy), so `_emit_index_notch`
  just activates the parked new member + parks old + moves the IndexDetail head.
Result: each spell in the index is mapped exactly the same in the contract, with the
index-link's permission (read->read, create->create). Details disposed on uncontract +
on Contract cleanup. All changed methods ast-parse.

## Note — 2026-06-30 — cleanup walk-back (transfer / index / spellbook / per-member Details)

Final dispose pass over everything in the per-member rework. One real leak found + fixed:
the per-member spell Details minted by `_add_index_to_contract` were NOT torn down on
index unlink or index destroy (only the IndexDetail was), so they survived until full
Contract cleanup.

Fix — authoritative member tracking on IndexDetail:
- IndexDetail gains `_member_ids: Set[str]` (slot/init) + `add_member`/`remove_member`/
  `member_ids()` + clear+del in `cleanup`. This is authoritative for teardown because the
  live index is already cleaned by the time `_emit_index_destroy` runs (cleanup_spell
  destroys the index at conduit.py:3988 BEFORE emitting at :3992), so members cannot be
  re-read off `spell_index` at that point.
- `_contract_member_spell` now returns bool (True iff it newly minted the Detail; False if
  it merged into a pre-existing direct spell contract). Callers track only newly-minted ids
  on the IndexDetail, so we never clobber an independent version-anchored contract.
- `_add_index_to_contract`: tracks minted ids on the STORED IndexDetail (re-link merges).
- `_emit_index_member_added` / `_emit_index_member_removed`: keep the set in sync.
- `_remove_index_from_contract` + `_emit_index_destroy`: iterate `index_detail.member_ids()`
  and `_uncontract_member_spell` each (removes+cleans the owner Detail and the borrower copy)
  BEFORE `index_detail.cleanup()`. `_uncontract_member_spell` is id-based + idempotent, so it
  is safe even after the owner member spell is gone and even if spell-cleanup beat it to the
  Detail.

Verified-clean (no new leaks) for the rest:
- Spellbook `_cleanup_components`: `_inactive_contracted_spells` (clear+del) and
  `_contracted_indexes` (clear+del) — both hold BORROWED objects, so drop refs only. Correct.
- SpellIndex.cleanup: clears `_spells_in_index` + dels it and the selected pointer. The new
  `is_empty`/`is_sole_member` are pure accessors (no state to clean).
- Transfer: `_migrate_inactive_members` + `_move_creations` register rollbacks
  (`_rollback_inactive_members`, `_rollback_creations_move`@964 confirmed); transfer cleanup
  clears `_rollback_actions`/`_preflight_summary` and dels all borrowed refs (no cleanup of
  borrowed conduits/spellbooks/managers). Correct.
- Contract `_clean_up`: cleans every Detail AND every IndexDetail (both wards) then clears all
  four maps; `cleanup` dels the index maps. Full-teardown path disposes everything the
  targeted paths also dispose.

## Notes

- DATETIME: 2026-07-01T07:53:37Z
  TYPE: FACT
  CLAIM: Consumed 2 mailbox NOTICEs from mediator_builder_0 (recorded here as durable truth;
    both are transaction-lane facts I must build AROUND, not touch). (1) The 3 index
    transactions' ADMISSION moved spellbook -> conduit: Conduit.notch_spell /
    add_to_spell_index / remove_from_spell_index now OPEN the tx on the conduit identity;
    my spellbook _notch_spell / _add_to_spell_index / _remove_from_spell_index are pure
    _apply_* seams (envelope removed). Facade+seam docstrings saying "spellbook admits" are
    now stale (conduit admits). (2) A self-admitting add_spell_to_contract tx exists:
    Conduit.add_spell_to_contract REUSES an open link/cluster window or self-admits
    ADD_SPELL_TO_CONTRACT (seals both contract conduits+wards EXCLUSIVE, spellbooks INTENT).
    CRITICAL for my lane: only add_spell_to_contract is wired; add_spells_to_contract (bulk)
    and remove_spell_from_contract STILL require an active link tx as before.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4815-4872 (remove_spell_from_contract: _qualify + _require_link_transaction_for_contract)
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2773-2862 (_remove_spell_from_contract body)
  IMPACT: The removal-block the user wants lands in the manual removal path, which is already
    link-tx-gated. My guard is additive on top of that gate; I do NOT touch the tx envelope.
  NEXT: add the index-membership removal guard; revert the redundant _member_ids tracking.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-01T07:53:37Z
  TYPE: DECISION
  CLAIM: RECONCILE to the user's model (post-cert, user-directed): "track the index, not the
    spells; map every member as a contract; and BLOCK manual removal of an index-member spell
    unless it is its own spell-detail contract." Source-verified reconciliation: (a) SpellIndex
    is authoritative-multi-member (epic 2026-06-14 Notes 2026-06-29/30) -- _spells_in_index is a
    genuine set; the index tracks its own members. (b) IndexDetail.has_spell(spell_id) ALREADY
    tests membership via spell_index._spells_in_index (details.py:155-158). So the IndexDetail +
    the live index ARE the membership oracle -- the _member_ids Set I added last session is
    redundant and must be REVERTED (over-engineering the user explicitly rejected: "you don't
    need to track spells in an index contract you just track the index").
  PLAN (3 contained changes, verify each):
    1. REVERT _member_ids: strip the slot/init/add_member/remove_member/member_ids()/cleanup
       lines from IndexDetail (details.py) and the add_member/remove_member/member_ids() call
       sites + the _contract_member_spell bool-return tracking in conduit_ward.py. Un-map paths
       instead iterate the live index (index_detail.spell_index.spells_in_index()).
    2. BLOCK guard in _remove_spell_from_contract (conduit_ward.py:2773): before removing, if the
       spell_id is a member of ANY IndexDetail's index in this contract (walk _get_index_detail_map
       + IndexDetail.has_spell), RAISE an expressive error ("spell is part of index-link contract
       <index_id>; remove the index via remove_index_from_contract instead"). This is the whole
       ask: index-member spells are contract-locked; only remove_index unmaps them.
    3. DESTROY ordering: _emit_index_destroy runs AFTER cleanup_spell tears the index down
       (conduit.py:3988 before :3992), so members can't be read off the cleaned index there.
       Capture the member ids (or just spell.spell_id, the sole remaining member) in
       Conduit.cleanup_spell BEFORE spellbook teardown and pass them to _emit_index_destroy --
       reads the live index at the right moment, no persistent tracking set.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-06-14_spellindex_genuine_index_operations_epic.md:778-881 (multi-member authoritative)
  - src/melder/aether/conduit/conduit_ward/contract/details.py:155-158 (IndexDetail.has_spell membership oracle)
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2820-2835 (removal detail-exists branch = guard insertion point)
  - src/melder/aether/conduit/conduit.py:3985-3992 (cleanup_spell captures will_destroy BEFORE teardown; destroy emit AFTER)
  IMPACT: Simplifies the per-member rework to the user's model; removes redundant state; adds the
    contract-lock guard. Removal-guard changes a public-path gating behavior (previously-allowed
    manual removal now raises for index members) -> flag the patch-gate question to the user.
  NEXT: confirm scope + patch-gate posture with user, then execute steps 1-3 with per-step verify.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
  prompt_id: 9c41e0aa73b1

- DATETIME: 2026-07-01T08:13:47Z
  TYPE: FACT
  CLAIM: FULL SYSTEM MODEL re-read from source (user-directed "read conduit_ward, spellbook
    notch/add-to-index, and linking; understand before changing"). Verified mechanics:
    NOTCH (_apply_notch, spellbook.py:2987): swaps which member is ACTIVE. outgoing active ->
      _deactivate_owned_spell (off the 4 active maps into _inactive_spells; _spell_ids kept) +
      _cleanup_creation_context; incoming (MUST already be parked in _inactive_spells) ->
      _reactivate_owned_spell; spell_index.update(new_id) (pointer + .add to member set); frame
      update_lookup; register_index (gated+dirty). PRECONDITION: incoming is a pre-staged inactive
      member -- notch ACTIVATES an existing member, it never adds a new one.
    ADD_TO_INDEX (_apply_add_to_index, :3095): moves an owned INACTIVE spell source->target
      (both owned by this spellbook). Membership-only: source_index.remove_member,
      target_index.add_member, spell.spell_index=target. If source empties -> _destroy_spell_index.
    REMOVE_FROM_INDEX (_apply_remove_from_index, :3251): moves an owned INACTIVE spell out of
      source into a FRESH SpellIndex(initial_id=spell_id); raises if sole member (use cleanup_spell);
      no index destroyed.
    LINKING per-spell (_add_spell_to_contract, conduit_ward.py:1576): creates a Detail via
      contract._add(owner_ward), then peer._spellbook._add_contracted_spell(spell) if active else
      _add_inactive_contracted_spell. CRITICAL: _add_contracted_spell keys spell_map[SpellIndex]=spell
      (by INDEX, not id) AND spreads existence -- it iterates spell_index._spells_in_index and adds
      EVERY member id to _contracted_spell_ids[conduit] (spellbook.py:2613-2617; same in the inactive
      variant :2663-2669). So contracting the active member already makes the borrower existence-aware
      of the whole lineage; the index-link adds the per-member DETAIL bookkeeping + FOLLOW-ON-NOTCH.
    DIFFERENCE plain-spell vs index-link: a plain spell contract is version-anchored -- on notch the
      owner fan-out _deactivate_borrowed_spell only PARKS the old borrowed copy; it does NOT activate
      the new one. The index-link (_emit_index_notch) is what makes the borrower FOLLOW: park old +
      _ensure_contracted_active(new). That follow-on-notch is the whole point of the index-link.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2987-3060 (_apply_notch), 3095-3174 (_apply_add_to_index), 3251-3324 (_apply_remove_from_index)
  - src/melder/aether/spellbook/spellbook.py:1318-1426 (owned de/reactivate), 1558-1647 (contracted de/reactivate/ensure_active)
  - src/melder/aether/spellbook/spellbook.py:2567-2624 (_add_contracted_spell keys by index + spreads member existence), 2628-2670 (_add_inactive_contracted_spell)
  - src/melder/aether/conduit/conduit.py:3782-3963 (notch/add/remove facades + emission), 3965-3992 (cleanup_spell)
  IMPACT: My per-member model is right (Details = bookkeeping; borrower copies active-by-index +
    parked-by-id; follow-on-notch via _emit_index_notch). Reverting _member_ids was correct -- the
    index (_spells_in_index) is the member oracle; borrower existence is already lineage-wide.
  NEXT: fix the two gaps below, then the guards.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
  prompt_id: 9c41e0aa73b1

- DATETIME: 2026-07-01T08:13:47Z
  TYPE: FACT
  CLAIM: TWO GAPS found while re-reading (must fix before the guards). (1) I BROKE a call site:
    my revert changed _emit_index_destroy to require member_ids: Iterable[str], but Conduit.cleanup_spell
    (conduit.py:3992) still calls _emit_index_destroy(index_id) with ONE arg -> TypeError at runtime.
    Fix: capture index.spells_in_index() BEFORE self._spellbook.cleanup_spell(spell) tears the index
    down, pass it in. (2) add_to_spell_index emits ONLY member_added for the TARGET
    (conduit.py:3907); moving an inactive spell also REMOVES it from source_index -- if source is
    index-linked its per-member contract must drop, and if source empties+destroys its index-link must
    be destroyed. The facade captures no source (spell.spell_index == target after the move). Fix:
    capture source_index = spell.spell_index BEFORE _add_to_spell_index; after commit emit
    member_removed(source) [+ destroy(source) when it emptied]. remove_from_spell_index is already
    correct (emits member_removed(source); the spell's fresh index has no contract).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3985-3992 (cleanup_spell destroy emit -- now arity-broken)
  - src/melder/aether/conduit/conduit.py:3899-3908 (add_to_spell_index: target-only emit)
  - src/melder/aether/spellbook/spellbook.py:3163-3173 (add_to_index removes from source, destroys if emptied)
  IMPACT: destroy emit is currently broken (runtime); add-to-index leaves a stale source-side member
    contract. Both violate "maintain these contracts dynamically eagerly".
  NEXT: (a) fix cleanup_spell member capture + _emit_index_destroy call; (b) add source-side emit to
    add_to_spell_index; (c) then removal guard + add-defer/permission guard via _find_governing_index_link.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
  prompt_id: 9c41e0aa73b1

- DATETIME: 2026-07-01T08:25:41Z
  TYPE: FACT
  CLAIM: LANDED (user-approved "finish"). The user's index-link model is now implemented end to end,
    tracking the index only (no member set):
    REVERTS (IndexDetail._member_ids over-tracking removed): details.py IndexDetail back to
      __init__/index_id/update_selected/cleanup (no add_member/remove_member/member_ids); conduit_ward
      _contract_member_spell returns None again; _add_index_to_contract maps members by reading
      index.spells_in_index(); _emit_index_member_added/_removed no longer track; _remove_index_from_contract
      reads index_detail.spell_index.spells_in_index() for teardown.
    FIX (broken call I had introduced): _emit_index_destroy(index_id, member_ids: Iterable[str]); the
      members are captured in Conduit.cleanup_spell via index.spells_in_index() BEFORE spellbook teardown
      and passed in (conduit.py:4004,4009).
    GAP FIX (eager both-side maintenance on add_to_spell_index): Conduit.add_to_spell_index now captures
      source_index/source_will_empty/source_members BEFORE the move, then after commit emits
      member_added(target) AND (source != target) member_removed(source) or, if the source emptied and was
      destroyed, _emit_index_destroy(source). remove_from_spell_index was already correct.
    GUARDS (index is the oracle via new ward helper _find_governing_index_link(contract, spell_id) ->
      checks IndexDetail.has_spell on both ward sides): (1) _remove_spell_from_contract RAISES if the spell
      is an index-link member ("remove the index instead"); (2) _add_spell_to_contract DEFERS (returns True,
      no-op) when the spell is index-governed at the SAME permission, and RAISES on a DIFFERENT permission
      ("permission governed by the index"). The index-link machinery uses contract._add/_remove directly, so
      it bypasses both public-path guards.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/contract/details.py (IndexDetail: _member_ids removed)
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2224 (_find_governing_index_link), 1648 (add guard), 2849 (remove guard), 2073 (_emit_index_destroy sig)
  - src/melder/aether/conduit/conduit.py:3894-3922 (add_to_spell_index both-side emit), 4004-4009 (cleanup_spell capture+destroy)
  VALIDATION: conduit_ward.py whole-file ast-parse OK; conduit.py facade slice + details.py IndexDetail
    slice ast-parse OK (whole-file bash parse of those two hit stale-mount TAIL truncation far past the
    edits -- verified real content via targeted range parse). Consistency sweep: both _emit_index_destroy
    calls pass member_ids; ZERO dangling _member_ids/add_member/member_ids() refs. Full 3.14t unit tree
    NOT RUN here (sandbox is 3.10) -- user runs to confirm green.
  IMPACT: closes the per-member-contract rework on the user's simplified model; the index (_spells_in_index)
    is the sole membership oracle; members are contract-locked while the index is linked.
  NEXT: user runs the 3.14t unit tree; then the held integration-test phase (epic item 7).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
  prompt_id: 5e2a9c0f71d8

- DATETIME: 2026-07-01T08:48:41Z
  TYPE: FACT
  CLAIM: Consumed mediator_builder_0 NOTICE (2026-07-01T08:47:27Z): they completed the REMOVE-side
    transaction envelope -- Conduit.remove_index_from_contract now reuses-or-self-admits a new
    REMOVE_SPELL_OR_INDEX_FROM_CONTRACT tx (seals both conduits+wards EXCLUSIVE, spellbooks INTENT);
    RemoveSpellOrIndexFromContractTransactionStrategy built + declared on the conduit identity (~L1081);
    add_index_to_contract docstring enriched. This is their transaction lane and does NOT touch my ward
    guards. ORTHOGONALITY CONFIRMED: my index-member removal guard lives INSIDE
    ConduitWard._remove_spell_from_contract and fires regardless of how the Conduit facade admits the tx,
    so their envelope change and my guard do not interact. LOOSE END they flagged: the Conduit
    remove_spell_from_contract facade still hard-requires a link tx (no self-admit) -- that is transaction-
    migration work in mediator_builder_0's lane (NOT mine per standing constraint); they offered to do it.
  EVIDENCE:
  - codex/context_compass/mailbox_board.md (message consumed/deleted this pass)
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py (_remove_spell_from_contract guard -- ward-side, tx-agnostic)
  NEXT: no action for me on the tx loose end; continue the integration-testing epic tranches.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
  prompt_id: 3d9a71c4e5b2
