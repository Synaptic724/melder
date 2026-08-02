# Epic: Outcome management for partial failure during structure creation

## Metadata
- Epic ID: EPIC-2026-07-27-transactional-structure-unwind
- Status: in_progress (CLAIMED by helper_f 2026-07-29 under owner directive;
  investigation lane only - no design, no implementation)
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p2
- Created: 2026-07-27T23:19:33Z
- Updated: 2026-07-29T22:21:25Z
- Target Window: UNKNOWN
- Related Program/Initiative: DevOps change control / crystallizer restore

## Problem / Opportunity

Owner's question, in his framing: *there are mediator transactions, and then
there are checkpoint-based transactions. So what happens if we try to create a
bunch of objects and one fails, and we start getting errors? What are the ways
we can manage these things? How can we unwind? DO we need to unwind? What tools
do people have to manage outcomes?*

That is NOT one question about one mechanism. It is a question about the SPACE
OF AVAILABLE STRATEGIES for a bad outcome, and about which of them melder
should offer its users.

### The two existing transaction concepts answer different questions - and
### neither answers this one

- **Mediator transactions** (`TransactionMediator` + `ChangeControlEmbargoManager`,
  claim modes x/s/ix) answer *"who may mutate what, right now, without racing."*
  They are an ADMISSION plane. They do not answer "undo what I already did."
- **Checkpoint transactions** (crystallizer `create_checkpoint` /
  `load_checkpoint`) answer *"put the whole world back the way it was at time T."*
  Coarse-grained, whole-world, and expensive.

Neither answers the actual runtime case: **I am halfway through building fifty
objects, number thirty-seven raised, what now?**

### The measured asymmetry (2026-07-27, source-verified)

Melder ALREADY has a mature partial-failure vocabulary. It exists in exactly one
place and was never brought to the runtime creation path:

- `restore_engine.py` - **80** occurrences of `shortfall`. Every unreplayable
  thing is a NAMED shortfall, never silent. Plus `_teardown_built()` for
  reverse-order all-or-nothing unwind.
- `creation_context.py` - the file that actually CONSTRUCTS objects and registers
  them into `Creations` - has **3** `except`/`finally` handlers in total.

So the most sophisticated answer melder has to "a large multi-unit build partly
failed" lives in restore, and the hot path that builds user objects has
effectively nothing. That gap, not the absence of transactions, is the
opportunity.

## The Option Space (the core deliverable of this epic)

Seven strategies exist for managing a partial-failure outcome. Melder already
ships FIVE of them somewhere in the tree. Unwind is the most expensive one and
should be the LAST resort, not the default.

| # | Strategy | What it means | Status in melder today |
|---|---|---|---|
| A | **Prevent** | Validate the whole plan before building anything | SHIPPED - phases 1-4 run before conjure; broken spells raise `SpellbookValidationError` before a conduit exists |
| B | **Abort the batch** | Cancel siblings, let nothing partial survive | SHIPPED - `PhaseScheduler` shared cancellation signal, `PhaseExecutionError` |
| C | **Discard the container** | Build into a throwaway scope; drop the scope on failure. No unwind needed | SHIPPED - lesser conduits, `SpellSpace.reset()` |
| D | **Unwind** | Journal applied ops, run inverses in reverse | PARTIAL - only `TransferOfOwnership`, via a private callback stack |
| E | **Rewind to checkpoint** | Coarse whole-world restore to a sealed point | SHIPPED - crystallizer `load_checkpoint`, all-or-nothing |
| F | **Record dirty, refuse use** | Leave the state, gate access to it | SHIPPED - `ChangeControlManager` dirty roots; meld refuses |
| G | **Honest partial + ledger** | Accept the partial result, report precisely what did NOT happen | SHIPPED IN RESTORE ONLY - `RestoreReport` shortfalls (80 uses) |

