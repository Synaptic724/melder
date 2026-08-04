# Task: Investigate SpellIndex Transfer Semantic Drift

## Metadata
- Task ID: TASK-2026-05-22-investigate-spellindex-transfer-semantic-drift
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-22T10:17:21Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Map the current semantic drift between `SpellIndex`, `Spell`, `Spellbook`, and
transfer-of-ownership code, then define the target split needed before runtime
cleanup starts.

## Ticket Contract
- ENTRY_GATE: the new epic/story are active and the board routes to this task
  for investigation.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/bind/spell_index.py`
  - `src/melder/aether/spellbook/spell.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  - directly related semantic investigation tickets/docs only when needed
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_index_runtime_grouping_semantics_task.md`
  - `codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md`
- EXIT_GATE: the current semantic drift and the target semantic split are both
  explicit enough to cut implementation tasks.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if current runtime behavior
  fundamentally conflicts with the user's rule that `SpellIndex` is index only.

## Scope Boundaries
- In scope:
  - current source semantics
  - target semantic split
  - implementation-slice planning notes
- Out of scope:
  - runtime cleanup edits
  - mutation socket API work
  - unrelated Crystallizer runtime changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a proper investigation-first
  lane and a real epic instead of more speculative discussion.

## Steps / Checklist
- [ ] Re-read `spell_index.py` with focus on identity vs attachment state.
- [ ] Re-read `spell.py` with focus on runtime stewardship state.
- [ ] Re-read `spellbook.py` with focus on registration and lookup maps.
- [ ] Re-read `transfer_of_ownership.py` with focus on what actually moves.
- [ ] Record the target semantic split and the first implementation cuts.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- evidence-backed semantic map of current drift
- target semantic split
- candidate implementation slices for cleanup

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-22_investigate_spellindex_transfer_semantic_drift_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Investigation only.

## Risks / Rollback Notes
- Risk: the current runtime mixes semantics more deeply than one cleanup pass
  can handle.
  Rollback: keep the task on semantic mapping only and cut smaller follow-up
  tasks instead of forcing one large redesign.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No pretending `SpellIndex` semantics are already cleaned up in runtime.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
- artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-22T10:17:21Z
  TYPE: FACT
  CLAIM: The current source mixes identification, registration, runtime
    stewardship, and version-selection semantics together. `SpellIndex` stores
    current-version and attachment fields, `Spell` separately stores conduit
    ownership, `Spellbook` separately owns owned and contracted spell-id maps,
    and transfer-of-ownership rewrites both the spell-side and index-side
    ownership fields in one move.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:32-41
  - src/melder/aether/spellbook/bind/spell_index.py:72-77
  - src/melder/aether/spellbook/bind/spell_index.py:113-173
  - src/melder/aether/spellbook/bind/spell_index.py:174-257
  - src/melder/aether/spellbook/spell.py:847-857
  - src/melder/aether/spellbook/spell.py:1007-1054
  - src/melder/aether/spellbook/spellbook.py:573-830
  - src/melder/aether/spellbook/spellbook.py:1362-1417
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:747-803
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1223-1342
  IMPACT: We need to define four separate semantic buckets before any runtime
    cleanup starts: pure index identity, spellbook registration, runtime
    stewardship, and mutation/version semantics.
  NEXT: turn those four buckets into the target semantic split and identify
    which current `SpellIndex` fields likely need to move out.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T10:17:21Z
  TYPE: FACT
  CLAIM: The current bind-time "does this spell already exist?" path is two
    layered checks, both driven by the new spell's SHA-based `spell_id` and
    normalized lookup key. `Bind._bind_logic(...)` always creates a fresh
    `SpellIndex` from the binding-profile fingerprint. `Spellbook.bind(...)`
    then first asks `Aether._check_for_spell(new_spell.spell_id, frame)`, which
    checks the frame's cached `_version_registry` and returns the `SpellIndex`
    advertising that version if found. Only after that does `Spellbook.bind(...)`
    enforce binding-signature uniqueness through `_assert_lookup_key_available(...)`
    before registering the new `SpellIndex` into `_lookup_spells` and the new
    `Spell` into `_spells`.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:241-301
  - src/melder/aether/spellbook/spellbook.py:2843-2875
  - src/melder/aether/aether.py:1243-1277
  - src/melder/aether/aetheric_frame/aetheric_frame.py:469-499
  - src/melder/aether/aetheric_frame/aetheric_frame.py:501-577
  - src/melder/aether/spellbook/spellbook.py:1362-1417
  IMPACT: In the current runtime, Aether-level "existence" means "a frame
    already has a registered SpellIndex that advertises this version id," not
    "the same lookup key is already bound." The lookup-key collision rule is a
    second, spellbook-local registration constraint.
  NEXT: use this split when defining which semantics belong to pure
    identification, which belong to frame-level version advertising, and which
    belong to spellbook registration ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T10:34:19Z
  TYPE: FACT
  CLAIM: The user's proposed extension point is bigger than transfer alone.
    Current runtime uses `SpellIndex.id` and `SpellIndex.current` far outside
    transfer-of-ownership: MutationResearch sessions are keyed by
    `SpellIndex.id` and cache `_root_version = target_index.current`, while
    Nexus publication and command lookup also carry `spell_index_id` alongside
    `owner_conduit_id`. So if transfer grows a "move this spell into another
    SpellIndex and delete the old index when empty" capability, we must define
    what happens to MutationResearch session anchoring, published spell
    records, command lookup by `spell_index_id`, and any old-index cleanup
    contract, not just the conduit/spellbook move.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:35-35
  - src/melder/mutation_research/mutation_research.py:111-111
  - src/melder/mutation_research/mutation_research.py:404-424
  - src/melder/mutation_research/mutation_research.py:427-506
  - src/melder/mutation_research/research/research.py:15-16
  - src/melder/mutation_research/research/research.py:39-41
  - src/melder/mutation_research/research/research.py:339-408
  - src/melder/nexus/frame_descriptor/spell_record.py:38-40
  - src/melder/nexus/frame_descriptor/spell_record.py:125-127
  - src/melder/nexus/frame_descriptor_manager.py:514-516
  - src/melder/nexus/rift/command_system/command_system.py:204-268
  - src/melder/nexus/rift/command_system/command_system.py:1379-1432
  IMPACT: The semantic cleanup has to define whether reindexing is:
    - a transfer operation
    - a mutation/version operation
    - or a separate reassociation operation
    because several subsystems already treat `spell_index_id` as a stable key.
  NEXT: define the candidate operation set explicitly:
    ownership transfer, reindex/reassociate, empty-index deletion, and
    downstream repair/update semantics for MutationResearch and Nexus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T10:34:19Z
  TYPE: DECISION
  CLAIM: The active investigation direction is now: keep the broad
    SpellIndex-management composition, extend `transfer_of_ownership` so a
    spell can be moved from one SpellIndex into another SpellIndex, delete the
    old index when it no longer contains any spells, and extend
    bind/spellbook/conduit to allow intentionally binding multiple spells under
    the same SpellIndex when the caller wants that categorization. Mutation
    branches and versions remain a separate system from this index-level
    grouping mechanic.
  EVIDENCE:
  - user_instruction: "we need to extend transfer_of_ownership to allow for transfering the underlying spell from 1 index to another"
  - user_instruction: "quite literally deleting the old index if it has no more spells in it"
  - user_instruction: "extend bind/spellbook/conduit to allow the user to bind multiple spells to the same index"
  - user_instruction: "mutation branches and versions are a seperate system"
  IMPACT: The investigation should stop trying to collapse SpellIndex into a
    pure one-spell slot and instead identify every current one-index -> one-spell
    assumption that blocks multi-spell grouping, transfer-to-new-index, and
    empty-index garbage collection.
  NEXT: map the exact one-index -> one-spell assumptions in Spellbook,
    Conduit, Aether, Nexus, and MutationResearch consumers so the follow-up
    implementation slices are concrete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T10:34:19Z
  TYPE: FACT
  CLAIM: A dedicated blast-radius artifact now exists for the proposed
    multi-spell-per-index and transfer-into-another-index mechanics. The
    artifact separates primary blockers from support helpers and downstream
    audit surfaces instead of leaving the sprawl only in ticket notes.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md:1-200
  IMPACT: The next turn can continue from one durable source of truth instead
    of replaying the cross-file search again.
  NEXT: keep widening the artifact with any newly discovered mechanics, then
    use it to cut bounded implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T10:34:19Z
  TYPE: FACT
  CLAIM: The broad sprawl pass shows the repo is not uniformly wrong. The
    current one-active-spell-through-`current` resolution story is mostly
    intact across Aether version advertising, current-version compiler/meld
    consumers, and Nexus read-side lookup. The real blockers are the singular
    spellbook storage/membership paths, singular contracted lookup paths, bind
    always minting a fresh index, transfer-of-ownership assuming same-index
    movement, the cluster helper reading singular spellbook storage, and
    SpellSystemStates carrying a one-owner-spellbook-per-index assumption.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md:42-42
  - codex/context_compass/artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md:63-152
  - codex/context_compass/artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md:154-200
  IMPACT: The cleanup can stay bounded. We do not need to treat every
    `spell_index.current` consumer as broken. We need to focus on membership,
    transfer, and owner-bookkeeping mechanics.
  NEXT: convert the blocker list into concrete implementation slices instead of
    widening the audit much farther.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T10:34:19Z
  TYPE: FACT
  CLAIM: `ConduitCluster` is not properly current-aware yet for a
    multi-spell-per-index model. It still resolves one spell from an index via
    `book._spells.get(spell_index)` and then uses that resolved spell's
    `spell.spell_id` as the cluster-root contract source. If one index manages
    many spells internally, cluster sharing/removal should resolve the active
    spell for that index explicitly instead of depending on singular spellbook
    storage. Separately, your reindex direction implies a built-in invalidation
    step: moving a spell into another index should gate that slot by default so
    the target-side spell is revalidated before normal trust resumes.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:438-470
  - src/melder/aether/conduit/conduit_cluster.py:490-517
  - src/melder/aether/conduit/conduit_cluster.py:545-561
  - codex/context_compass/artifacts/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md:173-193
  - user_instruction: "when the spell is notched into another index it should revalidate the spell"
  IMPACT: The implementation slices need at least one current-aware cluster
    resolver fix and one built-in reindex invalidation/revalidation rule, not
    just spellbook membership rewrites.
  NEXT: carry both mechanics into the follow-up implementation task plan after
    the semantic investigation closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T10:34:19Z
  TYPE: FACT
  CLAIM: `SpellIndex._owner_spell` has only two real runtime uses today. First,
    `SpellIndex.update(...)` reads it only to pass the concrete owner spell
    into `owner_spellbook._update_owned_spell_id(old_id, new_id, owner_spell)`.
    Second, `TransferOfOwnership._flip_registry_and_spellbooks(...)` reads it
    only as a sanity check before restamping the field back to the same live
    `spell_obj`; rollback also rewrites it directly. There are no broader read
    consumers elsewhere in src. So the field is currently acting as an owner-map
    maintenance convenience and transfer assertion field, not as a deep runtime
    truth surface.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:152-168
  - src/melder/aether/spellbook/bind/spell_index.py:174-200
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:797-799
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1332-1340
  - source_scan: `rg -n "_owner_spell\\b" src`
  IMPACT: This field looks like a good small seam to clean up early because its
    blast radius is narrow and well-defined.
  NEXT: decide whether to replace `_owner_spell` with explicit spellbook map
    maintenance inputs in `SpellIndex.update(...)` and transfer paths, or keep
    it temporarily until the broader membership mechanics are in place.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T13:46:49Z
  TYPE: FACT
  CLAIM: `Spell.owned_spell` appears to be a write-only runtime flag today.
    In live `src`, it is initialized to `None`, set to `True` when
    `_add_owned_conduit(...)` stamps conduit ownership, and deleted during
    cleanup. I did not find a runtime branch in `src` that reads
    `spell.owned_spell` to make behavior decisions. The remaining `src` grep
    hit is only a local variable named `owned_spell` in `ConduitWard`, not the
    field. Actual reads are in tests and test stubs.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:389-389
  - src/melder/aether/spellbook/spell.py:520-522
  - src/melder/aether/spellbook/spell.py:1049-1052
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2844-2852
  - source_scan: `rg -n "\\bowned_spell\\b|\\.owned_spell\\b" src/melder -g "*.py"`
  - source_scan: `rg -n "\\bowned_spell\\b|\\.owned_spell\\b" tests -g "*.py"`
  IMPACT: `owned_spell` looks like a legacy convenience flag rather than a
    live runtime contract. If we clean it up later, the real fallout is
    mostly tests, not active runtime behavior.
  NEXT: decide whether to keep `owned_spell` as documentation-only state or
    remove it entirely in a narrow cleanup slice after the current index work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T14:20:53Z
  TYPE: FACT
  CLAIM: Notching an active spell forward is already conceptually a multi-book
    propagation step in current code. `SpellIndex.update(...)` captures the
    owner spellbook plus every contracted spellbook attachment, updates the
    local `current` pointer first, then calls
    `_update_owned_spell_id(old_id, new_id, active_spell)` on the owner
    spellbook and `_update_contracted_spell_id(conduit_id, old_id, new_id, spell)`
    on every contracted spellbook. That means the runtime already expects a
    "one notch affects every book consuming this index" mechanic; what it lacks
    is an explicit transaction boundary around that propagation.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:155-171
  - src/melder/aether/spellbook/spellbook.py:618-706
  - src/melder/aether/spellbook/spellbook.py:806-906
  IMPACT: Any future active-spell flip, reindex, or version-notch mechanic
    should be modeled as a transaction that updates owner and contracted books
    together or fails/rolls back coherently. Otherwise the system can split
    state across consuming spellbooks.
  NEXT: keep transactionality as a first-class requirement in the transfer and
    active-spell-flip design, not as a later cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T16:05:00Z
  TYPE: FACT
  CLAIM: The repo already has a real change-control transaction stack that
    bind/scan are expected to use, and it is stronger than the current
    transfer path. `Spellbook.begin_transaction(...)` admits one immutable
    `ChangeControlTransactionRequest` through `ChangeControlManager`,
    opens the local binding window only for `BIND`, and explicitly states that
    scan is not its own transaction type and must run inside a bind
    transaction. `Conduit.begin_transaction(...)` is a conduit-scoped wrapper
    that adds conduit participation/scope rules, then delegates into the same
    Spellbook transaction path. Underneath that, the transaction manager builds
    immutable request payloads, the orchestrator serializes admission,
    creates/stores a staged mutation record, and commit/abort flow through
    registered validator/dirty-marker/commit-hook/abort-hook dispatch. By
    contrast, `TransferOfOwnership` currently manages rollback, incident
    reporting, and change intent itself without entering the public
    `transaction(...)` wrapper.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2133-2421
  - src/melder/aether/spellbook/spellbook.py:2423-2500
  - src/melder/aether/conduit/conduit.py:1812-2064
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:10-137
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py:31-462
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:308-818
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:252-551
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1-520
  IMPACT: We do not need to invent a second transaction framework for
    transfer-of-ownership. The likely implementation seam is to route transfer
    through the existing `TRANSFER_OWNERSHIP` request type so it gains
    admission, staged metadata, commit validation/hooks, and abort cleanup from
    the same system that already governs bind/scan and link flows.
  NEXT: trace the transfer-specific change-intent and rollback hooks in
    `TransferOfOwnership`, then compare them against the existing
    change-control staged metadata and hook surfaces to decide what should move
    into commit/abort hooks versus what should remain local to the transfer
    helper.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T16:18:00Z
  TYPE: FACT
  CLAIM: `TRANSFER_OWNERSHIP` is currently only a generic transaction type
    placeholder in the change-control system; there is no transfer-specific
    admission, staged-metadata, validator, dirty-marker, or abort behavior
    wired into that layer yet. The current ownership-move implementation
    instead uses only `register_pending_change(...)` /
    `clear_pending_change(...)` as a best-effort breadcrumb and then keeps its
    own rollback stack, lineage disable/lift logic, and incident reporting
    locally inside `TransferOfOwnership`.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:10-37
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:139-153
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:818-916
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/staged_mutation.py:1-87
  - src/melder/aether/conduit/conduit.py:1812-2064
  - src/melder/aether/conduit/conduit.py:2325-2356
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2921-2984
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:261-340
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:666-747
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1660-1737
  IMPACT: Hooking transfer into the transaction system is mostly an integration
    problem, not a missing-foundation problem. We need to define the transfer
    request shape and decide which current local behaviors become:
    - staged metadata updates
    - commit validation/hook work
    - dirty-marker work
    - abort-hook recovery
    versus what should remain inside the transfer helper as the actual runtime
    body.
  NEXT: cut the hook split explicitly by tracing the current transfer phases
    against the transaction lifecycle: admit -> stage -> execute body -> commit
    hooks -> abort hooks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T16:32:00Z
  TYPE: FACT
  CLAIM: A transfer transaction does not need multiple independent owners, but
    it does need multiple participants in its request scope. The current
    transaction model already supports one owner request covering many conduits
    and many scope surfaces through `conduit_ids`, `scope_keys`,
    `binding_keys`, and `contract_keys`. Conflict and embargo checks operate
    on those normalized scopes, not on "who opened the context manager." This
    is exactly how link and cluster-link flows involve peer conduits today. The
    gap for transfer is narrower: the request payload only has one first-class
    `spellbook_id`, so source-side ownership is modeled directly, but
    target-side and borrower-side spellbook participation would need to be
    carried via extra scope keys and/or transfer-specific metadata.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1812-1958
  - src/melder/aether/conduit/conduit_cluster.py:365-511
  - src/melder/aether/spellbook/spellbook.py:2133-2297
  - src/melder/aether/spellbook/spellbook.py:2652-2704
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:41-99
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py:224-328
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/conflict_manager/conflict_manager.py:44-81
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:222-334
  IMPACT: The right design is one source-owned `TRANSFER_OWNERSHIP`
    transaction whose request explicitly includes:
    source conduit, target conduit, and any borrower/cluster participants that
    will be mutated; plus scope keys for both spellbooks, the transferred
    binding slot, affected contract slots, and any affected cluster scope. We
    do not need multiple top-level transactions, but we do need a richer
    transfer request shape than the current local helper is producing.
  NEXT: define the exact transfer request payload and decide whether the
    current schema can carry it with metadata/scope keys or whether we need a
    first-class schema extension for transfer participants.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T16:44:00Z
  TYPE: FACT
  CLAIM: The cluster layer has two different mutation classes and they should
    not be treated the same. There are local cluster-state mutations and there
    are live cross-conduit contract mutations. The local cluster-state
    mutators are:
    `ConduitCloud.create_cluster(...)`, `delete_cluster(...)`,
    `add_conduit_to_cluster(...)`, `remove_conduit_from_cluster(...)`,
    `refresh_cluster_shares_for_conduit(...)`, plus the underlying
    `ConduitCluster.add_member(...)`, `remove_member(...)`,
    `add_shared_spell(...)`, and `remove_shared_spell(...)`. The live
    cross-conduit contract mutators are:
    `ConduitCluster.handle_join(...)`, `handle_leave(...)`,
    `refresh_member_shares(...)`, `add_and_share_spell(...)`,
    `remove_and_strip_spell(...)`, `share_to_borrower(...)`, and
    `remove_shared_from_borrower(...)`. Current code only wraps the contract
    mutations in conduit transactions, and even there it uses `LINK`, not
    `CLUSTER_LINK`. Membership and shared-root registry mutations currently
    happen as raw local state updates with only the cluster lock.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:309-410
  - src/melder/aether/conduit/conduit_cluster.py:124-176
  - src/melder/aether/conduit/conduit_cluster.py:202-240
  - src/melder/aether/conduit/conduit_cluster.py:241-287
  - src/melder/aether/conduit/conduit_cluster.py:304-326
  - src/melder/aether/conduit/conduit_cluster.py:327-380
  - src/melder/aether/conduit/conduit_cluster.py:381-437
  - src/melder/aether/conduit/conduit_cluster.py:438-524
  - src/melder/aether/conduit/conduit_cluster.py:579-589
  - src/melder/aether/conduit/conduit.py:1865-1868
  - src/melder/aether/spellbook/spellbook.py:2172-2175
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:33-37
  IMPACT: If we want cluster behavior to be transaction-correct, the
    transaction boundary must cover both classes of mutation, not just the
    borrower contract writes. In practical terms, the high-value operations
    that need top-level transaction treatment are:
    cluster create, cluster delete, member join/add, member leave/remove,
    shared-spell add/share, shared-spell remove/strip, and explicit refresh
    that repushes shares. The current `CLUSTER_LINK` transaction type is
    defined but not used by the cluster runtime.
  NEXT: decide whether cluster membership/shared-root operations should be
    promoted into a real `CLUSTER_LINK` transaction path, or whether they stay
    local state under one larger higher-level transfer/cluster transaction that
    explicitly wraps both the registry mutation and the downstream link
    mutations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T15:44:12Z
  TYPE: DECISION
  CLAIM: If we improve transaction recursion, the correct model is not
    arbitrary nested transactions. The current scalar `_active_change_request`
    on Spellbook should become one admitted root request plus a local nested
    frame stack for the same logical operation. Child operations should join
    the root request when compatible, widen staged metadata/scopes as needed,
    and only the outermost frame should actually commit or abort. Capability
    gates should replace exact-type gates for internal mutation helpers:
    transfer should stay a `TRANSFER_OWNERSHIP` root transaction for audit and
    admission, but it should be permitted to perform nested link- and
    cluster-share-class mutations without re-admitting a second top-level
    request.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2133-2359
  - src/melder/aether/spellbook/spellbook.py:2423-2704
  - src/melder/aether/conduit/conduit.py:1797-2064
  - src/melder/aether/conduit/conduit.py:3193-3283
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:302-503
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/conflict_manager/conflict_manager.py:44-81
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:222-406
  IMPACT: The current front-door gating is too coarse for transfer and cluster
    operations because it only supports one active request and exact-type
    expectations. A root-request + child-frame model would let:
    - `LINK` join `LINK`
    - transfer root transactions perform nested contract/cluster-share work
    - bind/scan keep their explicit bind window
    while still rejecting incompatible nested operations like unrelated bind
    during transfer.
  NEXT: map the capability matrix explicitly (`bind`, `contract_mutation`,
    `cluster_membership_mutation`, `cluster_share_mutation`,
    `ownership_transfer`) and decide which transaction roots grant which child
    capabilities.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T15:52:00Z
  TYPE: FACT
  CLAIM: `SpellSpace` already demonstrates the better recursion pattern for
    this repo: the recursive state does not live on the `SpellSpace` object,
    it lives on a conduit-owned `ContextVar` stack. `Conduit.enter_spellspace()`
    pushes a newly created `SpellSpace` onto `self._spellspace_stack`, nested
    spellspaces are therefore naturally supported by stack depth, and only the
    top entry is active. `SpellSpace.meld(...)` enforces correctness by asking
    the injected `Creations` manager for the current active spellspace, and
    `Creations` reads that from the same context-local stack. That means the
    recursion model is already: one shared owner context, nested frames, top-of-
    stack active semantics, and context-local isolation instead of one global
    scalar flag.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:246-247
  - src/melder/aether/conduit/conduit.py:587-596
  - src/melder/aether/conduit/conduit.py:663-695
  - src/melder/aether/conduit/spell_space/spell_space.py:17-41
  - src/melder/aether/conduit/spell_space/spell_space.py:135-170
  - src/melder/aether/conduit/creations/creations.py:40-50
  - src/melder/aether/conduit/creations/creations.py:581-587
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:1-250
  IMPACT: Transactions should copy this architecture instead of continuing
    with `_active_change_request` plus `_binding_transaction_active`. The right
    shape is a conduit/spellbook-owned context-local transaction frame stack
    over one root admitted request, with top-of-stack active capability checks.
  NEXT: derive the transaction redesign directly from the spellspace pattern:
    replace scalar active state with a context-local stack frame model and then
    attach root-request metadata plus capability grants to each frame entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the first investigation lane for cleaning up SpellIndex,
transfer-of-ownership, and version semantics. It exists to map current source
truth before the runtime cleanup is cut into implementation slices.

