# Task: Prove or retract the residual cross-object lock gaps and fix the real ones

## Metadata
- Task ID: TASK-2026-10-11-prove-and-fix-cross-object-lock-gaps
- Story: none (follow-up of TASK-2026-10-11-close-remaining-spell-map-races, its Note 13 items a-c)
- Status: done
- Owner: claude (directed by the owner 2026-10-11)
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-11T17:10:00Z
- Updated: 2026-10-12T21:14:45Z

- Completed: 2026-10-12T21:14:45Z
- Summary: Landed, notched 0.2.8231: index-link notifications, contract reads and bind's cross-frame sweep hold under
  concurrent link/sever, member moves and frame birth/teardown, and the listing deadlock is gone; release note
  'Index links, contract reads and binds across frames hold up under concurrent changes'. Turned in 2026-10-12.

## Objective
Take the three architecture-level residuals of the predecessor's Note 13 - (a) Conduit.cleanup_spell's walk of the
ward's contracts against link/sever, (b) a borrower's contract inspection against the owner's index moves and
destroys, (c) bind's cross-frame duplicate sweep against frame birth and detach - and for each either prove it
through the locks and mediators the real operations take or retract it. Explain each as a concrete situation. Fix
the ones that hold, cleanup_spell first, with the smallest change that holds, and land through the patch lane.

## Owner Direction
Owner, chat 2026-10-11, after the predecessor's Note 13:
- "your going to have to prove bind can fail with 2 or more frames because the mediator exists so you better not be
  on some mission to make perfection happen"
- "also sever link and link also use mediator so your not really winning here explain your failures using proper
  situations, fix the real races but your bind argument needs a lot of proof explain that like cleanup spell should
  use spells own lock properly so fix that for sure"
- Later, mid-implementation: "make sure you properly do this because there might be data structures where you
  do not need to snapshot at all and you can just grab the data from a single O(1) instead of O(n) request" and
  "because your snapshots always lead to extra latency in the system due to its process" (Note 7).
In scope: (a)-(c). Out of scope unless the owner adds them: (d)-(g) of Note 13 (wording, a live view, dead code).

## Ticket Contract
- ENTRY_GATE: owner direction (chat, 2026-10-11); this ticket and its attention_board.md row exist before the next
  investigation tranche. The (c) interleaving probe ran before this ticket existed and is recorded as its Note 1.
- EXECUTION_BOUNDARY: read src/melder for (a)-(c); reproduce in scratch copies under /tmp through public operations
  and the real locks and mediators only (a probe may pause a thread at a point it already passes, to make a window
  deterministic, never skip a lock or a claim); fix in scratch; land through the patch lane (patch docs, src, tests,
  docs, notch, release note, graph, assets and llm_support last) after the new tests and the full tree pass. No
  commit or push.
- DEPENDENCIES: working tree = 3d184cac plus the uncommitted 0.2.8229 and 0.2.8230 landings (predecessor tickets in
  review).
- EXIT_GATE: each item proven through real admission and locks or retracted with evidence; the proven ones fixed
  with regression tests and landed with the checks green.
- FAILURE_ESCALATION: DECISION_REQUEST for a new lock-order edge, a transaction-type change or a public contract
  change; BLOCKER if the VM disk (attention_board.md, Device VM disk) stops validation.

## Scope Boundaries
- In scope: Conduit.cleanup_spell, its Spellbook path and ConduitWard._emit_index_destroy against the writers of the
  ward's _contracts (ConduitWard._link, _sever_link); ConduitWard._get_spell_in_contracts against the contract
  detail-map writers; Aether._check_for_spell and _get_all_spell_ids against _ensure_frame_locked, _create_frame and
  _detach_cleaned_frame.
- Out of scope: (d)-(g) of the predecessor's Note 13; D-10, D-11, D-20; MelderOps code; the meld path.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (a), (b), (c), (c2) and the listing deadlock proven and landed as 0.2.8231 with checks green;
  acceptance, commit and push are the owner's. (Earlier: draft -> in_progress on the owner's chat direction.)
- from_state: review
- to_state: done
- transition_reason: (2026-10-12T21:14:45Z) the owner turned in every finished melder_1 ticket (chat 2026-10-12: "just close everything you finished");
  git add -A, commit, push, the Windows tiers and hosted CI remain the owner's.

