# Story: Unit tests for the built transactions (strategies + admission internals)

## Metadata
- Story ID: STORY-2026-06-20-cluster-tx-unit-tests
- Epic: EPIC-2026-06-20-cluster-transaction-test-suite
- Status: review
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p2
- Created: 2026-06-20T11:40:00Z
- Updated: 2026-06-20T11:52:00Z

## User Narrative
As the mediator-transaction owner, I want contract-level unit tests for every strategy I built, so
that a regression in scope planning / claim modes / admission internals fails fast without needing
the full runtime.

## Value / MRP Alignment
Unit tests are the cheapest, fastest guard on the transaction strategies' contracts (scope footprint,
claim modes, capabilities, error paths). They prove the DevOps-isolation half of each transaction in
isolation, which is exactly where regressions are most likely and hardest to spot at runtime.

## Ticket Contract
- ENTRY_GATE: epic routed + in_progress; unit fixture pattern confirmed
  (`_make_registry_and_identity`, inline DevopsIdentity construction, assert on returned plan dict).
- EXECUTION_BOUNDARY: ADD unit test files under
  `tests/unit/melder/aether/dev_ops/change_control_manager/`. No source edits.
- DEPENDENCIES: the wired strategies; existing
  `test_transaction_strategy_builder_and_strategies.py` as the fixture model.
- EXIT_GATE: ~40 new unit tests authored, self-reviewed, py_compile-clean; user runs the 3.14t unit
  tree and reports green.
- FAILURE_ESCALATION: CONFLICT if a strategy's real plan contradicts the wired contract; BLOCKER if
  the fixture cannot construct the registry/identity slice.

## Requirements (Functional)
- cluster_join / cluster_leave strategies (NEW, zero existing): build_start_plan scope_keys (conduit +
  ward + spellbook), scope_claims (spellbook INTENT; conduits/wards EXCLUSIVE/absent), capabilities,
  conduit_ids passthrough, metadata mode marker, _involved_conduit_ids raises on empty, on_start/on_end
  no-op, builder resolves both, enum values.
- Deepen thin strategies: unlink, notch, add_to_index, remove_from_index, bind, link, cluster_link,
  elect, unelect (error paths + scope/claim assertions not already covered).

## Requirements (Non-Functional)
- Contract-level assertions only (no Rank E/F existence checks).
- No `from __future__ import annotations` (unit-dir convention); Optional/Union typing; rich docstrings.
- Each test file well under the ~900 LOC single-write ceiling (split as needed).

## Scope Boundaries
- In scope: unit tests for the 11 transactions' strategies + builder/enum cross-cutting.
- Out of scope: component/integration tests (sibling stories); transfer_ownership; source edits.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: epic approved + broadened; unit fixture confirmed; authoring begun.

## Tasks (Implementation Checklist)
- [x] test_cluster_membership_transaction_strategies.py: cluster_join + cluster_leave + builder/enum
      cross-cutting (20 tests).
- [x] test_link_family_transaction_strategies_expansion.py: bind (4) + link (5) + unlink (3) +
      parametrized builder/enum across all 11 (22 cases).
- [x] test_index_and_leader_transaction_strategies_expansion.py: notch (3) + add_to_index (2) +
      remove_from_index (2) + elect (3) + unelect (4).
- [x] Enforce Ticket Microcycle across linked tasks.

## Acceptance Criteria
- ~40 new unit tests; cluster_join/cluster_leave fully covered; every test makes a contract assertion.
- User-run 3.14t unit tree green for the new files.

## Validation / Test Plan
- Not run (agent: Py3.10 sandbox cannot import the 3.14t chain).
- Recommended: `pytest tests/unit/melder/aether/dev_ops/change_control_manager -q` on .venv_new.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No Rank E/F filler tests.

## Notes
- DATETIME: 2026-06-20T11:40:00Z
  TYPE: PLAN
  CLAIM: Authoring the cluster_membership unit file first (cluster_join/cluster_leave have zero
    existing coverage). Mirrors the cluster_link strategy test pattern (inline DevopsIdentity build +
    register_spellbook_conduit_ownership + assert on plan scope_keys/scope_claims/capabilities).
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_strategy_builder_and_strategies.py:669-753
  IMPACT: Highest-value gap closed first.
  NEXT: Write test_cluster_membership_transaction_strategies.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T11:52:00Z
  TYPE: FACT
  CLAIM: 68 unit test instances landed across 3 new files (46 functions + 22 parametrized cases),
    all py_compile-clean. Covers cluster_join/cluster_leave fully (was zero); deepens
    bind/link/unlink claim modes; deepens notch/add/remove EXCLUSIVE binding seals; deepens
    elect (no-drain) + unelect (drain on_start / reopen on_end, fail-closed) via a RecordingGateOps
    double; parametrized builder + enum resolution across all 11 built transactions. Patterns cloned
    1:1 from the existing strategy test file so fixtures match.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_cluster_membership_transaction_strategies.py:1-470
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_link_family_transaction_strategies_expansion.py:1-520
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_index_and_leader_transaction_strategies_expansion.py:1-470
  IMPACT: Unit story over-delivered (68 vs 40 target). Pytest Not run (Py3.10 sandbox).
  NEXT: User runs the 3.14t unit tree; then proceed to the component story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Unit story of the cluster/mediator transaction test epic. ~40 new unit tests across two files: a
cluster_join/cluster_leave + cross-cutting file (the zero-coverage gap), and a coverage-expansion file
deepening the other strategies. Agent cannot run pytest; user runs the 3.14t unit tree.
