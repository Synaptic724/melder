# Epic: SpellIndex genuine-index operations (notch / add_to_index / remove_from_index)

- Completed: 2026-07-11T18:50:00Z
- Summary: Source-verified delivered (facades at conduit.py:4003/:4075,
  notch delegation landed) and green-covered by the owner's full-tree
  runs; closed on owner-directed general_0 cleanup - details in Status.

## Metadata
- Epic ID: EPIC-2026-06-14-spellindex-genuine-index-operations
- Status: closed (owner-directed cleanup 2026-07-12, melder_0 inheritor:
  source-verified delivered - add_to_spell_index/remove_from_spell_index
  facades live at conduit.py:4003/:4075 via the July index_link work;
  notch delegation recorded landed; the 2026-07-01 bug findings match
  the guards the restructure added and the code has survived every
  full-tree green since (9702 latest). Any residue surfaces as normal
  new work with fresh evidence, not this stale ticket.)
- Owner: cowork
- Agent Name: melder_0 (INHERITED 2026-07-12: general_0 + mediator_builder_0
  both owner-confirmed/marked departed; owner: "yeah sure inherit it")
- Priority: p1
- Created: 2026-06-14T23:17:53Z
- Updated: 2026-07-12T08:25:00Z

## Inheritance Note (melder_0, 2026-07-12)
- DATETIME: 2026-07-12T08:25:00Z
  TYPE: FACT
  CLAIM: Lane INHERITED. State on takeover: the four stories (notch
    finish split, add_to_index seam+facade, remove_from_index
    seam+facade, ADD/REMOVE strategy docstring rewrite) are DESIGNED with
    patches authored but NOT implemented. CONSUMING melder_0's never-read
    2026-07-01 NOTICE to general_0 (mailbox, deleted this pass) - two
    possible LIVE BUGS + one UNKNOWN in the contract/index seam, all
    unowned until now: (1) _remove_contracted_spell's active-branch on a
    LIVE index discards EVERY member id from _contracted_spell_ids and
    pops the whole index subscription (spellbook.py:2811-2824 at the
    time) - whole-index teardown on the single-member-removed path;
    (2) keying asymmetry: _add_contracted_spell registers under
    selected_spell_id (:2612) while removal unregisters under
    spell.spell_id (:2808); (3) UNKNOWN: whether
    _ensure_contracted_active/_activate_contract_spell re-key
    _contracted_spells_by_id old->new selected id on follow-on-notch.
    Line numbers predate three weeks of drift - re-verify from source
    before touching. RELATION to melder_0's graft lane: the graft's
    fresh-index-only law deliberately avoided these seams; implementing
    add/remove here later unlocks merge-grafts (owner dial).
  NEXT: fresh-session program - source re-verification of the three
    findings first (they may be bugs in shipped code), then the four
    stories per general_0's authored patches (re-validate patches
    against current source before consuming).
  REREAD: REQUIRED

- DATETIME: 2026-07-12T08:50:00Z
  TYPE: FACT
  CLAIM: OWNER CORRECTION CONFIRMED FROM SOURCE ("pretty sure the June
    work is probably done"): this epic's ticket state was STALE, not its
    code. Conduit.add_to_spell_index (conduit.py:4003) and
    Conduit.remove_from_spell_index (:4075) EXIST - the add/remove
    seams+facades (stories 2-3) landed through general_0's July
    index_link_contract work after this ticket's last update
    (2026-06-28); the lineage-map row separately records the notch
    delegation landing (_apply_notch -> SpellIndex.update rekey). The
    _remove_contracted_spell region has been restructured since my
    2026-07-01 findings (guards his landed row describes match my
    flagged concerns), so the "two live bugs" are LIKELY FIXED but the
    line-level claims are obsolete either way. REFRAMED SCOPE: this
    inherited lane is a VERIFY-AND-CLOSE pass (walk the four stories +
    the three findings against current source, close what's delivered,
    ticket only what genuinely remains) - NOT a build program.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4003-4075
  NEXT: the verify-and-close walk, fresh session.
  REREAD: REQUIRED
- Target Window: 2026-Q2
- Related Program/Initiative: SpellIndex lineage->index migration
  (map lane: tickets/tasks/2026-06-12_spell_index_lineage_separation_map_task.md ;
   rename lane: tickets/tasks/2026-06-17_spellindex_terminology_rename_execution_task.md ;
   transfer/version semantics: tickets/epics/2026-05-22_pin_down_spellindex_transfer_and_version_semantics_epic.md [mutres_0])

## Design History (this epic was rewritten 2026-06-20)
Originally authored on a MULTI-MEMBER premise (the SpellIndex holds a set/list of member
spells, one active + the rest dormant; object-level add/remove move members between
member-stores). That premise was WRONG and was reverted under user direction:
`_members` + 6 member methods removed from spell_index.py (commit 2b98352a reverted);
the `_apply_add_to_index`/`_apply_remove_from_index` member-move/mint seams + helpers +
entry methods removed from spellbook.py; `bump_door_epoch` removed from spell.py. The
reverted design + its correction trail live in the map-task notes + git history; they are
NOT the contract. The corrected model below is.

## Problem / Opportunity
SpellIndex was historically a one-spell / version-history "lineage" object. The goal is a
clean, correct index primitive: a stable identity that points to one resolvable spell, with
the operations that let an agent (and mutation_research) repoint it (notch) and move an
already-owned spell between indexes (add_to_index / remove_from_index) without corrupting the
resolution surface. The first build got the model wrong (members/order/mint); this epic
specifies the corrected model so the rebuild is right.

## MRP Alignment (Most Reasonable Product)
The index is the substrate beneath governed mutation (MutationResearch) and ASE state-shaping:
agents iterate on codegen'd spells and repoint what is resolvable. Getting resolution-surface
integrity right the first time is the MRP core; half-correct registration silently corrupts
meld/validity. Foundation-must-be-right work, not patch-later.

## CORRECTED MODEL (user-confirmed 2026-06-20; SUPERSEDED 2026-06-29 -- see Notes)
> SUPERSEDED 2026-06-29 (multi-member correction, user-directed). The single-spell
> claim in this section is WRONG vs the committed code + tests. Real model: SpellIndex
> HOLDS A SET of member ids (`_spells_in_index`) and tracks one ACTIVE member
> (`selected_spell_id`); `update(new_id)` selects AND adds to the set; only the active
> member is meld-by-id resolvable; the member set drives existence/ownership lookups
> (frame.find_index_for_spell/find_conduit_id_for_spell, per-conduit id caches,
> Detail.has_spell). The index organizes its member ids; the spell_id resolves.
### What a SpellIndex is (ORIGINAL 2026-06-20 claim -- INCORRECT, retained for history)
- A STABLE ULID identity that points to exactly ONE active spell. NOT a container of members;
  NO order. It solves the "mutable dictionary key" problem: a stable hashable key whose
  underlying spell can change.
- Versions of a spell are owned by mutation_research, NOT by the index.
- A spell is always in exactly one index; bind mints a fresh single-spell index per spell.

### Resolution: the index ORGANIZES, it does not resolve
- Two Spellbook-owned dicts are the wiring:
  - `_lookup_spells {(frame_key, binding_name) -> SpellIndex}` — binding -> index.
  - `_spells {SpellIndex -> active Spell}` — index -> the live spell.
- The meld component holds BOTH BY REFERENCE (`_owned_spells = spellbook._spells`,
  `_lookup_owned_spells = spellbook._lookup_spells`; meld.py:178,186). Cold binding
  resolution: `_lookup_owned_spells[key] -> index -> _owned_spells[index] -> Spell`
  (meld.py:1363-1367). After that, meld runs entirely off `spell_id`.
- WARM binding resolution caches `_input_resolution_cache {binding-input -> spell_id}`
  (per meld component, persistent, LRU-bounded; meld.py:195) and serves the cached spell_id
  via `_spell_id_pool` WITHOUT touching the index (conduit_meld.py:284-315). A binding does
  NOT re-read the index every meld.
- A raw `meld(spell_id)` bypasses the index entirely (id-pool / `_spells_by_id`).
- So the index is an ORGANIZING key in the resolution maps; the resolution CURRENCY is the
  spell_id. Everything downstream keys by spell_id: the id-pools, `_input_resolution_cache`,
  the fast-meld-door (`_fast_meld_doors` keyed by spell_id, guarded by `_door_epoch`;
  conduit_meld.py:66-82,251-256), and Creations (`get_creation(spell_id)`).

### Binding signatures + the uniqueness gate
- The binding signature `(frame_key, binding_name)` lives on the SPELL (`Spell._key`),
  NOT on the index. SpellIndex has no `_key`.
- Bind's FRAME-WIDE gate is the AETHER, by FINGERPRINT, not the signature:
  `_aether._check_for_spell(new_spell.spell_id, frame)` (spellbook.py:3138) consults the
  frame's `_selected_spell_registry` (per-conduit union of every index's
  `spells_in_index()`; aetheric_frame.py:635) — True if the spell_id exists in ANY index of
  ANY conduit in the frame. It does NOT check the binding signature.
- The binding-signature gate is LOCAL: `_assert_lookup_key_available` against THIS
  spellbook's `_lookup_spells`, called `check_contracted=False` at bind (spellbook.py:3157).
  So binding-signature uniqueness is per-spellbook, not frame-wide.
- The fingerprint (spell_id) folds in the "lookup signature" along with structure/existence/
  disposal (bind collision message), but the Aether compares the WHOLE fingerprint. So a real
  version (same signature, DIFFERENT code) has a DIFFERENT fingerprint — the Aether does not
  see two versions as duplicates; only the LOCAL signature check would collide.
- Each bind mints a FRESH index (bind.py:292), so the "same index -> idempotent" branch of
  `_assert_lookup_key_available` never fires for a new bind. Within one spellbook you cannot
  bind two spells on one signature; a version must attach to the EXISTING index via a NON-bind
  path, never re-bound.

## Operations (corrected)
### notch — repoint the index to a different (already-owned) spell
- The only operation that survived in concept. Makes a different, already-registered spell the
  index's active spell. Cold meld resolves via `_spells[index]`, NOT `index.selected_spell_id`,
  so the seam drives the Spellbook-owned state, not just the index's own pointer:
  1. `_spells[index] = new_spell` (what cold meld resolves to).
  2. `index._selected_spell` / `_selected_spell_id` = new (what compiler/validation read).
  3. VACATE the outgoing spell-id from `_spell_id_pool` + `_spells_by_id` so the warm
     `_input_resolution_cache` MISSES and re-resolves through the index to the new spell
     (conduit_meld.py:297-304 self-heal). The id change is the invalidation.
  4. Contracted spellbooks follow the notch (rekey old->new via `_update_contracted_spell_id`).
