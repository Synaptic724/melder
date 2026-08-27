# component_patch_dev_ops_transactions

## Metadata
- Patch ID: devops_scope_acquisition_2026_06_12
- Component: dev_ops change-control transaction plane
- Status: in_progress
- Owner: codex
- Agent Name: reviewer_0
- Created: 2026-06-12T21:42:50Z
- Updated: 2026-06-12T21:42:50Z

## Component Purpose and Boundary
- Current boundary:
  - admission = conflict scan over in-flight requests + binary embargo scan
  - pending = coarse cross-thread root FIFO (`_pending_root_starts`),
    default-off queueing flag
  - registry relational maps unmaintained by runtime (no live callers for
    link/cluster registration); ownership maintained by frame boundary writes
- Target boundary:
  - admission = atomic moded acquisition against the embargo-owned lock table
  - pending = scope-local blocking wait in the mediator with wake-on-release
  - registry relational maps maintained by strategy commit deltas under held
    scopes; fact records track last-reported baselines

## Before/After Behavior Summary
- Before: overlapping requests raise immediately on admission denial; five
  disjoint binds admit in parallel; two same-scope binds always collide
  (binary embargo); conflict and embargo double-report the same overlap.
- After: overlapping requests wait up to the configured timeout and admit
  when scopes release; share-compatible claims (S/S) admit concurrently on
  the same scope; X collisions serialize; denial-after-timeout carries
  blocking scope keys and holder request ids; one gate decides.

## Interface Deltas
- Inputs:
  - `build_request(..., scope_claims=...)` optional (key, mode) pairs
  - `EmbargoManager.try_acquire / acquire_blocking / release_owner`
  - `TransactionStrategy.apply_commit_delta(registry, staged, identity)`
- Outputs:
  - `ChangeControlAdmissionResult` rejection evidence now reports blocking
    scope keys (embargoes) and holder request ids (conflicts) from the lock
    table.
- Error semantics:
  - timeout raises `RuntimeError` with blocking evidence (same exception
    class as today's immediate denial; message gains holder detail).

## State and Lifecycle Deltas
- Owned state changes:
  - embargo manager: records gain `mode`; adds waiter bookkeeping and one
    `Condition` on the manager lock
  - mediator: `_pending_root_starts` and FIFO wait removed; thread-local
    stack and session map unchanged
  - registry: adds `_fact_records` keyed by (fact_family, region)
- Lifecycle/cleanup changes:
  - embargo cleanup notifies waiters before dropping state so blocked
    threads exit with timeout semantics instead of hanging
  - commit path order: session commit pipeline -> strategy commit delta ->
    orchestrator commit (release embargoes, remove in-flight, pop staged)

## Failure Mode Deltas
- New failure mode: scope-wait timeout (bounded, evidenced).
- Removed failure mode: immediate spurious denial for waitable overlap.
- Changed failure mode: admission denial evidence now names holders, not
  just scope keys.

## Dependency and Ordering Constraints
1. Lock table lands before orchestrator switch (default-X preserves
   semantics).
2. Orchestrator switch lands before mediator wait-retry (the retry loop
   needs acquisition-shaped rejections).
3. Commit-delta dispatch lands with strategy implementations in the same
   slice (abstract method forces all four families).
4. Fact records land last; they are additive.

## Validation Expectations
- Test/validation item 1: compatibility matrix truth table (9 cases).
- Test/validation item 2: disjoint parallel admission unchanged.
- Test/validation item 3: S/S same-scope concurrent admission.
- Test/validation item 4: X collision blocks, wakes on release, admits.
- Test/validation item 5: timeout surfaces blocking evidence.
- Test/validation item 6: same-owner re-entrant claims and S->X upgrade as
  sole holder.
- Test/validation item 7: commit deltas apply link/cluster/ownership facts
  and stamp fact records; abort applies nothing.
- Evidence target: new tests in
  `tests/unit/melder/aether/dev_ops/change_control_manager/`.

## Unknowns and Open Decisions
- UNKNOWN: binding-key claim admission relevance (kept coarse; see
  architecture patch).
- UNKNOWN: contention fairness requirements beyond timeout bound.

## Context / Handoff Summary
- One gate, moded claims, scope-local waiting, transaction-maintained
  registry truth with last-reported baselines. Config field removal and the
  information-strategy catalog are follow-up slices.
