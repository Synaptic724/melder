# Component Patch: SpellIndex active/inactive + frame-signature foundation — per-seam choreography

## Metadata
- Patch ID: COMPPATCH-2026-06-21-spellindex-active-inactive-frame-signature
- Status: draft (companion to the architecture_patch; build gate)
- Owner: cowork
- Agent: general_0 (author/design)
- Parent: system_docs/patches/active/2026-06-21_spellindex_active_inactive_frame_signature_foundation_architecture_patch.md
- Epic: tickets/epics/2026-06-14_spellindex_genuine_index_operations_epic.md
- Coordinates with: mediator_builder_0 (NOTCH/ADD/REMOVE strategies + seal), optimizer_0 (refcount perf)

## Purpose
The architecture_patch fixed the shape. This patch fixes the MECHANICS: exact fields, method
signatures, the deactivation cache-kill surface, and a per-slice test plan — so each slice is
buildable and independently verifiable without re-deriving the design. Still no code lands here.
"(verify at build)" marks a name/signature to confirm against source in the building slice.

## Grounded cache model (the surface every op must drive)
Three caches key off the ACTIVE spell_id; deactivation must invalidate all three coherently:
1. ID-POOLS — `_spells_by_id` + `_spell_id_pool` (spellbook.py:957-975 register; 1029-1040 update;
   1045+ unregister). meld-by-id reads these ONLY (meld.py:1253-1288). Evicting the id here makes
   `meld(old_id)` miss.
2. WARM input_resolution_cache (conduit_meld.py:284-315) — `{input -> spell_id}`, self-heals: on a
   pool miss it re-resolves through the index (297-303) and re-caches the new id. So an id-pool evict
   AUTO-invalidates the warm cache; no explicit clear needed.
3. FAST-DOOR (conduit_meld.py:251-256) — guarded by `door_spell._door_epoch == captured_epoch` AND
   `door_spell._creation_context is captured_context`. Per the inline contract (conduit_meld.py:246-248)
   context replacement funnels through `Spell._cleanup_creation_context`, which BUMPS `_door_epoch`.
   So turning the outgoing spell's creation_context OFF bumps the epoch → the fast-door guard misses →
   the cold lane rebuilds or errors. That is the door-kill.

DEACTIVATION CACHE-KILL (canonical, used by notch outgoing + disable):
  a. `_unregister_owned_spell_id(old_id, spell)` — drop `_spells_by_id[old_id]` + `_spell_id_pool[old_id]`
     (verify it also discards from `_spell_ids`; spellbook.py:1041 shows update() adds to `_spell_ids`,
     unregister must mirror — verify at build).
  b. `spell._cleanup_creation_context()` (or the disable-equivalent) — bumps `_door_epoch`, kills the
     fast-door; subsequent fast-door access throws AttributeError → treated as guard miss (266-271).
  c. warm cache self-heals via (a); no direct touch.
  RESULT: old_id is fully off the resolution surface; nothing double-frees (creation_context teardown is
  the single owner of door/lane teardown).

## Data structures (slice 1 + 2)
Spellbook.__init__ (additive; lock = existing `self._lock`):
- `self._inactive_spells: dict[str, Spell] = {}`                      # owned, key=spell_id
- `self._inactive_contracted_spells: dict[str, dict[str, Spell]] = {}` # conduit_id -> {spell_id -> Spell}
AethericFrame (frame RLock-guarded, beside `_selected_spell_registry`):
- `self._active_binding_signatures: dict[tuple[str,str], SpellIndex] = {}`  # (frame_key,binding)->index
- `self._spell_id_refcounts: dict[str, int] = {}`                           # union(active,inactive) existence
- optional `self._spell_id_to_index: dict[str, SpellIndex] = {}`            # find_index O(1) (slice 3)

## Method specs
### Frame signature authority (slice 2 — inert until bind claims)
- `claim_binding_signature(frame_key, binding_name, index) -> None`: under frame lock; if key present
  and maps to a DIFFERENT index → raise "binding signature already active in this frame"; else set.
- `release_binding_signature(frame_key, binding_name, index) -> None`: under lock; pop only if it maps
  to `index` (idempotent, no raise on absent).
- `is_binding_signature_available(frame_key, binding_name) -> bool`; `get_active_index(...) -> SpellIndex|None`.

### Frame refcount aggregate (slice 3 — replaces `_reindex_conduit_versions` re-derivation)
- `incr_spell_id(spell_id, index=None)` / `decr_spell_id(spell_id)`: under lock; dict get/+1//-1; on 0 pop
  (+ pop `_spell_id_to_index`). `has_spell(spell_id) -> _spell_id_refcounts.get(id,0) > 0`.
- `bulk_incr(spell_ids, ...)`: one lock acquire for conjure's whole set (replaces the bulk reindex,
  conduit.py:2025 path).
- DELETE `_reindex_conduit_versions` + the `spells_in_index()`-copy rebuild (aetheric_frame.py:604-633).
  Rewire register/unregister_spell_index + conjure bulk + transfer to push deltas. has_spell/find_index
  read the maps directly. EXISTENCE SPANS UNION: increments fire for BOTH active register AND
  bind_inactive staging, decrements on disable-to-gone / cleanup — so a sleeping candidate still counts.

### bind (slice 4 — the one hot-path change)
- After the existing local lookup-key assert + Aether fingerprint gate (spellbook.py:3138,3157), add:
  `frame.claim_binding_signature(spell._key.frame_key, spell._key.binding_name, index)` BEFORE the
  `_lookup_spells` write (3164). On raise, the bind fails early/deterministically (no partial registration).

