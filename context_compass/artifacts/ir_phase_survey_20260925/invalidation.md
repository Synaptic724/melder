# Survey record: the invalidation surface (D5)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 3, step S10).
Status: COMPLETE. Read by method (whole bodies): `spell_system_state.py:349-667` (`set_validity`,
`mark_structural_change`, `mark_dependency_change`, `mark_transitively_dirty`, `clear_dirty`),
`spell_system_states.py:299-352` (`register_index`), `:532-651` (`mark_structural_change`,
`compute_impact_closure`, `consume_dirty_indexes`), `:743-800` (`unregister_index`),
`:1108-1260` (`mark_collection_dependents_dirty`, `mark_contract_dependents_dirty`);
`change_control_manager.py:595-612`, `:837-873` (`_default_dirty_marker`); `spell.py:1324-1390`
(`Spell.invalidate_spell`); `spellbook.py:3060-3080`, `:3785-3810`, `:4732-4760`;
`conduit_ward.py:2531-2585` (`_invalidate_contract_consumers`); `transfer_of_ownership.py:687-750`,
`:846-882`; `transaction_request.py:62-77` (`ChangeTransactionType`); `aetheric_mediator/
transaction_type.py:1-80`. Call sites were located by grep and their enclosing functions named by
line; the meld door (`meld.py:786`) is cited from grep only and was not read.

## The two validity tiers and their transitions
- Structural tier: one `SpellSystemState` per spell INDEX (lineage), holding `validity`
  (`unknown|gated|valid|invalid|disabled`), a flag set (`new_index`, `structure_changed`,
  `dependencies_changed`, `impacted_by_dependency`, `contract_unvalidated`, `transfer_in_progress`,
  ...), `change_reason`, `transitively_dirty`, `last_validated_at`; every write goes through
  `set_validity` (spell_system_state.py:349-417), which publishes a changed validity to
  `RiskManager.on_structural_validity_change(index_id, validity)`. Helpers: `mark_structural_change`
  -> gated + `structure_changed` (:517-549); `mark_dependency_change` -> gated +
  `dependencies_changed` (:551-580); `mark_transitively_dirty` -> gated + `impacted_by_dependency`
  (:582-611); `clear_dirty(ts)` -> valid, clears the four topology flags only (contract, mutation
  and ops flags stay) (:613-666). The registry adds the index id to `_dirty_indexes` on every
  gating write; `consume_dirty_indexes` pops that set (spell_system_states.py:634-651).
- Per-conduit tier: `ConduitResolutionState` per conduit id (phase_06.md): spell/root validity
  maps, diagnostics, dirty flag, `last_validated_at`; `mark_conduit_dirty` (spell_system_states.py:
  1064-1086) is the coarse "this conduit view is stale" signal.

