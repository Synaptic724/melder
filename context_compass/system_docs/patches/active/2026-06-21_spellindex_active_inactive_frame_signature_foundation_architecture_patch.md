# Architecture Patch: SpellIndex active/inactive + frame-owned binding-signature foundation

## Metadata
- Patch ID: ARCHPATCH-2026-06-21-spellindex-active-inactive-frame-signature
- Status: draft (awaiting user accept of the resolved knobs, then component_patch)
- Owner: cowork
- Agent: general_0 (author/design)
- Priority: p1
- Created: 2026-06-21
- Parent Epic: tickets/epics/2026-06-14_spellindex_genuine_index_operations_epic.md
- Feeds: notch / add_to_index / remove_from_index seams (epic Stories)
- Coordinates with: mediator_builder_0 (ADD/REMOVE/NOTCH strategies intact), mutres_0
  (version-derivation epic), optimizer_0 (the ~15% frame-registry perf lane)

## Purpose
Specify the system-impacting data-model + invariant changes that must land BEFORE any
notch/add/remove code, so the build is correct the first time and thread-safe under
3.14t no-GIL. This patch is design only: no code lands on this artifact. The
component_patch (next) carries the per-method choreography; this one fixes the shape,
ownership, locking, and invariants.

## Scope
IN: (A) Spellbook active/inactive spell maps; (B) AethericFrame binding-signature
authority; (C) consolidation of the two redundant "version" caches into one
incrementally-pushed frame aggregate (removes the re-derivation tax). The resolution
contract (index organizes, spell_id resolves) and the seam-vs-strategy split are
inputs, not changes.

OUT: MutationResearch version-derivation (mutres_0); Creations lifecycle; cluster
surface (compiler_strategy_0's `_root_creations`); the notch/add/remove method bodies
(component_patch); nexus/acl ACL revision versioning (legit separate concept — leave).

## Current State (today's wiring — grounded)
- `_lookup_spells {(frame_key, binding_name) -> SpellIndex}` and
  `_spells {SpellIndex -> active Spell}` are the resolution maps; meld holds both by
  reference (meld.py:178,186) and cold-resolves binding -> index -> active spell
  (meld.py:1363-1367), then runs off `spell_id`.
- meld-by-id reads ONLY the id-pools: `_spell_id_pool` -> `_spells_by_id` ->
  `_contracted_spells_by_id` (meld.py:1253-1288); pools are written ONLY by
  `_register/_update_owned_spell_id` for the ACTIVE spell (spellbook.py:933-1040).
- Warm bindings cache `_input_resolution_cache {input -> spell_id}` and self-heal on a
  pool miss (conduit_meld.py:284-315).
- `SpellIndex._spells_in_index` is a SET OF SPELL-ID STRINGS — pure tracking, NOT a
  resolution store (spell_index.py:37,73,329; returns a COPY at :311).
- TWO redundant owned-id caches: `Spellbook._spell_versions` (Set[str], incremental at
  bind 3169-3175 + a rebuild `_refresh_local_spell_versions`:633) and
  `AethericFrame._selected_spell_registry {conduit_id -> Set[str]}` RE-DERIVED from index
  objects via `_reindex_conduit_versions` (aetheric_frame.py:604-633) — the lagging
  refresh + set-copies that optimizer_0's profile fingers for the ~15%.
- CONSEQUENCE (verified): a dormant candidate OBJECT has NO home today — the index
  holds only the one active, the pools hold only registered actives, `_spells_in_index`
  holds only id strings. Inactive/version candidates need an explicit home.

## Target Architecture
### A. Active/inactive spell maps (Spellbook) — additive, greenfield
- NEW `_inactive_spells {spell_id -> Spell}` (owned) and
  `_inactive_contracted_spells {conduit_id -> {spell_id -> Spell}}` (borrowed),
  mirroring the existing `_spells` / `_contracted_spells`.
- meld reads ONLY the active maps + id-pools, so **inactive = OFF the resolution
  surface, not meldable until promoted**. This is the homeless-candidate fix without
  re-introducing multi-member resolution: `_spells[index]` is still EXACTLY one active;
  inactive spells live in a SEPARATE map, never as members on the index.
- An index thus has ONE active spell + N inactive candidates. The "versions" concept is
  DELETED, not renamed: `Spellbook._spell_versions` / `_contracted_versions` become a
  DERIVED union (active ids ∪ inactive ids), not a third stored set.

### B. Frame-owned binding-signature authority (AethericFrame) — option B (user-locked)
- NEW `AethericFrame._active_binding_signatures {(frame_key, binding_name) -> SpellIndex}`
  with `claim / release / is_available / get_active`, frame-lock-guarded — symmetric with
  the spell_id existence registry the frame already owns.
- At most ONE spell is ACTIVE on a `(frame_key, binding_name)` per frame. Multiple
  candidates may be BOUND on the holding index; only one is active. `bind` CLAIMS the
  frame signature (raises "binding signature already active in this frame" if taken);
  `disable` RELEASES it. Because cross-frame linking does not exist (user-confirmed x2),
  a frame-unique signature makes within-frame links collision-free by construction, and
  transfer's missing target-side signature guard dissolves.

### C. Version-registry consolidation — push, don't re-derive
- DELETE the frame's re-derivation (`_reindex_conduit_versions` + `spells_in_index()`
  copies). Replace with a thin frame-wide **refcount id-index**
  `Dict[spell_id -> int]` (add=increment, remove=decrement, has_spell=count>0,
  find_index optional `Dict[spell_id -> SpellIndex]`), maintained by DELTAS pushed from
  the mutation seams that already hold the lock and know the change.