**The most important question in this epic is therefore NOT "how do we unwind"
but "which of A-G should apply where, and is D needed at all?"** C and G are
cheaper, already exist, and may cover most real cases. An expensive journal
+ inverse system that duplicates what a throwaway lesser conduit already gives
you for free would be a bad trade.

## MRP Alignment (Most Reasonable Product)

MRP, not MVP. A half-built undo is strictly WORSE than none, because callers
trust it and it silently misses effects. The MRP bar: pick the smallest set of
strategies that make outcomes honest, and make the failure semantics of the
creation path documented and predictable. "Predictable and honest" beats
"powerful and partial" here.

Explicitly not MRP-worthy for a first slice: savepoint nesting, cross-frame
unwind, a public transaction API.

## Ticket Contract
- ENTRY_GATE: BACKLOG. Entry requires owner activation and an assigned agent.
- EXECUTION_BOUNDARY: Investigation and option analysis ONLY. No implementation,
  no strategy edits, no changes to the admission plane or restore engine.
- DEPENDENCIES: mediator admission plane (shipped); crystallizer checkpoint lane
  (shipped); `patch_framework_gating.md` applies the moment this leaves
  investigation.
- EXIT_GATE: Lanes 1-6 answered with source evidence; an owner DECISION recorded
  on which of strategies A-G melder will offer and where; blast radius accepted.
- FAILURE_ESCALATION: DECISION_REQUEST on the eager-mirror conflict; CONFLICT if
  a lane shows the creation path cannot be made honest without breaking meld
  performance.

## Goals (Outcomes)
- A documented, evidence-backed answer to "what happens when object 37 of 50
  fails" - which today is UNKNOWN.
- An explicit owner decision on which strategies (A-G) melder offers, and where.
- A user-facing vocabulary for managing outcomes, not just internal machinery.
- A defensible answer to "do we need unwind at all", including "no" as a
  legitimate result.

## Non-Goals (Explicit Exclusions)
- Re-litigating admission, claim modes, or scope acquisition. They work.
- Changing the crystallizer restore engine. It is the REFERENCE implementation
  to learn from, not a target.
- Building a general journal before proving C and G do not already suffice.

## Scope Boundaries
- In scope: the meld/creation hot path (`meld.py`, `creation_context.py`,
  `creations.py`), the 15 transaction strategy families, `TransactionSession`,
  and the user-facing surface for outcome control.
- Out of scope: crystallizer restore internals, ACL chain rollback - both are
  working reference implementations.

## State Transition Event
- from_state: (new)
- to_state: draft
- transition_reason: Owner captured the requirement and directed an epic to
  explore mechanisms, options, and blast radius. Filed to BACKLOG because the
  owner explicitly said "saving this for later".

## Blast Radius (owner asked explicitly)

MEASURED:
- **15 transaction strategy families** would each need an inverse IF strategy D
  is chosen: add_spell_or_index_to_contract, add_to_index, bind, cluster_join,
  cluster_leave, cluster_link, conjure, elect_conduit_cluster_leader, link,
  notch, remove_from_index, remove_spell_or_index_from_contract,
  transfer_ownership, unelect/elect leader, unlink.
- **1 ABC** (`TransactionStrategy`) gains hooks; all 15 recompile against it.
- **6 existing rollback dialects** fold or are grandfathered with a reason:
  `TransferOfOwnership` (private callback stack), `RestoreEngine._teardown_built`,
  `ResidenceRegistry._rollback_claim`, `FrameACLConfigurationChain.rollback_to_configuration`,
  `NetworkVersioner.restore_network`, `ConduitWard._restore_detail_snapshot`.
- **The meld hot path** - any per-construction bookkeeping is paid on EVERY
  meld. This is the cost centre and the reason D may lose to C.
- Test surface NOT counted. Counting it is its own task.

IF only strategies C and G are chosen, blast radius collapses to roughly the
creation path plus a result object - dramatically cheaper than D.

## Investigation Lanes (questions to answer, NOT designs to follow)

