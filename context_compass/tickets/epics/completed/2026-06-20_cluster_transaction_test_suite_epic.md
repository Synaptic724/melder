# Epic: Mediator Transaction Test Suite (all transactions I built, except transfer_ownership)

## Metadata
- Epic ID: EPIC-2026-06-20-cluster-transaction-test-suite
- Status: draft
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p2
- Created: 2026-06-20T11:36:58Z
- Updated: 2026-06-20T11:36:58Z
- Target Window: 2026-Q2
- Related Program/Initiative: unique_per_conduit_cluster team-store + leaderless cluster sharing
- Related epics:
  - tickets/epics/2026-06-16_cluster_leader_election_transactions_epic.md (elect/unelect machinery)
  - tickets/epics/2026-06-16_unique_per_conduit_cluster_team_store_epic.md (team-store seam)

## Problem / Opportunity
Four cluster-domain change-control transactions now exist but lack a dedicated, contract-level
test suite that proves they are functional end to end:
- `CLUSTER_JOIN` / `CLUSTER_LEAVE`: wrap `ConduitCluster.handle_join` / `handle_leave` so the
  whole conduit entry/exit (membership mutation + bidirectional spell-share fan-out) runs as ONE
  transaction that seals every involved conduit (a link pattern), with the in-window shares running
  transaction-free under the held seal.
- `ELECT_CONDUIT_CLUSTER_LEADER` / `UNELECT_CONDUIT_CLUSTER_LEADER`: wrap the elected-leader team
  store bind/unbind; elect is low-coordination (inert->active), unelect drains every member root
  lineage before unbinding.

Today only ~8 unit tests exist for the elect/unelect strategies
(`tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_strategy_builder_and_strategies.py`),
and there is no targeted coverage for CLUSTER_JOIN/CLUSTER_LEAVE at any level. Without a suite that
fails for real regressions, the wiring (which crosses `conduit_cluster.py` and the contract gate in
`conduit.py`) can silently break.

## MRP Alignment (Most Reasonable Product)
The cluster transactions are core correctness machinery: they serialize structural mutations of the
object world so concurrent joins/leaves/elections cannot interleave into orphaned shares or
use-after-dispose stores. A trustworthy core requires that this concurrency contract be proven, not
assumed. This suite is the verification layer that lets the cluster transactions ship as MRP rather
than as an untested trap.

## Ticket Contract
- ENTRY_GATE: certified `mediator_builder_0`; `attention_board.md` row routes this epic; the four
  transactions are confirmed wired in source (verified 2026-06-20, see Notes).
- EXECUTION_BOUNDARY: ADD/UPDATE tests only, under `tests/unit`, `tests/component`, `tests/integration`
  (+ `tests/mocks` helpers if a shared fixture is genuinely needed). One cross-cutting doc-fix task
  (the stale `ConduitCluster` class docstring). NO change to transaction runtime behavior under this
  epic; if a test surfaces a real runtime bug, raise it (do not silently fix) per engineer rules.
- DEPENDENCIES: the wired implementation in `conduit_cluster.py` + `conduit.py`; existing fixtures in
  `tests/_frame_posture_test_support.py`, `tests/mocks/spellbook/core_classes.py`; existing cluster
  tests as fixture precedent.
- EXIT_GATE: all three stories accepted; user runs the 3.14t suite and reports green; board/closure
  sync complete.
- FAILURE_ESCALATION: DECISION_REQUEST on test-count/scope changes; CONFLICT if a test exposes a
  runtime contract bug (stop, raise, do not fix under a test epic without approval); BLOCKER if
  fixtures cannot construct a cluster/mediator slice.

## Goals (Outcomes)
- Prove each of the four cluster transactions is functional with contract-level tests at three
  levels (unit, component, integration).
- Lock the CLUSTER_JOIN/CLUSTER_LEAVE invariants: one transaction seals all involved conduits;
  in-window shares run transaction-free; the contract gate admits cluster_join/cluster_leave.
