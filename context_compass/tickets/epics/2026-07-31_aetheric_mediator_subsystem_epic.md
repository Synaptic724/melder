# Epic: AethericMediator - a standalone top-level thread/transaction plane

## Metadata
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: in_progress (bootstrap started 2026-07-31 under owner directive)
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-07-31T23:00:41Z
- Target Window: UNKNOWN
- Related Program/Initiative: EPIC-2026-07-27-transactional-structure-unwind
  (the investigation that produced this direction)

## Problem / Opportunity

THREE SUBSYSTEMS INDEPENDENTLY SOLVED THE SAME PROBLEM THREE DIFFERENT WAYS.
That is the defect. Not any individual race.

- Crystallizer: `LoadGate` (global exclusive) + engine-local `_build_lock` +
  posture idempotence.
- Nexus: `RiftGate` + `RiftGateController` + drain-and-refresh choreography +
  config-backed timeouts.
- MutationResearch: a declared one-way lock order + a dedicated `_emission_lock`
  + hand-written compensation (`_rollback_claim`, join restore).

Each is a local answer to "coordinate structural mutation across threads",
invented separately because there was no shared plane to reach for. The bug
trail confirms the cost: BUG-031 (emission lock), BUG-048 (lane governance), the
2026-07-12 CreationGate drain-race ticket-first fix - all found and patched once
per subsystem, in that subsystem's own vocabulary.

Two structural facts make this compound rather than stabilise:
1. `Aether._ensure_frame(...)` + `bind_frame_configuration(...)` CANNOT be made
   atomic by anything that exists today, because the only admission authority
   (the mediator) is owned by the frame being created. Not patchable - it needs
   an authority ABOVE.
2. Free-threaded 3.14t removed the accidental serialisation the GIL used to
   provide, so every hand-rolled protection is load-bearing now in a way it was
   not when these were written.

WHAT THIS BUYS: coherence, not correctness. Nothing is on fire today. This is
consolidation so the fourth subsystem does not invent a fourth answer, and so
concurrency bugs stop being discovered once per subsystem.

## MRP Alignment

MRP, not MVP. A half-built admission plane is worse than none: callers trust it
and it silently fails to isolate. The bar is that the claim vocabulary and the
acquisition semantics are right the first time, because all three subsystems will
be written against them.

## Ticket Contract
- ENTRY_GATE: owner directive given 2026-07-31; core bootstrap authorised.
- EXECUTION_BOUNDARY: build the STANDALONE plane only. Wiring into MR/Nexus/
  Crystallizer is a separate story and is gated on the per-subsystem surveys.
- DEPENDENCIES: `melder.utilities` only (Cleanable, synchronization primitives).
  Explicitly NOT `melder.aether`.
- EXIT_GATE: core plane exists and is tested standalone; all three subsystem
  surveys complete; owner rules on wiring order.
- FAILURE_ESCALATION: DECISION_REQUEST on open question 1 and 2 below.

## Owner Constraints (non-negotiable, from the 2026-07-31 directive)
1. Lives at `src/melder/aether/aetheric_mediator/`.
2. Named `aetheric_mediator`.
3. Aether MANAGES it (holds it), and it is constructed IMMEDIATELY, first, right
   after Aether itself is built.
4. IT MUST NOT DEPEND ON AETHER. One-way only: Aether knows about the plane, the
   plane knows nothing about Aether. This is what lets it exist before any frame
   can, and what keeps it testable in isolation.
5. Model it on the WORKING DevOps subsystem - the whole shape, not one component.
   It may omit components, but it is not "just the embargo manager".
6. Wire into MR / Nexus / Crystallizer only when those subsystems are ENABLED AND
   ACTIVE; they emit their basic conditions to the plane.
7. Lightweight, but just as effective.

## SURVEY DEPENDENCY DISCHARGED (bootstrap_0, 2026-08-02T19:35:00Z)