## Event -> writer -> state written (D5 table)
| event (family) | code that marks | state written | snapshot consequence |
| --- | --- | --- | --- |
| bind / bind_inactive (BIND) | `Spellbook.bind` -> `register_index(index, owner)` (spellbook.py:5397; spell_system_states.py:299-352) | new or re-bound lineage: gated, `structure_changed`, reason `register_or_rebind`, dirty | new spell id enters the live set: per-spell rows miss for it; per-conduit key changes |
| bind after conjure (BIND) | `Spellbook._mark_collection_dependents_dirty({frame_key})` (spellbook.py:3073-3077, :4732-4760) -> `mark_collection_dependents_dirty` (:1108-1178) | every `list[Frame]` / OVERRIDE_REQUIRED consumer of that frame key in the book: gated, `dependencies_changed` | consumers' phase-3 rows change (collection DI scans the pool); covered by keying on the visible id set |
| any committed structural transaction | CCM commit dispatch (:604-612) -> `_default_dirty_marker(staged)` (:837-873) | collection dependents of staged binding frame keys (as above); contract dependents of staged contract keys: gated, `contract_unvalidated` | the generic commit-side fan-out; same key coverage as the two rows above plus the contracted set |
| notch (NOTCH) | `_apply_notch`: `register_index` for the incoming member (:3772); `spell.invalidate_spell` (:3803; spell.py:1324-1390) | lineage gated `structure_changed`; creation context cleared; `resolution_required` flipped back False so meld's validation lane recompiles (:3795-3810); phases 1-4 for the member run at the notch commit | selected spell id changes under the same index id: live id set changes (key), per-spell rows for the incoming member miss or hit on its own id |
| add_to_index / remove_from_index | membership-only seams (architecture :738-767); `_destroy_spell_index` -> `unregister_index` (spellbook.py:4001; spell_system_states.py:743-800) | dependents of the destroyed index: transitively gated via `compute_impact_closure` (:573-632); topology, collection and contract indexes dropped | a minted or destroyed index changes LINEAGE ids; rows carrying index ids (phase-5 `lineage_id`) go stale even when spell ids do not (see below) |
| link / unlink; contract add/remove (LINK, UNLINK, ADD/REMOVE_SPELL_OR_INDEX_TO/FROM_CONTRACT; dynamic only) | `ConduitWard._add_spell_to_contract` (:1953), `_remove_spell_from_contract` (:3142), `_remove_all_spells_from_contract` (:3286), `_remove_contract` on both wards (:1153, :1158) -> `_invalidate_contract_consumers` (:2531-2585) -> `mark_contract_dependents_dirty` (:1180-1260) | contract consumers in the book: gated, `contract_unvalidated`, NOT transitively dirty; their creations extracted (:2579-2585) | `spellbook._contracted_spells` and the visible (borrowed) set change: per-conduit rows for 4-7 must key on the contracted set and the visible set; per-spell 1-3 rows survive |
| transfer_ownership (TRANSFER_OWNERSHIP; dynamic) | `_mark_lineage_disabled` (:846-882): `disabled` + `transfer_in_progress` with rollback; `_mark_lineage_dirty` / `_gate_transfer_impacts` (:687-750): `mark_structural_change`, `compute_impact_closure`, `mark_conduit_dirty` per impacted conduit; registry flips `unregister_index`/`register_index` across books (:992-993, :1449, :1477) | the ONLY production writer of the per-conduit dirty flag; lineage and its closure gated | owned sets of both books change; every impacted conduit's tier-2 rows are void; per-spell rows keep their ids |
| spell cleanup / remove (`cleanup_and_remove_spell`, `_cleanup_spells`, `cleanup_spell`) | `unregister_index` (spellbook.py:566, :649) ; `invalidate_spell(cleaned_up_spell)` (:4204) | dependents transitively gated; index removed | id leaves the live set: key change |
| conjure (CONJURE) | phase 3 `update_dependencies` gates + dirties every index each pass; phase 4 `clear_dirty` or gated `contract_unvalidated` (phase_03.md, phase_04.md); phase 6 per-conduit verdicts (phase_06.md) | internal to the pass | a hydrate replays these writes instead of the phases |
| meld-time gate | `Meld._ensure_lineage_resolvable`: UNKNOWN/GATED -> local structural rerun; broken -> `set_validity(invalid)` (meld.py:786, grep only) | invalid on a broken spell | rows hydrated as `valid` are trusted by meld; rows hydrated as gated trigger the rerun |
| cluster join/leave/link, leader election (CLUSTER_*, ELECT/UNELECT) | no caller of any `mark_*`/`set_validity` found under `conduit/conduit_cluster.py` (grep) | none in the registry | UNKNOWN effect on rows (runtime-lane existence resolution); not a key input on today's evidence |
| mutation promotion (MUTATION) | producers absent (architecture Unknowns :178-202) | none today | UNKNOWN |
| frame posture settle / freeze | `with_system_state` before freeze; frozen after (architecture :1033-1073) | not a registry write | posture is a KEY input (phase 4, phase 6), not an invalidation event: it cannot change after freeze |
| release, Python tag, format generation | `.melc` admission (cache_seam.md) | wholesale cold cache | envelope-level; the snapshot inherits the same four stamps |
| crystallizer restore | replays binds through public verbs with FRESH index ULIDs (architecture "never-rehydrate-ULIDs", :1210-1212) | as bind | spell ids survive; index ids do not: rows must not carry raw index ULIDs |

## What the snapshot must do
1. Capture rows only at the end of a pass that left the lineage `valid` (phase 4 `clear_dirty`) and
   the conduit bucket clean (phase 6 `clear_conduit_dirty`); rows captured from a gated pass would
   hydrate a verdict the runtime never reached.
2. Hydrate by replaying the SAME registry writes the phases perform (register/update dependencies,
   topology, `clear_dirty(ts)`, bulk validity, diagnostics, component-of, revalidator) into a fresh
   registry, then the flags on Spell (`resolution_complete`, `resolution_required`). Every event in
   the table above then keeps working unchanged, because it writes through the registry, not through
   the phases: no new invalidation hook is needed for structural events.
3. Key the tiers so that membership events are caught before hydration: per-spell rows on the spell
   id; per-conduit rows on (sorted visible ids, sorted owned ids, frame posture, sorted contracted
   keys). Link/sever, transfer, notch and index moves all change one of those inputs.
4. Store lineage references by binding key or by a hydration-time translation map, never raw index
   ULIDs: `SpellSystemNode.lineage_id`, `phase5_root_lineage_id` and the `ConduitResolutionState`
   root/spell maps are keyed by VERSION id (fine) but the phase-5 nodes carry the index id
   (phase_05.md; spell_system_states.py:299-352 mints states per index id).
5. `RiskManager` fan-out: hydrated validity writes publish through `set_validity` and the conduit
   bucket exactly as live writes do (spell_system_state.py:409-417; conduit_resolution_state.py:
   375-385), so replaying the writes keeps DevOps risk gating consistent. UNKNOWN: whether the risk
   manager treats a burst of hydrated `valid` publications as events worth logging.

## Contradictions
- `src_architecture.md:768-773` ("Sequence: Change-Control Revalidation") and `:485-486` describe
  the dirty-root loop as live; phase_07.md records that `notify_spell_changed` has no shipped
  caller. The registry-side gating in this table IS live; only the CCM dirty-root loop is not.
- `src_architecture.md:1132` "ChangeControl blocks roots marked dirty for the active conduit" is
  mechanically true and unreachable from shipped paths (same finding).

## UNKNOWN (with where to look)
- Cluster and leader-election effects on resolution rows: `conduit/conduit_cluster.py` and the
  cluster transaction strategies (no registry writes found by grep).
- Whether `bind_inactive` runs phases 1-4 for parked members (rows may or may not exist before a
  notch): `spellbook.py` bind_inactive path.
- `RiskManager.on_structural_validity_change` / `on_resolution_validity_change` bodies:
  `dev_ops/risk_manager/risk_manager.py`.
- The meld-time gate body (`meld.py:930-1040`): another agent's lane; cited from grep and the
  architecture sequence only.