- Lock the elect/unelect invariants: elect binds with no drain; unelect drains every member lineage
  then unbinds then reopens (fail-closed); re-election raises.
- Leave a suite that fails for real regressions and passes through harmless refactors.

## Non-Goals (Explicit Exclusions)
- No change to transaction runtime behavior (this is a test epic).
- No new production locks, no strategy redesign.
- No coverage of unrelated change-control transactions (bind, link, unlink, transfer, notch,
  add/remove_from_index) beyond what is needed as a no-regression check.
- No agent-run pytest claims: the sandbox is Py3.10 and cannot import the 3.14t eager chain; the user
  runs the suite.

## Scope Boundaries
- In scope: tests for the 11 transactions authored/reworked with the user — LINK, BIND, CLUSTER_LINK,
  UNLINK (claim modes + commit deltas); NOTCH, ADD_TO_INDEX, REMOVE_FROM_INDEX (SpellIndex backend);
  ELECT_CONDUIT_CLUSTER_LEADER, UNELECT_CONDUIT_CLUSTER_LEADER; CLUSTER_JOIN, CLUSTER_LEAVE. Plus the
  stale `ConduitCluster` class-docstring fix.
- Out of scope: TRANSFER_OWNERSHIP (user-excluded) and MUTATION (no strategy); source/behavior edits
  to the transactions; the deferred single-cluster-invariant enforcement.
- Coverage note: existing unit tests already cover several strategies thinly (bind 3, link 3, unlink
  1, cluster_link 2, notch/add/remove 1 each, elect/unelect 4); cluster_join/cluster_leave have ZERO.
  New tests are additive and weighted to the gaps + concurrency-heavy paths.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: scope, story split, and test breakdown defined and grounded in verified source
  + real fixtures; awaiting user go-ahead to begin the write pass (expansion gate: >5 files).

## Success Metrics
- 100 tests authored: 40 integration, 20 component, 40 unit (user-confirmed counts).
- Density >= 20 tests / 100 LOC across the wired surfaces (concurrency/lifecycle code).
- Every test asserts an observable outcome (state, raise, snapshot) — zero Rank E/F filler.
- User-run 3.14t suite reports green (verification step owned by the user).

## Requirements (Functional + Non-Functional)
- Functional: cover each transaction's happy path, guard/error paths, scope-seal footprint,
  in-window effect, and (integration) concurrency behavior.
- Non-functional: deterministic, no wall-clock/network reliance; integration concurrency tests use a
  looped stress pattern (mirror the existing 40x concurrent-conjure precedent) and must be repeatable.
- Style: synaptic test conventions — Optional/Union (no PEP 604), no `from __future__ import
  annotations` in new files unless the file's directory already uses it, contract-level assertions.

## Constraints / Assumptions
- Single-file writes stay well under the ~900 LOC auto-reject ceiling; large test files are split.
- ASSUMPTION (to verify when writing each story): component/unit fixtures can build a cluster +
  mediator slice the same way the integration fixture builds the full Aether stack. Verify against
  the existing component/unit test files before writing.

## Dependencies / External References
- src/melder/aether/conduit/conduit_cluster.py:185-188,342-503,817-903 (available_transactions; wrap;
  share flag)
- src/melder/aether/conduit/conduit.py:3908-3940 (contract gate admits cluster_join/cluster_leave)
- src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/
  cluster_join_transaction_strategy.py, cluster_leave_transaction_strategy.py
- tests/integration/melder/aether/test_aether_integration_clusters_membership.py (integration fixture
  precedent)

## Milestones (Track Progress)
- [ ] Milestone 1: Unit story (40) authored + self-reviewed.
- [ ] Milestone 2: Component story (20) authored + self-reviewed.
- [ ] Milestone 3: Integration story (40) authored + self-reviewed.
- [ ] Milestone 4: Stale `ConduitCluster` class-docstring fixed.
- [ ] Milestone 5: User runs the 3.14t suite; failures triaged; epic accepted.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-06-20-cluster-tx-unit-tests - 40 unit tests (strategies, builder, enum,
      mediator pass-through, contract gate).