1. **What actually happens today?** Build a graph where dependency N of M
   raises. Do the already-constructed objects stay registered in `Creations`?
   Are they reachable? Are they disposed? This is currently UNKNOWN and it is
   the single most important unknown in this epic - everything else is
   speculation until it is answered with a real repro.
2. **Do we need unwind at all?** Test whether "build into a lesser conduit and
   drop it" (strategy C) already covers the common case. If it does, D is a
   luxury. Answer this BEFORE costing a journal.
3. **Can the shortfall ledger generalise?** `RestoreReport` carries 80 shortfall
   sites and is the most mature partial-failure surface in the repo. Question:
   is it liftable to a general `BuildReport` for meld, or is it restore-shaped?
4. **What does a USER get?** Today a caller has try/except, `cleanup()`, lesser
   conduit scoping, and checkpoints. There is no `meld_many` with a failure
   policy, no partial-result object, no "build these fifty and tell me which
   failed". What is the smallest user-facing vocabulary worth shipping?
5. **Where do the two existing transaction concepts meet?** A mediator
   transaction can abort; a checkpoint can rewind. Is there a case where a
   mediator abort should trigger a checkpoint rewind, or are they deliberately
   independent? Answer determines whether this is one system or two.
6. **Failure during unwind.** Fatal, retried, or recorded-dirty? Note melder
   already has a dirty vocabulary (`ChangeControlManager` dirty roots,
   `SpellState` flags, `RiskManager`), so recorded-dirty may be nearly free
   here. Note also that four `SpellState` flags still have no producers - that
   may be exactly where a dirty-unwind state belongs.

## Recommended Direction (owner-set 2026-07-31: lightweight, Aether-hosted)

Owner ruling: transactionalize the TOP level, store the plane in Aether, model it
on the DevOps plane but do NOT reproduce its depth - "lightweight but just as
effective".

### The insight that keeps it small
The lightweight thing already exists ONE LAYER DOWN, and it is
`ChangeControlEmbargoManager`, NOT `TransactionMediator`. The embargo manager is
purely the claim table (modes, atomic all-or-nothing acquisition, blocking
evidence, release-wakes-waiters, cleanup-notifies). All the DEPTH -
strategy families, `apply_commit_delta`, commit validators, the 15 registered
transaction types - lives in the mediator ABOVE it. So the top level can hoist
the claim table WITHOUT hoisting the machinery.

### KEEP (the minimum that is still "just as effective")
- CLAIM TABLE with scope keys. Scope key at this level = FRAME NAME (plus a
  world-scope key, see the LoadGate law below).
- CLAIM MODES, starting at `x` / `s` only. `ix` (intent) exists below to let
  additive piece-work coexist with whole-unit exclusivity; add it here only when
  a concrete case appears, not up front.
- SESSION with commit/abort and a recorded OUTCOME. `TransactionSession` already
  carries exactly what the owner's two-outcome policy needs: `mark_abort_only`,
  `mark_aborted`, `mark_committed`, `status`, `failure_reason`,
  `register_rollback_action`, `run_abort_pipeline`.
- SAME-THREAD JOIN semantics. Without it a load re-entering its own span
  deadlocks against itself.
- TEACH-GRADE BLOCKING EVIDENCE on wait timeout (scope key + holder). LoadGate
  already does a light version of this; keep the behaviour.
- PER-REQUEST OUTCOME POLICY: `on_failure: unwind | leave_broken`, honoured by
  the session. This is where the owner's two outcomes actually live.

### DROP (present below, not needed above)
- `TransactionStrategyBuilder` + per-family strategies. The top level has a
  handful of unit kinds, and `LoadPlan` ALREADY does planning and level
  compilation - there is nothing for a strategy registry to add.
- `apply_commit_delta` / `DevopsFactRecord` baselines. That exists to serve
  DevOps information strategies; the top level has no such consumer.
- Commit validators / commit hooks, until a caller needs one.

