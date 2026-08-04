

# Task: Map SpellIndex vs lineage separation (partial migration) + notch design

- Completed: 2026-07-11T18:50:00Z
- Summary: Mapping served its purpose (corrected single-selected model
  shipped; add/remove seams landed via index_link); closed on
  owner-directed general_0 cleanup - residuals recorded in Status.

## Metadata
- Task ID: TASK-2026-06-12-spell-index-lineage-separation-map
- Story: none
- Status: closed (owner-directed cleanup 2026-07-12, melder_0 inheritor:
  the mapping served its purpose - the corrected model shipped,
  _apply_notch delegates to SpellIndex.update, add/remove seams landed
  via index_link (conduit.py:4003/:4075); the two open rows (update()'s
  commented object-substitution block + orphaned mediator strategies)
  are recorded residue - re-ticket with fresh source evidence if they
  ever matter.)
- Owner: cowork
- Agent Name: general_0 (inherited + closed by melder_0)
- Priority: p1
- Created: 2026-06-12T23:45:26Z
- Updated: 2026-06-13T11:52:03Z

## Objective
USER INTENT (verbatim capture, 2026-06-12): "SpellIndex ... shouldn't
mean lineage and we're in a partial migration so we need to map out how
this will work because the lineage has 1 amazing use case we can
organize a directory of spells and notch between them so if you're
iterating over mutations of spells you can notch it and meld it."
USER ADDITION: also a full spell_id audit - generation, guarantees,
and every consumption surface - because "these two mechanics must be
iron clad". Deliverable: a complete map of the current SpellIndex AND
spell_id semantics vs the intended post-migration split - SpellIndex as identity/registry surface,
lineage as an ordered directory of spell mutations with a NOTCH selector
(move the notch to a version; meld resolves the notched version) - plus
the migration plan from the current partial state.

## Ticket Contract
- ENTRY_GATE: active board row; research read of
  `src/melder/aether/spellbook/bind/spell_index.py` and every consumer
  surface (spellbook.py 66 refs, aether.py, meld.py, conduit.py,
  conduit_cluster.py, mutation_research/) BEFORE proposing the design.
- EXECUTION_BOUNDARY: DESIGN/MAPPING ONLY until the user approves the
  map; then edits as user directs. mutation_research is read-only
  context (other policies exclude it from edit scope).
- DEPENDENCIES: none.
- EXIT_GATE: user accepts the map + migration plan; implementation (if
  any) ticketed separately or this ticket extended by user decision.