One of this epic's three EXIT_GATE conditions - "all three subsystem surveys
complete" - is MET. `STORY-2026-07-31-subsystem-transactional-survey` is closed
with all three tasks delivered read-only:

| subsystem | its answer to "coordinate structural mutation" | plane absorbs it? |
| --- | --- | --- |
| Crystallizer | global exclusive gate (one load at a time, process-wide) + best-effort teardown | YES |
| Nexus | per-unit gates + hand-rolled block / drain / refresh / reopen | YES |
| MutationResearch | declared one-way lock order + one atomic two-phase primitive + hand-placed compensation | **NO - the lock order cannot be expressed as claims** |

THE FINDING THAT MATTERS FOR WIRING ORDER: a scope-claim plane grants sets of
scopes atomically; it says nothing about the sequence in which a holder takes its
own mutexes afterwards. MR's central safety property is exactly such a sequence
(emission -> root -> set -> crystallizer), so a transaction can hold every
correct claim and still invert its own locks and deadlock. Wiring MR is an
ADDITION on top of an invariant that stays hand-maintained - and the plane will
otherwise give a false impression that concurrency is now handled there.

Still open on the EXIT_GATE: core plane proven standalone, and the owner's ruling
on wiring order (plus open questions 1 and 2, which gate the wiring story).


## Component Split (modelled on DevOps)

CORRECTED 2026-07-31 after actually reading the DevOps subsystem. An earlier
revision of this section listed the strategy layer as an optional "seam" and
proposed dropping `apply_commit_delta`. BOTH WERE WRONG. See the findings notes.

The DevOps plane is FIVE pieces, and the port needs all five:

1. VOCABULARY - a closed `StrEnum` of transaction types. `StrEnum` specifically,
   because these values TRAVEL into request payloads, admission evidence, and
   logs. Its own contract states the discipline: adding a structural operation
   means adding a member here PLUS a strategy, never threading a new ad-hoc
   string through the control plane.
2. REQUEST - an immutable frozen record, FROZEN BEFORE ADMISSION so admission is
   deterministic and replayable: conflict detection and claim acquisition read a
   fixed snapshot, so one request cannot admit differently depending on when its
   fields are read. Carries scope keys, per-key `scope_claims` modes, hashes,
   identity edges, and metadata.
3. VERDICT - an immutable admission result returning EVIDENCE, NOT A BOOL:
   machine-readable `reasons`, blocking `conflicts`, contended `embargoes`. This
   is the single most important piece for the owner's reporting requirement.
4. STRATEGY - an ABC with four hooks (`build_start_plan`, `on_start`, `on_end`,
   `apply_commit_delta`), registered as CLASSES not instances, stateless.
5. CLAIM TABLE + ORCHESTRATED ADMISSION - moded, atomic, all-or-nothing, with
   named blocking evidence.

Plus the plane-level pieces this port already assumed: identity, mediator front
door (ingress, per-identity root sessions, same-thread joins, bounded wait),
and session (status, depth, join/leave, rollback actions, abort pipeline,
outcome policy).

STILL OMITTED (genuinely DevOps-specific):
- the concrete DevOps strategy families; each subsystem registers its own
- the registry's RELATIONAL mirrors (spellbook<->conduit ownership, link and
  cluster membership maps). Relational truth belongs to each subsystem; the top
  plane should hold transaction ACTIVITY and FACT BASELINES only. OPEN QUESTION 4.
- commit validators / commit hooks, until a caller needs one
- `StagedMutation`, unless staging proves necessary

## Key Design Decisions (recorded, open to challenge)

- ONE SHARED PLANE, not one per subsystem. The crystallizer's job is driving the
  other two (`_replay_mutation_research`, `_replay_nexus`), so per-subsystem
  planes would force acquisition ACROSS planes and manufacture an AB-BA hazard.
  One table means one atomic acquisition over every scope a load needs.
- SCOPE KEYS ARE NAMESPACED AND FLAT: `mr:set:<name>`, `nexus:frame:<name>`,
  `cryst:load:<id>`, `frame:<name>`.