## Steps / Checklist
- [x] (c): deterministic interleaving through real frame creation, an unforced stress, and a read of what bind and
      frame creation hold.
- [x] (a): read cleanup_spell, _emit_index_destroy and link/sever with their transactions and locks; prove or retract.
- [x] (b): read _get_spell_in_contracts and the detail-map writers; prove or retract.
- [x] Report each item to the owner as a concrete situation, proven or retracted (turn-in report, chat).
- [x] Patch docs for the proven items and the mapping note; scratch fix; red/green; full tree.
- [x] Land as the next notch (0.2.8231); assets and llm_support rebuilt last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A proof or a retraction per item; fixes with regression tests for the proven ones; the landed change set.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit_ward/conduit_ward.py, src/melder/aether/conduit/conduit.py,
  src/melder/aether/spellbook/spellbook.py, src/melder/aether/aether.py,
  src/melder/aether/aetheric_frame/aetheric_frame.py, src/melder/__version__.py
- tests: three new files (tests/unit/melder/aether/test_aetheric_frame_cleanup_race.py,
  tests/component/melder/aether/test_aether_component_frame_sweep_races.py,
  tests/component/melder/aether/conduit/test_conduit_component_lock_gaps.py) and two updated
  (tests/unit/melder/aether/test_aetheric_frame.py,
  tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py)
- release_docs/next_version_release.md; system_docs src_architecture, src_components, their indexes and the graph
- generated: src/melder/_build_assets manifests and payloads, llm_support bundles
- context_compass/artifacts/cross_object_lock_gaps_20261011/ (evidence)

## Validation
- New tests red on base and green on cand at gil=0 and gil=1, 30/30 repeats, the full tree at gil=0 on cand (Note 11);
  post-landing unit_arch/llm/build/gh/top and the new and updated files on the landed tree; graph, assets and
  llm_support checks OK (Note 13). Not run: the full tree at gil=1, the Windows tiers, hosted CI, coverage.

## Risks / Rollback Notes
- A lock added to cleanup_spell or to the frame sweep must not add a lock-order edge; measure it before landing.

## Applicable Anti-Patterns
- [x] No sleep-based reproduction presented as deterministic.
- [x] No reproduction that skips a lock, a claim or a transaction the real operation takes.
- [x] No behaviour claim from a search hit alone.
- [x] No defensive guard without contract evidence.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner turn-in, 2026-10-12)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/cross_object_lock_gaps_20261011/
  - system_docs/patches/completed/cross_object_lock_gaps_2026_10_11/ (five patch docs, archived at landing)
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch docs, at landing)
- CLEANUP_TRIGGER: patch docs promoted and archived at landing; evidence decided at turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: free-threaded dict iteration; which lock or claim each writer and reader holds
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes

- DATETIME: 2026-10-11T17:24:00Z
  TYPE: FACT
  CLAIM: Item (c), read through: nothing a frame birth or detach takes orders against bind's cross-frame sweep.
    Spellbook.bind runs inside a transaction admitted by the binding frame's OWN DevOps TransactionMediator
    (begin_transaction -> _get_required_transaction_mediator -> that frame's ChangeControlManager); its collision
    check calls Aether._check_for_spell, which, with two or more frames under process-wide ids (the default), walks
    self._aetheric_frames.items() live with no Aether lock and no plane claim (_get_all_spell_ids does the same).
    Frame birth (Spellbook(aetheric_frame=<new>) -> Aether._ensure_frame) takes the aetheric plane's FRAME_CREATE
    claim (world IX + frame:<name> X) and inserts under the Aether lock; detach (AethericFrame.cleanup ->
    _detach_cleaned_frame) pops under the Aether lock only. Bind holds no plane claim and never takes the Aether
    lock, so the two mediators never meet. AethericFrame.has_spell also checks cleaned before taking the frame lock
    while cleanup deletes _selected_spell_registry under it - the SpellIndex.has_spell shape fixed in 0.2.8230.
  EVIDENCE:
  - src/melder/aether/aether.py:2523-2583
  - src/melder/aether/aether.py:2762-2808
  - src/melder/aether/spellbook/spellbook.py:5337-5400
  - src/melder/aether/spellbook/spellbook.py:3652-3664
  - src/melder/aether/spellbook/spellbook.py:4298-4370
  - src/melder/aether/aether.py:1187-1302
  - src/melder/aether/aether.py:1332-1376
  - src/melder/aether/aether.py:405-464
  - src/melder/aether/aetheric_frame/aetheric_frame.py:229-265
  - src/melder/aether/aetheric_frame/aetheric_frame.py:274-345
  - src/melder/aether/aetheric_frame/aetheric_frame.py:853-878
  IMPACT: The mediator does not protect this walk: the plane serializes frame creation against whole-world work and
    same-name births, and the frame-local mediator serializes one frame's mutations; the sweep belongs to neither.
  NEXT: Measure it: a deterministic interleaving through real frame creation, then an unforced stress.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T17:24:00Z
  TYPE: MEASURE
  CLAIM: Item (c) is real. Deterministic: with the binder paused inside the sweep (after the real has_spell of
    frame-b; nothing skipped), a Spellbook for frame-c is constructed on another thread through the public
    constructor (plane claim + Aether lock) and completes while the binder waits; on resume bind raises
    RuntimeError('dictionary changed size during iteration') on -X gil=0 and gil=1, and ServiceA is not registered.
    Unforced (nothing patched or paused), 3000 binds into frame-a beside frames a and b, 3 runs each: births only
    (1000 new tenant frames) - gil=0 266-286 binds fail with that error, gil=1 none; births with each frame cleaned
    straight after (frame count stays ~3) - gil=0 69-78 fail ("AethericFrame has already been cleaned." 66-73, the
    size error 3-4, and AttributeError "... no attribute '_selected_spell_registry'" once in two runs), gil=1 159 in
    one run of three. Every run registered + failures == 3000: a failed bind publishes nothing.
  EVIDENCE:
  - context_compass/artifacts/cross_object_lock_gaps_20261011/c_interleaving_probe.py:1-80
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/c_interleaving_gil0.log:1-5
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/c_interleaving_gil1.log:1-5
  - context_compass/artifacts/cross_object_lock_gaps_20261011/c_unforced_stress.py:1-72
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/c_unforced_grow_gil0.log:1-6
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/c_unforced_churn_gil0.log:1-6
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/c_unforced_churn_gil1.log:1-6
  IMPACT: Situation: a server with one frame per tenant binds late spells for tenant A while tenant B is onboarded
    (its first Spellbook births its frame) or a Nexus-managed frame collapses; tenant A's bind fails with an error
    unrelated to its own spell. It fails clean (a retry binds), it needs two or more frames, and it is off the meld
    path. Fix shape: both sweeps iterate a one-call snapshot and skip frames that read cleaned, with a cleanup-safe
    frame probe like SpellIndex._has_spell_unless_cleaned.
  NEXT: Read item (a): Conduit.cleanup_spell, ConduitWard._emit_index_destroy, _link and _sever_link and the
    transactions and locks each takes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T17:31:00Z
  TYPE: FACT
  CLAIM: Item (a), read through against the mediator. The frame mediator does serialize LINK/UNLINK against NOTCH,
    ADD_TO_INDEX and REMOVE_FROM_INDEX (each claims the participant conduits EXCLUSIVE; the index verbs also claim the
    spellbook EXCLUSIVE, link INTENT). But the owner-side index emissions that walk the owner ward's contract registry
    run OUTSIDE every transaction window: notch_spell, add_to_spell_index and remove_from_spell_index call
    end_transaction and only then _emit_index_notch / _emit_index_member_added / _emit_index_member_removed /
    _emit_index_destroy; bind_inactive emits member-added after its bind window; and cleanup_spell has no transaction at
    all (Spellbook.cleanup_spell: "not yet sealed by a mediator transaction"). All four emissions iterate
    self._contracts.values() with no ward lock, while link (_create_new_contract) and sever (_remove_contract) write
    that dict under SafeGuard of both ward locks and _get_links reads it under the ward lock. Conduit.cleanup_spell
    also reads spell.spell_index and the index's membership with no lock before the Spellbook re-decides under the Book
    lock, so a second call on a disposed spell raises AttributeError. Lock orders in force: ward -> contract -> Book
    (sever), ward -> Book (link), spell -> Book (Spell.cleanup); spellbook.py never takes a ward lock.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5320-5409
  - src/melder/aether/conduit/conduit.py:5410-5487
  - src/melder/aether/conduit/conduit.py:5488-5550
  - src/melder/aether/conduit/conduit.py:5551-5584
  - src/melder/aether/conduit/conduit.py:3960-3974
  - src/melder/aether/spellbook/spellbook.py:4184-4296
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2368
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2369-2405
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2479-2524
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:858-951
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1051-1146
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1329-1342
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py:40-80
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:250-269
  - src/melder/aether/spellbook/spell.py:550-645
  IMPACT: The owner's point holds for the transactions themselves; it does not reach the emissions, which run after
    the window closes, nor cleanup_spell, which never opens one. Fix: the emissions walk under the ward's own lock
    (the order link and sever already take); cleanup_spell reads the spell under its own lock and emits only what the
    Spellbook actually destroyed.
  NEXT: Read item (b) the same way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T17:31:00Z
  TYPE: FACT
  CLAIM: Item (b), read through. ConduitWard._get_spell_in_contracts (public Conduit.get_spell_in_contracts) and
    _get_spells_in_contract_by_conduit (public get_spells_in_contract_by_conduit, and the by-name variant) walk a
    contract's per-spell detail maps holding only the CALLER's ward lock and no transaction. The owner writes its
    detail map under the contract lock (_uncontract_member_spell, the contract transactions) or with no lock at all
    (_contract_member_spell, reached from _emit_index_member_added after the owner's window), and cleans a removed
    Detail after releasing the contract lock - so the reader can meet a resize, a cleaned Detail, or a Detail whose
    fields cleanup has deleted.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3504-3564
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3565-3640
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2407-2478
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:237-300
  - src/melder/aether/conduit/conduit.py:6836-6859
  IMPACT: Readers must hold the contract's own lock while they walk its detail maps, and the one unlocked writer must
    take it; ward -> contract is the order sever already takes.
  NEXT: Measure (a) and (b) through the public verbs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T17:31:00Z
  TYPE: MEASURE
  CLAIM: Items (a) and (b) are real. Deterministic (one thread paused after a real read inside its walk; the other
    side is a public verb admitted by the mediator), -X gil=0 and gil=1 alike: cleanup_spell of a sole member while
    owner.link(C) is admitted mid-walk raises 'dictionary changed size during iteration' after the spell is disposed,
    and borrower B still tracks the destroyed index and keeps its IndexDetail; notch_spell with two index-linked
    borrowers raises the same after its NOTCH transaction committed, and borrower B2 is left with NO active copy of
    the lineage (the old head was parked by _deactivate_borrowed_spell, the new one never delivered); a borrower's
    get_spell_in_contracts raises the same while the owner stages a member onto the linked index. Unforced, 20 s each:
    notch vs link/sever churn - gil=0 41 of 94,247 notches fail, gil=1 none of 82,211; inspection vs stage/split -
    gil=0 42,305 failures plus "Detail has already been cleaned." x15 and AttributeError on Detail x8, gil=1 168 +
    20 + 4 ("dictionary keys changed during iteration"). A second cleanup_spell of a disposed spell raises
    AttributeError "'Spell' object has no attribute 'spell_index'".
  EVIDENCE:
  - context_compass/artifacts/cross_object_lock_gaps_20261011/a_interleaving_probe.py:1-143
  - context_compass/artifacts/cross_object_lock_gaps_20261011/b_interleaving_probe.py:1-104
  - context_compass/artifacts/cross_object_lock_gaps_20261011/ab_unforced_stress.py:1-146
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/a_cleanup_gil0.log:1-6
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/a_notch_gil0.log:1-5
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/b_gil0.log:1-3
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/ab_unforced_notch_vs_link_gil0.log:1-2
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/ab_unforced_inspect_vs_stage_gil0.log:1-2
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/ab_unforced_inspect_vs_stage_gil1.log:1-2
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/ab_double_cleanup_gil0.log:1-1
  IMPACT: (a) leaves borrowers out of step with the owner's lineage - a dead index still subscribed, or a borrower
    with no active copy - and the verb raises after its change committed; (b) is a spurious read failure. None is on
    the meld path. All three of the predecessor's architecture-level residuals are proven; none is retracted.
  NEXT: Write the patch docs (cross_object_lock_gaps_2026_10_11) and the implementation mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T17:33:00Z
  TYPE: PLAN
  CLAIM: Patch docs written and consumed (cross_object_lock_gaps_2026_10_11: architecture, three component patches,
    code description). Mapping: invariant 1 -> the four owner-side emissions walk under the ward lock -> cleanup_spell
    and notch_spell paused mid-emission while owner.link(C) runs (the link must wait; no error; borrowers consistent);
    invariant 2 -> contract-lock walks in _get_spell_in_contracts and _get_spells_in_contract_by_conduit plus the locked
    _contract_member_spell write -> get_spell_in_contracts paused mid-walk while the owner stages a member;
    invariant 3 -> Spellbook._dispose_spell decides under the Book lock and returns the destroyed index id, Conduit
    emits exactly that -> second cleanup_spell raises the new RuntimeError, F9 cascade unchanged; invariant 4 ->
    snapshot frame sweeps with cleanup-safe frame probes -> bind paused mid-sweep while a frame is born and while one
    is cleaned, probe unit tests; invariant 5 -> no new lock-order kind (read off the code), full tree without a hang.
    Order: scratch copies (base, cand) of the working tree, new tests red on base, src on cand, green, full tree,
    then landing as 0.2.8231 in one change set.
  EVIDENCE:
  - context_compass/system_docs/patches/active/cross_object_lock_gaps_2026_10_11/architecture_patch.md:1-63
  - context_compass/system_docs/patches/active/cross_object_lock_gaps_2026_10_11/code_description_patch_lock_gaps.md:1-25
  IMPACT: Implementation and tests are fixed before code is written; no transaction type and no public signature
    changes, so no decision is needed before landing.
  NEXT: Copy the working tree to /tmp/cc_lock/{base,cand} and write the new tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T17:51:00Z
  TYPE: DECISION
  CLAIM: Owner, chat 2026-10-11, mid-implementation: "make sure you properly do this because there might be data
    structures where you do not need to snapshot at all and you can just grab the data from a single O(1) instead of
    O(n) request" and "your snapshots always lead to extra latency in the system due to its process". Rule for this
    lane: no read-side copy where the reader can hold the writers' lock for its walk or answer by key; where a walk
    must cover a collection whose writers it cannot lock out (frames: frame cleanup holds the frame lock and then
    the Aether lock), the writers publish an immutable view on their rare write and readers take it in one read.
    Applied: the frame sweep reads a tuple Aether republishes on frame birth and detach (no per-bind copy);
    get_spell_in_contracts tries the detail keyed by the id (O(1)) before the lineage walk; the contract listing
    walks the detail maps under the contract lock and resolves each id by key through the Book (O(1)
    find_spell_by_id outbound; the per-peer lookup inbound) instead of copying keys; the ward emissions keep holding
    the ward lock (no copy). The 0.2.8230 snapshots are not reworked here.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-11_prove_and_fix_cross_object_lock_gaps_task.md:20-31
  - src/melder/aether/aetheric_frame/aetheric_frame.py:229-271
  - src/melder/aether/aether.py:405-464
  IMPACT: The 0.2.8231 cut changes shape before landing; patch docs and tests follow.
  NEXT: Prove the deadlock found while reworking the contract listing, then re-cut the change set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T17:51:00Z
  TYPE: MEASURE
  CLAIM: Found while reworking the contract listing and proven: Conduit.get_spells_in_contract_by_conduit deadlocks
    with sever_link (or link) on the same conduit. The listing holds the ward lock and resolves inbound spells through
    Conduit.find_contracted_spell, which takes the conduit lock; sever takes the conduit lock first and the ward locks
    second. With the lister paused just after taking the ward lock and borrower.sever_link(owner) started (admitted by
    the mediator), on 0.2.8230 both threads are still blocked 5 s after release, -X gil=0 and gil=1. Resolving by key
    through the Book (no conduit lock) removes the inverted edge.
  EVIDENCE:
  - context_compass/artifacts/cross_object_lock_gaps_20261011/d_deadlock_probe.py:1-96
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/d_deadlock_base_gil0.log:1-4
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/d_deadlock_base_gil1.log:1-4
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3565-3617
  - src/melder/aether/conduit/conduit.py:3191-3215
  - src/melder/aether/conduit/conduit.py:5617-5660
  IMPACT: A permanent hang, worse than the races; it is in the method this lane already changes, so the fix rides
    in 0.2.8231 (no new lock, one fewer edge).
  NEXT: Re-cut apply_0_2_8231.py and the tests, rerun red/green and repeats.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T18:17:02Z
  TYPE: FACT
  CLAIM: Re-read of the re-cut frame probes before validating them (re-onboarded after a compaction). (1) The
    probes now take the frame lock once and inline the membership test instead of re-entering has_spell. (2)
    `_find_index_for_spell_unless_cleaned`, like the public `find_index_for_spell`, tests
    `spell_id in spell_index.spells_in_index()`, which copies every index's member set (O(members) per index) and
    raises RuntimeError for a cleaned index; `SpellIndex._has_spell_unless_cleaned` answers the same lineage
    membership in O(1) under the index lock, copies nothing and answers False for a cleaned index (the frame -> index
    lock edge the public method already takes). (3) `_selected_spell_registry` holds LIVE references to each
    conjured Book's `_spell_ids`, which that Book mutates under its own lock, not the frame lock: the probes' `in`
    and `set.update` are single calls and exact under a concurrent writer, but the public `spells_in_index` copies
    those sets element by element, and `_get_all_spell_ids` reads the own frame through it in the conjure preflight
    (`_spell_id_integrity_checker`). HYPOTHESIS: a bind into one conjured Book while another Book of the same frame
    conjures can raise "Set changed size during iteration". (4) The probes' `is None` registry checks are dead:
    the registries exist from __init__ until cleanup deletes them under the frame lock after setting `_cleaned`.
    (5) Notes 3-8 carried DATETIMEs ahead of the clock; corrected from file mtimes (Notes 3-5 at or before 17:31,
    Note 6 at 17:33, Notes 7-8 at 17:51), and the artifact rows of the patch docs from 18:20 to 17:32:46.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:853-925
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1060-1110
  - src/melder/aether/spellbook/bind/spell_index.py:274-345
  - src/melder/aether/spellbook/spellbook.py:2567-2589
  - src/melder/aether/spellbook/spellbook.py:2672-2745
  - src/melder/aether/aether.py:2762-2810
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/apply_0_2_8231.py:476-560
  IMPACT: (2) and (4) change the probes before landing: O(1) membership, no per-index copy, no dead guards.
    (3) is unproven; if a stress shows it, the public spells_in_index takes each set with one update call.
  NEXT: Measure (3) through public verbs (late binds into a conjured Book while another Book of that frame conjures).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T18:21:29Z
  TYPE: MEASURE
  CLAIM: Note 9 (3) is real. Unforced, nothing patched or paused, on 0.2.8230 (the base copy): one thread late-binds
    2,900 classes into Book A (dynamic, conjured in frame-f, so the frame holds A's live `_spell_ids`), the other
    reads the frame's ids. Public `aether.get_frame("frame-f").spells_in_index()` in a loop: -X gil=0 1,988, 2,158
    and 1,953 of ~150,000 reads raise RuntimeError "Set changed size during iteration" in spells_in_index; gil=1
    none. Through conjure (a new dynamic Book in frame-f binds one class and conjures while A late-binds 600): gil=0
    5, 2 and 0 of 227-277 conjures fail with the same error raised in spells_in_index under conjure's preflight; gil=1
    none (2-3 conjures fit the window). No bind failed.
  EVIDENCE:
  - context_compass/artifacts/cross_object_lock_gaps_20261011/c2_spell_ids_read_stress.py:1-93
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/c2_base_gil0.log:1-18
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/c2_base_gil1.log:1-42
  - src/melder/aether/aetheric_frame/aetheric_frame.py:879-900
  IMPACT: Situation: in a dynamic world one Book keeps late-binding spells while a second Book of the same frame
    conjures; the second conjure fails its preflight with an error that has nothing to do with its spells (a retry
    passes). Fix (no lock, no copy beyond the method's own result): spells_in_index takes each Book's set with one
    `result.update(...)` call, exact under the Book's writer on 3.14t, as the probe `_spells_in_index_unless_cleaned`
    already does; `_find_index_for_spell_unless_cleaned` probes each index with `SpellIndex._has_spell_unless_cleaned`
    (O(1), no per-index copy); the probes drop the dead registry `is None` checks.
  NEXT: Apply those three edits to apply_0_2_8231.py, add a c2 regression test, re-cut cand and rerun red/green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T18:33:55Z
  TYPE: MEASURE
  CLAIM: Cut v3 of 0.2.8231 (v2 plus Note 10: O(1) frame probes without the dead guards, spells_in_index taking
    each Book's set with one update) validated on /tmp/cc_lock/cand. New tests 13/13 on -X gil=0 and gil=1 and
    30/30 repeat runs (15 per mode). On base (0.2.8230) 12 fail for the races they target - AttributeError '_lock'
    for the cleanup race, "Set changed size during iteration" for the Book binding mid-read, "dictionary changed
    size during iteration" for both frame sweeps and the ward emission and inspection tests, AttributeError
    'spell_index' for the second cleanup_spell - or for the probes they call, which base lacks; the deadlock test
    fails and hangs there (rc=124) and passes on cand in 0.7 s. The frame-sweep tests now park the binder as it
    releases frame-b's lock (a wrapper over the real RLock), the point every shape of the sweep passes, since the
    probes no longer call has_spell. Full tree gil=0: all 23 chunks green (unit_aether 4200 passed, comp_aether
    1318 + 1 xfailed, int_cryst 273 + 3 xfailed). After-probes on cand: (c) grow and churn 3 runs each, 3000/3000
    registered, no failure; (c2) no failure in 12 runs, with the public read 3x faster than on base (450-467k reads
    per 8 s against 149-154k per 9 s at gil=0; 80-131k against 17-27k at gil=1). The (a)/(b) and deadlock after-runs
    of v2 stand: v3 changes only aetheric_frame.py.
  EVIDENCE:
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/apply_0_2_8231.py:1-686
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/newtests/test_aetheric_frame_cleanup_race.py:1-218
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/newtests/test_aether_component_frame_sweep_races.py:1-183
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/new_tests_cand_gil0.log:1-2
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/new_tests_cand_gil1.log:1-2
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/new_tests_base_gil0.log:1-449
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/new_tests_cand_repeats.log:1-30
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/new_deadlock_test_base_gil0.log:1-3
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/summary_full_cand_0_2_8231_v3_gil0.txt:1-25
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/after_c_unforced_v3_gil0.log:1-12
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/after_c2_cand_gil0.log:1-18
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/after_c2_cand_gil1.log:1-18
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/after_ab_unforced_gil0.log:1-4
  - context_compass/artifacts/cross_object_lock_gaps_20261011/runs/after_d_deadlock_gil0.log:1-4
  IMPACT: The change set is ready to land as 0.2.8231; the full tree under gil=1, the Windows tiers and hosted CI
    remain not run.
  NEXT: Bring the five patch docs to the v3 design (published frame view, keyed contract lookups, the deadlock fix,
    the kept frame lock, the O(1) probes, the Book-set copy), then land.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T18:38:57Z
  TYPE: PLAN
  CLAIM: Patch docs brought to the landed design (v3) and re-consumed; v1 copies kept in scratch. Mapping:
    inv 1 (emissions under the ward lock) -> conduit_ward.py emissions -> cleanup/notch emission tests; inv 2 (detail
    maps under the contract lock) -> _contract_member_spell and both contract reads -> inspection test; inv 3 (keyed
    reads, no conduit lock under the ward lock) -> _get_spell_in_contracts keyed-first, the listing through the Book,
    Spellbook._find_contracted_spell_by_id by key -> deadlock test and the updated listing unit test; inv 4 ->
    Conduit.cleanup_spell and Spellbook._dispose_spell -> double-cleanup test plus the F9 suite; inv 5 -> the Aether
    frame view and the probes -> both frame-sweep tests and the probe unit tests; inv 6 -> spells_in_index and the
    probe with one call per Book set -> the mid-read unit test; inv 7 -> no new kind of edge, read off the code (the
    Book helpers the new ward-locked walks call reach no Aether or frame) -> full tree without a hang. The existing
    test_conduit_ward_contracts.py update now types its fake lookup Optional[FakeSpell] (no PEP 604). Landing order:
    verify the five src files and two test files in the working tree are byte-identical to base, apply src and tests,
    notch 0.2.8231, release note, src_architecture/src_components and their indexes, graph (extract --strict, accept
    re-read nodes, assemble, --check), archive the patch folder, boards, ticket to review, assets and llm_support last.
  EVIDENCE:
  - context_compass/system_docs/patches/active/cross_object_lock_gaps_2026_10_11/architecture_patch.md:1-81
  - context_compass/system_docs/patches/active/cross_object_lock_gaps_2026_10_11/component_patch_conduit_ward.md:1-45
  - context_compass/system_docs/patches/active/cross_object_lock_gaps_2026_10_11/component_patch_spell_disposal.md:1-30
  - context_compass/system_docs/patches/active/cross_object_lock_gaps_2026_10_11/component_patch_aether_frame_sweep.md:1-37
  - context_compass/system_docs/patches/active/cross_object_lock_gaps_2026_10_11/code_description_patch_lock_gaps.md:1-42
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/apply_test_updates.py:1-87
  IMPACT: Docs, code and tests agree; no decision is open before landing (no transaction type, lock-order kind or
    public signature changes).
  NEXT: Verify the working tree against base, then apply the change set to the repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T19:02:08Z
  TYPE: MEASURE
  CLAIM: Landed as 0.2.8231 in the working tree (not committed). The five src files and the two updated test files
    were byte-identical to base before applying and are byte-identical to the validated cand after; the three new
    test files are installed (CRLF, like their neighbours). __version__ 0.2.8231; release-note section "Index links,
    contract reads and binds across frames hold up under concurrent changes" plus a packaging line and the 0.2.8231
    rebuild line. src_architecture (invariant, failure mode, code map, handoff) and src_components (Spellbook Core,
    Aether Singleton, AethericFrame Services, Conduit Runtime, ConduitWard and Contracts, code map, handoff; the
    stale teardown lock note corrected) updated, both indexes current. Graph: the five changed classes re-read, given
    the new responsibilities and accepted (stale census 209 -> 204), extract --strict skipped nothing, assemble
    --check verified 587 ranges; extract --check exits 1 on the 204 stale nodes that predate this lane (none new,
    none orphaned). Patch folder archived to patches/completed. Assets rebuilt (bind guard 622 entries, unchanged)
    and llm_support rebuilt with --include-untracked; both --check OK, and OK again after the post-landing runs.
    Post-landing on the tree at gil=0: unit_arch 18, unit_llm 28, unit_build 116, unit_gh 491, unit_top 145 passed;
    the new and updated test files 159 passed.
  EVIDENCE:
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/README.txt:1-20
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/land_docs_0_2_8231.py:1-232
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/extract2_0_2_8231.log:1-46
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/assemble_check_0_2_8231.log:1-4
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/assets_check_after_tests.log:1-3
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/llm_check_after_tests.log:1-3
  - context_compass/artifacts/cross_object_lock_gaps_20261011/scratch_0.2.8231/runs/post_landing_tree_gil0.txt:1-6
  - release_docs/next_version_release.md:70-99
  IMPACT: (a), (b), (c), (c2) and the listing deadlock are fixed and landed; residuals: the Spellbook-internal window
    between cleanup_spell's locked decision and its disposal against an index move into the same index, and
    Conduit.find_contracted_spell's live walk of the contracted map under the conduit lock; the 0.2.8230 snapshots
    are not reworked. Not run: the full tree at gil=1, the Windows tiers, hosted CI, coverage.
  NEXT: Owner: git add -A (three new test files, the archived patch folder, the evidence folder), commit and push;
    accept or redirect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
IN REVIEW (melder_1, 2026-10-11T19:02:34Z): all three of the predecessor's Note-13 residuals were proven through the
real locks and mediators (none retracted), plus (c2) and a deadlock found on the way, and all landed as 0.2.8231 in
the working tree (not committed). (a) the owner-side index emissions walk the ward's contracts under the ward lock;
(b) contract detail maps are read and written under the contract lock, by key first; the listing resolves through
the Book and no longer deadlocks with link/sever; cleanup_spell emits what Spellbook._dispose_spell's locked
decision reports; (c) bind's cross-frame sweep reads a frame view Aether republishes on frame birth and detach,
through cleanup-safe O(1) frame probes; (c2) the frame copies each Book's live id set in one call. Owner rule
applied (Note 7): no per-call snapshot where a keyed read or the writers' lock serves. Evidence: Notes 1-13 and
context_compass/artifacts/cross_object_lock_gaps_20261011/. Open for the owner: git add -A, commit and push, Windows
tiers, hosted CI, acceptance. Residuals: Note 13 IMPACT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
