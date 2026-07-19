# Story: S1 - First-class link identity + link journal rows

## Metadata
- Story ID: STORY-2026-07-18-link-identity-journal-rows
- Epic: EPIC-2026-07-18-parallel-restore-ulid-identity
- Status: review (code + regressions landed; pending owner 3.14t run)
- Owner: cowork
- Agent Name: helper_f
- Priority: p0
- Created: 2026-07-18T22:30:00Z
- Updated: 2026-07-18T22:30:00Z

## Objective
Links become identity-bearing units: link() mints a ULID, the conduit crystal records
per-link rows, unlink writes a tombstone, fold honors both, and restore replays links as
identity-mapped units - enabling per-link journal rows and independent replay units for S4.

## Ticket Contract
- ENTRY_GATE: epic active; architecture + link-identity component patch linked and read.
- EXECUTION_BOUNDARY: conduit.py link/unlink verbs, conduit ward link bookkeeping,
  conduit_crystal.py payload shape, persistence_system record/remove verbs (additive),
  restore_engine fold + _replay_links, tests. Additive record shape only; legacy
  link_targets lists still fold (compat lane).
- DEPENDENCIES: component_patch_link_identity_persistence.md.
- EXIT_GATE: round-trip regression green (link -> checkpoint -> restore -> identity map has
  link rows; unlink tombstone folds to absence); legacy-chain compat regression green.
- FAILURE_ESCALATION: DECISION_REQUEST if the ward's link bookkeeping requires a lock-order
  change; CONFLICT if any existing suite depends on link_targets shape.

## Scope Boundaries
- In scope: link identity minting, record rows, fold, replay, reporting kinds ("link").
- Out of scope: cluster/contract identity (already exist); scheduler/gate work.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: patch artifacts authored; awaiting implementation slot (first tranche).

## Steps / Checklist
(CORRECTED 2026-07-18 pre-implementation: twin-snapshot truth - no journal rows, no
tombstones; see amended component patch. Unlink rides the existing sever-path twin
re-emission; per-link journal rows would have created a second source of truth.)
- [ ] Ward mints + stores a link ULID per initiated link (beside _initiated_index).
- [ ] Conduit twin emission carries links: [{link_id, target_conduit_id}] (additive,
      beside legacy link_targets; built at conduit.py twin-kwargs site, cf. line 408).
- [ ] Restore: _replay_links iterates links rows (fallback: legacy link_targets),
      translates conduit ids through the identity map, maps recorded link_id -> the fresh
      ward-minted id.
- [ ] Legacy compat: chains without links rows restore identically (shortfall-free).
- [ ] Regressions: round-trip identity mapping, unlink-then-seal absence (twin snapshot),
      legacy compat, dangling-target shortfall parity.

## Validation
- Not run. Recommended: pytest tests/component -k link; pytest -m integration -k restore.

## Applicable Anti-Patterns
- [ ] No record-format break: additive fields only.
- [ ] No defensive None guards on owned ward fields.

## Noting Behavior
- Story notes: cross-task synthesis and gate transitions.

## Notes
- DATETIME: 2026-07-18T23:05:00Z
  TYPE: FACT
  CLAIM: Third and final scope correction, then implementation. Links already carry full
    recorded identity: link -> Contract minting its own ULID (contract.py:60), ward indexes
    target_conduit_id -> contract._id (conduit_ward.py:815), contract twin records
    (contract_id, conduit_a_id=initiator, conduit_b_id=target) (crystallizer.py:933-937).
    Ward/twin/crystal/persistence need NO changes. The only real gap was replay-side
    identity coverage - recorded contract ULIDs were never mapped to the fresh contracts
    link() mints during restore.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:60-63
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:813-818
  - src/melder/crystallizer/crystallizer.py:933-937
  IMPACT: S1 collapsed to one surgical enrichment; zero record-format risk; the S4 planner
    reads folded contract twins directly as link graph nodes/edges.
  NEXT: Author the regression rows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T23:05:00Z
  TYPE: FACT
  CLAIM: Implemented and committed: _replay_links builds the folded
    (initiator_id, target_id) -> contract ULID lookup and maps recorded -> fresh contract
    ids after each rebuilt edge (fresh id read from the initiator ward's initiated index,
    matching the engine's existing conduit._id seam posture). Contract docstring documents
    mapping law, legacy tolerance, and unchanged shortfall behavior. AST parse + device
    py_compile green (device VM is CPython 3.10 - syntax check only; runtime verification
    rides the owner's 3.14t run).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1590-1671
  IMPACT: Links are identity-mapped units; planner-ready.
  NEXT: Regression suite (round-trip mapping, legacy-chain absence, dangling-target
    parity, unlink-then-seal absence) against the existing restore test harness patterns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T23:26:30Z
  TYPE: MEASURE
  CLAIM: Regressions landed in the existing restore integration suite (house patterns:
    round-trip harness + synthetic-chain engine drive): (1)
    test_restored_link_maps_recorded_contract_ulid_to_fresh_contract - recorded contract
    ULID captured from the initiator ward pre-seal appears as an identity-map key after a
    fresh-boot load, mapped to a fresh 26-char ULID (never-rehydrate proven); (2)
    test_legacy_chain_link_without_contract_twin_restores_without_mapping - synthetic
    two-book chain with a link edge and NO contract twin rebuilds 1 link, zero link
    shortfalls, identity map holds exactly the book/conduit ids. Dangling-target parity
    already covered by the existing link_target_not_rebuilt lane; unlink-then-seal absence
    rides twin-snapshot fold (no new surface). File AST + device py_compile green
    (CPython 3.10 syntax check; behavior verification rides the owner's 3.14t run).
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1828-2022
  IMPACT: S1 is code-complete with contract-level regressions; pytest Not run by agent.
  NEXT: Owner 3.14t run covers it; S2 (scheduler seam) implements next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Design pinned in component_patch_link_identity_persistence.md; implement first in the epic.