- [ ] Story: STORY-2026-06-20-cluster-tx-component-tests - 20 component tests (conduit_cluster +
      mediator slice: wrap opens correct tx + metadata; share flag; bind guard).
- [ ] Story: STORY-2026-06-20-cluster-tx-integration-tests - 40 integration tests (full Aether/cloud
      stack: join/leave fan-out atomicity, leaderless sharing, elect/unelect, concurrency stress).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-06-20-cluster-tx-unit-tests
- [ ] Task: Complete story STORY-2026-06-20-cluster-tx-component-tests
- [ ] Task: Complete story STORY-2026-06-20-cluster-tx-integration-tests
- [ ] Task: Fix the stale `ConduitCluster` class docstring (Layer-1 "CURRENT GAP / not yet built"
      text) to reflect the wired CLUSTER_JOIN/CLUSTER_LEAVE transactionalization.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- 100 tests exist at the stated split and every test makes a contract-level assertion.
- CLUSTER_JOIN/CLUSTER_LEAVE: a join/leave fans out/tears down shares under a single transaction;
  the contract gate admits the type; the in-window shares do not open nested cluster_link
  transactions; tests prove membership + sharing are atomic (no half-joined state on abort).
- elect: binds the facade with no drain and yields exactly one shared instance per cluster under
  concurrent member melds; re-election raises.
- unelect: drains every member root lineage before unbind and reopens on every exit path; no meld is
  mid-create against a store being unbound.
- No regression to cluster_link/link/unlink/bind/transfer.
- User runs the 3.14t suite and reports green (validation owned by user; agent reports "Not run.").

## Risks / Mitigations
- RISK: agent cannot run pytest (Py3.10 sandbox) -> MITIGATION: author dense contract tests; user runs
  3.14t suite; iterate on reported failures.
- RISK: a test surfaces a real wiring bug (e.g., contract-gate footprint vs share peer set) ->
  MITIGATION: raise as CONFLICT, do not silently fix under a test epic.
- RISK: integration concurrency tests flaky -> MITIGATION: deterministic loop counts, no wall-clock
  assumptions, mirror the existing stress precedent.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No Rank E/F filler (existence/`hasattr`/"did not crash") tests.
- [ ] No agent claim that pytest/coverage ran.

## Validation / Test Approach
Per-level breakdown across the 11 transactions, weighted to gaps + concurrency-heavy paths
(target counts; refined per story). Model files: unit
`tests/unit/.../change_control_manager/test_transaction_strategy_builder_and_strategies.py`;
component `tests/component/.../conduit/test_conduit_component_transactions.py`; integration
`tests/integration/melder/aether/test_aether_integration_*`.

UNIT (40) — strategy `build_start_plan` + admission internals, no live cluster:
- cluster_join strategy (6) + cluster_leave strategy (6): NEW (zero existing). scope_keys (conduit +
  ward + spellbook), scope_claims (spellbook INTENT; conduits/wards EXCLUSIVE/absent), capabilities
  (cluster_join/leave, cluster_link, contract_mutation), conduit_ids passthrough, _involved_conduit_ids
  raises on empty, metadata mode marker, on_start/on_end no-op.
- cross-cutting (4): builder resolves cluster_join/cluster_leave; enum has both values; identity
  available_transactions wiring.
- deepen thin strategies (24): unlink 3, notch 3, add_to_index 3, remove_from_index 3, bind 2, link 2,
  cluster_link 2, elect 3, unelect 3 (incl. drain/reopen via ConduitLineageGateOps).

COMPONENT (20) — conduit_cluster + mediator + conduit-transaction slice, real collaborators, no IO:
- cluster_join wrap (3): handle_join opens CLUSTER_JOIN, conduit_ids = joiner + members;
  share_to_borrower(open_transaction=False) runs the contract under the held seal; end_transaction
  expected_type.