### LAW 1 - LoadGate becomes a degenerate claim, not a deleted component
The current global-exclusive LoadGate is EXACTLY equivalent to one exclusive
claim on a world scope key. Re-express it that way rather than removing it:
every load that legitimately needs the whole world keeps today's behaviour
unchanged, while frame-scoped loads (formations are single-frame BY LAW -
"multi-frame windows refuse") claim only their frame and gain disjoint
parallelism. Backwards compatible by construction.

### LAW 2 - Declare the one-way order BEFORE building anything
Two admission planes can deadlock against each other (AB-BA): a load holding an
Aether claim while an inner frame transaction waits on a frame claim held by a
thread waiting on the Aether claim. The order is:
    AETHER PLANE CLAIMS -> FRAME PLANE CLAIMS, NEVER THE REVERSE.
MutationResearch's entire threadsafety story is a declared one-way lock order
(`spellbook -> emission -> root -> set -> child/crystallizer`); this plane needs
the same discipline stated up front, not discovered in a bug.

### What this does NOT deliver (state plainly, do not oversell)
It organizes threads; it does NOT unify transactions. Inner frame-level
transactions still open their own per-identity root sessions and still genuinely
commit as the load proceeds. Turning N sibling commits into ONE transaction
requires the frame mediator to know about and JOIN the Aether session - that is
the deep version the owner explicitly does not want. Sell this plane on DISJOINT
PARALLELISM and AGENT REPAIR, not on transactional integrity.

## Milestones (Track Progress)
- [ ] Milestone 1: Lane 1 answered with a real repro - what happens today.
- [ ] Milestone 2: Lane 2 answered - is unwind needed, yes or no.
- [ ] Milestone 3: Owner DECISION on which of A-G melder offers and where.
- [ ] Milestone 4: Blast radius priced against that decision, tests included.

## Stories (Required to Complete)
- [ ] Story: <none yet - epic is investigation-stage and undesigned>

## Acceptance Criteria (Epic Done)
- Lane 1 has a reproducible answer, not a hypothesis.
- "Do we need unwind" has a recorded owner decision, and "no" is an acceptable
  outcome.
- Each of the six existing dialects is marked fold / grandfather / delete with a
  reason.
- The user-facing outcome vocabulary is specified, even if the answer is "none".
- No implementation has occurred under this epic.

## Risks / Mitigations
- RISK: someone builds a journal + inverse system before answering lane 2, and
  it duplicates what lesser-conduit scoping already provides free.
  MITIGATION: lane 2 is a gate on lanes 3-6.
- RISK: per-construction bookkeeping lands on the meld hot path and costs
  measurable throughput. MITIGATION: benchmark before design; the repo's
  measured-not-intuited discipline applies.
- RISK: partial rollout leaves some families with inverses and some without -
  worse than none, because callers cannot tell which. MITIGATION: all 15 or an
  explicit documented subset with a refusal for the rest.

## Constraints / Assumptions
- CONFLICT, unresolved: the plane deliberately chose EAGER mirrors -
  "Relational commit deltas: NOT NEEDED (chosen final design: eager, not lazy)".
  Link and cluster mirrors are written AT THE MUTATION SITE, not at commit, so a
  journal has no single point holding the reversible effect set. This is a
  go/no-go gate for strategy D specifically. It does NOT block C or G.
  EVIDENCE: context_compass/system_docs/src_components.md:1847-1855
- Python 3.14t free-threaded: unwind runs under contention; nothing may
  reintroduce a global lock on the mutation path.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.
- [ ] No building a second transaction plane beside the working one.
- [ ] No costing strategy D before lane 2 answers whether it is needed.

## Validation / Test Approach
Not run - investigation-stage, no code. When it leaves investigation,
`patch_framework_gating.md` applies: changing an ABC that 15 families implement
is system-impacting.

## Open Questions
- Is unwind meant to be USER-facing ("roll this back for me") or only internal
  failure recovery? The requirement says "rolled back if required", which reads
  both ways, and the answer changes the entire surface.