### bind_inactive (slice 5)
- Signature (per architecture Q2): `bind_inactive(spell, index)` — stage onto an EXISTING index.
  Body: assert ownership; `_inactive_spells[spell.spell_id] = spell`; `index._spells_in_index.add(spell.spell_id)`
  (verify method name on SpellIndex); `frame.incr_spell_id(spell.spell_id, index)`. Claims NO signature,
  touches NO id-pools, NO `_spells[index]`. Spell is inert/unmeldable until notch promotes it.

### _apply_notch (slice 6 — under the mediator notch seal)
Precondition: `new_id in _inactive_spells` (notch PROMOTES, never mints). Steps, in the held window:
  1. outgoing = `_spells[index]`; run DEACTIVATION CACHE-KILL (a,b above) on outgoing; move it
     `_inactive_spells[outgoing.spell_id] = outgoing`.
  2. incoming = `_inactive_spells.pop(new_id)`; `_register_owned_spell_id(new_id, incoming)`;
     `_spells[index] = incoming`; set `index._selected_spell`/`_selected_spell_id = new_id` (compiler/
     validation read path stays in sync — architecture invariant #1).
  3. Frame: signature UNCHANGED (clean-notch / Q1 — same index keeps its one signature); refcount net-zero
     (both ids already counted in the union).
  4. Validity: set incoming GATED; cheap-notch fast-path — if `compute_impact_closure([index])`
     (spell_system_states.py:535) is empty → SKIP fan-out; else mark the dependent-root closure dirty.
  5. Contracted fan-out (owner-driven): for each borrower that held outgoing's id, move its borrowed copy
     old->`_inactive_contracted_spells[cid]`, bring incoming into `_contracted_spells[cid]`, rekey via
     `_update_contracted_spell_id` (verify), and mark THAT conduit's dependent-root closure dirty. The
     notch seal scope-claims owner + all affected borrower conduits (cross-conduit, per epic 6b).
  6. Revalidation timing: LAZY (next-resolve, the transfer/link pattern) unless user wants eager.

### disable (slice 6) = notch-to-nothing
  outgoing -> DEACTIVATION CACHE-KILL + `_inactive_spells`; `_spells.pop(index)` (verify) ; index pointer
  cleared; `frame.release_binding_signature(...)`; drop `_lookup_spells[key]`; refcount stays (still
  inactive-present) until cleanup actually removes it.

### transfer / add_to_index / remove_from_index (slice 7)
- `_flip_registry_and_spellbooks` (transfer_of_ownership.py:1272-1408) MUST also move the index's
  `_inactive_spells` entries (currently moves only active) — else candidates orphan on transfer.
- Before repointing the destination binding, assert `is_binding_signature_available` on the dest
  (closes the silent-clobber the epic 16:15 note found). add/remove build on this flip, never mint.

## Build slices (each: implement -> full 3.14t tree green -> commit)
1. inactive maps + cleanup walk (active+inactive) — inert.
2. frame signature registry + methods — inert.
3. frame refcount aggregate + delta push; delete `_reindex` re-derivation — perf, behavior-preserving.
4. bind claims the frame signature — one hot-path change.
5. bind_inactive.
6. _apply_notch swap + cheap-notch + cross-conduit dirtying; disable.
7. transfer/add/remove carry inactive + dest signature guard.

## Test plan (per slice, additive)
1. construct Spellbook → maps exist empty; cleanup walks both without error.
2. claim/release/is_available/get_active: claim twice same index = ok; different index = raise; release
   idempotent.
3. refcount: register/unregister/bulk parity vs old has_spell on a fixture frame; find_index O(1) correct;
   no `spells_in_index()` copies on the hot path (assert call removed).
4. bind a colliding signature in one frame → raises "already active"; distinct binding_name → ok.
5. bind_inactive → spell in `_inactive_spells`, in `_spells_in_index`, NOT meldable by id, NOT in `_spells`,
   refcount incremented.
6. notch promote: meld (cold+warm) sees new spell; `meld(old_id)` misses; fast-door rebuilds; impact-empty
   index skips fan-out; borrower conduits see the swap + revalidate; can notch back. disable → unmeldable +
   signature freed + binding key dropped.
7. transfer carrying an index with inactive candidates preserves them; dest-signature collision raises
   instead of clobbering; add/remove move an owned spell with no re-mint (spell+creations identity preserved).

## Notes
- DATETIME: 2026-06-21
  TYPE: PLAN
  CLAIM: Component patch — per-seam choreography + the canonical deactivation cache-kill surface
    (id-pool evict + creation_context-off bumps door_epoch + warm-cache self-heal), grounded in the
    id-pool/meld-door source. Specifies fields, frame signature + refcount methods, bind claim,
    bind_inactive, _apply_notch swap (with cheap-notch + cross-conduit fan-out), disable, transfer carry,
    and a per-slice test plan. "(verify at build)" flags the ~4 method names to confirm in-slice
    (`_unregister_owned_spell_id` `_spell_ids` discard, SpellIndex `_spells_in_index` add, `_spells.pop`,
    `_update_contracted_spell_id`).
  EVIDENCE:
  - spellbook.py:957-1043 (id-pool register/update; unregister at 1045+) ; meld.py:1253-1288
  - conduit_meld.py:246-271 (fast-door guard + creation_context bump) ; 284-315 (warm self-heal)
  - aetheric_frame.py:604-633 (the reindex re-derivation to delete) ; spell_system_states.py:535 (impact closure)
  - transfer_of_ownership.py:1272-1408 (flip — must carry inactive + dest signature guard)
  NEXT: user confirms knobs Q1/Q2 (non-blocking for slices 1-3) -> build slice 1 (inert inactive maps).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
