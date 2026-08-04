# Task (SPIKE): Mediator coverage assessment — conjure, pre-conjure bind, SpellSystemStates

## Metadata
- Task ID: TASK-2026-06-20-mediator-coverage-spike
- Story: UNKNOWN (precedes a possible mediator-coverage-expansion epic)
- Status: review
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p2
- Created: 2026-06-20T19:20:00Z
- Updated: 2026-06-20T20:04:00Z

## Objective
Read-only investigation: do `conjure`, pre-conjure `bind`, and SpellSystemStates activities need
their own mediator (change-control) transactions? Understand each, then give a transact / don't-transact
verdict grounded in the cost model (registration-time = cheap to transact; hot-path = needs a frequency
gate; transactions arbitrate cross-identity STRUCTURAL conflict, not frame-local bookkeeping).

## Findings

### 1. Pre-conjure bind — ALREADY TRANSACTED (no work)
- `BindTransactionStrategy.build_start_plan` already branches on the identity's `conjured` flag:
  - pre-conjure: spellbook-only scope, INTENT claim on the spellbook, initiator `spellbook:<id>`,
    `conduit_ids=()`.
  - post-conjure: spellbook + paired root conduit + conduit_ward + cluster memberships (resolved via
    topology reads only: get_identity / get_clusters_for_conduit / get_primary_conduit_id_for_spellbook).
- EVIDENCE: bind_transaction_strategy.py:82-101 (branch), :103-158 (pre), :160-267 (post).
- Verdict: nothing to build; bind is envelope-clean and covers both postures.

### 2. Conjure — BEST new candidate, but the trickiest (one design wrinkle)
- No CONJURE value in ChangeTransactionType (transaction_request.py:10-46: BIND/LINK/TRANSFER_OWNERSHIP/
  .../CLUSTER_JOIN — no conjure). Conjure opens ZERO change-control transaction.
- Conjure IS the genesis structural event: spellbook -> births root Conduit + ConduitWard, runs
  structural + resolution phases, wires ownership into spells, registers the conduit identity, flips
  `conjured`. Cross-identity + once-per-spellbook (registration-time => cheap-to-transact bucket).
- It is NOT a live correctness gap today: conjure runs fully under `Spellbook._lock` with a single-conjure
  invariant (`if self._conjured: raise`), and the new conduit is not observable to anyone until conjure
  publishes it, so the cross-identity contention surface is ~nil. EVIDENCE: spellbook.py:4119-4163.
- The case FOR a CONJURE transaction is consistency / observability / free-threading, not a race fix:
  it is the only structural genesis event invisible to the mediator (no embargo/audit/risk trail), and
  under no-GIL 3.14t we are trying to move OFF reliance on one coarse object lock.
- WRINKLE: unlike bind/link/transfer (which seal already-existing identities), conjure CREATES the
  conduit identity mid-window. Recommended shape if pursued: seal only the activation tail
  (`_activate_conjured_conduit` — publish/ownership-wire/flag-flip), claiming spellbook EXCLUSIVE for the
  window and registering+claiming conduit/ward at activation; do NOT wrap the heavy phase compute in the
  seal. EVIDENCE: spellbook_creation_system.py:161-237.

### 3. SpellSystemStates activities — DON'T transact
- Frame-local "control tower": lineage validity/dirty flags, dependency DAG (+reverse edges), per-conduit
  resolution verdicts, targeted collection/contract invalidation. Every method is RLock-guarded.
- Mutators split two ways:
  - hot-path / high-frequency (update_dependencies, mark_structural_change, compute_impact_closure,
    mark_collection/contract_dependents_dirty, consume_dirty_indexes, set_conduit_*_validity): these
    record validation results; they do not arbitrate cross-identity structural conflict. Wrapping them in
    mediator windows fails the frequency gate (contention on every validation pass) for ~no benefit.
  - registration-time (register_index): already called from the bind path, so it already rides inside the
    BIND window; no separate transaction needed.
- EVIDENCE: spell_system_states.py:246-300 (register_index), :438-594 (deps/impact), :863-1190 (resolution
  + targeted dirty); spell_system_state.py:299-537 (validity/flag transitions, all locked).
- Verdict: leave untransacted. If conjure gets a transaction, the resolution-phase writes during conjure
  are covered by that window; otherwise they stay frame-local bookkeeping.

## Recommendation (REVISED 2026-06-20T20:02 — see REVISION note; section 3 above is superseded)
- Pre-conjure bind: closed (already done).
- SpellSystemStates: REVERSED -> bring under the mediator. Not by wrapping every set_validity (conjure-time
  writes are already serialized under the spellbook lock), but via a spell-lineage scope + a spell-state
  /remediation transaction, with the EXISTING lineage-affecting strategies (NOTCH, ADD/REMOVE_FROM_INDEX,
  TRANSFER_OWNERSHIP) also claiming the lineage scope. This is the high-value piece.
- MUTATION: DESCOPED (user 2026-06-20T20:04). Stays out until everything else is done; it will be its own
  new subsystem, not a strategy bolted onto this work. The lineage scope is designed so MUTATION can adopt
  it later without rework.
- Conjure: optional. Full mediator coverage / shed the coarse spellbook lock under 3.14t -> seal the
  activation tail (mid-window identity creation). Not a correctness gap today. NEEDS USER CALL.

## Validation
- Read-only spike. No source edits. No pytest.

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: investigation complete; verdicts recorded; conjure decision returned to user.