- `update()` reduces to the INTERNAL index repoint (pointer + `_spells_in_index` set); the
  Spellbook `_apply_notch` SEAM owns the surrounding map work (#1-#4); the mediator `notch`
  transaction provides the EXCLUSIVE seal. Today `_apply_notch` is a thin delegate to
  `update()` (which reaches into the spellbook maps itself) — that split is part of the build.
- No cache-invalidation orchestration beyond the id-vacate: door cache, creations, and the
  input_resolution_cache all key by spell_id and follow the new id.

### add_to_index / remove_from_index — move an OWNED spell between indexes (transfer-flip)
- These STAY (user-directed 2026-06-19). NOT bind/link acquisitions; NOT the deleted
  member-store moves. Moving a spell the spellbook ALREADY OWNS is a TRANSFER-of-ownership-
  pattern flip — the owned spell (its compiled object + creations) is the asset and must be
  preserved, not re-minted.
- Reference mechanism: `transfer_of_ownership.py` — `_assert_ownership` (gate on
  `spell._owner_conduit_id`; :443), then `_flip_registry_and_spellbooks` (move the EXISTING
  spell+index between registries with collision checks + rollback; :1272-1408), carry creations
  (`_move_creations`), repoint borrowers, gate the lineage during, roll back on failure. The
  deleted `_apply_remove_from_index` was ILLEGAL: it MINTED a fresh SpellIndex into the
  Spellbook maps (re-ran bind's registration) instead of flipping an owned one.
- add_to_index = move an owned spell onto another index. remove_from_index = separate an owned
  spell into its own index. Both build on the flip, not a mint.
- The mediator ADD_TO_INDEX / REMOVE_FROM_INDEX strategies + enum + builder/mediator
  registration + tests are INTACT (mediator_builder_0). They await the rebuilt Spellbook/Conduit
  entry points + `_apply_*` seams on the flip pattern.

## OPEN DECISIONS (DECISION_REQUEST — block the build)
1. DISABLE-SIGNATURE FORK: when a spell deactivates, does its binding signature STAY owned by
   the index (versioning: index keeps the signature, swaps the active spell) or LEAVE
   `_lookup_spells` (freed for re-claim)? Drives different ops.
2. NOTCH SUBSTITUTION MODEL: when notching to a new version, is the active spell's `.spell_id`
   rekeyed IN PLACE, or is a DISTINCT codegen Spell SUBSTITUTED (the `update()` commented
   block)? "meld sees a spell that's not set" implies a distinct object; `update()` as-written
   rekeys the same object.
3. OLD-ID DISPOSITION ON NOTCH: EVICT the outgoing spell-id from the pools (warm cache
   self-heals; `meld(old_id)` then fails) vs KEEP it (old id still id-meldable, but notch must
   explicitly clear `_input_resolution_cache`, which is per-conduit and broader).
4. ADD/REMOVE MECHANICS: when an owned spell moves onto another index, what becomes of its old
   index (GC'd vs kept), and does the target index already exist or get created?

## SEAM vs STRATEGY responsibility split (unchanged, still valid)
- STRATEGY (`*_transaction_strategy.py`): builds the EXCLUSIVE seal + stamps devops fact
  baselines only (ids via `staged`, not live objects). No object-level registration.
- SEAM (Spellbook `_apply_*`): owns the entire object-level resolution-surface choreography
  inside the held window.

## Ticket Contract
- ENTRY_GATE: corrected model accepted by user; rename lane done (awaiting 3.14t); mediator
  ADD/REMOVE/NOTCH strategies intact.
- EXECUTION_BOUNDARY: SpellIndex resolution model + the notch responsibility split + the
  add_to_index/remove_from_index seams (transfer-flip) + entry points + conduit facades +
  strategy docstring rewrites. EXCLUDES MutationResearch derivation, Creations lifecycle, and
  the cluster surface (compiler_strategy_0's in-flight `_root_creations` refactor).
- EXIT_GATE: notch + add + remove implemented on the corrected model; resolution/validity/
  Nexus/registry coherent; full unit tree green in the user's 3.14t venv; user-accepted.
- FAILURE_ESCALATION: DECISION_REQUEST for the open forks above; CONFLICT if a consumer assumes
  the index resolves via `selected_spell_id` rather than `_spells[index]`.

## Goals (Outcomes)
- notch repoints the index's single active spell coherently (maps + pointer + id-vacate +
  contracted), visible to both cold and warm meld.
- add_to_index / remove_from_index move an OWNED spell between indexes via the transfer-flip,
  preserving the spell + creations, never re-minting.
- No corruption of the resolution surface after any op.

## Non-Goals (Explicit Exclusions)
- No MutationResearch version-derivation semantics (versions are theirs).
- No Creations disposal / instance lifecycle changes (resolution-only).
- No cluster-surface changes while compiler_strategy_0's `_root_creations` refactor is in flight.
- No multi-member SpellIndex (the reverted premise); no member set, no order, no mint.

## Scope Boundaries
- In scope: the resolution model, notch finish, add/remove seams on the flip pattern, entry
  points + conduit facades, strategy docstrings.
- Out of scope: members, order, the mint, mutation engine, creations, cluster keying.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: corrected model captured; the four open forks must be user-decided before
  build can start (blocking DECISION_REQUESTs).

## Requirements (Functional + Non-Functional)
- Each op atomic under its mediator transaction seal; resolution writes inside the held window.
- notch drives `_spells[index]` + the index pointer + old-id vacate (per the decided disposition).
- add/remove follow the transfer-flip (assert ownership -> flip -> carry creations -> rollback).
- Truthful validation: full unit tree (not folder-scoped) run by the user in 3.14t.

## Constraints / Assumptions
- Strategy layer cannot access live objects (ids only) -> seam owns object choreography.
- Mount intermittently truncates large file-tool writes -> use atomic writes + verify
  (py_compile / line count).
- 3.14t nogil: thread-safety is paramount; `selected_spell_id` stays a lock-free read; writers
  serialize via the seal.

## Stories (Required to Complete)
- [x] Story: resolve the 4 open forks -- RESOLVED via converged design + architecture_patch
      (option B frame-owned signatures; active/inactive maps; forks #1-4 folded in). Two impl
      knobs (Q1 clean-notch, Q2 bind_inactive attach-existing) leaned in the patch, await user
      confirm; non-blocking for inert slices 1-3.
- [ ] Story: notch finish — split `update()` (internal-only) vs seam (maps + id-vacate), on the
      decided substitution model; with tests.
- [ ] Story: add_to_index seam + entry + conduit facade on the transfer-flip pattern; with tests.
- [ ] Story: remove_from_index seam + entry + conduit facade on the transfer-flip pattern; with tests.
- [ ] Story: rewrite the ADD/REMOVE strategy docstrings to the flip mechanism (coordinate with
      mediator_builder_0).

## Acceptance Criteria (Epic Done)
- All stories accepted; notch + add + remove callable; resolution/validity/Nexus coherent; full
  unit tree green (user-run 3.14t); board/closure synced.

## Risks / Mitigations
- RISK: a consumer reads `spell_index.selected_spell_id` expecting it to be the resolved spell —
  cold meld uses `_spells[index]`. MITIGATION: keep the two in sync on every notch.
- RISK: notch not visible through a warm binding because the old id lingers in the pools.
  MITIGATION: vacate the old id (decision #3) so the input_resolution_cache self-heals.
- RISK: add/remove re-mint instead of flipping (the original bug). MITIGATION: build on
  transfer_of_ownership's flip + ownership assertion + rollback; never hand-register.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No treating the index as the resolution authority (it organizes; spell_id resolves).
- [ ] No hand-registering a spell+index outside bind/link/transfer (the deleted mint).

## Notes
- DATETIME: 2026-06-14T23:17:53Z
  TYPE: PLAN
  CLAIM: Epic originally authored by general_0 on the multi-member premise (now reverted; see
    Design History). Strategy = seal + devops baseline only; the seam owns the object-level
    resolution-surface choreography. Preserved for history; superseded by the 2026-06-20
    corrected model.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-06-12_spell_index_lineage_separation_map_task.md
  NEXT: superseded.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T11:57:23Z
  TYPE: DECISION
  CLAIM: Epic body rewritten to the corrected single-spell model (user-directed). SpellIndex =
    a single-spell organizing key; resolution via `_spells[index]` + the spell_id pools (index
    organizes, spell_id resolves); uniqueness split (Aether-fingerprint frame-wide vs local
    binding-signature); notch = repoint + vacate old id; add/remove = transfer-flip on owned
    spells (NOT a mint). Four open forks are blocking DECISION_REQUESTs.
  EVIDENCE:
  - meld.py:178,186,195,1363-1367 ; conduit_meld.py:284-315,66-82
  - spellbook.py:3138,3157 ; aetheric_frame.py:635 ; bind.py:292
  - transfer_of_ownership.py:443,1272-1408
  NEXT: user decides the 4 forks -> build notch/add/remove per story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T15:36:04Z
  TYPE: FACT
  CLAIM: Consumed two mailbox messages from mediator_builder_0 (2026-06-19): (1) NOTICE -
    enum-sweep landed; spellbook.py(4409)+conduit.py(4657) write-window RELEASED; my
    notch-facade edits preserved. (2) ACK - ADD_TO_INDEX/REMOVE_FROM_INDEX STAY intact
    (strategies+enum+builder/mediator registration+tests), standing by for the Spellbook/
    Conduit entry points + _apply_* seams on the transfer-of-ownership pattern. Both are
    already reflected in this epic's contract.
  EVIDENCE:
  - codex/context_compass/mailbox_board.md (messages deleted on consume)
  NEXT: resolve the 4 open forks with the user, then build per story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-06-20T16:15:44Z
  TYPE: FACT
  CLAIM: Cross-spellbook binding-signature collision handling is ASYMMETRIC, verified in
    source. _assert_lookup_key_available checks _lookup_spells for a (frame_key,binding) ->
    DIFFERENT-SpellIndex collision, local and/or contracted, gated by check_local/
    check_contracted. (1) BIND: check_local=True, check_contracted=False -> signature unique
    only WITHIN the local spellbook. (2) LINK/borrow (_add_spell_to_contract ->
    _assert(check_local=False, check_contracted=True); mirror _add_contracted_spell): borrowed
    signature checked against OTHER contracted peers but NOT against the borrower's LOCAL
    bindings -> a local binding silently shadows a contracted one (find_spell_key resolves
    local-first). (3) TRANSFER flip (_flip_registry_and_spellbooks): checks SPELL_ID collision
    on target _spells_by_id/_spell_id_pool (raises) but does NO binding-signature check --
    tgt_book._lookup_spells[spell_obj._key] = index is set unconditionally, so a target that
    already binds that signature to a DIFFERENT-code spell (different spell_id, so the id check
    passes) is silently CLOBBERED and its own spell is orphaned from its lookup key (still
    id-resolvable, no longer binding-resolvable). User assumption 'transfer checks the binding
    signature' is FALSE: it checks spell_id, not signature.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1708-1762
  - src/melder/aether/spellbook/spellbook.py:3138-3166
  - src/melder/aether/spellbook/spellbook.py:2238-2255
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1664-1677
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1331-1364
  IMPACT: add_to_index/remove_from_index build on the transfer flip; reused as-is they inherit
    the missing target-side signature check. The seam MUST assert lookup-key availability
    (check_local=True) on the destination binding before repointing, or a move can clobber a
    destination binding. Directly informs fork #2 (keep binding-target mgmt spellbook-local).
  NEXT: user decision -- is transfer's missing signature-check a bug to fix in THIS epic, or
    flagged to the transfer/version epic (mutres_0)? Then spec add/remove with the check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T16:35:44Z
  TYPE: FACT
  CLAIM: Resolution does NOT overwrite on duplicate signatures in the normal path; the model is
    bounded. _lookup_spells maps (frame,binding) -> SpellIndex (indirection), _spells[index] ->
    active Spell (spellbook.py:3164-3165); the index indirection is WHY notch swaps the active
    spell without re-keying the binding dict or breaking warm refs. WITHIN a spellbook bind's
    _assert_lookup_key_available(check_local=True) raises BEFORE any _lookup_spells write
    (1737-1747), so no duplicate _key slot forms. ACROSS spellbooks in one frame: same-fingerprint
    dup is blocked frame-wide by Aether _check_for_spell(spell_id) (3138); different-code/
    same-signature is ALLOWED+safe -- separate _lookup_spells dicts, spellbook-rooted resolution
    (local-first then contracted; find_spell_key:1764-1777). The ONLY real dict-overwrite is the
    unguarded transfer write (transfer_of_ownership.py:1353).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3138-3166
  - src/melder/aether/spellbook/spellbook.py:1737-1747
  - src/melder/aether/spellbook/spellbook.py:1764-1777
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1351-1364
  IMPACT: 'Duplication' is bounded: a feature across books (rooted resolution disambiguates),
    blocked within a book, a bug only on transfer. Fork #2 (keep binding-target mgmt
    spellbook-local) stays viable; the fix is a guard on the move/transfer path, not a resolution
    redesign.
  NEXT: user calls fork #2 + whether to fix the transfer guard in THIS epic or mutres_0's.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-20T17:06:39Z
  TYPE: DECISION
  CLAIM: Binding-signature uniqueness is FRAME-OWNED (option B, user-locked). The AethericFrame
    becomes the authority for binding signatures, symmetric with the spell_id registry it already
    owns: at most ONE spell may be ACTIVE on a given (frame_key, binding_name) per frame. Multiple
    spells (versions) may be BOUND on the holding SpellIndex; only one is active. bind CLAIMS the
    frame signature (raises 'binding signature already active in this frame' if taken); disable
    RELEASES it; notch and transfer do NOT change signature->index (same index) so they leave the
    frame registry untouched. Supersedes the prior 'binding signatures are spellbook-local' model.
  RATIONALE: removes the frame-owns-id-but-not-signature asymmetry; converts late link-time
    collisions into early deterministic bind-time failures; makes WITHIN-frame links collision-free
    by construction. CROSS-FRAME LINKING DOES NOT EXIST (user-confirmed x2), so a frame-unique
    signature => links can never surface a signature collision. Cost accepted: lose 'two
    spellbooks, same signature, different impls, one frame' (Melder expresses multi-impl via
    distinct binding_name / collection DI, so an exact same-signature collision is ~always a bug).
  EVIDENCE:
  - user decision 2026-06-20 (this session); cross-frame linking confirmed absent (x2)
  - src/melder/aether/aetheric_frame/aetheric_frame.py (owns _selected_spell_registry; add signature registry here)
  - src/melder/aether/spellbook/spellbook.py:3138-3166 (bind gate: add frame-signature claim)
  IMPACT: Re-scopes this epic. The frame binding-signature authority is a new system-impacting
    foundation lane (AethericFrame + bind + transfer) that FEEDS the notch/add/remove seams.
    Resolves fork #1 (disable frees, notch keeps) and fork #2 (frame-owned) at once. Transfer's
    missing-signature-guard bug dissolves by construction under B.
  NEXT: write patch artifacts (architecture_patch + component_patch) for the frame-signature
    authority before any code; notch can be built in parallel (independent of the frame registry).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-20T17:26:25Z
  TYPE: FACT
  CLAIM: CORRECTION (a prior chat claim was wrong): a spell is NOT meldable-by-id just because
    its id sits in an index. _spells_in_index is a SET OF SPELL-ID STRINGS (spell_index.py:37,73,
    329), pure tracking. meld(spell_id) resolves ONLY via the id->object pools:
    _resolve_spell_by_id checks _spell_id_pool then _spells_by_id then _contracted_spells_by_id
    (meld.py:1253-1288). Those pools are written ONLY by _register_owned_spell_id /
    _update_owned_spell_id (spellbook.py:933-975, 977-1040) for the OWNED/ACTIVE spell.
    CONSEQUENCE: dormant candidate OBJECTS have NO home today -- the index holds only the ONE
    active (_selected_spell; _spells[index]=active), the pools hold only registered actives, and
    _spells_in_index holds only ids. bind-inactive/versions therefore need an explicit decision
    on where candidate objects live and whether they are reachable while dormant.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:37,73,329
  - src/melder/aether/conduit/meld/meld.py:1253-1288
  - src/melder/aether/spellbook/spellbook.py:933-975
  - src/melder/aether/spellbook/spellbook.py:977-1040
  IMPACT: Real sub-decision for bind-inactive + notch: (a) register dormant candidates in the
    id-pools (id-meldable while dormant, but puts possibly-uncompiled spells on the resolution
    surface) vs (b) hold dormant candidates OFF the resolution surface (mutation_research session
    for versions / a candidate store for bind-inactive), meldable only after notch promotes them
    via _register/_update_owned_spell_id. Lean (b): dormant = not resolvable until activated.
  NEXT: user picks (a) vs (b) for dormant-candidate home + reachability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T17:30:44Z
  TYPE: PLAN
  CLAIM: Converged design (user-proposed; greenfield -- no inactive-spell infra exists today, so
    additive, no migration). Spellbook gains INACTIVE mirrors of its existing ACTIVE maps:
    _inactive_spells (owned) + _inactive_contracted_spells (borrowed), alongside _spells /
    _contracted_spells. meld reads ONLY the active maps + id-pools, so inactive = OFF the
    resolution surface, not meldable until promoted (this is option b; solves the homeless-
    candidate problem). Stays single-active-pointer: inactive spells are a SEPARATE map, NOT
    members on the index -- does NOT re-introduce the rejected multi-member-resolution model;
    _spells[index] is still exactly one active. notch = SWAP: outgoing active -> _inactive_spells
    (unregister id-pools, release frame signature); incoming inactive -> _spells[index] (register
    id-pools, claim frame signature); nothing destroyed (can notch back). disable =
    notch-to-nothing (active->inactive, signature released). bind-inactive = stage object into
    _inactive_spells (+ id into _spells_in_index), claim nothing. Borrowed spell going inactive ->
    _inactive_contracted_spells.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:933-975 (id-pool register == the promotion point)
  - src/melder/aether/conduit/meld/meld.py:1253-1288 (meld reads active id-pools only)
  - this session: option B (frame-owned signatures) + option b (dormant off-surface)
  IMPACT: Foundation lane = Spellbook structure (new inactive maps) + AethericFrame signature
    registry + notch/disable/bind-inactive seams. System-impacting -> patch artifacts required
    before code. Folds forks #1-#4 + the bind-inactive capability into one coherent structure.
  OPEN: (1) _inactive_spells keying (lean spell_id; _spells_in_index as index->ids tracker);
    (2) validity-on-promotion (notch sets new active GATED so existing meld revalidation compiles);
    (3) cleanup walks active + inactive.
  NEXT: on user go, write architecture_patch + component_patch for the inactive-maps +
    frame-signature foundation, then build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T17:41:54Z
  TYPE: DECISION
  CLAIM: notch / deactivation lifecycle (user-driven; my refinements on 5/6b):
    (1) Contracted fan-out is OWNER-CONDUIT-driven + transactional: owner notch moves each
    borrower's old active borrowed spell -> _inactive_contracted_spells and brings the new active
    into _contracted_spells, reusing the contracted propagation update() already performs; the
    notch transaction strategy seals owner + affected contracted scopes. (verify exact propagation
    method at spec.)
    (2) Transfer carries inactive: _flip_registry_and_spellbooks must move the index's
    _inactive_spells entries too, not just the active.
    (3) notch PRECONDITION: target must already exist in _inactive_spells (notch PROMOTES; never
    mints/registers -- staging is bind-inactive / mutation_research).
    (4) Frame-owned binding-signature uniqueness (option B) stays.
    (5) Deactivation invalidation: evict outgoing id from _spell_id_pool/_spells_by_id (covers
    meld(spell_id) + warm _input_resolution_cache self-heal) AND kill the retained fast-door/lane
    path by turning the inactive spell's creation_context OFF (access -> throw, acceptable). Exact
    cache surface (door epoch vs creation_context vs pools) verified at spec so all of it dies and
    nothing double-frees.
    (6a) Inactive spells are NOT flagged dirty -- dirty is a meld-gate concept and inactive is OFF
    the resolution surface; dirtiness attaches at PROMOTION.
    (6b) notch revalidates the conduit TARGETED + LAZY: set the newly-active lineage GATED + mark
    its component-of dependent roots dirty in the conduit resolution state; existing meld-time
    revalidation recompiles on next resolve (same pattern transfer/link use). Not an eager
    whole-conduit sweep unless explicitly wanted.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:933-1040 (id-pool register/update/unregister)
  - src/melder/aether/conduit/meld/meld.py:1253-1288 (meld-by-id reads pools only)
  - src_components.md: ChangeControlManager dirty-roots + component-of; ConduitResolutionState;
    gated meld-time revalidation
  IMPACT: notch is mostly ORCHESTRATION of existing machinery (gated validity, dirty roots,
    component-of, creation_context build, CreationGate drain, contracted propagation) + the new
    active/inactive map moves + the frame signature claim. Lane is contained.
  NEXT: write architecture_patch + component_patch for the inactive-maps + frame-signature
    foundation; then build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T17:44:40Z
  TYPE: DECISION
  CLAIM: REFINES 6b (revalidation scope on notch) -- user correction. Revalidate ALL spells that
    used the outgoing spell_id, WHEREVER it was used, not just the owner conduit. Scope = the
    COMPLETE consumer closure of the notched lineage: (a) owner conduit -- the lineage's
    component-of dependent roots; (b) EVERY contracted borrower conduit that had the spell_id --
    its own component-of dependent roots. The owner-driven notch fan-out (point 1) marks dirty in
    each of those conduits, so the cross-conduit consumer set is covered. Unit of revalidation is
    the consuming ROOT: revalidating a root re-checks every spell in its dependency tree, so 'all
    associated spells' are checked via their consuming roots (root = entry point, tree = what gets
    validated).
  TIMING (open knob, not scope): marking the whole closure dirty/GATED guarantees none can
    resolve stale (each revalidates before its next meld). LAZY = revalidate on next resolve
    (existing transfer/link pattern, identical correctness); EAGER = revalidate the whole closure
    synchronously inside the notch transaction (heavier, holds the seal longer). Lean lazy; user
    to confirm.
  EVIDENCE:
  - src_components.md: ChangeControlManager component-of + per-conduit dirty-roots;
    ConduitResolutionState; gated meld-time revalidation
  - this session: owner-driven contracted fan-out (notch lifecycle point 1)
  IMPACT: notch must mark the dependent-root closure dirty in the owner conduit AND in every
    borrower conduit that contracted the spell_id (cross-conduit, not conduit-local). The notch
    transaction scope-claims must span all those conduits.
  NEXT: fold into patch artifacts; build with cross-conduit consumer-closure dirtying.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T19:18:55Z
  TYPE: PLAN
  CLAIM: Implementation plan for the active/inactive + frame-signature foundation. New structures
    (additive): AethericFrame._active_binding_signatures {(frame_key,binding)->SpellIndex} +
    claim/release/is_available/get_active (frame-lock-guarded); Spellbook._inactive_spells
    {spell_id->Spell} + _inactive_contracted_spells {conduit_id->{spell_id->Spell}}. Build order,
    safest-first, each an independently-tested slice: (1) add inactive maps + cleanup walk (inert,
    zero behavior change); (2) add frame signature registry + methods (inert until claimed); (3)
    wire bind to claim the frame signature (the one hot-path change, isolated); (4) bind_inactive
    (stage into _inactive_spells + index _spells_in_index, claim nothing); (5) _apply_notch swap
    under the notch transaction (outgoing->inactive: evict id-pools + creation_context off;
    incoming->active: register pools + _spells[index] + GATED; compute_impact_closure +
    mark_contract_dependents_dirty + mark_conduit_dirty; borrowers old->_inactive_contracted_spells);
    (6) disable (active->inactive, release frame signature, drop _lookup_spells); (7) transfer/add/
    remove carry inactive + frame-claim guard. GATE: system-impacting -> architecture_patch +
    component_patch required before code (also the agreed blast-radius/safety map).
  EVIDENCE:
  - epic Notes this session (converged design + notch lifecycle + 6b closure)
  - src/melder/aether/spellbook/spellbook.py:933-1040,3138-3166 (id-pools, bind gate)
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:535,1003,1110
  OPEN (shape the seam bodies; resolve before patch artifacts):
    Q1 clean vs general signature on notch -- do candidates always share the index's ONE signature
    (notch never touches the frame registry) or can notch re-key to a different signature (release
    old + claim new)? User's earlier notch algo implied general; active/inactive 'notch keeps
    signature' implies clean.
    Q2 bind_inactive API -- fresh index vs attach to existing index vs both, and how the caller
    specifies.
  NEXT: resolve Q1+Q2 with user, then write architecture_patch + component_patch, then build slice 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T19:21:42Z
  TYPE: HYPOTHESIS
  CLAIM: The aetheric_frame version-registry chain (_reindex_conduit_versions +
    _selected_spell_registry) is a strong candidate for the ~15% slowdown (user's remember_to_fix
    branch). _selected_spell_registry {conduit_id->Set[spell_id]} is a DERIVED cache of
    _spell_registry {conduit_id->Set[SpellIndex]}. register_spell_index updates it INCREMENTALLY
    (.update, cheap), but unregister_spell_index / unregister_conduit_spells /
    register_conduit_spells call _reindex_conduit_versions, which throws away the conduit's cached
    set and FULL-REBUILDS it by iterating every index in the conduit and calling
    spell_index.spells_in_index() on each -- and spells_in_index() returns a COPY
    (set(self._spells_in_index), spell_index.py:311) under the index lock. So a single
    unregister = O(indexes-in-conduit) index-lock acquisitions + set allocations. The docstring
    says this per-conduit reindex REPLACED an old full-registry rebuild to fix a 'dict changed
    size during iteration' race -- so the slowdown is the price of the thread-safety fix done via
    coarse full-rebuilds + copies. Readers: has_spell (bind-time _check_for_spell) iterates all
    conduits' sets; find_index_for_spell/find_conduit_id_for_spell scan _spell_registry calling
    spells_in_index() per index (more copies). The add-incremental / remove-full-rebuild asymmetry
    is the smell.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:604-633 (_reindex full rebuild)
  - src/melder/aether/aetheric_frame/aetheric_frame.py:727-809 (call sites; add vs remove asymmetry)
  - src/melder/aether/aetheric_frame/aetheric_frame.py:635-712 (has_spell/spells_in_index/find_*)
  - src/melder/aether/spellbook/bind/spell_index.py:311 (spells_in_index returns a COPY)
  FIX DIRECTION: replace the derived per-conduit set cache with an INCREMENTALLY-maintained
    frame-wide id index -- Dict[spell_id->int refcount] (or Dict[spell_id->SpellIndex]) under the
    frame lock: add=increment, remove=decrement, has_spell=count>0, find_index=direct lookup. O(1)
    maintenance, no rebuilds, no set copies, no add/remove asymmetry, and find_index_for_spell goes
    O(indexes x ids) -> O(1). Keeps thread-safety (no whole-dict iteration) without the rebuild tax.
  CONNECTION: SAME design move as the new frame binding-signature registry (option B) -- both are
    frame-wide incrementally-maintained indexes for fast bind-time checks. Design them together
    (incremental/refcounted); fold the version-registry fix into the frame-authority lane so we
    don't add a SECOND weird-maintenance registry. Also: our notch/disable/add/remove will churn
    register/unregister_spell_index heavily -- on the current chain they'd inherit the full-rebuild
    tax, so fixing this first de-risks the seam build too.
  CAVEAT: 15% is the user's measurement, not mine; the culprit is a grounded hypothesis. Profile
    reindex/has_spell vs the rest to confirm before committing the fix as the cause.
  NEXT: confirm fix direction with user; profile; fold into the frame-authority patch artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T19:27:14Z
  TYPE: FACT
  CLAIM: Read remember_to_fix tip commit 73321b829 -- it SHARPENS the perf hypothesis. The diff
    shows the tip commit was itself an IMPROVEMENT: it replaced refresh_version_registry() (a FULL
    rebuild of ALL conduits' version sets, iterating the whole _spell_registry -> the source of the
    'dict changed size during iteration' race) with _reindex_conduit_versions(conduit_id) +
    incremental .update on register_spell_index. So _reindex is NOT the regression -- it's the
    lighter replacement. The REAL ~15% source is the branch's shift from a LAZY manually-refreshed
    cache to EAGER per-mutation maintenance under the frame RLock: the old _check_for_spell /
    _get_all_spell_versions docstrings said 'call _refresh_version_registry AFTER mutation so this
    stays accurate' (lazy, refresh-on-demand); commit abf8b9bda then routed every _spell_registry
    mutation through frame-owned lock-serialized methods that maintain the cache EAGERLY on every
    register/unregister. So the hot bind/conjure registration path now pays: frame-RLock acquire
    (contended under no-GIL parallel binds) + cache maintenance (reindex or .update calling
    get_all_versions/spells_in_index, which COPIES the set) on EVERY mutation. That eager-under-lock
    tax on the hot path is the regression, not the per-conduit reindex itself.
  EVIDENCE:
  - git remember_to_fix tip 73321b829 (aether.py -33, aetheric_frame.py ~73): full-rebuild ->
    per-conduit reindex; removed _refresh_version_registry; old docstrings show the prior LAZY model
  - commit abf8b9bda (encapsulate _spell_registry in lock-serialized frame methods) = the eager+lock shift
  - current branch codex_features2 carries the same structure (renamed _selected_spell_registry)
  FIX (sharpened): keep eager consistency (no racy lazy refresh) but make per-mutation maintenance
    O(1): frame-wide Dict[spell_id->int refcount] under the frame lock (add=increment,
    remove=decrement, has_spell=count>0). No reindex, no set copies, no add/remove asymmetry, no
    whole-dict iteration. Removes most of the per-mutation tax while staying race-safe. Also profile
    the frame-RLock itself -- if binds parallelize on one frame the lock is a second axis (measure
    before adding finer locking).
  CONNECTION: fold into the frame-authority lane -- the incremental refcount id-index is the SAME
    construct as the option-B binding-signature registry; build both incremental under one refactor.
  NEXT: confirm direction; user profiles eager-maintenance + frame-lock on the bind/conjure path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T19:36:49Z
  TYPE: FACT
  CLAIM: Version-registry maintenance call-site map (grounds 'managed via conjure'). BULK path:
    conjure -> conduit.py:2025 _register_conduit_spells_in_aether -> spellbook.py:1867 ->
    aether.py:1315 frame.register_conduit_spells(conduit_id, whole_set) = ONE bulk call per conduit;
    cleanup unregisters bulk (conduit.py:664). INCREMENTAL path: bind (spellbook.py:3224
    _register_single_spell_index), transfer (transfer_of_ownership.py:1303-1322), notch/add/remove
    (coming). So conjure is the bulk driver, but an incremental single-index path also exists.
  ANALYSIS: the real lever is DELTA/REFCOUNT vs SET-RECOMPUTE, not push(bottom-up) vs pull(top-down).
    Current code recomputes from index sets via spells_in_index() COPIES (full reindex on remove,
    copy+union on add). A frame-wide Dict[spell_id->refcount] updated by the specific delta is O(1)
    either direction. The bottom-up instinct is right BECAUSE the delta is known at the leaf -- but
    driving the delta from the MUTATION SEAM (bind/notch/conjure code, which already holds the lock
    and knows the change) is cleaner than coupling SpellIndex itself to the frame registry (avoids
    IoC coupling of the leaf). Also: a pure per-index leaf-push would regress conjure (N pushes vs 1
    bulk).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2025,664 ; spellbook.py:1867,1889,3224
  - src/melder/aether/aether.py:1315,1338,1341,1366,1397
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1303-1322
  RECOMMENDATION: keep the frame as registry OWNER (top-down ownership) but maintain by DELTAS into
    a refcount id-map: conjure = one bulk increment pass (1 lock), incremental ops = single
    id-delta; both feed the same map. Same construct as the option-B binding-signature registry ->
    one frame-authority refactor.
  NEXT: user reacts to delta-via-seams vs full leaf-push bottom-up; then patch artifacts.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-20T19:46:12Z
  TYPE: DECISION
  CLAIM: Version-system consolidation (user-directed; grounded). TWO redundant version caches exist
    today: (1) Spellbook._spell_versions Set[str] -- per-spellbook, maintained INCREMENTALLY (add at
    bind spellbook.py:3169-3175 + rekey 1042; discard at unregister 1091) and also has a rebuild
    _refresh_local_spell_versions:633; (2) AethericFrame._selected_spell_registry
    Dict[conduit_id->Set[str]] -- per-frame, RE-DERIVED from index objects via
    _reindex_conduit_versions (spells_in_index() copies = the 'weird lagging refresh'). Both track
    'owned version ids'. The frame cache exists only because the frame wants a frame-WIDE view and
    chose to re-derive from indexes instead of receiving the spellbook-owned set. SpellIndex drives
    nothing; the SPELLBOOK is the natural owner and already hosts the set.
  DECISION DIRECTION: consolidate to spellbook-owned versions, maintained PURELY incrementally
    (drop the refresh/reindex rebuilds), and feed the frame-wide existence check via a simple
    spellbook->frame delta PUSH (frame keeps a thin refcount/dict aggregate) instead of frame
    re-derivation. Deletes a whole redundant subsystem + the refresh tax (the ~15% candidate).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:147,258,633-654,1042,1091,3169-3175
  - src/melder/aether/aetheric_frame/aetheric_frame.py:604-633
  IMPACT: Frame-authority lane = (a) spellbook owns versions, incremental only, pushes deltas;
    (b) frame keeps a thin pushed aggregate for has_spell/find_index (refcount id-map + optional
    id->index); (c) the same push pattern carries the option-B binding-signature registry -- one
    coherent 'spellbooks push, frame aggregates' refactor. Bigger than a perf patch: it removes the
    redundant frame re-derivation. System-impacting -> patch artifacts.
  NEXT: confirm we consolidate as part of the frame-authority lane; then patch artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T20:30:01Z
  TYPE: HYPOTHESIS
  CLAIM: Design exploration (user; 'down the road') + reframe confirmation. (1) CONFIRMED:
    'versions' = WHAT'S IN THE INDEX (candidate spell_ids), NOT a lineage/version-history. Lineage
    (v1->v2->v3 governed chain, mutation_research's idea) was found infeasible AND restrictive;
    candidate-set-per-index is more flexible (any set the index can resolve to, one active =
    active/inactive). (2) SAFE-NOTCH conditions: a notch is cheap/safe when the replaced spell is
    (a) contract-IDENTICAL (consumers' structural resolution unchanged -> skip dependent
    revalidation) or (b) has NO DEPENDENTS (empty impact closure -> no fan-out). The no-dependents
    check is DOABLE TODAY via compute_impact_closure([index]) / direct_dependents -> a 'cheap-notch
    fast-path' (skip 6b fan-out when the closure is just the index). The contract-identical check is
    harder (needs contract comparison) -> future optimization. (3) EMERGENT CAPABILITY: a fixed
    unique singleton that notches then becomes UNMELDABLE (one-shot / sealed) -- feasible with the
    active/inactive deactivation we designed (creation_context off + evict from pools = the
    'unmeldable' state). Not extra machinery; a capability the foundation grants.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:535 (compute_impact_closure / direct_dependents)
  - this session: active/inactive deactivation (creation_context off + pool evict) = unmeldable state
  IMPACT: notch seam should branch on impact-closure size: empty -> cheap-notch (no fan-out);
    non-empty -> full 6b revalidation. Contract-identical fast-path + sealed-singleton are FUTURE,
    NOT foundation scope -- but the foundation (active/inactive + frame authority) is what enables
    them, so build it clean.
  NEXT: keep cheap-notch (no-dependents) branch in the notch seam spec; park the rest as later.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-20T20:35:39Z
  TYPE: DECISION
  CLAIM: REMOVE the 'versions' concept entirely; replace with active + inactive spells
    (user-proposed, confirmed as the fit). 'versions' was always the half-built active/inactive
    candidate set, so it collapses cleanly: an index has ONE active spell + N inactive candidates;
    there is no separate 'version' concept. Old->new mapping: SpellIndex._spells_in_index ('all ids
    seen') -> the index's active+inactive candidate ids; Spellbook._spell_versions (owned id set) ->
    active ids UNION inactive ids (DERIVED from the two maps, not a third set); _contracted_versions
    -> contracted active+inactive; frame _selected_spell_registry re-derivation -> a thin PUSHED
    aggregate over that union; compiler version_id/spell_version_id -> spell_id (pure rename).
  CRITICAL CORRECTNESS REQUIREMENT: inactive spells STILL EXIST for uniqueness. The frame
    existence check (_check_for_spell/has_spell at bind, aether.py:1252) and the index candidate set
    must span active UNION inactive, NOT just active -- because the reason 'all ids seen' was
    tracked is existence-uniqueness, and a dormant candidate's spell_id is still allocated/taken. If
    the aggregate counted only active, bind could re-mint a duplicate of a sleeping spell. So frame
    aggregate = active UNION inactive; find_index_for_spell must resolve both.
  OPEN (spec detail, not blocker): keying -- active is one-per-index, inactive is many-per-spell_id;
    relationship to existing _spells (index->active) + _lookup_spells.
  EVIDENCE:
  - this session: versions=candidates reframe; _spell_versions/_selected_spell_registry redundancy
  - src/melder/aether/aether.py:1252 (_check_for_spell -- existence check that must span the union)
  IMPACT: This is the foundation's core data model -- no 'versions', just active+inactive per index
    with an existence aggregate over their union. Folds the version-system consolidation + the
    rename + the active/inactive build into ONE coherent change.
  NEXT: spec keying + the existence-spans-union aggregate in the patch artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T20:44:46Z
  TYPE: FACT
  CLAIM: version audit RE-RUN uncapped -- scope is BIGGER than the first (capped) pass, and the
    bucketing gains a 4th category. src/melder: 829+ occ across 80+ files (still capped at 80);
    tests: 374+ across 60+ files; plus system_docs (uncounted). CORRECTION to a prior assumption:
    NEXUS is NOT mostly the spell_id synonym -- the bulk of nexus 'version' is the ACL config
    REVISION/VERSION CHAINS (frame_acl_validator.py:71, frame_acl_view_configuration.py:84,
    frame_acl_{command,codegen}_configuration:36, view/command/codegen ACL profiles ~11 each,
    frame_acl_compiled_access_surface:20). That is a LEGIT, SEPARATE versioning concept (named ACL
    revision chains) -- DO NOT rename it. Buckets now: (A) mutation_research spell versions
    (placeholder, ignore); (B) generic cache/package/CAS version stamps -- keep; (B2 NEW) nexus/acl
    ACL revision versioning -- keep, separate; (C) spell-version-as-spell_id RENAME targets,
    concentrated in aether/spellbook/spell_compiler/conduit (spellbook.py:138, aetheric_frame:31,
    aether:17, conduit:13, compiler symbolic_graph/phases/blueprints/adjacency/requirements_finder/
    topology, lineage_version_conflict_strategy:17, dev_ops/spell_system_states/*). AMBIGUOUS:
    nexus/rift/frame_viewer/* + frame_descriptor_manager (view 'version' could be
    spell_id-in-descriptor OR descriptor revision) -- needs a read to classify before rename.
  EVIDENCE:
  - src/melder count grep (829/80) + token grep (persisted 21KB)
  - src/melder/nexus/acl/frame_acl_validator.py:71 ; nexus/acl/configurations/frame_acl_view_configuration.py:84
  IMPACT: rename scope = aether/spellbook/compiler/conduit + tests + docs; nexus/acl ACL versioning
    EXPLICITLY out of scope (legit separate concept); nexus descriptor/viewer needs classification.
    My earlier 'nexus is probably the same synonym' guess was WRONG -- corrected by the uncapped grep.
  NEXT: classify nexus/rift/frame_viewer + frame_descriptor 'version' (1 read); then codemod scope is set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-22T00:20:00Z
  TYPE: FACT
  CLAIM: Rename-lane PREP fully complete (code + tests + canonical maps + architecture docs).
    version->spell_id landed: 2a/2b spellbook locals, aether.py, snapshot keys, 2 test fixes, and the
    symbolic-graph/validation subsystem (identity_mixing version_ids->spell_ids; contracted_version_drift
    + lineage_version_conflict locals lineage_to_versions/visible_versions/versions -> spell_id forms;
    KEPT lineage_id + the test-coupled diagnostic codes). Canonical maps + architecture docs aligned:
    src_components.md (_spell_versions/_contracted_versions -> _spell_ids/_contracted_spell_ids; version
    caches/registry prose); src_architecture.md (version registries/identifiers/lookups -> selected-spell/
    spell-id); crystallizer "concrete spell version" -> "concrete spell" x3. Graph JSONs already current.
    All remaining doc 'version' is real versioning by design (MutationResearch/package/Python/ACL chains/
    SpellSpace counter/door-stamp/schema). Compiles on 3.10; user runs 3.14t + commits.
  EVIDENCE:
  - tickets/tasks/2026-06-20_spellindex_version_to_spell_id_tier2_rename_task.md (full trail)
  - system_docs/{src_architecture.md, src_components.md} (aligned)
  - src/melder/aether/spellbook/spell_compiler/system/validation/*_strategy.py (renamed locals, py_compile OK)
  NEXT: foundation lane (active/inactive + frame-owned signatures + version-registry consolidation) is the
    remaining build. GATE = architecture_patch + component_patch before code. architecture_patch AUTHORED:
    system_docs/patches/active/2026-06-21_spellindex_active_inactive_frame_signature_foundation_architecture_patch.md
    (knobs Q1 clean-notch, Q2 bind_inactive attach-existing). component_patch is the next artifact, then
    inert slice 1 (add _inactive_spells maps, zero behavior change). User-directed: docs first, no build yet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-28T23:22:16Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: REONBOARD (general_0, synaptic_python_developer) after compaction + user re-onboard.
    Read AGENTS-first + full general/engineer/synaptic SKILLS chain + mission/psychology/gtm +
    boards + src_architecture.md + src_components.md; readable_src_graph.json held on-demand
    (engineer ask-before-read gate; user did not request a full read). Consumed crystal_0 NOTICE
    (2026-06-20): prose-only lineage->index reframe of src_architecture.md + src_components.md
    already landed and was re-verified during onboarding reads; no clobber risk. STALENESS: this
    epic's Notes + the attention_board row lag the actual pre-compaction session, which authored
    both foundation patches and built the active/inactive + frame-consolidation slices and was
    mid the frame full-ref (delete dead _reindex_conduit_spell_ids + make register_conduit_spells
    spell_ids required + update ~10 frame/aether tests). Per compaction rules I will RE-VERIFY
    code state before recording it as fact or editing.
  EVIDENCE:
  - codex/context_compass/mailbox_board.md (crystal_0 message consumed/deleted this pass)
  - src/melder/aether/aetheric_frame/aetheric_frame.py:604-633,727-776
  - codex/context_compass/system_docs/patches/active/2026-06-21_spellindex_active_inactive_frame_signature_foundation_architecture_patch.md
  NEXT: re-verify aetheric_frame + spellbook + frame tests; then finish the full-ref under the patch gate (user go required before code edit).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-28T23:30:42Z
  TYPE: FACT
  CLAIM: Frame-consolidation full-ref LANDED (verified this session). aetheric_frame.py:
    deleted dead _reindex_conduit_spell_ids + its section header; register_conduit_spells now
    REQUIRES spell_ids (dropped the None fallback) and stores the live Spellbook `_spell_ids`
    reference directly; stale reindex docstring/comment refreshed. Tests moved to the live-ref
    contract: 8 register_conduit_spells calls in test_aetheric_frame.py pass an explicit id set;
    the unregister pop-empty assertion flipped to '"c1" not in frame._spell_registry';
    test_aether.py mock assert now expects the 3-arg call. Source has ZERO _reindex refs.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py (register_conduit_spells; reindex removed)
  - tests/unit/melder/aether/test_aetheric_frame.py:316,323,337,338,381,390,397-398,433,434
  - tests/unit/melder/aether/test_aether.py:987
  IMPACT: frame holds only the live owned-id reference -- no per-mutation re-derivation; the O(N)
    reindex tax is gone. Behavior-preserving (frame-authority consolidation, patch slices 1-3 family).
  NEXT: user runs the full 3.14t unit tree (sandbox is 3.10 -> tests NOT RUN here) to confirm green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-29T21:58:14Z
  TYPE: FACT
  CLAIM: general_0 re-onboarded (synaptic_python_developer) + read this epic's full document program at
    user direction ("read all the documents in your epic"): the epic, both foundation patches
    (architecture + component), the map/correction-trail tas
- DATETIME: 2026-06-29T22:43:26Z
  TYPE: FACT
  CLAIM: SpellIndex.update() reduced to a pure id repoint (user-directed:
    "spellindex update needs to become just an ID Update"). spell_index.py:
    removed the _spells_in_index history set entirely (out of __slots__,
    __init__, cleanup); update() now sets only _selected_spell_id under the
    write lock (no .add); spells_in_index() returns {selected_spell_id};
    has_spell(id) is (id == selected_spell_id); both are now lock-free reads
    matching the selected_spell_id property contract. Kept _spells_in_index as
    a read-only @property returning {selected_spell_id} so the 8 external
    attribute-style readers keep working with correct single-active semantics
    and ZERO edits to those files. Pre-checked: the only mutators of
    _spells_in_index were ever inside spell_index.py (.add/.clear); all
    external uses are read-only iteration/membership.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py (update / spells_in_index / has_spell / _spells_in_index property; __slots__ / __init__ / cleanup)
  - read-only external readers, unchanged, now single-active: spellbook.py:693,2339,2512,2563,2587,3419; conduit_ward/contract/details.py:155; conduit_ward.py:1929
  VALIDATION: sandbox py_compile OK (3.10); standalone behavioral test PASS
    against the actual edited file (repoint carries no history; hash stable
    across repoint; identity by ULID; cleanup idempotent + post-clean raises).
    Full 3.14t unit tree NOT RUN here (sandbox is 3.10) -- user runs to confirm green.
  IMPACT: the index now holds no version history -- "the index organizes, the
    spell_id resolves" holds literally. update() has exactly one caller
    (_apply_notch, spellbook.py ~2827). transfer_of_ownership does NOT depend on
    update() or the history set (only _enumerate_borrowers:500 read has_spell,
    which already has the selected_spell_id fallback) -- no transfer change
    required for this directive.
  NEXT: (optional, cross-file -> patch gate) migrate the 8 _spells_in_index
    readers to spells_in_index() and drop the compat property; then build the
    _apply_notch seam that consumes the id-only update.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: f07f4e5d5c2c

- DATETIME: 2026-06-29T23:30:28Z
  TYPE: FACT
  CLAIM: REGRESSION REVERTED + multi-member model re-confirmed from source (user
    correction 2026-06-29: "there can be multiple spells in the index, it's NOT a
    history, it's an index"). My prior-session spell_index.py edit (collapse
    _spells_in_index -> {selected_spell_id}; update() id-only) was WRONG and left
    the file non-compiling (truncated); fully reverted to committed HEAD via
    git show HEAD -> /tmp -> verify -> copy (0 diff vs HEAD, compiles, NUL=0,
    400 lines). HEAD SpellIndex IS genuinely multi-member: _spells_in_index is a
    SET seeded {initial_id} and grown by update() via .add(new_id);
    selected_spell_id is just the ACTIVE member. Tests pin it
    (test_spell_index.py:163 spells_in_index()=={"v1","v2","v3"}).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py (HEAD: _spells_in_index set; update() .add; spells_in_index()/has_spell())
  - tests/unit/melder/spellbook/bind/test_spell_index.py:163-219
  - git e9dcedd38 removed the _members OBJECT store, NOT the _spells_in_index id-set
  IMPACT: model = ONE active member (live Spell object + resolution-pool entry)
    PLUS a SET of member ids tracked for existence/ownership. Resolution pools
    _spells_by_id/_spell_id_pool hold only the active id (spellbook.py:948,992),
    so meld-by-id resolves only the active (meld.py:1307-1318). The member SET
    drives existence/ownership: frame.find_index_for_spell (aetheric_frame.py:687
    spell_id in index.spells_in_index()), find_conduit_id_for_spell (913
    index.has_spell), spellbook per-conduit id caches (spellbook.py:693,2339,2512,
    2587,3419 iterate _spells_in_index), Detail.has_spell (details.py:155). bind
    warms _spell_ids from the member set (spellbook.py:3417-3424); transfer flips
    only the active id (transfer:1330,1355). Collapsing the set breaks every
    by-member-id lookup.
  CONFLICT: this epic body's "CORRECTED MODEL (user-confirmed 2026-06-20):
    single active spell, NOT a container of members, no multi-member" CONTRADICTS
    the committed code + tests + the user's 2026-06-29 multi-member correction.
    The 2026-06-20 single-spell direction is stale and must be reconciled.
  NEXT: user confirms multi-member is authoritative + names the concrete next
    change (the id SET is restored by the revert; is more wanted, e.g. dormant-
    member object homes per the active/inactive notes?).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
  prompt_id: 65dd142d960c

- DATETIME: 2026-06-29T23:41:38Z
  TYPE: FACT
  CLAIM: FIX LANDED (user-directed "fix the set", NOT a revert). spell_index.py is the
    lean working version with _spells_in_index restored as a GENUINE member set:
    __slots__ carries it; __init__ seeds {initial_id}; update(new_id) sets
    _selected_spell_id AND _spells_in_index.add(new_id) (pure id+set, NO spellbook
    propagation -- that belongs to the notch seam); spells_in_index() returns
    set(self._spells_in_index); has_spell() is membership; cleanup clears+dels it.
    HEAD attachment apparatus (_attach_owner/_attach_contracted/_owner_spellbook/
    _contracted_spellbooks/_selected_spell) NOT reintroduced -- grep confirmed ZERO
    external callers (dead at HEAD).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py (230 lines)
  - grep: attachment methods referenced only within spell_index.py (no external callers)
  VALIDATION: sandbox py_compile OK (3.10); standalone behavioral test PASS --
    SI("v1")->update("v2")->update("v3") => spells_in_index()=={"v1","v2","v3"},
    selected="v3", hash stable, cleanup idempotent + post-clean raises. Matches
    test_spell_index.py:163. Full 3.14t unit tree NOT RUN here (sandbox is 3.10).
  IMPACT: multi-member set is back on the resolution surface; the by-member lookups
    (frame.find_index_for_spell/find_conduit_id_for_spell, spellbook per-conduit id
    caches, Detail.has_spell) work again. update() is now the pure id+set repoint;
    map propagation belongs to _apply_notch (unbuilt).
  NEXT: build the _apply_notch seam to own the spellbook map propagation that update()
    no longer does, on the multi-member model; user runs the 3.14t tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
  prompt_id: 2ae9ffb7c647

- DATETIME: 2026-06-30T09:02:21Z
  TYPE: FACT
  CLAIM: _apply_notch WIRED (owner-side, user-directed). Replaced the stub with the
    active/inactive swap using the BUILT methods: outgoing -> _deactivate_owned_spell
    (parks off the 4 active maps, keeps _spell_ids existence) + outgoing.
    _cleanup_creation_context() (door-kill: bumps door epoch so the warm fast-door
    misses); incoming -> _reactivate_owned_spell (promote from _inactive_spells into
    the 4 active maps); spell_index.update(new_id) (pointer + member set);
    frame.update_lookup(spell._key, new_id) (repoint the binding signature old->new);
    _spell_system_states.register_index (gated + dirty -> lazy meld-time revalidation).
    Swap is atomic under self._lock; the notch mediator transaction seals the scope.
    Precondition: incoming spell parked in _inactive_spells (bind_inactive or prior
    notch). NOTE: the build correctly diverged from component_patch step-1
    ("_unregister_owned_spell_id" discards _spell_ids -> drops existence); the
    dedicated _deactivate_owned_spell keeps existence across the inactive window.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2797 (_apply_notch rewrite); 1309/1364 (de/reactivate owned); 1417/1484 (contracted pair)
  - src/melder/aether/aetheric_frame/aetheric_frame.py:738 (update_lookup, doc "notch")
  - system_docs/patches/active/2026-06-21_..._component_patch.md (slice 6 _apply_notch step list)
  VALIDATION: sandbox py_compile OK (3.10). NOT RUN: full 3.14t tree (component_patch
    slice-6 test: notch promote -> cold+warm meld sees new spell, meld(old_id) misses,
    fast-door rebuilds, notch-back works).
  IMPACT: owner-side notch complete. DEFERRED (next slice): contracted/borrower
    fan-out (owner-driven, cross-conduit, under the same seal) -- a notch on a SHARED
    index does NOT yet update borrowers' contracted maps. DEPENDENCY: bind_inactive
    (how a candidate gets parked into _inactive_spells) -- verify it is built.
  NEXT: confirm bind_inactive exists; then wire the contracted fan-out; user runs 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: a3265836129a

- DATETIME: 2026-06-30T09:12:15Z
  TYPE: FACT
  CLAIM: bind_inactive SET UP (slice 5, user-directed) -- 3 additive pieces, all
    compile (3.10): (1) SpellIndex.add_member(spell_id) -- adds to _spells_in_index
    WITHOUT selecting (behavioral test PASS: add_member after update keeps selected,
    adds the member); (2) Spellbook.bind_inactive(*, spell_index, spell) -- parks the
    spell in _inactive_spells, _spell_ids.add (existence via the live-ref the frame
    reads), spell_index.add_member; touches NO id-pools / _spells[index] / signature;
    guards already-active and already-staged; under self._lock. (3) Conduit.bind_inactive
    facade -> spellbook. Adapted patch slice-5 to BUILT reality: existence via _spell_ids
    (the frame _selected_spell_registry live-ref), NOT the unbuilt frame.incr_spell_id
    refcount aggregate.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py (add_member)
  - src/melder/aether/spellbook/spellbook.py (bind_inactive, near notch_spell)
  - src/melder/aether/conduit/conduit.py (bind_inactive facade)
  VALIDATION: py_compile OK all 3 (3.10); add_member behavioral test PASS. NOT RUN:
    full 3.14t end-to-end (bind -> bind_inactive stage -> notch promote -> cold+warm
    meld sees new, meld(old_id) misses, notch-back), per component_patch slice 5+6.
  IMPACT: notch is now exercisable end-to-end. Candidate staging + promotion both exist.
  DEFERRED: contracted/borrower fan-out for a notch on a SHARED index (cross-conduit).
  NEXT: user runs the 3.14t tree (bind_inactive + notch integration); then borrower fan-out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: dc9e292969e5

- DATETIME: 2026-06-30T09:28:59Z
  TYPE: FACT
  CLAIM: bind_inactive REVISED to a bool flag on bind (user correction: "it should be a
    bool on bind, not a method"). REMOVED the standalone Spellbook.bind_inactive method +
    Conduit.bind_inactive facade. ADDED bind_inactive: bool = False to public bind AND
    _bind_under_active_transaction (threaded both call sites). When True, the bind
    registration routes the setters to the INACTIVE pathing: SpellIndex.add_member (record
    the id as a member, no active select) + Spellbook parks the spell in _inactive_spells +
    _spell_ids.add (existence); SKIPS claim_lookup / _lookup_spells / _spells[index] /
    _register_owned_spell_id. The spell keeps its own minted index, inert/unmeldable until
    notch_spell promotes it. SpellIndex.add_member retained (the index inactive setter).
    Supersedes the prior 2026-06-29 "bind_inactive SET UP -- 3 additive pieces" note.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3366 + 3440-3452 (flag + inactive branch); 3540/3611/3632 (public bind sig + 2 call sites)
  - src/melder/aether/spellbook/bind/spell_index.py (add_member)
  VALIDATION: py_compile OK (3.10). NOT RUN: full 3.14t end-to-end -- bind(bind_inactive=True)
    stages inert (not in _spells/id-pools/lookup) -> notch_spell promotes -> cold+warm meld.
  IMPACT: bind_inactive is the documented bool flag on bind; no separate method/facade.
  NEXT: user runs the 3.14t tree (bind_inactive + notch integration); then contracted fan-out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: f12d3c2f2aa0

- DATETIME: 2026-06-30T10:08:13Z
  TYPE: FACT
  CLAIM: add_to_spell_index FULL CYCLE coded (user-directed; seam-side only -- "trust the
    mediator", linking/borrower fan-out deferred). 5 pieces, all compile (3.10):
    (1) SpellIndex.remove_member(spell_id) -- discard from _spells_in_index, leaves the
    selected pointer (unit test PASS: remove leaves selected, idempotent).
    (2) Spellbook.add_to_spell_index (public) -- admits ChangeTransactionType.ADD_TO_INDEX
    (mirrors notch_spell) -> seam.
    (3) Spellbook._apply_add_to_index -- ownership gate (spell._spellbook is self) + INACTIVE
    guard (spell_id in _inactive_spells, else "notch away first") + membership-only move
    (source_index.remove_member / target_index.add_member / spell.spell_index=target, under
    self._lock) + if source emptied -> destroy. id-keyed state (_inactive_spells/_spell_ids/
    id-pools/nexus/door/creations) travels with the spell untouched.
    (4) Spellbook._destroy_spell_index -- IDEMPOTENT local teardown: _spells.pop +
    _lookup_spells.pop(binding_key) (under lock); frame.release_lookup(binding_key);
    aether._remove_single_spell_index(owner_conduit_id, index, frame); states.unregister_index
    (closure/risk, idempotent); index.cleanup(). Each step no-ops when the index was never
    registered there (inactive-only index touches almost none).
    (5) Conduit.add_to_spell_index facade.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py (add_to_spell_index / _apply_add_to_index / _destroy_spell_index, before begin_transaction)
  - src/melder/aether/spellbook/bind/spell_index.py (remove_member)
  - src/melder/aether/conduit/conduit.py (add_to_spell_index facade)
  - unregister_index idempotency: spell_system_states.py:682-770
  VALIDATION: py_compile OK all 3 (3.10); remove_member unit PASS. NOT RUN: full 3.14t
    (add_to_spell_index move + source-index destroy end-to-end).
  IMPACT: move an owned inactive spell between indexes; emptied source index destroyed across
    spellbook maps + frame signature/registry + spell-system states + the index object.
  DEFERRED: shared/contracted-index borrower fan-out on destroy (the linking case);
    remove_from_spell_index (reuses _destroy_spell_index).
  NEXT: user runs 3.14t; then remove_from_spell_index; then the linking/borrower fan-out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: 27b686b76c82

- DATETIME: 2026-06-30T10:14:29Z
  TYPE: FACT
  CLAIM: remove_from_spell_index coded (user-directed; seam-side, mediator trusted, linking
    deferred). CORRECTION to a prior note: remove does NOT reuse _destroy_spell_index -- it
    never empties the source (sole-member = no-op; 2+ members = source survives), so NO index
    is destroyed; instead it MINTS a fresh inactive index for the separated spell. Pieces:
    (1) Spellbook.remove_from_spell_index (public) -> admits ChangeTransactionType.
    REMOVE_FROM_INDEX (mirrors add_to_spell_index) -> seam.
    (2) Spellbook._apply_remove_from_index -- gates: spell._spellbook is self (ownership) +
    spell_id in _inactive_spells (inactive) + spell.spell_index is source_index (membership);
    if source_index.spells_in_index() == {spell_id} -> no-op (already its own index); else
    new_index = SpellIndex(initial_id=spell_id); source_index.remove_member(spell_id);
    spell.spell_index = new_index. Under self._lock. id-keyed state untouched (spell stays
    inactive owned).
    (3) Conduit.remove_from_spell_index facade.
    IMPORT CHANGE: promoted SpellIndex from TYPE_CHECKING-only to a runtime import in
    spellbook.py (line 25) so SpellIndex(initial_id=...) resolves at runtime -- py_compile
    would NOT have caught the NameError. No cycle (spell_index.py has no runtime path back to
    spellbook; already loaded via bind.py).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:25 (runtime import); 3024 (remove_from_spell_index); 3077 (_apply_remove_from_index); 3140 (mint)
  - src/melder/aether/conduit/conduit.py (remove_from_spell_index facade)
  VALIDATION: py_compile OK both (3.10). NOT RUN: 3.14t -- also re-verify the promoted SpellIndex
    import imports cleanly (no cycle) on the real interpreter.
  IMPACT: full index-operation set now exists: bind, bind(bind_inactive=True), notch_spell,
    add_to_spell_index (+ index destroy), remove_from_spell_index.
  DEFERRED: shared/contracted-index borrower fan-out (linking) -- still the one open piece, hits
    add's _destroy_spell_index and (eventually) notch.
  NEXT: user runs 3.14t across the whole set; then the linking/borrower fan-out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: ec46822e3d83

- DATETIME: 2026-06-30T11:08:56Z
  TYPE: FACT
  CLAIM: add/remove model LOCKED (user clarification) + cleanup_spell added. Model: add_to_
    spell_index and remove_from_spell_index operate ONLY on an INACTIVE spell -- to move the
    ACTIVE one the caller calls notch_spell FIRST (separately) to make a different member
    active (which deactivates the one being moved); NO notch_to param. add_to_spell_index was
    already correct (require inactive; 1-member -> move + destroy; 2+ -> move + survive).
    CHANGES this pass:
    (1) remove_from_spell_index sole-member case: NO-OP -> ERROR ("only member of its index;
    use cleanup_spell to dispose it instead"). Docstrings updated.
    (2) NEW Spellbook.cleanup_spell(spell) + Conduit.cleanup_spell facade -- full disposal:
    ownership gate; guard (cannot dispose the ACTIVE member of a MULTI-member index -> notch
    first; sole member always disposable); active path -> _spells.pop + _lookup_spells.pop +
    _unregister_owned_spell_id (id-pools/_spell_ids/Nexus) + release_lookup + _unregister_spell_
    with_risk_manager; inactive path -> _inactive_spells.pop + _spell_ids.discard; then
    index.remove_member; extract_spell_creations (conduit store); _cleanup_creation_context
    (door); _destroy_spell_index if emptied; spell.cleanup() last.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py (cleanup_spell; remove sole-member error)
  - src/melder/aether/conduit/conduit.py (cleanup_spell facade)
  - Spell.cleanup tears down only the spell object's own fields: spell.py:495-525
  - extract_spell_creations: creations/creations.py:280 (same call transfer uses)
  VALIDATION: py_compile OK both (3.10). NOT RUN: 3.14t.
  FLAGS (verify/follow-up): (a) extract_spell_creations lifts creations off the store, but
    whether the extracted instantiated objects need their disposal methods explicitly run is a
    verify-on-3.14t item. (b) cleanup_spell is NOT mediator-sealed (no cleanup transaction type
    exists) -- map mutations run under the Spellbook lock; a CLEANUP strategy is the mediator
    follow-up (mediator_builder_0). (c) small unsealed window between computing index_emptied
    and _destroy_spell_index.
  NEXT: user runs 3.14t across notch/bind_inactive/add/remove/cleanup_spell; then the linking
    borrower fan-out; then (maybe) a cleanup_spell mediator strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: 7d0b8265c169

- DATETIME: 2026-06-30T11:31:00Z
  TYPE: FACT
  CLAIM: Revalidation + active-switch wired via the SPELL-OWNED helper (user-directed: "the
    SPELL has the methods, don't invent"). Replaced the compute_impact_closure +
    mark_conduit_dirty I had added in notch AND cleanup_spell with spell.invalidate_spell()
    (spell.py:1002) -- it clears the creation context, sets resolution_complete=False/
    resolution_required=True, and calls SpellSystemStates.mark_structural_change(spell_index).
    _active switch (spell.py:303, "flipped by notch/disable") now flipped in
    _deactivate_owned_spell (False) + _reactivate_owned_spell (True) [so notch deactivates the
    previous + activates the new], bind_inactive branch (False), and cleanup_spell active path
    (False). add/remove move INACTIVE spells only, so _active stays correct there.
    bind_inactive: CONFIRMED there is NO method (grep def bind_inactive = none) -- it is only
    the bind(..., bind_inactive=False) bool modifier, as agreed.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2865 (notch invalidate_spell), 3235 (cleanup invalidate_spell), 1363/1417/3234/3839 (_active flips)
  - src/melder/aether/spellbook/spell.py:1002 (invalidate_spell), 303 (_active)
  VALIDATION: py_compile OK (3.10). NOT RUN: 3.14t.
  OPEN: (a) conduit Creations STORE instance-disposal in cleanup_spell still pending the right
    primitive (extract is move-not-dispose). (b) linking/borrower fan-out still deferred.
  NEXT: user runs 3.14t; resolve creations-store disposal; then linking fan-out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
  prompt_id: f72cb2b66e65

---

## Note — 2026-06-30 — Dynamic-mode gating + dependent-recheck experiment

**Gating (implemented, conduit-side, verified py_compile + NUL=0):**
`Conduit.notch_spell`, `Conduit.add_to_spell_index`, `Conduit.remove_from_spell_index`
each now raise `RuntimeError("Dynamic environment is not enabled. ...")` when
`not self.__dynamic_environment__`, matching the existing per-method gate pattern
used elsewhere in `conduit.py` (e.g. set_policy, ownership transfer, link). Placed
right after `check_cleaned()`, before the `_spellbook is None` check. `cleanup_spell`
facade left ungated for now (its active path already requires dynamic via
`spell.invalidate_spell()`); flagged as an open question for the user.

**Two control planes (evidence):**
- SpellSystemStates: `invalidate_spell` -> `mark_structural_change` flags ONLY the
  changed index (spell_system_state.py:469-470 "direct change to the index itself,
  not downstream impact"). Dependent fan-out = `compute_impact_closure`, called only
  in `unregister_index` (spell_system_states.py:720) and transfer (633).
- ChangeControlManager: meld gate reads `is_root_dirty` -> `_dirty_roots_by_conduit`
  (meld.py:749). Populated by `notify_spell_changed` (CCM:1362) via `component_of`
  (built by compiler phase 5 `rebuild_component_of`). `notify_spell_changed` has NO
  engine caller in src — existing tests call it manually
  (test_conduit_component_meld_gating.py:135).

**Open empirical question (the user's bet):** does `cleanup_spell(dependency)` force
its dependents to recheck? cleanup destroys the index -> `unregister_index` ->
`compute_impact_closure`, which DOES walk `direct_dependents` on the SpellSystemStates
plane. Whether that reaches the CCM plane meld gates on is the open question.

**Experiment (built, not run — sandbox is Py3.10, melder needs 3.14t):**
`tests/experimentation/test_cleanup_dependency_forces_dependent_recheck_experiment.py`
Dynamic mode: Root(dep1,dep2,dep3) + OtherRoot(dep1); compile both (phase 5 builds
both planes); `cleanup_spell(dep1)`; observe dependents on SSS plane
(`system_state.validity`) and CCM plane (`is_root_dirty`) with NO nudging; then a
CONTROL that manually calls `notify_spell_changed(dep1_id)` to prove the CCM fan-out
works when triggered. Prints A/B/D/E snapshots + an F verdict. Asserts only the
setup invariant (graph built), not the contested outcome. **Run on 3.14t:**
`python -m pytest tests/experimentation/test_cleanup_dependency_forces_dependent_recheck_experiment.py -q -s`

---

## Note — 2026-06-30 — cleanup_spell fix (invalidate-first) + experiment run 1

**Experiment run 1 results (user, 3.14t):** Phase A confirmed the dependency graph
is built on BOTH planes — `dep1_sss_direct_dependents` = {root_index, other_root_index};
CCM `component_of[dep1_id]` = {root_id, other_root_id}. Baseline both roots valid,
`is_root_dirty` False. Phase C FAILED: `cleanup_and_remove_spell` raised
"could not resolve the requested local spell".

**Root cause:** my `cleanup_spell` hand-rolled the map teardown (`_unregister_owned_spell_id`
etc.) and THEN called `spell.cleanup()`, which routes to the authoritative
`cleanup_and_remove_spell` (spell.py:458-460 when `_spellbook_cleanup` is False).
That canonical path re-looks-up the spell in `_spells_by_id` (spellbook.py:542) —
already removed by my hand-rolled teardown — so it raised. Double-teardown.

**Fix (cleanup_spell, via FILE TOOLS):** restructured to the user's required order —
INVALIDATE FIRST (`spell.invalidate_spell()` while index + edges still exist), THEN
clean up. Active sole-member path now delegates to the authoritative
`cleanup_and_remove_spell` (which sets `_spellbook_cleanup=True` before
`spell.cleanup()`, so no re-entry; its `unregister_index` -> `compute_impact_closure`
fans the dependent closure). Inactive-member path drops just that member, destroys
the index only if it empties, sets `_spellbook_cleanup=True`, then `spell.cleanup()`.
Multi-member active guard unchanged. Docstring updated. Method ast-parses clean, NUL=0.

**TOOLING HAZARD (important):** the bash mount serves a TRUNCATED copy of large files —
`spellbook.py` reads as 5134 lines cut mid-statement at `conduit_i` (real file is
5141 lines, closes cleanly; file-tool Read + the user's successful import both prove
it). So `bash` codemods that read+rewrite spellbook.py would write back truncated
corruption (the py_compile gate caught it once). RULE: edit spellbook.py (and other
>~200KB files) with the FILE TOOLS (Read/Edit), not bash read/rewrite. Bash is fine
for reads of regions before the truncation offset and for small files (conduit.py
edits worked).

## Note — 2026-06-30 — experiment run 2 (PASS) — result

After the cleanup_spell fix, run 2 passed. Decisive observations:
- **SpellSystemStates plane: dependents auto-flagged.** root_validity and
  other_root_validity both flipped `valid` -> `gated` after `cleanup_spell(dep1)`
  with NO manual nudging. This is cleanup -> `cleanup_and_remove_spell` ->
  `unregister_index` -> `compute_impact_closure` walking `direct_dependents` ->
  `mark_transitively_dirty`. So invalidation DOES propagate to dependents here.
- **CCM plane (meld's is_root_dirty gate): NOT auto-flagged.** `is_root_dirty(root)`
  and `(other_root)` stayed False after cleanup; `ccm_dirty_roots` empty. Only the
  Phase E control (`notify_spell_changed(dep1_id)`) flipped both to True — proving
  the CCM fan-out works but is not driven by cleanup/invalidate.
- **meld(root) after cleanup:** failed with `SpellCrafter Phase 3: no DI candidate
  found for parameter 'dep1'`. NOTE: in this run root was compiled (`run_all_phases`)
  but never melded/cached before cleanup, so this is the first meld and fails at DI
  because dep1 is physically gone — it does NOT cleanly isolate "gated forces a
  re-check of an already-cached dependent". A tighter run would meld(root) BEFORE
  cleanup, then re-meld after, to prove the cached dependent re-checks vs returns stale.

**Verdict:** user's bet holds on the validity plane — cleanup auto-gates dependents.
Open design choice: is the SSS `gated` signal sufficient, or should invalidate/cleanup
also drive `notify_spell_changed` so the CCM `is_root_dirty` meld-gate hard-rejects
dependents with a "dirty root" error before DI? Deferred to user.

## Note — 2026-06-30 — change reasons for notch + cleanup

Added two `SpellStateChangeReason` members (appended logically; no `.value`
serialization exists anywhere, so member order is safe):
- `selected_different_spell` — notch repointed the index to a different existing
  member (general selection, explicitly NOT a mutation, so not `mutation_promoted`).
- `cleaned_up_spell` — owning spell disposed via cleanup_spell (no `disposed`/
  `cleaned` existed in this enum; `cleaned` is only on SpellValidity).

Wiring:
- `cleanup_spell` (spellbook.py): `spell.invalidate_spell(change_reason=
  SpellStateChangeReason.cleaned_up_spell)`.
- notch signature extended end-to-end to carry the reason (default
  `selected_different_spell`): `Conduit.notch_spell` -> `Spellbook.notch_spell`
  -> `Spellbook._apply_notch` -> `spell.invalidate_spell(change_reason=...)`.
  Backward-compatible (param defaulted), so existing callers are unaffected.
- Runtime import of `SpellStateChangeReason` added to spellbook.py and conduit.py
  (the enum is a leaf module; spell.py already imports it the same way, so no
  cycle). Used as a signature default, hence runtime not TYPE_CHECKING.

Note: the reason tags the DIRECTLY-changed index. Dependents ("the other spells")
are still flagged by `compute_impact_closure` -> `mark_transitively_dirty`
(`impacted_by_dependency` / `dependency_changed`) — unchanged. For cleanup the
source index is unregistered right after, so its `cleaned_up_spell` tag is brief;
for notch the index survives so `selected_different_spell` persists on its state.

Verification: enum py_compiles; spellbook.py (notch_spell, _apply_notch,
cleanup_spell) and conduit.py (notch_spell facade) changed regions ast-parse clean
with NUL=0. Full-file bash py_compile not possible (large-file mount-read
truncation on spellbook.py/conduit.py); file-tool edits wrote the real files.

## Note — 2026-06-30 — ownership review of add/remove + target-ownership guard

Questions raised: (1) removing an active member must notch the index; (2) add/remove
must only act on indexes we own.

(1) Notch-on-active-removal — already enforced. Both `_apply_add_to_index` (2978) and
`_apply_remove_from_index` (3142) reject an active spell ("is active; notch away before
moving it"); `cleanup_spell` has the same multi-member active guard. So removing an
active member is impossible without first notching the index to a surviving member
(or, for a sole member, cleanup destroys the index — nothing to notch to). No change.

(2) Ownership:
- remove_from_spell_index: ALREADY safe. Checks `spell._spellbook is self` (3132) AND
  `spell.spell_index is source_index` (3152) -> source index is provably the owned
  spell's own index. It mints a fresh index for the separated spell (no foreign target).
- add_to_spell_index: HAD A GAP. It checked spell ownership (covers the source index)
  but never checked the TARGET. FIXED: added `if target_index not in self._spells:` ->
  raise. A foreign/borrowed index can't be a key in our `_spells`, so this rejects the
  cross-ownership splice. Chose the local `_spells` check (mirrors remove's local
  spell<->index<->spellbook chain) over reaching into SpellSystemStates'
  `_index_owner_spellbook_id`. Caveat: this treats "owned" as "owned ACTIVE index";
  an owned inactive-only index would be rejected as a target — acceptable since a valid
  consolidation target has a live active member. Docstrings (public contract + seam
  Steps/Raises) updated. ast-parse clean, NUL=0.

Open: if inactive-only owned indexes must be valid add targets, switch the guard to the
SpellSystemStates owner record (owner_spellbook_id == self._id) instead of `_spells`.

### Correction — add_to_index target-ownership guard

Replaced the earlier `target_index in self._spells` guard with the correct O(1)
owned-id check: `if target_index.selected_spell_id not in self._spell_ids: raise`.
`self._spell_ids` (spellbook.py:266, `Set[str]`, ALL owned ids active+inactive) is
the canonical ownership signal — same notion used elsewhere. This is a single set
membership (no map-key/object check), and it also removes the prior "owned
inactive-only index rejected" caveat since `_spell_ids` covers inactive ids too.
Docstrings updated to match. ast-parse clean.

## Note — 2026-06-30 — efficiency review of notch/add/remove/cleanup

Fixed: four spots built a full set COPY via `SpellIndex.spells_in_index()` only to
test emptiness or sole-membership. Added two O(1) helpers on SpellIndex that test the
live `_spells_in_index` set directly (no copy, no set construction):
- `is_empty()` -> `not self._spells_in_index`
- `is_sole_member(spell_id)` -> `len(members) == 1 and spell_id in members`
Replaced: `_apply_add_to_index` source-empty (was `not ...spells_in_index()`),
`_apply_remove_from_index` sole-member (was `... == {spell_id}`), `cleanup_spell`
is_sole + index_emptied. Also moved `binding_key`/`owner_conduit_id` in cleanup_spell
into the inactive branch (the only place they're used; the active path delegates to
cleanup_and_remove_spell which recomputes them).

Confirmed clean (O(1) dict/set/identity, no copies): notch seam (self._spells.get),
add/remove/cleanup ownership + inactive + membership gates (`in self._inactive_spells`,
`selected_spell_id in self._spell_ids`, `is X`).

FLAG (not changed — needs a decision): `_apply_notch` has no explicit ownership/
membership gate the way add/remove/cleanup do. The promoted spell is implicitly owned
(it must be parked in this spellbook's `_inactive_spells` for `_reactivate_owned_spell`),
but nothing asserts `spell` actually belongs to `spell_index` — `spell_index.update()`
would just add it. Candidate guard: assert `spell.spell_index is spell_index` (or
`spell_index.has_spell(spell.spell_id)`) before promoting.

### Correction — retract the "notch lacks a gate" flag

That flag was wrong. All three ops admit a mediator change-control transaction in
their PUBLIC method before the `_apply_*` seam runs: `notch_spell` -> NOTCH,
`add_to_spell_index` -> ADD_TO_INDEX, `remove_from_spell_index` -> REMOVE_FROM_INDEX
(each does start_transaction -> _apply -> end_transaction). The seam runs inside that
held/sealed window — the transaction IS the gate, and notch has it exactly like the
other two. I mistook the inline `spell._spellbook is self` line (present in add/remove
seams, an argument-validation detail) for "the gate." Re-validating inside the
mediator-sealed window would be re-inventing protection the mediator already provides
("trust the mediator"). No change to notch.

## Note — 2026-06-30 — linking investigation (relation to index ops)

Linking: `ConduitWard._link` -> `_create_new_contract` creates one symmetric `Contract`
stored in BOTH wards' `_contracts` (contract_id -> Contract), and calls
`_spellbook._create_link_contract(peer_id)` on both spellbooks to make per-peer
contracted buckets. `_add_spell_to_contract` (conduit_ward:1576) contracts the
SpellIndex LINEAGE (current version id is only the initial reference; "on mutation the
lineage advances and lookups resolve to the new version").

Borrower-side mirror on Spellbook (keyed by owner conduit_id): `_contracted_spells`
(active index->spell, 270), `_lookup_contracted_spells` (271), `_contracted_spells_by_id`,
`_inactive_contracted_spells` (parked, 274), `_contracted_spell_ids` (existence, 273).
Park/unpark primitives EXIST: `_deactivate_contracted_spell` (1420) /
`_reactivate_contracted_spell` (1487) — exact mirrors of the owned versions, operating
on the contracted maps + shared `_spell_id_pool`; they do NOT touch the shared
SpellIndex or the owner framewide lookup.

Relation to my index ops = the DEFERRED borrower fan-out. My notch/add/remove/cleanup/
destroy are OWNER-SIDE ONLY (the `_apply_notch` + `_destroy_spell_index` docstrings say
so). For a SHARED index:
- notch A->B: borrowers still hold A active in `_contracted_spells[owner_cid][index]`,
  so they resolve STALE A. Fan-out: per borrower `_deactivate_contracted_spell(owner_cid,A)`
  + `_reactivate_contracted_spell(owner_cid,B)`.
- cleanup/destroy: borrowers hold contracted copies keyed by the dead index -> dangling.
  Fan-out: drop from each borrower's contracted maps + clean copies.
- add/remove: membership change on the shared index; borrower view may need sync.
Enumeration is owner-conduit-driven via ward `_contracts` -> peer spellbooks. Must run
under the SAME mediator seal (cross-conduit; the seal must claim borrower surfaces too).

KEY OPEN QUESTION for the build: `_reactivate_contracted_spell` needs B already PARKED in
the borrower's `_inactive_contracted_spells`. If only A was contracted at link time, the
borrower has no B copy — the notch fan-out must first CONTRACT the new version B to the
borrower (mint the copy) before it can activate it. This is the lineage-advance path that
`_add_spell_to_contract` hints at and the next slice must wire.

## Note — 2026-06-30 — borrower fan-out PLAN (proposed, not built)

Read: Contract (conduit_ward/contract/contract.py) = `_ward_a/_ward_b` + per-ward
`_details_a/_details_b` (spell_id->Detail); `_get_peer`, `_check_if_exists`,
`_find_spell_in_ward`. Ward enumeration: `_get_links()` (1061, all peer conduits from
`_initiated_index`+`_received_index`), `_find_contract_by_id(cid)` (837),
`_get_spell_contract_keys(spell)` (1811). Conduit txn: `begin_transaction` (2334)
already routes LINK/UNLINK/TRANSFER via mediator + BIND-delegates to spellbook;
`end_transaction` (2475). Spellbook borrower primitives ALREADY EXIST:
`_deactivate_contracted_spell`/`_reactivate_contracted_spell` (1420/1487), link-agnostic
(take conduit_id+spell). Proposed: keep spellbook link-agnostic (owner `_apply_*` +
contracted activate/inactivate); put the link-walk in a Conduit method (`_get_links` ->
contract-covers-spell -> peer._spellbook.<contracted op>); MOVE the NOTCH/ADD/REMOVE
txn admission UP from spellbook to conduit so one mediator seal spans owner+borrowers.
OPEN: notch A->B needs B already parked in borrower; if only A contracted, fan-out must
lazily contract B first (via _add_spell_to_contract lineage path). Enumerate by
binding/contract key (stable across versions), not the version id.

### Correction — transaction ownership is a principle, not an option

The spellbook must own ZERO transactions for these ops. Responsibility split:
- Spellbook = execution only: `_apply_notch`/`_apply_add_to_index`/`_apply_remove_from_index`
  (owner local) + `_activate_contract_spell`/`_inactivate_contract_spell` (borrower local).
  NO mediator.start/end anywhere in the spellbook for these. The current public
  `notch_spell`/`add_to_spell_index`/`remove_from_spell_index` (which admit the txn) get
  stripped down to the `_apply_*` seams.
- Conduit = transaction owner + orchestrator: admits NOTCH/ADD_TO_INDEX/REMOVE_FROM_INDEX
  (it already has `_get_required_transaction_mediator()`, `_transaction_identity`,
  begin/end_transaction), then drives owner `_apply_*` + the borrower fan-out under the
  one seal. Conduit becomes the SOLE txn entry for these ops.
Note: same principle implies BIND (currently conduit delegates to spellbook.begin_transaction)
should eventually flip too — keeping this slice to the 3 index ops unless told otherwise.

## Note — 2026-06-30 — built: conduit fan-out + spellbook contracted execution methods

Scope: NOT migrating transactions (other agent does that). Built the execution +
orchestration so the migration can drop in.

Spellbook (link-agnostic execution, take conduit_id+spell_id only, no conduit/ward refs):
- `_inactivate_contract_spell(conduit_id, spell_id)`: resolve this book's active borrowed
  copy via `_contracted_spells_by_id[conduit_id][spell_id]`; if present, delegate to
  `_deactivate_contracted_spell`. Idempotent no-op otherwise.
- `_activate_contract_spell(conduit_id, spell_id)`: mirror via `_inactive_contracted_spells`
  -> `_reactivate_contracted_spell`. Idempotent.

Conduit (owns link knowledge):
- `_deactivate_borrowed_spell(spell_id)`: walk `self._conduit_ward._get_links()`, call
  `peer._spellbook._inactivate_contract_spell(self._id, spell_id)` on each. Idempotent per
  peer (spellbook self-filters), so non-borrowers are skipped — no contract-direction logic.
- `notch_spell` facade now: capture `outgoing_id = spell_index.selected_spell_id` BEFORE the
  notch, call `self._spellbook.notch_spell(...)`, then `_deactivate_borrowed_spell(outgoing_id)`
  when `outgoing_id != spell.spell_id`. add_to_spell_index/remove_from_spell_index unchanged
  (they move INACTIVE spells -> no active-borrow fan-out; destroy-source borrower cleanup is
  the separately-deferred slice).

HANDOFF for the transaction agent: today `spellbook.notch_spell` still opens/closes its own
NOTCH transaction, so the fan-out currently runs AFTER that seal closes. When you migrate the
txn up to the conduit, the call site is already positioned: wrap [spellbook owner work +
`_deactivate_borrowed_spell`] in the one conduit-owned seal, and swap the spellbook public
call for the `_apply_*` seam. ast-parse clean, NUL=0.

## Note — 2026-06-30 — spellbook index-op methods made private

Renamed (only callers were the 3 conduit facades; no tests/other src call them):
- Spellbook.notch_spell -> _notch_spell, add_to_spell_index -> _add_to_spell_index,
  remove_from_spell_index -> _remove_from_spell_index. Docstrings flipped Public API ->
  Internal; origin_surface metadata strings updated to match.
- Conduit facades (still PUBLIC notch_spell/add_to_spell_index/remove_from_spell_index) now
  call the private spellbook methods. Public surface = conduit; spellbook executes privately.
Verified: no public spellbook defs remain, 3 private defs present, conduit calls all hit the
underscored names, conduit publics intact, all methods ast-parse. (Full-file run is the
user's 3.14t suite; bash can't compile the truncated large-file view.)

## Note — 2026-06-30 — transfer-of-ownership investigation

Read transfer_of_ownership.py. execute() (308): _mark_lineage_disabled -> flip ->
_move_creations -> borrower unshare/repoint -> _lift_disable(gated) -> rollback stack.
_flip_registry_and_spellbooks (1267): moves Aether registry + ONLY the selected member
(`spell_id = spell_index.selected_spell_id`) across the 4 active maps (_spells,
_lookup_spells, _spells_by_id, _spell_id_pool), sets spell._spellbook/_owner_conduit_id,
register_index on target, risk+nexus. _move_creations rehomes creations.
_enumerate_borrowers (454) inventories contract+cluster borrowers by spell_id ->
unshare/repoint. _gate_transfer_impacts (606) compute_impact_closure on the lineage.

GAPS vs the multi-member + contracted model we built:
1. (HEADLINE) Inactive members NOT carried. Flip moves only the selected member; the
   index's other members parked in src._inactive_spells (+ src._spell_ids) are orphaned
   on the source. After transfer, notching the moved index to an inactive member fails on
   target (_reactivate_owned_spell can't find it). Need: move every member in
   spell_index.spells_in_index() that's parked -> tgt._inactive_spells/_spell_ids, and
   repoint each inactive spell's _spellbook/_spell_system_states to target.
2. Borrowed-copy ownership change. Borrowers key contracted copies by OWNER conduit_id
   (_contracted_spells[src_id]); after transfer owner=target. Existing _enumerate_borrowers
   + unshare handles contracts, but confirm: re-key to target vs sever. Connection: our
   Conduit._deactivate_borrowed_spell could be reused (source deactivates borrowed copies
   on transfer, borrowers re-borrow from new owner).
3. No dest-signature guard. Flip does tgt._lookup_spells[spell._key]=index (1348) without
   checking target already owns a different index at that binding key -> clobber risk.
4. Target _spell_ids: flip adds to _spells_by_id/_spell_id_pool but not obviously
   tgt._spell_ids (existence set). Verify + add (for active + carried inactive members).

Architecture note: the flip reaches DIRECTLY into spellbook maps (src_book._spells.pop,
tgt_book._spells[...]=...). Under our "spellbook executes its own responsibilities"
principle, the inactive-member move + signature guard should be a SPELLBOOK method the
transfer calls. Open: refactor to spellbook method vs match existing direct-reach.
Investigation only; no code changed.

## Note — 2026-07-01 — general_0 — `_compiler_artifact` guard CONFLICT resolved (revert)

- DATETIME: 2026-07-01T12:37:14Z
- TYPE: FACT
- CLAIM: The 7 Spell property `if self._compiler_artifact is None: return None/False`
  guards (added under user direction during the notch/harden pass) are the banned
  defensive-None-guard-on-owned-field pattern AND are non-functional. `_compiler_artifact`
  is constructed unconditionally at `__init__`, `.cleanup()`'d, then **`del`'d** — it is
  never assigned `None` anywhere. So the guard is a dead branch pre-cleanup, and post-cleanup
  the slot is deleted (accessing it raises `AttributeError`, never returns `None`). The
  "uncompiled spell" case the guard was meant to cover is ALREADY handled: the artifact
  OBJECT always exists; its FIELDS (`_validation_result_phase4`, etc.) are `None` until the
  phases run, so the properties already return `None` with no guard on the artifact itself.
- EVIDENCE:
  - src/melder/aether/spellbook/spell.py:382 (unconditional construct)
  - src/melder/aether/spellbook/spell.py:476,524 (cleanup() then `del`, no `= None`)
  - src/melder/aether/spellbook/spell.py:930-1012 (the 7 added guards)
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:42-54
- IMPACT: The guards should be reverted to direct access (`return self._compiler_artifact._X`),
  or replaced with `check_cleaned()` fail-fast if a live-object contract is wanted. They add
  banned guard clutter and mislead readers into thinking the artifact is optional.
- NEXT: On user approval, revert the 7 guards in spell.py (single reviewable diff).
- REREAD: REQUIRED
- SCORE_0_TO_10: 8

## Note — 2026-07-01 — general_0 — does an inactive member in a SpellIndex still make sense?

- DATETIME: 2026-07-01T12:37:14Z
- TYPE: STRATEGY_DISCUSSION
- CLAIM: The multi-member SpellIndex + `bind_inactive` contradicts the project's own
  version-ownership philosophy. `IMPORTANT_CONSIDERATION.md` §2 states version history is
  owned by MutationResearch NOT the index, and §B/rule-2 that non-active versions "may still
  need to exist but cannot behave like ordinary active runtime spells" (visible to mutation/
  snapshot, not parked as ordinary Spellbook state). But the live code makes the index a
  member CONTAINER (`_spells_in_index` set; `add_member` "stage an inactive candidate
  (bind_inactive)") and parks inactive members as full owned Spells in `_inactive_spells` +
  `_spell_ids` (post-conjure even wiring a CreationContextFactory) — i.e. the index/spellbook
  are doing MutationResearch's job, and inactive members ARE treated as ordinary (inert)
  runtime spells. SpellIndex's stated purpose is "solve the mutable dictionary key problem"
  (one stable key -> one mutable active spell); a member SET conflates the stable-key role
  with a version-container role. The model has already flip-flopped single<->multi-member
  (epic Design History + CORRECTED MODEL supersede note), which is itself a signal the
  multi-member premise is unstable. This is the user's doubt and it is evidence-backed.
- EVIDENCE:
  - codex/context_compass/artifacts/IMPORTANT_CONSIDERATION.md:69-81
  - codex/context_compass/artifacts/IMPORTANT_CONSIDERATION.md:118-130
  - codex/context_compass/artifacts/IMPORTANT_CONSIDERATION.md:266-278
  - src/melder/aether/spellbook/bind/spell_index.py:13-31,136-150
  - src/melder/aether/spellbook/spellbook.py:4019-4058 (bind_inactive branch)
- IMPACT: If inactive-in-index is dropped, `bind_inactive`, `_inactive_spells`, `add_member`/
  `remove_member`/`_spells_in_index`, the notch-between-members seam, and the transfer/
  borrower-fan-out complexity for inactive members all collapse to a simpler "index = one
  active spell; alternatives owned by MutationResearch" model. If kept, it stays a pragmatic
  stopgap until MutationResearch exists, carrying the ownership smell + transfer gaps.
- NEXT: DECISION_REQUEST to user — (A) index = strictly one active spell, retire bind_inactive
  and route alternates through MutationResearch; or (B) keep multi-member as a stopgap.
- REREAD: REQUIRED
- SCORE_0_TO_10: 9

## Note — 2026-07-01 — general_0 — PLAN: extract bind_inactive -> conduit+spellbook `_bind_inactive`

- DATETIME: 2026-07-01T13:51:26Z
- TYPE: PLAN
- CLAIM: User decision (C, refined): `bind_inactive` is a real staging op but does not belong
  as a `bind` flag — it needs a target SpellIndex and belongs on the conduit (linking). Part 1
  = pure migration (no deep notch changes yet). Machinery all exists.
  Investigation facts:
  - Conduit index-op facades share ONE shape: check_cleaned -> `if not __dynamic_environment__:
    raise` -> mediator.start_transaction(TYPE, metadata) -> try spellbook `_apply/_op` /
    except end(False)+raise -> end(True) -> ward index-link maintenance. (conduit.py:3809-3851
    notch, 3871-3923 add_to_index)
  - `_bind.bind` ALWAYS mints a fresh index from the fingerprint (bind.py:293); no external-index
    param. So attach-to-provided-index = create-then-fold.
  - `_apply_add_to_index` (spellbook.py:3112-3235) is the membership-only move primitive:
    requires spell in `_inactive_spells` + target owned (`target_index.selected_spell_id in
    _spell_ids`), then source.remove_member -> target add -> repoint `spell.spell_index` ->
    destroy source if empty. Exactly the attach step.
  - Shared create (`_bind.bind` + collision check + `_add_hooks_to_spell`) is
    `_bind_under_active_transaction:3973-4017`, before the bind_inactive branch (4019-4058).
- EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3783-3851,3853-3923
  - src/melder/aether/spellbook/spellbook.py:3935-4058 (internal bind + inactive branch)
  - src/melder/aether/spellbook/spellbook.py:4136-4242 (public bind + passthrough)
  - src/melder/aether/spellbook/spellbook.py:3112-3181 (_apply_add_to_index)
  - src/melder/aether/spellbook/bind/bind.py:293,340-349 (fresh index mint)
- IMPACT: API-breaking (drops `bind_inactive` param on public `bind`); system-impacting (new
  conduit surface + spellbook method). Existing patch lane
  `system_docs/patches/active/2026-06-21_spellindex_active_inactive_frame_signature_foundation_*`
  covers active/inactive foundation; this slice extends it.
- PLAN (part 1, migration only):
  1. Extract shared create (3973-4017) -> helper `_create_bound_spell(...)` returning new_spell;
     `_bind_under_active_transaction` calls it then active-register; drop `bind_inactive`
     param+branch.
  2. New spellbook `_bind_inactive(*, spell, spell_index, existence, permissions, spellframe,
     binding_name, disposal_method_names, profile, **kwargs) -> str`: create via helper -> park
     (migrated branch) -> `_apply_add_to_index(new_spell, spell_index)` -> return spell_id.
  3. New conduit `bind_inactive(*, spell, spell_index, existence, ...)`: mirror notch/add facade
     (dynamic gate + mediator BIND txn + delegate + end). Disabled when not dynamic.
  4. Remove `bind_inactive` param from public `bind` (4146) + `_bind_under_active_transaction`
     (3945) + passthroughs (4219,4240) + docstring.
  DEFERRED to part 2: deep notch change (run bind's post-conjure activation machinery when
  notching an inactive member to active).
- NEXT: On user go-ahead (confirm D1 txn-type=reuse BIND, D2 attach=reuse `_apply_add_to_index`,
  D3 extend existing active/inactive patch), execute steps 1-4 as one coherent diff.
- REREAD: REQUIRED
- SCORE_0_TO_10: 9

## Note — 2026-07-01 — general_0 — IMPLEMENTED part 1: bind_inactive extracted (no txn wiring)

- DATETIME: 2026-07-01T14:07:26Z
- TYPE: FACT
- CLAIM: Built per user scope (transaction mechanics explicitly EXCLUDED — another agent owns
  that lane). Changes:
  - spellbook.py: NEW `_create_bound_spell` (shared create half: enum convert, disposal
    resolve, `_bind.bind`, collision check, hooks -> returns Spell). `_bind_under_active_transaction`
    now calls it (dropped inline create + the whole `if bind_inactive` branch + the param).
  - spellbook.py: NEW `_bind_inactive(*, spell, spell_index, existence, ...)` SEAM: create via
    helper -> park (`_active=False`, `_dynamic_environment=True`, `_inactive_spells`,
    factory-if-conjured, `_spell_ids`) -> fold onto the provided index via
    `_apply_add_to_index(new_spell, spell_index)` -> return spell_id. Dynamic-posture gated.
    NO transaction admission (seam runs inside the window the conduit/mediator lane will hold).
  - spellbook.py public `bind`: removed `bind_inactive` param + docstring + both passthroughs.
  - conduit.py: NEW public `bind_inactive(*, spell, spell_index, existence, ...)` facade:
    check_cleaned + normal-conduit + `__dynamic_environment__` gate + spellbook-None guard ->
    delegate to `_spellbook._bind_inactive`. NO `self.transaction(...)`/`self._lock` (deferred).
    Added `Union` to conduit typing imports.
  - Ownership verified: `Spell.__init__` stamps `_spellbook` at construction (spell.py:352),
    so `_apply_add_to_index`'s `spell._spellbook is self` gate passes for the fresh spell.
- EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4061 (_create_bound_spell), 4163 (_bind_inactive),
    4274 (bind, param gone), 3935 (_bind_under_active_transaction, param gone)
  - src/melder/aether/conduit/conduit.py:2689 (bind_inactive facade), 5-16 (Union import)
- IMPACT / OPEN:
  - NOT end-to-end functional yet: conduit.bind_inactive holds no transaction window; the
    transaction agent must wrap [create + park + _apply_add_to_index] in one seal.
  - BREAKS 11 call sites in 6 integration test files (all use old `bind(bind_inactive=True)`):
    test_index_lifecycle_and_depth, test_index_link_meld_and_probes, test_index_link_notch_follow,
    test_index_transfer_ownership, test_spell_index_notch_lifecycle, test_spell_index_op_guards.
    These need migration to `conduit.bind_inactive(spell=..., spell_index=...)` (scaffold tests).
  - Stale docstring: spell_index.py `add_member` still cites `Spellbook.bind_inactive` (now
    `Conduit.bind_inactive`); `add_member` may now be unused by the bind path.
  - NOT COMPILED: sandbox is Py3.10 + bash mount truncates these large files (py_compile stops
    ~line 5307); verified structurally via file-tool Reads. User runs 3.14t.
  - PART 2 (deferred, user-directed): modify notch deeply to run bind's post-conjure activation
    machinery when promoting an inactive member to active.
- NEXT: user runs 3.14t import/smoke; decide test-migration owner + part-2 notch start.
- REREAD: REQUIRED
- SCORE_0_TO_10: 9

## Note — 2026-07-01 — general_0 — migrated integration tests off `bind(bind_inactive=True)`

- DATETIME: 2026-07-01T14:07:26Z
- TYPE: FACT
- CLAIM: Removed the old `book.bind(..., bind_inactive=True)` flag from all 6 integration files
  and moved staging to `conduit.bind_inactive(spell=..., spell_index=<owned index>, ...)`.
  Whole-tree `bind_inactive=True` grep now = 0. Pattern per case:
  - Setup helpers (A active + B inactive on A's index): folded `bind_inactive` +
    `add_to_spell_index(B, I_A)` into one `conduit.bind_inactive(spell=B, spell_index=I_A)`.
    (lifecycle _two_member_conduit; meld_probes _two_member_linked + transfer test;
    notch_follow both link helpers; notch_lifecycle _two_member_index.)
  - Standalone `bind_inactive` with no target (meld_probes
    test_bind_inactive_spell_is_not_meldable_until_notched): added an active A and attached B to
    A's index.
  - REVIEW NEEDED (2 semantic shifts):
    - notch_follow test_add_member_to_linked_index_propagates_parked_copy: now adds the member
      via `bind_inactive` (not a separate post-link `add_to_spell_index`). Its borrower-copy
      assertion depends on bind_inactive propagating the new member to index-link borrowers --
      that fan-out is conduit orchestration NOT yet wired (deferred), so this test will fail
      until it is.
    - op_guards test_remove_from_spell_index_rejects_sole_member: the old premise (an inactive
      spell that is the SOLE member of its own index) is impossible in the index model (an
      inactive member always has the active member beside it). Rewrote it to remove the ACTIVE
      sole member; this may now overlap with test_remove_from_spell_index_raises_active.
- EVIDENCE:
  - tests/integration/melder/aether/conduit/test_index_lifecycle_and_depth_integration.py:67-79
  - tests/integration/melder/aether/conduit/test_index_link_meld_and_probes_integration.py:87-101,192-204,222-243
  - tests/integration/melder/aether/conduit/test_index_link_notch_follow_integration.py:85-98,159-167,204-219
  - tests/integration/melder/aether/conduit/test_index_transfer_ownership_integration.py:72-84
  - tests/integration/melder/aether/conduit/test_spell_index_notch_lifecycle.py:11-19,78-91
  - tests/integration/melder/aether/conduit/test_spell_index_op_guards.py:125-138
- IMPACT: bind_inactive is now the single staging entry (create + attach-to-index); the test
  suite reflects it. Tests are NOT runnable to green yet: (a) conduit.bind_inactive holds no
  txn window, (b) borrower fan-out for a linked-index member-add is unwired. Both are the
  deferred orchestration/transaction lane.
- NEXT: user 3.14t run once txn window + linked-index fan-out land; confirm the 2 review items.
- REREAD: REQUIRED
- SCORE_0_TO_10: 8