- `LoadGate` IS NOT DELETED, IT IS RE-EXPRESSED as one exclusive claim on a
  world scope key. Today's global-exclusive behaviour is preserved exactly for
  loads that need the whole world; frame-scoped loads claim only their frames and
  gain disjoint parallelism. Backwards compatible by construction.
- THE FRAME-LEVEL DEVOPS MEDIATOR STAYS WHERE IT IS. This is a PEER plane at a
  higher scope, not a replacement. Frame -> its mediator ordering is retained.

## Non-Goals (Explicit Exclusions)
- Replacing or modifying the DevOps frame-level plane.
- Unifying inner frame transactions into the top session (see open question 2).
- Transactionalising Aether itself. Aether hosts the plane; it is not a
  participant.

## Open Questions (BLOCKING - resolve before wiring)
1. Does the top plane claim FRAME scope keys, or only subsystem keys? Claiming
   frames overlaps the frame plane's own scopes and needs a declared order.
   Claiming only subsystem keys leaves frame creation unprotected - which was the
   original hole this started from.
2. Do inner frame transactions JOIN the top session, or stay siblings? Sibling =
   the plane ORGANISES threads. Join = it UNIFIES transactions, which is a much
   larger build and the owner has leaned against it.
3. What are each subsystem's "basic conditions" that get emitted on enable? The
   three surveys answer this.
4. Does the aetheric registry mirror subsystem RELATIONSHIPS, or only
   transaction ACTIVITY plus fact baselines? DevOps mirrors a great deal -
   spellbook<->conduit ownership, conduit links, cluster membership - and those
   mirrors are what its information strategies read. Proposed answer: the top
   plane holds activity and facts ONLY, and relational truth stays owned by each
   subsystem. Not yet ruled.
5. Does `apply_commit_delta` come up here? Its job below is stamping freshness
   baselines so readers can skip re-derivation. If reporting means "activity plus
   admission evidence", it can be dropped; if it means "and I can tell what is
   stale", it must come. Leaning KEEP, given the owner named logging/reporting as
   a driver.
6. What is the aetheric SCOPE HIERARCHY? The `ix` finding makes this concrete and
   urgent: `world` -> `frame:<name>` -> subsystem keys is the shape that makes
   LoadGate a degenerate case. Needs confirming against the three surveys.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-07-31-aetheric-mediator-core - build the standalone plane
- [ ] Story: STORY-2026-07-31-subsystem-transactional-survey - what to
      transactionalize in MR / Nexus / Crystallizer
- [ ] Story: STORY-2026-07-31-aetheric-mediator-wiring - activation-gated wiring
      (BLOCKED on the survey + open questions 1 and 2)

## Acceptance Criteria (Epic Done)
- The plane exists standalone with ZERO imports from `melder.aether`, provable by
  a grep in its own test.
- Modes and the compatibility matrix are tested directly.
- Acquisition is proven atomic all-or-nothing under concurrency.
- All three surveys are complete with source evidence.
- Open questions 1 and 2 have recorded owner decisions.
- Wiring has NOT happened without those decisions.

## Risks / Mitigations
- RISK: two admission planes deadlock against each other (AB-BA). MITIGATION:
  declare the one-way order BEFORE building - AETHER PLANE CLAIMS -> FRAME PLANE
  CLAIMS, never the reverse. MR's threadsafety story is a declared order, not a
  discovered one; match that discipline.
- RISK: the plane accretes DevOps depth by default and stops being lightweight.
  MITIGATION: the omitted list above is a contract; adding to it needs a reason
  recorded in the decision log.
- RISK: blast radius across three working subsystems. MITIGATION: the plane ships
  and is tested STANDALONE first; wiring is a separate, gated story.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No import of `melder.aether` from inside the plane.
- [ ] No wiring before the surveys and open questions 1-2 are resolved.

## Validation / Test Approach
Not run. Standalone unit tests belong to the core story; the no-Aether-import
rule should be a test, not a convention.