- conjure = one bulk increment pass (1 lock acquire), incremental ops = single id-delta;
  both feed the same map. O(1) either direction, no rebuilds, no set copies, no
  add/remove asymmetry. Same construct as (B) — build both under one frame-authority
  refactor.

## CRITICAL invariant — existence spans active ∪ inactive
The frame existence check (`_check_for_spell` / `has_spell` at bind, aether.py:1252) and
the refcount aggregate MUST count active UNION inactive. A dormant candidate's spell_id is
still allocated/taken; if the aggregate counted only active, bind could re-mint a
duplicate of a sleeping spell. `find_index_for_spell` must resolve both. (This is the
whole reason "all ids seen" was ever tracked.)

## Resolution invariants (unchanged, restated as guardrails)
1. The index ORGANIZES; the spell_id RESOLVES. No consumer may treat
   `spell_index.selected_spell_id` as the resolved spell — cold meld uses `_spells[index]`.
2. `_spells[index]` is exactly one active Spell. Inactive candidates are never on the
   resolution surface until promoted via `_register/_update_owned_spell_id`.
3. Existence/uniqueness spans active ∪ inactive (above).
4. 3.14t: `selected_spell_id` stays a lock-free read; all writers serialize via the
   mediator seal; frame registries are frame-lock-guarded; no whole-dict iteration on
   hot paths.

## Resolved knobs (my recommendations — user can override any in one word)
- Q1 (notch signature): **CLEAN** — candidates share the index's ONE signature; notch
  PROMOTES within the same index and NEVER touches the frame signature registry. (Locked
  by option B + the active/inactive model; the "general/re-key" variant is rejected.)