- FAILURE_ESCALATION: DECISION_REQUEST notes for every semantic fork
  (this is the user's architecture; UNKNOWN-first, no guessing).

## Scope Boundaries
- In scope: current-state semantics inventory (what SpellIndex means at
  each consumer today; which parts already migrated vs not), the
  index/lineage split design, notch mechanics (directory of mutations,
  notch pointer, meld-resolves-notched), migration sequencing.
- Out of scope (until user approves): any src edits; mediator; compiler
  phase internals beyond what SpellIndex touches.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: User directed this as the single focus ("lets go
  focus on specifically 1 thing").

## Steps / Checklist
- [x] Research read: spell_index.py in full (398 LOC, read complete)
- [ ] spell_id audit (USER ADDITION 2026-06-12: "audit how spell_id
      works and where its consumed because these two mechanics must be
      iron clad its a huge part of the system"): generation (bind-time
      fingerprint), uniqueness/stability guarantees, every consumption
      surface (_spell_id_pool, meld id-string lane, fast-door keys,
      cache keys, aether registry, ward/transfer, nexus records,
      mutation_research), and how spell_id relates to SpellIndex and to
      lineage/version identity in the proposed split (id-of-version vs
      id-of-lineage MUST be explicit)
- [ ] Consumer inventory: spellbook.py (66 refs), meld.py, conduit.py,
      conduit_cluster.py, aether.py, mutation_research (read-only)
- [ ] Identify partial-migration seams (what already treats SpellIndex
      as identity-only vs what still conflates lineage)
- [ ] Draft the split: SpellIndex (identity/registry) vs lineage
      (ordered mutation directory + notch selector + meld resolution)
- [ ] DECISION_REQUEST notes for semantic forks; user reviews map
- [ ] Run Ticket Microcycle during execution.

## Deliverables
- Evidence-backed current-state map + proposed split + migration plan
  (in this ticket's Notes; promoted to a doc if user wants one)

## Files / Paths Impacted
- None yet (design phase). Read targets listed in ENTRY_GATE.

## Validation
- Not run. Design phase has no executable validation.

## Risks / Rollback Notes
- Partial migration means BOTH semantics are live somewhere; the map
  must label each consumer's current assumption explicitly or the
  migration will break meld/ward surfaces silently.
- Notch + meld interacts with the fast meld door (door entries key on
  spell-id strings and capture creations): notching a lineage MUST
  invalidate or re-key affected doors - design constraint to carry.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Noting Behavior
- Note focus: per-consumer semantics findings with `path:start-end`
  evidence; DECISION_REQUEST for every fork; append-only.

## Notes
- DATETIME: 2026-06-12T23:45:26Z
  TYPE: PLAN
  CLAIM: Lane opened on user direction. Known going in: SpellIndex
    class at src/melder/aether/spellbook/bind/spell_index.py; heaviest
    consumers spellbook.py (66 refs), then aether/meld/conduit/
    conduit_cluster; mutation_research references it 27x across two
    files (the mutation-iteration consumer the notch use case serves).
    Prior-lane facts that interact: meld resolves id-strings through
    `_spell_id_pool` then `_resolve_spell_by_id`; fast doors key on the
    id string and capture (spell, context, creations, epoch) - notch
    semantics must define what happens to doors when the notched
    version changes (epoch bump at the notch chokepoint is the natural
    fit). Ward lineage links (`_link_lesser_conduit`) are CONDUIT
    lineage - distinct concept from spell lineage; the map must keep
    these namespaces from colliding.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:1-1
  IMPACT: Architecture-defining; everything melds through these
    semantics.
  NEXT: read spell_index.py in full (LOC check first), then the
    spellbook.py consumer surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T00:40:00Z
  TYPE: FACT
  CLAIM: spell_index.py read in full. Current anatomy: SpellIndex IS
    already a two-level identity - immutable ULID `_id` (hash/eq based
    ONLY on this; the stable dict-key identity = id-of-LINEAGE) plus
    mutable `_current_id` version pointer (SHA256 = id-of-VERSION).
    `update(new_id)` IS a proto-notch: moves the pointer, records the
    version in `_versions`, and propagates old_id->new_id through
    `_update_owned_spell_id` / `_update_contracted_spell_id` lookup-map
    renames on the owner + contracted spellbooks. THE PARTIAL-MIGRATION
    SEAM IS EXPLICIT IN SOURCE: update() contains a commented-out block
    (lines 166-172) with the author's note - "not fully sure how
    mutations will work and if original spell is substituted or not...
    could even take a codegen version of the spell and store it and
    substitute" - so today an update RENAMES map keys but the live
    Spell object keeps its OLD spell_id attribute and old compiled
    artifacts: maps point new_id -> stale-built Spell. Gaps vs the
    user's notch use case: (1) `_versions` is an unordered SET - cannot
    iterate mutations in order; notching needs an ordered directory
    (list + position, prev/next); (2) no notch-then-meld lane - meld
    takes version id strings, nothing resolves "lineage ULID -> current
    notch -> spell"; (3) un-answered substitution semantics (rebuild
    via deferred resolution / stored codegen variants per version /
    spell-object swap); (4) `current` is a deliberate lock-free hot
    read (compiler phases, thousands/conjure) - notch design must not
    re-lock it. Door interaction confirmed: a notch flip MUST bump
    `Spell._door_epoch` and the id-keyed fast doors/_spell_id_pool
    entries for old_id must be handled (rename or natural miss).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:16-77
  - src/melder/aether/spellbook/bind/spell_index.py:137-181
  - src/melder/aether/spellbook/bind/spell_index.py:297-330
  IMPACT: The split the user wants is half-built: ULID=lineage id and
    SHA=version id already exist and never collide in hashing. The
    migration is about (a) making every consumer say WHICH id it means,
    (b) upgrading `_versions` set -> ordered mutation directory with
    notch movement, (c) deciding substitution semantics (the in-source
    open question), (d) a meld-by-lineage resolution lane.
  NEXT: consumer inventory - spellbook.py's 66 refs first
    (_update_owned_spell_id/_update_contracted_spell_id/
    _register_owned_spell_id and every SpellIndex/spell_id read site),
    labeling each as version-id vs lineage-id semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T11:52:03Z
  TYPE: DECISION
  CLAIM: Lane reassigned from compiler_builder_0 -> general_0 by explicit
    user direction ("take the lane now overwrite compiler_builder_0").
    Owner/Agent Name updated to cowork/general_0. compiler_builder_0's
    prior notes are PRESERVED (append-only); only ownership changed.
    CORRECTION 2026-06-13T11:55Z: user confirmed compiler_builder_0 is
    not a real agent; the mailbox NOTICE + board alert were retracted and
    its stale check-in row marked departed - no coordination was needed.
    Lane stays DESIGN/MAPPING ONLY per the existing Ticket Contract; no
    src edits until the user approves the map.
  EVIDENCE:
  - codex/context_compass/attention_board.md:31-34
  IMPACT: general_0 now owns the SpellIndex lineage-separation map; board
    + mailbox synchronized to the new owner.
  NEXT: complete the consumer-semantics labeling and draft the
    index/lineage+notch split for user review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T11:52:03Z
  TYPE: FACT
  CLAIM: spell_id audit (the user's "iron clad" addition) completed by
    general_0. GENERATION: spell_id is a deterministic SHA256 from
    `Bind.sha256_profile(...)` over `v4-binding` + binding-shape
    (class: name/qualname/module/bases/mro/annotation-keys/method-names/
    init_signature; callable: signature/params/repr/flags; instance:
    type/module/repr) + spellframe + binding_name + existence.name +
    disposal method names, joined `::`. At bind, the same fingerprint
    seeds THREE surfaces at once: SpellIndex(initial_id), Spell(spell_id),
    and registry keys -> spell.spell_id == spell.spell_index.current ==
    fingerprint at t0. v4 hashes the constructor signature, not source
    text (constructor change invalidates, docstring edit does not).
    `spell_id_inspector(...)` recomputes the same hash without registering.
    GUARANTEE: content-addressed by binding shape; equal signature ->
    equal id, material change -> new id. CONSUMPTION (version-id = SHA):
    Spellbook `_spells_by_id`, `_spell_id_pool` (owned+contracted; Meld
    holds a direct ref), `_contracted_spells_by_id[conduit_id][id]`;
    `meld("<sha>")` -> `_resolve_spell_by_id` (pool then by_id);
    validity/change-control gate on `spell.spell_index.current`
    (`is_root_dirty(conduit_id, id)`, `get_spell_validity(id)`); Nexus
    SpellRecord.spell_index_id; on `update()` the rekey pops old/inserts
    new across by_id + pool + `_spell_versions` then
    `_replace_spell_record_in_nexus`. LINEAGE-id (ULID `SpellIndex.id`)
    keys: `_spells{SpellIndex->Spell}`, `_lookup_spells` values, and
    MutationResearch `Research` sessions (snapshot `.current` as
    `_root_version`). CONFLATION SEAM confirmed: after `update()` the maps
    point new_id -> spell but `spell.spell_id` ATTRIBUTE stays old (the
    commented-out substitution block) and compiled artifacts are stale;
    meld reads `.current` so resolution still works, but `spell.spell_id`
    is a latent stale-read trap.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:284-360
  - src/melder/aether/spellbook/bind/bind.py:402-499
  - src/melder/aether/spellbook/spellbook.py:930-1045
  - src/melder/aether/spellbook/spellbook.py:1096-1300
  - src/melder/aether/conduit/meld/meld.py:1253-1281
  - src/melder/aether/conduit/meld/meld.py:713-997
  - src/melder/aether/spellbook/bind/spell_index.py:137-181
  IMPACT: The id-of-version vs id-of-lineage split is half-built; the
    migration must (a) make every consumer declare which id it means,
    (b) turn `_versions` set -> ordered notch directory, (c) resolve the
    `spell.spell_id` attribute substitution question, (d) add a
    meld-by-lineage(notch) lane that bumps `Spell._door_epoch`.
  NEXT: label conduit.py / conduit_cluster.py / aether.py consumer sites
    (version-id vs lineage-id) and draft the split + migration sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T12:12:14Z
  TYPE: FACT
  CLAIM: Reframe locked by user: SpellIndex is NOT a lineage; it becomes a
    genuine first-class INDEX (collection) of spells/versions that agents
    add to, remove from, and notch (move current selection), with meld
    resolving the notched member - integrity preserved. INTEGRITY SURFACES
    any add/remove/notch must keep coherent (evidence-backed this session):
    (1) Spellbook `_spells {SpellIndex->Spell}` is SINGULAR today
    (`_find_spell` = `_spells.get(index)`); this is the core blocker.
    (2) `_spells_by_id`/`_spell_id_pool`/`_contracted_spells_by_id` keyed by
    current version id = the meld resolution surface; rekey on notch.
    (3) `_lookup_spells {bind-key->SpellIndex}` enforces ONE index per
    binding signature via `_assert_lookup_key_available`.
    (4) AethericFrame `_spell_registry {conduit_id->Set[SpellIndex]}` +
    `_version_registry` rebuilt from `SpellIndex.get_all_versions()`;
    `Aether._check_for_spell(version_id)` resolves version->index and is the
    bind-time global uniqueness gate; `find_and_return_spell_index`.
    (5) SpellSystemStates keys BOTH `_states_by_index_id` (ULID) and
    `_states_by_spell_id` (version), plus `_index_owner_spellbook_id`,
    `_collection_frames_by_index`, `_dirty_indexes` (collection scaffolding
    already half-present).
    (6) `Spell._door_epoch` = fast-meld-door invalidation; a notch/remove
    that changes the resolved member MUST bump it (bump sites assume
    per-spell serialization).
    (7) Nexus `SpellRecord.spell_index_id` (`_replace_spell_record_in_nexus`
    on version change). (8) ConduitCluster `shared_spells {owner->Set[
    SpellIndex]}` + cluster-root id derived from `spell.spell_id`;
    `_resolve_spell_from_index` = `book._spells.get(index)`. (9)
    MutationResearch `Research` keyed by `SpellIndex.id` snapshotting
    `.current` (read-only/excluded from edit scope). BIND CHOREOGRAPHY (the
    template add() must mirror): `_check_for_spell` version-uniqueness ->
    `_assert_lookup_key_available` bind-key -> `_lookup_spells[key]=index`
    -> `_spells[index]=spell` -> `index._attach_owner` (registers id maps)
    -> warm `_spell_versions` -> if conjured: stamp conduit, Creations,
    frame registry, SpellSystemStates, `refresh_version_registry`.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3094-3125
  - src/melder/aether/spellbook/spellbook.py:1496-1510
  - src/melder/aether/spellbook/spellbook.py:1705-1760
  - src/melder/aether/aetheric_frame/aetheric_frame.py:604-700
  - src/melder/aether/aether.py:1254-1318
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:246-298
  - src/melder/aether/spellbook/spell.py:362-369
  - src/melder/aether/conduit/conduit_cluster.py:602-618
  IMPACT: add/remove/notch each touch a fixed, enumerated surface set;
    integrity = keeping these in lockstep within one serialized mutation.
  NEXT: user decides the design forks below before any model is drafted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T12:12:14Z
  TYPE: DECISION_REQUEST
  CLAIM: Design forks for the genuine-index model (user's architecture; no
    src edits until decided). F1 MEMBER TYPE: members are Spell objects
    (ordered list + notch ptr; notch=O(1) ptr move+epoch bump, no rebuild,
    kills the stale-spell_id seam) vs version-id snapshots (lighter store,
    notch needs rehydration - the commented-out "stored codegen variant"
    idea) vs hybrid. Recommend Spell-objects first. F2 MEMBER HOMOGENEITY
    (PIVOTAL): are members versions of ONE binding signature (homogeneous -
    keeps `_lookup_spells`, `_check_for_spell`, cluster-root coherent) or
    can heterogeneous DIFFERENT spells live under one index (large blast
    radius: breaks bind-key 1:1, needs reindex/transfer - the May
    blast-radius artifact)? Recommend homogeneous-first. F3 ORDER: ordered
    sequence so "notch forward/back/to" is well-defined; `_versions` set ->
    ordered directory. F4 ADD activation: append-without-auto-notch
    (explicit notch to activate; meld resolution never changes silently) vs
    add-becomes-current. Recommend append-only-then-notch. F5 REMOVE:
    forbid removing the current notch unless last member; last-member
    removal triggers index GC across all surfaces in #1-9; non-current
    removal just drops member + version registry + door cache. F6 CONCURRENCY/
    "change during meld": notch serialized under index/spell lock + epoch
    bump; lock-free `.current` read preserved (atomic ptr: in-flight meld
    sees old-or-new, next meld rebuilds via epoch miss). Need user intent on
    whether "change during meld" means notch AS PART OF a meld call. F7
    TRANSACTIONALITY: route index add/remove/notch through DevOps change-
    control (mediator already has BIND/LINK/TRANSFER/MUTATION/CLUSTER_LINK)
    so concurrent agents can't corrupt an index, vs index-local lock only.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md:1-1
  - src/melder/aether/spellbook/bind/spell_index.py:137-181
  IMPACT: F2 (homogeneity) gates everything else - heterogeneous members
    are a different, much larger project than versioned members + notch.
  NEXT: get user decisions on F1-F7, then draft the member model + add/
    remove/notch operation specs + migration sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T12:18:04Z
  TYPE: DECISION
  CLAIM: User refined the model (frontier/world-first; do not impose
    baseline VCS/db framing). CANONICAL MODEL: (1) bind's job is to mint
    IDENTITY - a deeply-defined SHA256 over bound shape, dedup-guaranteed;
    spells may be codegen'd live in Nexus by agents; every bound object is
    a distinct, real, independently-meldable identity. (2) The INDEX is a
    SEPARATE EXPLICIT container an agent attaches already-identified objects
    to BECAUSE IT WANTS TO ITERATE ("I have this object, add it in, move
    current to the new one"). Identity-creation and index-membership are
    two DIFFERENT acts (today bind fuses them 1:1 - that fusion is what we
    unwind). (3) The index is the STABLE HANDLE; members are distinct
    identities; the NOTCH = which member the HANDLE resolves to; every
    member stays directly meldable by its own SHA. (4) MUTATION semantics
    (how the next object derives from the prior) are DELIBERATELY UNDEFINED
    - the index is only the substrate that makes iterating between concrete
    identities possible, not the mutation engine. CONSEQUENCE: the earlier
    F2 homogeneous-vs-heterogeneous axis is RETIRED - members are not
    "versions of one binding signature," they are distinct identities an
    agent chose to group; the binding-key/`_lookup_spells` 1:1-per-index
    assumption must be revisited around the index-handle being the stable
    name.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:284-360
  - src/melder/aether/spellbook/bind/spell_index.py:16-31
  IMPACT: Operations decouple: bind() = mint+register identity;
    index.add(identity) = attach; index.notch(member) = set current;
    index.remove(member) = detach; meld(handle) = notched member;
    meld(sha) = exact member. add/remove are lighter than bind (identity
    already exists). Resolution-by-name vs resolution-by-handle is the new
    open seam.
  NEXT: user decides (Q1) free-standing identity vs bind-seeds-default-
    index; (Q2) index-handle as primary stable name vs per-member bind-key
    lookup; (Q3) membership exclusive vs an identity in many indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T12:37:59Z
  TYPE: DECISION
  CLAIM: User answered Q1 + Q3 (overriding general_0's free-standing lean).
    Q1 = INDEX IS NOT OPT-IN: EVERY spell ALWAYS has exactly one index;
    bind keeps minting a default single-member index (refactoring to
    free-standing identity is "a nightmare" - keeps the resolve-through-
    index machinery: frame `_spell_registry` Set[SpellIndex],
    SpellSystemStates `_states_by_index_id`, Nexus `spell_index_id`). Q3 =
    EXCLUSIVE membership: a spell lives in one index at a time; you MOVE it
    between indexes, never share/copy. CORE PRIMITIVE = MOVE A SPELL
    BETWEEN INDEXES; "add into an index" = move it in (grouping a default-
    born spell into another index); "separate" = move a member out of a
    multi-member index into its own fresh single-member index (split);
    plus NOTCH within an index. ITERATION LOOP: codegen A' (born in its own
    default index) -> move A' into A's index -> notch to A'. Reduces blast
    radius vs free-standing: the only hard storage blocker stays
    `_spells {index->ONE spell}` becoming multi-member; the rest is
    move/notch/GC bookkeeping over the enumerated integrity surfaces.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3122-3125
  - src/melder/aether/spellbook/spellbook.py:1496-1510
  - codex/context_compass/artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md:300-372
  IMPACT: F1=Spell objects, Q1=always-indexed, Q3=exclusive are LOCKED.
    `_spells` multi-member + move(A: X->Y) + separate(=move to fresh Y) +
    notch + empty-index GC are the operation set. The May reindex-transfer
    + empty-index-GC exploration is now the confirmed direction (bounded by
    always-indexed + exclusive).
  NEXT: resolve the still-open seams - (S1) multi-member resolution: does
    meld(name/bind-key) return the SPECIFIC keyed member while
    meld(index-handle) returns the NOTCHED member; (S2) notch behavior on
    move (re-notch source to which neighbor; moved member current in dest);
    (S3) empty-index GC on last-member move-out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T13:01:37Z
  TYPE: FACT
  CLAIM: VERIFIED the bind-availability over-scan (user asked to double-
    check). `Spellbook.bind` -> `Aether._check_for_spell(spell_id, frame)`
    -> `frame.has_version(spell_id)` -> reads `_version_registry`, which
    `refresh_version_registry()` rebuilds by unioning
    `SpellIndex.get_all_versions()` per index, and `get_all_versions()`
    returns the FULL `_versions` HISTORY set (every id ever pointed at via
    `update()`). So the "is this binding taken?" SHA check scans the entire
    version HISTORY across ALL indexes in the frame, not just active spells
    - dead historical ids stay "taken" forever as you iterate. The
    `_assert_lookup_key_available` bind-key check is fine (each index
    contributes only its one active spell's key). FIX DIRECTION (user):
    scope bind/availability to ACTIVE spells only.
  EVIDENCE:
  - src/melder/aether/aether.py:1254-1290
  - src/melder/aether/aetheric_frame/aetheric_frame.py:604-662
  - src/melder/aether/spellbook/bind/spell_index.py:331-349
  IMPACT: The version-registry's history-union is the root of the bad
    workflow; in the new model the registry/availability must advertise
    only the ACTIVE (notched) member of each index.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T13:01:37Z
  TYPE: DECISION
  CLAIM: Resolution model LOCKED (user). Each spell keeps its unique
    binding; the index stays a resolver/grouping tool. ONLY THE ACTIVE
    (notched) MEMBER IS LIVE: registered in `_spells_by_id`/`_spell_id_pool`,
    advertised in the version registry, and counted for binding-availability;
    inactive members are held dormant in the index, NOT directly meldable
    until notched active. NOTCH = the current_spell, nothing more (S2: "the
    current_spell is notched thats it") - it generalizes today's
    `update()`-rekey: de-register old active id -> register new active id +
    bump `Spell._door_epoch`. BIND/AVAILABILITY checks scoped to active
    spells (fix the version-registry history-union). EMPTY INDEX cannot
    exist except transiently INSIDE a transaction (S3) -> index mutations
    (move/notch/separate/GC) are transactional (affirms the change-control/
    mediator path); an index emptied mid-txn is GC'd before commit. OPS:
    move(spell X->Y) is the regroup primitive (add=move-in, separate=move-
    to-fresh-index); notch(member) sets current_spell.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:137-181
  - src/melder/aether/spellbook/spellbook.py:930-1045
  IMPACT: Q1 always-indexed, Q3 exclusive, S1 active-only-live, S2 notch=
    current_spell, S3 empty-only-in-txn are all LOCKED. Model is ready to
    draft as member-store + move/notch/GC operation specs.
  NEXT: confirm the one implication (inactive members NOT meldable-by-SHA
    until notched) then draft operation specs + migration sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T14:46:42Z
  TYPE: DECISION
  CLAIM: Resolved the "shared signature vs logical construct" tension via
    the LOOKUP-KEY vs SHA split. Lookup key (frame_key, binding_key) =
    RESOLUTION LOCATION (what you call); SHA spell_id = CONCRETE IDENTITY
    (what you bind). They are independent: two spells can share a lookup
    key with different SHAs (same name/spellframe/binding_name, different
    constructor shape). So an index need NOT choose between "versions" and
    "logical grouping": members sharing a lookup key = versions (notch
    swaps which SHA answers at one call-location); members with different
    lookup keys = a logical grouping (notch changes which location is live).
    INTEGRITY RULE (user): on NOTCH, run the bind system's lookup-
    eligibility check (`_assert_lookup_key_available`) scoped to ACTIVE
    spells - vacate the outgoing active member's lookup key, claim the
    incoming member's lookup key (must be free among active, or already
    owned by this index), rekey SHA maps, bump door epoch. Today that check
    REJECTS a 2nd spell on the same lookup key; relaxing it to "only active
    members count" is THE single change that lets same-lookup-key versions
    coexist dormant in one index. CONFIRMED: lookup key can differ from SHA
    (sha256_profile includes init_signature/methods/etc; the (frame,bind)
    key does not).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1705-1760
  - src/melder/aether/spellbook/bind/bind.py:440-499
  - src/melder/utilities/helpers/general_helpers.py:1-1
  IMPACT: bind-availability AND notch-availability share one active-scoped
    lookup-eligibility check; same-lookup-key versioning is enabled by
    active-scoping; lookup key = resolution location is the unit the notch
    switches.
  NEXT: confirm the "locked/none" notch option (below), then draft specs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T14:46:42Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: User insight (assess value): "workflows use spellindex to lock out
    resolution steps... with AI work more valuable than I understand."
    general_0 assessment: because only the ACTIVE member occupies a
    resolution location, the NOTCH is a live switch on what is callable
    there -> SpellIndex becomes a RESOLUTION-CONTROL surface, not just a
    version holder. Uses: (a) capability gating - notch to real impl =
    enabled, notch away = location dormant/unresolvable = capability
    circuit-breaker; (b) workflow sequencing - a step is not callable until
    its index is notched live; (c) actor/ASE state-shaping - an actor
    controls its own/field resolvable surface at runtime by managing
    notches (= "active mental space / what's live in the working set"); (d)
    governance seam - who may notch = who controls what resolves (dovetails
    Nexus/ACL gating). NEW FORK: does the notch get a "locked/none"
    position (members present, NO live member -> location deliberately
    unresolvable = the explicit lockout)? Powerful but breaks the "always
    exactly one current_spell" invariant - user decision whether in scope
    now or a later layer.
  EVIDENCE:
  - codex/context_compass/mission.md:140-175
  - src/melder/aether/spellbook/spell.py:362-369
  IMPACT: Reframes SpellIndex from version-holder to runtime resolution-
    control / capability-gating primitive aligned with the actor/ASE
    direction; the "locked/none" notch is the explicit lockout capability.
  NEXT: user decides locked/none-notch scope; then draft member-store +
    move/notch(+eligibility)/GC specs + migration sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T14:51:07Z
  TYPE: FACT
  CLAIM: PIVOTAL (user Q: do lookup keys bind to SpellIndex or spell?).
    VERIFIED: lookup keys bind to the SPELLINDEX, not the spell.
    `Spellbook._lookup_spells: Dict[tuple, SpellIndex]` (256); bind does
    `_lookup_spells[new_spell._key] = spell_index` (3122). Meld name lane:
    key -> `_lookup_owned_spells[key]` = SpellIndex -> `_owned_spells[
    spell_index]` = Spell (`_resolve_local_by_lookup_key` meld.py:1367,
    `_owned_spells` = `spellbook._spells`). So the key->index->spell
    indirection ALREADY EXISTS. CONSEQUENCE = the work splits in two:
    (A) VERSIONING IS LIGHT/CONTAINED - members share a lookup key; make
    `_spells[index]` go single->members+notch and name resolution AUTO-
    follows the notch; `_lookup_spells` untouched, frame `_spell_registry`,
    SpellSystemStates `_states_by_index_id`, Nexus `spell_index_id` all
    untouched (they key on the index); only real changes are `_spells`
    multi-member + the SHA-pool rekey on notch (which `update()` already
    does) + active-scoped availability. NO lookup-key vacate/claim dance.
    (B) REGROUPING IS THE HEFTY PART - move-between-indexes / separate /
    logical-grouping with DIFFERENT keys per index fights key->index:
    under it EVERY call through an index yields the notched member
    regardless of which key was used, so different-key members in one index
    are incoherent. That case needs key->spell (name-resolution redesign)
    or per-member key bookkeeping + rekey-on-move.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:256-256
  - src/melder/aether/spellbook/spellbook.py:3122-3123
  - src/melder/aether/conduit/meld/meld.py:1290-1334
  - src/melder/aether/conduit/meld/meld.py:1360-1370
  IMPACT: Resolves hefty-vs-light. Versioning core is mostly free given the
    existing key->index design; heft lives ENTIRELY in the cross-index
    move/regroup ambition. SCOPING FORK: Path A (versioned resolution slot
    - light, delivers iterate+notch+lockout) now, Path B (move/separate/
    logical-grouping) later; vs commit to the key->spell redesign now.
  NEXT: user picks Path A-first vs Path B-now; then draft specs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-13T16:28:06Z
  TYPE: DECISION
  CLAIM: TRANSACTIONALITY DECIDED (read the devops/mediator map): notch (and
    later move/separate) route through the TransactionMediator as a new
    transaction family, NOT index-local locks. WHY (stronger than "complex"):
    (1) bind already IS a mediator transaction (BindTransactionStrategy) and
    notch contends on the SAME scope keys the plane already uses -
    `binding:<key>` (lookup-key availability) + `scope:spellbook:<id>` (the
    maps); separate planes => notch can race a concurrent bind on the same
    key; same plane => correct by construction. (2) The mediator IS the
    no-GIL answer: posture is "parallel by default, serialize only on real
    overlap"; the hot path never enters it (Meld only checks is_root_dirty/
    validity), so routing notch through it PRESERVES the lock-free `.current`
    read - writer serializes via scope claims, `apply_commit_delta` rekeys
    the maps WHILE SCOPES HELD (race-free), commit marks dependents dirty so
    next meld re-gates. (3) Cheap + idiomatic: admission is one atomic claim
    over declared keys; a solo notch claims a tiny disjoint set (spellbook +
    binding key) => parallel-friendly; new families plug in via
    `TransactionStrategy` + builder registration (no per-family branches).
    "Empty index only in a transaction" = empty is a legal in-flight state
    resolved before commit. Path A notch = small claim set; Path B move =
    bigger (two indexes + registry). PRINCIPLE NOTED: macro scope-claim
    synchronization displaces per-object/per-field locks - locks don't
    vanish (1 RLock/manager + embargo Condition remain), they RELOCATE to
    the real consistency boundary, which is exactly what lets the hot path
    stay lock-free on no-GIL.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-06-13_devops_mediator_system_map.md:128-285
  - src/melder/aether/spellbook/spellbook.py:3094-3125
  IMPACT: F7 transactionality LOCKED = mediator transaction. Open: add a new
    NOTCH/INDEX TransactionStrategy family vs fold into reserved (on-hold)
    MUTATION type - decide after reading strategy source.
  NEXT: read TransactionStrategy base + BindTransactionStrategy + embargo
    try_acquire in SOURCE (not just the map) to pin the scope-claim shape;
    then draft the notch-as-transaction Path A spec.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-13T17:03:19Z
  TYPE: DECISION
  CLAIM: Transaction TAXONOMY (user enumerated create-index+transfer-in,
    transfer-between+destroy-old, notch as "all new transactions").
    Refinement: because an empty/half-built index cannot be visible at
    rest, the ops collapse into TWO new mediator transaction families, with
    create/destroy riding INSIDE move (atomic units, not chains):
    (1) NOTCH (intra-index, Path A) = make spell S current in its index;
    claim set ~ {scope:spellbook:<owner>, binding:<key>}; effect = swap
    active member, rekey SHA pool, bump door epoch, mark dependents dirty;
    parallel-friendly.
    (2) MOVE (inter-index, Path B) = transfer spell A from index X -> Y;
    CONTAINS create (mint Y if new = separate/split = "create + transfer
    in") and destroy (GC X if left empty = "transfer out + destroy old"),
    both inside the one transaction so no empty/orphan index ever exists at
    rest (satisfies "empty only inside a transaction"); claim set ~ {both
    spellbook scopes, binding:<moved key>, frame registry scope}.
    So "create+transfer-in" and "transfer-out+destroy" are NOT chains of
    small txns - each is ONE atomic MOVE with create/destroy as end-steps.
    Net new mediator surface = 2 strategies (NOTCH, MOVE) on the bind
    pattern; NOTCH ships first (Path A), MOVE second (Path B).
  EVIDENCE:
  - codex/context_compass/artifacts/2026-06-13_devops_mediator_system_map.md:128-285
  - src/melder/aether/spellbook/bind/spell_index.py:137-181
  IMPACT: Operation set is now a clean 2-family transaction taxonomy;
    create/destroy are not standalone transactions.
  NEXT: read TransactionStrategy base + BindTransactionStrategy + embargo
    try_acquire in SOURCE to confirm exact scope keys, then draft the
    NOTCH (and MOVE) strategy specs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T22:10:49Z
  TYPE: DECISION
  CLAIM: HANDOFF RECEIVED from mediator_builder_0 - the SpellIndex transaction
    BACKEND is landed + green (ticket 2026-06-14_spell_index_transactions_
    backend_task.md). Built: ChangeTransactionType.NOTCH/ADD_TO_INDEX/
    REMOVE_FROM_INDEX; Notch/AddToIndex/RemoveFromIndex TransactionStrategy
    (registered + mediator allow-listed); Spellbook entry methods notch_spell /
    add_spell_into_spellindex / remove_spell_from_spellindex (admit->seam->
    commit/abort); Conduit facades; claim-set seal unit tests (user-run green
    in 3.14t). THE SEAL (user-locked 2026-06-14): each op claims EXCLUSIVE the
    owning spellbook scope + owning conduit scope + the targeted binding key
    (add_to_index seals BOTH source+target); NO index scope key (spellbook-X
    already serializes every structural op on the book). MY PART = the three
    Spellbook `_apply_*` seams, currently NotImplementedError, run INSIDE the
    held race-safe window; commit-side fact baselines + dirty marking already
    done by base apply_commit_delta:
    - _apply_notch(spell_index, member): make member active; de-register
      outgoing active SHA + register incoming in id maps; bump Spell._door_epoch.
    - _apply_add_to_index(spell, source_index, target_index): detach from
      source, attach to target, GC source if emptied; rekey SHA maps + epoch.
    - _apply_remove_from_index(spell, source_index): detach from source, mint a
      fresh single-member index; rekey + epoch.
    Implementing these REQUIRES building the SpellIndex MULTI-MEMBER MODEL
    (today still single-member: `_active_spell` + `_versions` set, no member
    list). OPERATIONAL RISK (backend ticket): this mount intermittently
    truncates large-file writes mid-stream -> targeted edits only, py_compile
    re-verify, recover from git HEAD if nibbled.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-06-14_spell_index_transactions_backend_task.md:33-66
  - src/melder/aether/spellbook/spellbook.py:2539-2740
  - src/melder/aether/conduit/conduit.py:3405-3460
  IMPACT: Lane converts design -> implementation: build the multi-member
    SpellIndex model + wire the three seams into the ready transaction windows.
  NEXT: propose the implementation plan to the user; on approval build the
    member-store model + the three _apply_* seams + end-to-end tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T23:00:47Z
  TYPE: CONFLICT
  CLAIM: EXPLORATION (user: "do not fuck this up... maybe mismatches because it
    was treated like a lineage... explore everything"; NO EDITS). ROOT
    MISMATCH: the codebase treats `spell.spell_index.current` as a synonym for
    `spell.spell_id` (one index = one spell = one current version). True for the
    ACTIVE member; FALSE for dormant members. ~174 sites / ~48 files rely on it
    (mostly compiler/codegen reading the active spell's own current = safe), but
    the lifecycle/seam paths break it. CONCRETE MISMATCHES:
    M1 NOTCH-UNDERSPECIFIED (my earlier draft seam was WRONG/incomplete): the
    NotchTransactionStrategy only builds the seal + (base apply_commit_delta)
    stamps DEVOPS fact baselines; on_start/on_end are no-ops; it does NOT touch
    SpellSystemStates/Nexus/structural revalidation. So the SEAM must ALSO:
    (a) call SpellSystemStates.register_index(index) to move current_spell_id to
    the new active SHA, re-key _states_by_spell_id, and mark structural dirty
    (meld validity gates on `spell.spell_index.current` -> get_spell_validity ->
    _states_by_spell_id); (b) _publish_spell_record_to_nexus(new_active) because
    _register_owned_spell_id does NOT publish (953-972) while
    _unregister_owned_spell_id DID remove the old record (1090). My posted notch
    code omitted both -> would leave new active with stale validity + no Nexus
    record. DO NOT SHIP IT AS-IS.
    M2 transfer_of_ownership is HARD-WIRED 1:1: sets spell_index._active_spell =
    spell_obj directly (838-872,1383-1389), uses spell_index.current as the
    moved spell's id (843), relocates the WHOLE spell.spell_index between
    conduits -> on a multi-member index it moves all members / wrong id for a
    dormant member. Needs a decision: forbid transfer on multi-member indexes,
    or make transfer member-aware.
    M3 VERSION-REGISTRY OVER-SCAN: AethericFrame._version_registry rebuilt from
    SpellIndex.get_all_versions() (full _versions history) -> _check_for_spell
    reports dormant members' SHAs as "taken." Dormant must be invisible to
    availability -> active-only fix required.
    M4 register_index = the dirty+revalidate engine (marks structural change +
    dirty); unregister_index computes impact closure + marks dependents dirty +
    notifies RiskManager. Mint calls register_index; GC calls unregister_index.
    M5 MOVE must reassign spell.spell_index (settable slot 247; del 523) AND
    invalidate the moved spell's creation context + compiler artifacts
    (transfer does _cleanup_creation_context + cleanup_phase_artifacts +
    resolution_complete=False, 864-871) so it recompiles in its new context.
    SEAM RESPONSIBILITY (now precise): strategy = seal + devops baseline ONLY;
    the seam owns the FULL choreography - notch = active swap + id rekey + door
    epoch + register_index + Nexus publish; mint(remove_from_index) = bind's
    full registration block (3322-3388); GC(add_to_index emptied source) =
    cleanup_and_remove_spell's full block (538-560) minus cleaning the spell.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:985-997
  - src/melder/aether/spellbook/spellbook.py:953-972
  - src/melder/aether/spellbook/spellbook.py:1042-1090
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:246-298
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:838-895
  - .../transaction_manager/strategies/notch_transaction_strategy.py:1-220
  IMPACT: my posted notch seam is INCOMPLETE; do not implement any seam until
    the per-seam choreography (register_index/unregister_index + Nexus + frame
    registry + spell.spell_index reassign + artifact invalidation) is fully
    pinned and the transfer-vs-multi-member conflict (M2) is decided by user.
  NEXT: still to explore before writing move seams - ConduitCluster multi-member
    sharing on GC; contracted-spell multi-member; add/remove strategy bodies
    (confirm same seal-only pattern); exhaustive dormant-inertness in meld.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Design-only lane, owned by general_0 (cowork). EXPLORATION (no edits): root
mismatch = spell.spell_index.current treated as synonym for spell.spell_id
(lineage-era 1:1); breaks for dormant members. My earlier notch draft is
INCOMPLETE (missing register_index + Nexus publish). transfer_of_ownership is
hard-wired 1:1 (M2 - needs user decision). Strategy = seal + devops baseline
only; the SEAM owns the full register/unregister/dirty/Nexus choreography. Do
not write any seam until per-seam choreography pinned + M2 decided. HANDOFF:
mediator_builder_0
landed the 3-transaction SpellIndex backend (notch/add_to_index/remove_from_
index) with the user-locked spellbook+conduit+binding seal; general_0 owns the
three Spellbook `_apply_*` member-store seams (NotImplementedError today) which
require building the SpellIndex multi-member model. LOCKED MODEL: every spell
always in exactly one index (bind mints a default single-member index;
not opt-in); exclusive membership; index = resolver/grouping tool; each
spell keeps a unique binding; ONLY the active/notched member is live
(registered/resolvable/availability-counted), inactive members dormant
until notched; notch = current_spell (generalizes update()-rekey + door
epoch); bind/availability checks must scope to ACTIVE spells (today they
over-scan version HISTORY via get_all_versions union - VERIFIED); empty
index only valid inside a transaction -> move/notch/separate/GC are
transactional. Core ops: move(spell X->Y) [add=move-in, separate=move-to-
fresh-index] + notch. No src edits until the user approves the model. Map current
SpellIndex semantics across all consumers (partial migration - both
meanings live), then propose the split: SpellIndex = identity/registry;
lineage = ordered directory of spell mutations with a notch selector,
meld resolves the notched version. spell_id audit done (see 2026-06-13
FACT): spell_id = SHA binding-shape fingerprint = SpellIndex.current
(id-of-version); ULID = id-of-lineage; conflation seam is the stale
`spell.spell_id` attribute after `update()`. DECISION_REQUEST every fork.
No src edits until the user approves the map. Carry constraint: notch
must integrate with fast-door epoch invalidation; spell lineage must not
collide with conduit-ward lineage naming.