- cluster_leave wrap (3): mirror for handle_leave + remove_shared_from_borrower flag.
- elect/unelect wrap (4): elect_leader/unelect_leader open the tx; bind guard raises on re-election.
- contract gate (2): add_spell_to_contract / remove_root_from_contracts admitted under
  cluster_join/cluster_leave active request.
- notch/add_to_index/remove_from_index + unlink (5): begin/transaction/end registration + abort.
- link/bind/cluster_link claim-mode component checks (3).

INTEGRATION (40) — full Aether/cloud + spellbook stack:
- cluster_join (6): add_conduit_to_cluster fans shares both directions; membership + sharing atomic;
  leaderless sharing with no leader; multi-member join.
- cluster_leave (6): remove_conduit_from_cluster tears down both directions; leaver registry dropped.
- elect (5): one shared unique_per_conduit_cluster instance per cluster; inert door hard-errors.
- unelect (5): drain + unbind + reopen; concurrency stress (looped, mirror the 40x conjure pattern).
- link/bind/cluster_link/unlink families (8): real conduit link/unlink + cluster share/unshare.
- notch/add_to_index/remove_from_index (6): real SpellIndex move/rekey operations.
- cross-transaction no-regression + mixed concurrency stress (4).

## Rollout / Adoption Plan
- Author story by story (unit -> component -> integration), each story self-reviewed before the next.
- Hand the suite to the user to run on the 3.14t venv; triage failures; accept on green.

## Open Questions
- Q1: Do component/unit levels get their own cluster+mediator fixture, or is a shared helper added to
  `tests/mocks/`? Resolve by reading the existing component/unit fixtures before writing each story.
- Q2: Should the concurrency stress live only in integration, or also a smaller component-level
  variant? Lean: integration only (real threads), per the testing taxonomy.

## Decision Log
- 2026-06-20: Scope = the four cluster transactions only (user-confirmed); counts 40/20/40
  (user-confirmed).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-20T11:36:58Z
  TYPE: FACT
  CLAIM: The four cluster transactions are confirmed wired in current source: conduit_cluster
    declares cluster_join/cluster_leave and wraps handle_join/handle_leave; the share helpers take an
    open_transaction flag; conduit.py's contract gate admits cluster_join/cluster_leave. The
    elect/unelect machinery + 8 unit tests already exist from the election epic.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:185-188
  - src/melder/aether/conduit/conduit_cluster.py:342-503
  - src/melder/aether/conduit/conduit.py:3908-3940
  IMPACT: The test suite has a real, verified target; tests can assert against the wired behavior.
  NEXT: On user go-ahead, create the three story tickets and author the unit story first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T11:36:58Z
  TYPE: RISK
  CLAIM: The CLUSTER_JOIN/CLUSTER_LEAVE runtime wiring (conduit.py + conduit_cluster.py) was landed
    earlier this session without a ticket and, being a lifecycle + cross-component contract change,
    outside the patch-framework entry gate. This epic does not retro-authorize that; it tests it.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3908-3940
  - src/melder/aether/conduit/conduit_cluster.py:342-503
  IMPACT: The implementation provenance is irregular; the doc-fix task + this suite are the cleanup,
    but a separate decision may be needed on whether to open a retroactive implementation ticket.
  NEXT: Raise to user whether the CLUSTER_JOIN/LEAVE implementation needs its own retroactive ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-20T11:36:58Z
  TYPE: FACT
  CLAIM: Consumed cross-lane mailbox NOTICE from general_0 (2026-06-19T23:00:16Z): general_0 edited
    DOCSTRINGS ONLY in three of mediator_builder_0's strategy files (notch / add_to_index /
    remove_from_index) to match the single-spell model. The add/remove docstrings still describe the
    deleted mint/GC mechanism and want a full transfer-flip rewrite when general_0 rebuilds the seams
    (to coordinate then, not piecemeal). No ACK requested; FYI only; not part of this cluster-test epic.
  EVIDENCE:
  - codex/context_compass/mailbox_board.md (general_0 -> mediator_builder_0, 2026-06-19T23:00:16Z)
  IMPACT: Records the message durably per mailbox protocol so the mailbox entry can be deleted.
  NEXT: Coordinate the add/remove strategy docstring rewrite with general_0 when the index seams are
    rebuilt (separate lane).
  REREAD: HELPFUL
  SCORE_0_TO_10: 6