- Should a failed meld leave objects reachable for diagnosis, or is silent
  disposal preferable? These are opposite answers and both are defensible.
- Is `TransferOfOwnership`'s private callback stack the intended prototype, or
  an accident to be replaced?

## Decision Log
- 2026-07-29 OWNER DIRECTION (supersedes the earlier "raise a mediator into
  Aether" idea). Three parts:
  1) The bootstrap ORDER STAYS AS IS: create the frame, then its mediator. That
     sequence is reasonable and is NOT the thing to change. The mediator remains
     frame-owned.
  2) The CRYSTALLIZER gets its own LIGHTWEIGHT MEDIATOR + transaction system at
     load level. Rationale: today the loader is "doing our best to accommodate"
     the absence of transactional authority above the frame - LoadGate plus
     engine-local `_build_lock` plus posture idempotence - and that is
     accommodation, not design.
  3) A load transaction should FIGURE OUT WHAT IT IS MAKING, TRY TO MAKE IT, and
     on failure take ONE OF TWO OUTCOMES:
       (a) unwind it and raise, or
       (b) LEAVE IT IN PLACE IN A BROKEN STATE SO AGENTS CAN REPAIR IT.
     Outcome (b) is a first-class design intent, not a degraded fallback: a
     half-built world is a WORK SURFACE for agents, not merely a failure.
- 2026-07-27: Filed to BACKLOG per owner ("saving this for later").
- 2026-07-27: Epic REFRAMED after owner correction. First draft scoped this to
  "wire an inverse hook into the mediator plane" - too narrow, and it missed
  that unwind is one option among seven, that checkpoint transactions are a
  separate existing concept, and that "do we need to unwind" is a live question
  rather than a settled premise.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - (none)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a while backlogged

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: ask user before implementation