## Decision Log
- 2026-07-31: Owner directed bootstrap. Name, location, Aether-hosted-but-
  independent, model-on-DevOps, activation-gated wiring, lightweight-but-
  effective. Recorded verbatim in Owner Constraints above.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: ask user before implementation

## Notes
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: DECISION
  CLAIM: Epic opened under owner directive. The plane is a CONSOLIDATION play -
    it buys one vocabulary for scope claiming across three subsystems that
    currently have three. It is explicitly NOT sold as fixing a live defect.
  EVIDENCE:
  - context_compass/tickets/epics/2026-07-27_transactional_structure_unwind_epic.md
  IMPACT: Sets the success bar at coherence, so the epic is not judged against an
    outage that does not exist.
  NEXT: Bootstrap the core claim vocabulary; open the three survey tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: RISK
  CLAIM: The agent filing this epic (helper_f) has a heavily loaded context from
    a long investigation session. The surveys are therefore deliberately written
    as SELF-CONTAINED tasks a FRESH agent can execute without inheriting that
    context.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-31_survey_mr_transactional_surface_task.md
  IMPACT: Prevents this epic's quality from depending on one contaminated
    session.
  NEXT: Keep every survey task's Required Reads explicit and short.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-31T23:00:41Z
  TYPE: FACT
  CLAIM: THE STRATEGY LAYER IS THE POINT, NOT DECORATION. `build_start_plan` is
    where SCOPE PROPORTIONALITY is decided, and that decision is the whole
    difference between a claim plane and a global mutex with extra steps.
    `BindTransactionStrategy` exists almost entirely to answer "what does a bind
    actually touch": pre-conjure ONE spellbook; post-conjure the book + paired
    root conduit + its ward + any cluster memberships. It EXPLICITLY REFUSES to
    model bind as multi-conduit fanout, because "a generic topology expansion
    would claim every conduit associated with the book and serialize unrelated
    work across the whole frame".
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:22-85
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py:20-86
  IMPACT: Corrects this epic's earlier framing of strategies as an optional
    extension seam. Without them, callers hand-author their own scope sets and
    the plane degenerates to ad-hoc claiming - the exact failure it exists to
    end. ALSO: each subsystem SURVEY's real output IS the input to a strategy.
    "What does a checkpoint load actually touch?" is `build_start_plan` for
    `checkpoint_load`. The surveys and the strategies are the same work.
  NEXT: Read `transaction_strategy_builder.py` for the registration/dispatch
    contract before designing the aetheric equivalent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: FACT
  CLAIM: `INTENT` IS A HIERARCHICAL PARENT-SCOPE MARKER, AND IT ALREADY SOLVES
    THE LOADGATE RE-EXPRESSION. DevOps documents it as marking "a parent scope so
    a whole-spellbook claim (transfer) blocks piece-work without serializing it".
    Applied here: a whole-world load claims `world` EXCLUSIVE and shuts
    everything out (today's LoadGate, verbatim); a frame-scoped load claims
    `world` INTENT + `frame:A` EXCLUSIVE; a second claims `world` INTENT +
    `frame:B` EXCLUSIVE. The two coexist on the parent, never contend on the
    children, and the whole-world load still excludes both.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:18-67
  IMPACT: The disjoint-parallelism goal needs NO new mechanism. It falls out of
    mode semantics that already ship and are already proven. LoadGate is not
    replaced by something novel - it is the degenerate `x`-on-world case.
  NEXT: Confirm the aetheric scope hierarchy (`world` -> `frame:<name>` ->
    subsystem keys?) as part of the surveys.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: MEASURE
  CLAIM: The bootstrapped `ClaimCompatibility` matrix was VERIFIED against
    DevOps and matches exactly. `EXCLUSIVE` admits nothing; `SHARED` coexists
    with `SHARED` only; `INTENT` coexists with `INTENT` only - so SHARED vs
    INTENT is denied in DevOps too. The conservative default taken during
    bootstrap was correct, and is now evidenced rather than assumed. Two
    corrections applied to the shipped file: `ClaimMode` switched from `Enum` to
    `StrEnum` (DevOps uses `StrEnum` deliberately because the values travel into
    payloads and LOGS), and the docstring now cites provenance instead of
    describing a guess.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:27-33
  - src/melder/aether/aetheric_mediator/claim_mode.py
  IMPACT: Removes a live correctness risk in already-written code, and aligns
    the log/payload representation with the plane it is modelled on.
  NEXT: Continue with the builder and orchestrator.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: FACT
  CLAIM: THE REPORTING THE OWNER WANTS IS TWO MECHANISMS, BOTH FALLING OUT OF
    THE PLANE EXISTING - it is not a logging layer bolted on afterwards.
    (1) FACT BASELINES: `apply_commit_delta` runs at commit WHILE THE
    TRANSACTION STILL HOLDS ITS CLAIMS, and its BASE-CLASS DEFAULT stamps
    `report_fact(fact_family, region, reporter)` per region (`spellbook:<id>`,
    `conduit:<id>`). Information strategies then read those baselines and skip
    re-derivation when nothing has changed since.
    (2) LIVE ACTIVITY INDEXES: the registry keeps
    `list_live_transactions_for_scope` / `_for_identity` / `_for_type`, which is
    literally "what is happening right now, along one axis".
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py:168-229
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:385-471
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1476-1629
  IMPACT: Reverses this epic's earlier proposal to DROP `apply_commit_delta`.
    Dropping it would delete the freshness half of the reporting story the owner
    explicitly asked for. It stays unless the owner rules otherwise
    (open question 5).
  NEXT: Owner ruling on open questions 4 and 5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-01 04:40
  TYPE: IMPLEMENT
  CLAIM: The plane deferred teardown to the cycle collector on EVERY
    transaction, and its two "frozen" records were mutable in place. Both are
    now closed, and the fixes overlap: freezing the metadata is what made the
    per-transaction copies removable.
  EVIDENCE:
    - src/melder/aether/aetheric_mediator/transaction_session.py:532-590
      New `discard_inverses()`. A rollback inverse is a closure and a useful
      one captures the session, giving
      `session -> _rollback_actions -> _RollbackAction -> closure -> session`.
      Refcounting cannot see through that, so every finished transaction was
      surviving until an unrelated collector pass. Terminal-only, idempotent,
      returns the discarded descriptions.
    - src/melder/aether/aetheric_mediator/mediator.py:_finalize
      Calls `discard_inverses()`, so the thread that finishes the transaction
      cuts the cycle. Deliberately NOT a full `cleanup()`: every accessor is
      guarded by `check_cleaned()`, so cleaning here would stop a caller
      reading the outcome of its own transaction.
    - src/melder/aether/aetheric_mediator/mediator.py:begin (except branch)
      Full `cleanup()` there instead, and BEFORE `_finalize`. That session
      never escaped - `begin` raises rather than returning it - so nobody is
      owed a readable outcome, and the `cleaned` guard in `_finalize` then
      correctly skips a discard on a session still nominally OPEN.
    - src/melder/aether/aetheric_mediator/staged_transaction.py:63-110
      `from_request` was called 3x per transaction (begin/commit/fail). Beyond
      the wasted allocations, `admitted_at=time.time()` in commit/fail
      RESTAMPED the field with the commit time, so it reported the wrong
      moment. Built once at admission now, carried on the session.
    - src/melder/aether/aetheric_mediator/transaction_request.py:MetadataPolicy
      `normalize` now returns a DEEPLY frozen structure - proxy mappings and
      tuples at every depth. `@dataclass(frozen=True)` only blocks rebinding a
      field, so the old `Dict[str, Any]` left both records advertising
      themselves as detached and safe to retain while any holder could edit
      them.
    - Allocation count per transaction went 3 metadata structures -> 1:
      `begin` built two independent dicts from one input (and so the strategy
      planned against a different object than the request carried), and
      `from_request` copied again. The staged record now SHARES the request's
      mapping, which is safe only because it is frozen.
  IMPACT: Transaction teardown is deterministic and owned by the finishing
    thread, matching the repo's cleanup discipline. The immutability the two
    records claim in their docstrings is now real rather than aspirational.
  NEXT: Owner runs the suite. Component tests added for deallocation run with
    `gc` DISABLED so an observation is proof rather than a timing artefact;
    one test deliberately documents the hazard by showing an unfinalised
    session frees nothing until the collector is re-enabled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01 05:20
  TYPE: IMPLEMENT
  CLAIM: Audited every class in the plane against the rule that a record
    holding a COMPLEX type must be a normal class with cleanup, not a
    dataclass. Exactly one violated it, and it was the worst possible one.
  EVIDENCE:
    - Full AST audit: only 3 dataclasses remain - `AdmissionResult`,
      `TransactionRequest`, `StagedTransaction` - and all three are frozen
      value records. Their one non-scalar field, `metadata`, is now a deeply
      frozen mapping enforced by `MetadataPolicy`, so they are legitimately
      dataclasses. Everything else was already a normal slotted class.
    - src/melder/aether/aetheric_mediator/transaction_session.py:_RollbackAction
      THE VIOLATION. It owns `action: Callable` - a closure, which pins
      whatever its defining scope held (session, frame, conduit, spellbook) -
      and had no cleanup. Now `Cleanable` with an explicit `cleanup` that
      `del`s the closure. Precedent is direct: `ChangeControlManager.cleanup`
      explicitly `del`s `_commit_hook`, `_abort_hook`, `_commit_validator`,
      `_structural_validator`, `_dirty_marker` rather than trusting them to
      fall away.
    - transaction_session.py:_run_inverses
      Releases each record in a `finally` as it runs, not in a batch after the
      loop. A raising inverse produces a caught exception whose traceback
      references the unwind frame and therefore every closure still pending;
      releasing as we go bounds that to the record in hand.
    - transaction_session.py:fail
      UNWIND now empties `_rollback_actions` when it hands the records to the
      unwind. Ownership transfers outright, so exactly one place is
      responsible for releasing them - two holders is how a double-release or
      a missed release happens.
    - claim_table.py:cleanup
      `_claims` is `Dict[str, List[_GrantedClaim]]` but only the outer dict
      was cleared. Inner lists are now emptied first, mirroring how
      `ChangeControlManager.cleanup` walks its nested per-conduit maps
      clearing innermost sets before their containers. Matters because
      `release` REBUILDS these lists, so a concurrent reader can hold an
      older one.
  IMPACT: The only complex-typed record in the package now releases on
    command, on the thread that finished with it, including on the failing
    unwind path. No dataclass in the plane holds a reference type.
  NEXT: Judgment call recorded for owner review - `_GrantedClaim` and
    `ClaimBlock` hold live `Identity` objects rather than flattened strings,
    which differs from `TransactionRequest`, which deliberately flattens the
    submitter. Left as-is: `Identity` is an immutable value object of str/int
    slots, so it is not a liveness leak, and making every granted claim
    `Cleanable` would add per-claim overhead on the acquisition hot path for
    no lifecycle benefit. Reverse this if `Identity` ever gains a reference.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary

Owner-directed. Build a standalone top-level thread/transaction plane at
`src/melder/aether/aetheric_mediator/`, hosted by Aether but with ZERO dependency
on it, modelled on the working DevOps change-control subsystem minus its
frame-specific depth.

The single most important constraint: THE PLANE MUST NOT IMPORT `melder.aether`.
That is what lets it be constructed before any frame exists and tested in
isolation. Make it a test, not a convention.

Do not wire it into MR / Nexus / Crystallizer until the three surveys are done and
open questions 1 and 2 have owner decisions. The plane ships standalone first.