## Notes
- DATETIME: 2026-06-20T19:20:00Z
  TYPE: DECISION
  CLAIM: Two of three closed without work (pre-conjure bind already transacted; SpellSystemStates is
    hot-path/frame-local + registration rides inside BIND). Conjure is the only real candidate and is a
    consistency/free-threading play, not a race fix; its wrinkle is mid-window identity creation, so seal
    the activation tail only.
  EVIDENCE:
  - src/.../strategies/bind_transaction_strategy.py:82-267
  - src/melder/aether/spellbook/spellbook.py:4119-4163
  - src/melder/aether/spellbook/spellbook_creation_system.py:161-237
  - src/.../spell_system_states/spell_system_states.py:246-300,438-594,863-1190
  - src/.../change_control_manager/transaction_request/transaction_request.py:10-46
  IMPACT: Scopes a potential mediator-coverage-expansion epic down to (at most) one transaction: CONJURE.
  NEXT: User decides whether to spike the CONJURE transaction design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-06-20T20:02:00Z
  TYPE: REVISION
  CLAIM: REVERSING the section-3 "don't transact SpellSystemStates" verdict after deeper scoping
    (user-directed). Two of my original objections were wrong and a third gap surfaced:
    (1) FREQUENCY: state writes are NOT a per-meld hot path. All set_conduit_*_validity / dirty writers
        are conjure-time (spellbook_creation_system, compiler_phase_6) or validation/remediation-time
        (spell_system_validation_system). Matches the user's "only during conjure and if there's an issue."
    (2) BYPASS GAP (the real issue): state-health writes go DIRECT to spell_system_states with NO mediator
        claim and a best-effort try/except (spell_system_validation_system.py:244-261). So "addressing an
        issue" on a spell holds no seal -> a NOTCH/TRANSFER/index op can be admitted concurrently, and a
        structural op's own spellbook+conduit EXCLUSIVE seal (notch_transaction_strategy.py:110-141) does
        NOT protect the state record because the state writer ignores the embargo. Both directions race.
    (3) NO LINEAGE SCOPE: scope vocabulary is spellbook/identity/transaction_owner/conduit/cluster/binding
        /contract (transaction_manager.py:262-395) -- nothing keyed by spell_index_id. No fine-grained
        handle to serialize lineage remediation vs structural ops without taking the whole spellbook/conduit.
    (4) MUTATION UNWIRED: ChangeTransactionType.MUTATION exists (transaction_request.py:38) but is NOT
        registered in the strategy builder (transaction_strategy_builder.py:334-392). The user's "what if a
        mutation is triggered" is literally unguarded today.
  EVIDENCE:
  - src/.../spell_compiler/system/spell_system_validation_system.py:244-261 (bypass, best-effort)
  - src/.../strategies/notch_transaction_strategy.py:110-141 (structural seal ignores the state record)
  - src/.../transaction_manager/transaction_manager.py:262-395 (no lineage scope)
  - src/.../strategies/transaction_strategy_builder.py:334-392 (MUTATION not registered)
  - callers: spellbook_creation_system.py:2262, spell_system_validation_system.py:245, compiler_phase_6.py:458
  PROPOSED SHAPE (mediator-coverage-expansion epic, pending user direction):
  - A. make_scope_key_spell_lineage(spell_index_id) -- new lineage scope.
  - B. SPELL_STATE / remediation transaction: claims affected lineage(s) EXCLUSIVE while devops works the
       SpellSystemState (gate/revalidate/clear-dirty); route the validation-system "issue" path through it.
  - C. lineage-affecting strategies (NOTCH, ADD/REMOVE_FROM_INDEX, TRANSFER_OWNERSHIP, + new MUTATION) also
       claim the lineage scope -> structural ops and remediation mutually serialize at lineage granularity.
  - D. wire MUTATION to a real strategy as part of this.
  - Conjure-time bulk writes stay in the (single-threaded, spellbook-locked) conjure/compile path; the value
    is the LIVE post-conjure remediation race, exactly the user's "if there's an issue" case.
  - COORDINATION: B/C/D touch the spell compiler + validation system (likely other agents' surfaces) ->
    mailbox before any edit.
  NEXT: User decides scope (lineage scope + remediation tx + MUTATION, and whether CONJURE rides along).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-20T20:04:00Z
  TYPE: DECISION
  CLAIM: User descoped MUTATION from this effort: "mutation stays out until we finish everything else, it'll
    be a new subsystem." So the mediator-coverage-expansion scope is now (1) lineage scope, (2) spell-state
    /remediation transaction, (3) existing NOTCH / ADD_TO_INDEX / REMOVE_FROM_INDEX / TRANSFER_OWNERSHIP also
    claim the lineage scope. MUTATION wiring is explicitly deferred to its own future subsystem; the lineage
    scope is to be designed so MUTATION can adopt it later with no rework. CONJURE remains a separate
    optional item.
  EVIDENCE: this ticket (REVISION note 2026-06-20T20:02) + Recommendation block.
  NEXT: User decides whether to author the epic + stories for the 3-part scope.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Read-only assessment of whether conjure / pre-conjure bind / SpellSystemStates need mediator transactions.
Result: bind already covers pre/post-conjure; SpellSystemStates should stay untransacted (hot-path +
already-inside-BIND registration); conjure is the only candidate and is optional (consistency/3.14t, not a
correctness gap) — pending a user call on whether to design a CONJURE transaction.