## Notes
- DATETIME: 2026-07-27T23:19:33Z
  TYPE: FACT
  CLAIM: Melder's mature partial-failure vocabulary exists in restore ONLY and
    was never brought to the runtime creation path. `restore_engine.py` carries
    80 `shortfall` sites plus reverse-order `_teardown_built`;
    `creation_context.py`, which constructs and registers user objects, has 3
    `except`/`finally` handlers in total.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1-2700
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-900
  IMPACT: Reframes the epic from "build transactions" to "the answer already
    exists in one subsystem; decide whether to generalise it".
  NEXT: Lane 1 - build a real repro of a mid-graph construction failure and
    observe what survives.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-27T23:19:33Z
  TYPE: UNKNOWN
  CLAIM: What happens today when construction fails partway through a dependency
    graph is NOT KNOWN. Whether already-built objects remain registered in
    `Creations`, remain reachable, or are disposed has not been observed.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-900
  IMPACT: Every strategy choice depends on this. It must not be promoted to FACT
    without a repro.
  NEXT: Write the repro. Do not design until it is answered.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-27T23:19:33Z
  TYPE: FACT
  CLAIM: `TransactionSession` already implements the unwind plumbing
    (`register_rollback_action`, `run_abort_pipeline`, abort hooks), but
    `TransactionStrategy` declares only build_start_plan/on_start/on_end/
    apply_commit_delta - no inverse hook. The 15 families that know what a
    mutation did have no sanctioned path to feed the session that could undo it.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:409-527
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py:20-169
  IMPACT: IF strategy D is chosen, it is a wiring job on an 80%-capable plane,
    not a greenfield build. Materially cheaper than it first appears.
  NEXT: Gate on lane 2 - do not cost this until unwind is proven necessary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-27T23:19:33Z
  TYPE: HYPOTHESIS
  CLAIM: `run_abort_pipeline() -> List[BaseException]` suggests unwind failures
    are COLLECTED and returned rather than raised - meaning question 6 may
    already have an unchosen de-facto answer.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:502
  IMPACT: If nothing consumes that list, unwind failures are currently silent -
    precisely the failure mode this requirement exists to prevent.
  NEXT: Trace callers. UNKNOWN until traced; do not promote to FACT.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-29T22:21:25Z
  TYPE: FACT
  CLAIM: LANE 1 ANSWERED - this RESOLVES the SCORE-10 UNKNOWN above. When a
    dependency-graph build fails partway, melder FAILS FAST, TRANSLATES THE ERROR
    RICHLY, AND LEAVES EVERYTHING ALREADY BUILT IN PLACE, WITH NO RECORD OF WHAT
    WAS LEFT. Mechanically: the phase-11 door emits, PER STEP, a try/except around
    the inlined constructor call - `try: instance_N = target_N(dep=instance_1,...)`
    / `except Exception as exc: _raise_meld_construction_error(spell_N, exc)`.
    That helper's ENTIRE body is `raise MeldExecutionError(spell_id, spell_name,
    message, inner=exc) from exc` - no disposal, no unwind, no compensation. The
    error propagates out of the executor, out of `CreationContext.execute` (whose
    only `finally` releases the CreationGate ticket, nothing else), and out of
    meld. Registration is emitted INLINE per step via `_append_register_source`
    (five call sites) gated on `row["must_register"]`, so every step before the
    failure that carried `must_register=True` IS ALREADY IN `Creations` AND STAYS
    THERE. Steps without registration simply become garbage.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:589-638
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:334-478
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1082
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:603-613
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:265-272
  IMPACT: Melder's current posture is the WEAKEST quadrant of the option space:
    partial state PERSISTS and does so SILENTLY. It is not strategy F, because F
    pairs surviving state with refuse-to-use gating and there is no such gating
    here; and it is not strategy G, because G pairs a partial result with a
    shortfall ledger and no ledger exists on this path. The caller receives one
    rich error naming the FAILING spell and has no way to learn which of the
    preceding steps survived in `Creations`.
  NEXT: Lane 2 - determine whether lesser-conduit discard (strategy C) actually
    disposes creations built inside it. If it does, C is the cheap fix and unwind
    (D) stays unnecessary. That is now the gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-29T22:21:25Z
  TYPE: FACT
  CLAIM: The generic fallback path behaves identically to the inlined fast path
    on failure - `_raise_meld_construction_error`'s docstring states it "mirrors
    the error wrapping in `_construct_spell_instance` so the inlined fast path and
    the generic fallback report construction failures identically". So the finding
    above is not fast-path-only. Separately: the emitted handler catches
    `Exception`, not `BaseException`, so `KeyboardInterrupt`/`SystemExit`
    propagate untranslated.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:603-610
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:636
  IMPACT: Closes the "maybe only the optimized lane behaves this way" escape
    hatch. Both construction lanes leak partial state identically.
  NEXT: Same as above - lane 2.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-29T22:21:25Z
  TYPE: RISK
  CLAIM: `CreationContext.load_cached` swallows a previous context's cleanup
    failure with a bare `except Exception: pass`, undocumented as best-effort.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:231-234
  IMPACT: Minor and out of this epic's scope, but it is a silent-failure site on
    the same path the epic is about, and repo policy bans undocumented
    `except: pass` in owned runtime code.
  NEXT: Raise as a separate task if the owner wants it; do NOT fix under this
    investigation epic.
  REREAD: HELPFUL
  SCORE_0_TO_10: 6

- DATETIME: 2026-07-29T22:46:22Z
  TYPE: DECISION
  CLAIM: Direction set by owner - lightweight mediator + transaction system IN
    THE CRYSTALLIZER at load level, frame->its-mediator creation order retained,
    and a per-transaction failure policy offering unwind-and-raise OR
    leave-broken-for-agent-repair. The current LoadGate + `_build_lock` +
    posture-idempotence arrangement is explicitly named as ACCOMMODATION for
    missing authority, not as the intended design.
  EVIDENCE:
  - context_compass/tickets/epics/2026-07-27_transactional_structure_unwind_epic.md (Decision Log, 2026-07-29)
  IMPACT: Closes the "what are we solutioning" question and retires the
    raise-mediator-into-Aether option. Problems 2 and 3 from the four-problem
    split are now in scope; problem 1 (frame not on the teardown stack) becomes a
    HARD PREREQUISITE for outcome (a); problem 4 (record/world divergence)
    becomes a HARD PREREQUISITE for outcome (b).
  NEXT: Adjudicate the three consequences recorded in the note below before any
    design work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-29T22:46:22Z
  TYPE: FACT
  CLAIM: HALF OF THE OWNER'S REQUIREMENT ALREADY EXISTS. "Figure out what it is
    making" is shipped: `LoadPlan` is declarative and INSPECTABLE BEFORE
    ACTIVATION (scope world|conduit|frame, per-kind key counts), and
    `_build_plan_levels()` compiles the folded world into dependency LEVELS
    (frame -> its books; both endpoint books -> each link edge; member books ->
    their clusters). The missing half is the OUTCOME POLICY, not the planning.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/load_plan.py
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:758-772
  IMPACT: Scopes the work down materially. A crystallizer mediator does not need
    to invent plan derivation; it needs to own admission + per-unit outcome
    policy over a plan that already exists and is already level-compiled.
  NEXT: Confirm whether LoadPlan is the right carrier for a per-unit outcome
    policy field, or whether policy belongs on the mediator.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-29T22:46:22Z
  TYPE: RISK
  CLAIM: Three consequences gate the owner's direction, each blocking a specific
    half of it.
    (1) OUTCOME (a) IS IMPOSSIBLE TODAY: the frame is `record_built` only and is
        NEVER pushed to `_built_stack` (restore_engine.py:1605 vs :1802/:1871),
        so `_teardown_built()` cannot unwind a frame. Any unwind-and-raise
        outcome is incomplete by construction until frame becomes a stacked
        unit.
    (2) OUTCOME (b) IS CURRENTLY A TRAP, NOT A WORK SURFACE: a half-built frame
        keeps a FROZEN posture, and `bind_frame_configuration` is idempotent only
        against a MATCHING posture - a conflicting frozen posture keeps canonical
        frame truth and merely logs. So a cross-checkpoint retry against a
        leave-broken world silently inherits the dead run's posture. For (b) to
        be repairable rather than poisoned, posture must be re-authorable by the
        repairing agent.
    (3) A CRYSTALLIZER MEDIATOR IS STILL AN OUTER LAYER OVER N INNER COMMITS.
        The inner frame-level transactions genuinely commit as the load proceeds
        (per-identity root sessions, LoadGate grants the cohort free passage).
        So the outer mediator must decide what it actually owns: INVERSES for
        those committed inner transactions, or OBJECT TEARDOWN as a proxy (what
        `_teardown_built` does today). If it owns teardown only, it is better
        bookkeeping over the same mechanism rather than a transaction system.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1605
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1802
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1871
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1670-1708
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:354-361
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:496-503
  IMPACT: (1) and (2) are cheap and local; (3) is the actual architecture
    decision and determines whether this epic delivers a transaction system or a
    better-instrumented driver.
  NEXT: Get an owner ruling on (3) - inverses or teardown-as-proxy - since (1)
    and (2) are implementation work either way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary

BACKLOGGED BY DESIGN - owner said "saving this for later". No board row, no
assigned agent, no active routing.

Read the Option Space table first. The framing that matters: melder has TWO
existing transaction concepts that answer DIFFERENT questions - mediator
transactions answer "who may mutate concurrently", checkpoint transactions
answer "restore the whole world to time T" - and NEITHER answers "object 37 of
50 just failed". Seven strategies exist for that; melder already ships five of
them somewhere; unwind is the most expensive and is not obviously needed.

Do lane 1 first: nobody currently knows what happens when a mid-graph
construction fails. Then lane 2: if throwing away a lesser conduit already
covers the common case, strategy D may never be worth building. Do not cost the
journal before that question is answered.