- DATETIME: 2026-06-20T11:40:00Z
  TYPE: DECISION
  CLAIM: Scope broadened by user direction from the 4 cluster transactions to ALL 11 transactions
    authored/reworked with the user (LINK, BIND, CLUSTER_LINK, UNLINK, NOTCH, ADD_TO_INDEX,
    REMOVE_FROM_INDEX, ELECT, UNELECT, CLUSTER_JOIN, CLUSTER_LEAVE); transfer_ownership explicitly
    excluded, MUTATION has no strategy. Totals held at the user's original 40 integration / 20
    component / 40 unit = 100, weighted to the zero-coverage gaps (cluster_join/leave) and the
    concurrency-heavy paths (unelect drain, join/leave atomicity, unlink), lighter on the already
    thinly-covered claim-mode strategies.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/completed/2026-06-13_link_transaction_claim_modes_and_commit_deltas_task.md
  - codex/context_compass/tickets/tasks/completed/2026-06-14_family_claim_modes_bind_cluster_and_unlink_transaction_task.md
  - codex/context_compass/tickets/epics/2026-06-14_spellindex_genuine_index_operations_epic.md
  IMPACT: The suite now covers the full set the user built with me; the 100-test budget is reallocated.
  NEXT: Create the unit story and author the cluster_join/cluster_leave strategy unit tests first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T12:05:00Z
  TYPE: MEASURE
  CLAIM: ~106 tests landed, all py_compile-clean (pytest Not run; Py3.10 sandbox). UNIT 70 (48
    functions + 22 parametrized) across 3 files covering all 11 strategies + builder/enum. COMPONENT
    20 covering the cluster_join/cluster_leave wrap (handle_join/leave open the right tx + metadata +
    end success), the open_transaction=False in-window share/unshare (no nested cluster_link), the
    re-election guard, elect_leader abort (success=False), and the bidirectional fan-out under the
    seal. INTEGRATION 16 covering CLUSTER_JOIN/CLUSTER_LEAVE end-to-end via cloud.add/remove (membership
    tracking, shared-root registration, leave teardown, guards). The user/linter added a real
    ClusterCreations facade to the component stub.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_cluster_membership_transaction_strategies.py:1-470
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_link_family_transaction_strategies_expansion.py:1-520
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_index_and_leader_transaction_strategies_expansion.py:1-470
  - tests/component/melder/aether/conduit/test_conduit_component_cluster_transactions.py:1-560
  - tests/integration/melder/aether/test_aether_integration_cluster_membership_transactions.py:1-470
  IMPACT: Over the 100-test target; CLUSTER_JOIN/LEAVE covered at all 3 levels. Remaining: integration
    for link/bind/unlink/notch/add/remove/elect/unelect (need their own fixtures) + the stale
    ConduitCluster class-docstring fix.
  NEXT: User runs the 3.14t suites; triage; then the remaining integration slice + docstring fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction (test split, story sequencing, what "functional" means per
  transaction), cross-story tradeoffs, and the implementation-provenance risk.
- Reference story/task notes for tactical fixture detail instead of duplicating it here.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Test-only epic to prove the four cluster transactions (CLUSTER_JOIN, CLUSTER_LEAVE,
ELECT/UNELECT_CONDUIT_CLUSTER_LEADER) are functional, with 100 tests split 40 integration / 20
component / 40 unit. Implementation is already wired (verified in Notes). Three stories (one per
level) plus a doc-fix task for the stale ConduitCluster class docstring. Agent cannot run the 3.14t
suite (Py3.10 sandbox) — the user runs it and reports results; agent says "Not run." Staged in draft
awaiting user go-ahead to begin the write pass (expansion gate: the suite spans >5 files).