- Q2 (bind_inactive API): **attach to an EXISTING index** as the primary form (stage a
  candidate into that index's `_inactive_spells` + `_spells_in_index`, claim nothing); a
  fresh-index bind_inactive is the degenerate case of normal bind + immediate deactivate,
  not a separate API.
- Keying: `_inactive_spells` keyed by **spell_id** (active is one-per-index via
  `_spells`; inactive is many-per-index via the id set in `_spells_in_index`).
- Notch fast-path: when `compute_impact_closure([index])` is empty (no dependents), skip
  the 6b cross-conduit revalidation fan-out (cheap-notch). Contract-identical fast-path is
  FUTURE, not foundation.

## Operations mapped onto the foundation (bodies => component_patch)
- notch = SWAP: outgoing active -> `_inactive_spells` (evict id-pools, creation_context
  off); incoming inactive -> `_spells[index]` (register id-pools, GATED). Owner-driven
  contracted fan-out moves each borrower's old active -> `_inactive_contracted_spells`.
  Revalidate the COMPLETE consumer closure (owner + every borrower conduit that had the
  id) via dependent-root dirtying; LAZY (next-resolve) unless user wants eager.
- disable = notch-to-nothing (active -> inactive, release frame signature, drop
  `_lookup_spells`).
- bind = additionally CLAIM the frame signature (the one hot-path change, isolated).
- transfer/add/remove = `_flip_registry_and_spellbooks` must carry `_inactive_spells`
  too, + assert frame-signature availability on the destination before repointing.

## Build slices (safest-first; each independently testable; gate before each: green)
1. Add inactive maps + cleanup walk (active+inactive) — INERT, zero behavior change.
2. Add frame signature registry + methods — INERT until claimed.
3. Add frame refcount id-index + delta-push; delete `_reindex`/`_refresh` re-derivation;
   wire conjure bulk + incremental seams — behavior-preserving perf consolidation.
4. Wire bind to CLAIM the frame signature (the one hot-path change).
5. bind_inactive (stage into `_inactive_spells` + `_spells_in_index`).
6. `_apply_notch` swap under the notch transaction (+ cheap-notch fast-path + cross-conduit
   closure dirtying).
7. disable; then transfer/add/remove carry inactive + frame-claim guard.

## Blast radius / safety map
- Files: spellbook.py (new maps, derived versions, bind claim, id-pool seams),
  aetheric_frame.py (signature registry + refcount aggregate, delete re-derivation),
  aether.py (existence check spans union; bulk push), conduit_meld.py (no change —
  reads pools), transfer_of_ownership.py (carry inactive + dest guard), spell_index.py
  (`_spells_in_index` stays the id tracker).
- Hot paths touched: bind (frame claim), conjure registration (bulk push), every
  register/unregister (delta vs rebuild — net FASTER). meld cold/warm UNCHANGED.
- no-GIL: frame registries under the frame RLock; profile the RLock itself under parallel
  binds (optimizer_0) — if contended, that's a second, separately-measured axis.

## Invariants / risks / rollback
- RISK: a consumer reads `selected_spell_id` as resolved — keep it in sync with
  `_spells[index]` on every notch. RISK: warm binding misses notch — id-vacate drives the
  self-heal. RISK: add/remove re-mint (the original bug) — build on the flip + ownership
  assertion + rollback, never hand-register. RISK: existence aggregate counts active-only
  — bind re-mints a sleeper; aggregate MUST span the union.
- Rollback: slices 1-3 are additive/behavior-preserving (revert independently). Slices
  4-7 are seam-scoped under the mediator seal (transaction rollback + git revert per
  slice).

## Acceptance (this patch)
- User accepts the resolved knobs (Q1/Q2/keying) or amends them.
- Then component_patch details each seam body + the exact cache-kill surface (door epoch
  vs creation_context vs pools) so all of it dies and nothing double-frees.
- Then build slice 1. Full unit tree green in the user's 3.14t venv gates every slice.

## Notes
- DATETIME: 2026-06-21
  TYPE: PLAN
  CLAIM: Architecture patch authored from the epic's converged design (active/inactive +
    frame-owned signatures + version-registry consolidation). Folds forks #1-#4 + the
    bind-inactive capability + the ~15% perf consolidation into one foundation. Resolved
    the two remaining knobs (Q1 clean-notch, Q2 bind_inactive-attaches-existing) with a
    lean for user override. No code lands on this artifact; component_patch is next.
  EVIDENCE:
  - tickets/epics/2026-06-14_spellindex_genuine_index_operations_epic.md (Notes 2026-06-20)
  - spellbook.py:933-1040,3138-3175 ; meld.py:1253-1288,1363-1367 ;
    conduit_meld.py:284-315 ; aetheric_frame.py:604-633 ; aether.py:1252 ;
    spell_index.py:37,311 ; transfer_of_ownership.py:1303-1364
  NEXT: user accepts/amends the resolved knobs -> write component_patch -> build slice 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
