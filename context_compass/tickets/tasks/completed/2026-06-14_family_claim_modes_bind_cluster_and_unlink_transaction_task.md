# Task: Family claim modes (bind + cluster) and the unlink/sever transaction

## Metadata
- Task ID: TASK-2026-06-14-family-claim-modes-and-unlink-transaction
- Story: STORY-2026-06-12-implement-scope-acquisition-control-plane
- Status: completed
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p1
- Created: 2026-06-14T16:40:19Z
- Updated: 2026-06-14T16:40:19Z

## Objective
Complete the scope-acquisition story's "family claim-mode refinement +
relational commit deltas" follow-up for the lanes the link task did not cover
(bind, cluster_link, transfer), AND land the separate sever/unlink transaction
family the user directed. Companion to the link task
(`tickets/tasks/completed/2026-06-13_link_transaction_claim_modes_and_commit_deltas_task.md`).

## Outcome (all lanes landed, user-validated in the 3.14t venv)
- bind: claim modes — IX on the owning spellbook (pre-conjure) and IX on the
  owning spellbook + IX on each affected cluster (post-conjure); conduit/ward
  EXCLUSIVE (the conjure owns them).
- cluster_link: claim modes — IX on each participant's owning spellbook; cluster,
  conduits, and wards stay EXCLUSIVE. No commit delta (membership mirror is eager).
- transfer_ownership: no change needed — it already claims EXCLUSIVE on every
  scope (no scope_claims override), which is the strongest mode.
- unlink/sever (new transaction family, by user direction):
  - Step A: `ChangeTransactionType.UNLINK` + `UnlinkTransactionStrategy`
    (X conduits/wards, IX spellbooks, mirroring link) + builder registration +
    builder-resolve and claim-mode unit tests.
  - Step B: `Conduit.sever_link` self-admits the unlink transaction (admit ->
    ward sever -> commit). Added `unlink` to `begin_transaction` routing +
    `dynamic_only`, to the mediator `start_transaction` allow-list, and to the
    conduit identity's declared `available_transactions`.
  - Step C: `ConduitWard._remove_contract` re-resolves the borrowing side's
    `SpellContract` consumers on a whole-link sever (mirrors per-spell
    `_remove_spell_from_contract`), so the next meld revalidates; existing
    creations rebuild lazily, nothing torn down eagerly.

## Key Decision — relational commit deltas are REDUNDANT
The story EXIT_GATE said "all four strategies apply commit deltas." That is
intentionally revised: no strategy needs a relational commit delta, because the
mirrors are maintained EAGERLY at the mutation site and are now race-safe under
the transaction's held claims:
- link mirror: ward `_add_spell_to_contract` -> identity `register_provider_conduit`
  -> registry `register_conduit_link`; sever via `_remove_contract` ->
  `unregister_provider_conduit`.
- cluster-membership mirror: `ConduitCluster.add_member`/`remove_member` ->
  identity `register/unregister_cluster_member` -> registry
  `register/unregister_cluster_membership`.
Base `apply_commit_delta` still stamps spellbook+conduit fact baselines at commit,
so freshness facts are written without per-family delta overrides.

## Claim-mode compatibility (authoritative, embargo_manager._modes_compatible)
- EXCLUSIVE (x): incompatible with everything.
- SHARED (s): compatible only with SHARED.
- INTENT (ix): compatible only with INTENT.
So spellbook-IX lets links/binds/cluster-ops coexist on a spellbook while still
blocking a whole-spellbook EXCLUSIVE claim (a transfer), and vice versa.

## Files / Paths Impacted
- strategies/bind_transaction_strategy.py (claim modes)
- strategies/cluster_link_transaction_strategy.py (claim modes)
- strategies/unlink_transaction_strategy.py (NEW)
- strategies/transaction_strategy_builder.py (register unlink)
- change_control_manager/transaction_request/transaction_request.py (UNLINK enum)
- change_control_manager/transaction_manager/transaction_mediator.py (allow-list)
- src/melder/aether/conduit/conduit.py (begin_transaction routing + dynamic_only
  + available_transactions + sever_link self-admit)
- src/melder/aether/conduit/conduit_ward/conduit_ward.py (_remove_contract
  consumer re-resolution)
- tests/unit/.../test_transaction_strategy_builder_and_strategies.py (bind,
  cluster, unlink claim-mode tests + builder resolve)

## Stale-test reconciliations (pending/wait model, pre-existing drift)
Two integration tests asserted the OLD immediate "Change-control admission
denied" but the scope-acquisition pending/wait model now waits-then-times-out on
a scope collision. Updated to shrink the frame mediator wait and assert
"Timed out waiting for blocked scopes" with the blocking scope key named:
- tests/integration/melder/conduit/test_conduit_integration_public_api.py
  (test_conduit_begin_transaction_sets_conduit_scope_key)
- tests/integration/melder/spellbook/test_spellbook_integration_core.py
  (test_spellbook_integration_begin_transaction_conflict_rejects_overlapping_scope)

## Validation (user-run, 3.14t venv)
- change-control unit ring: 234 passed.
- conduit unit + conduit integration: 1244 passed.
- spellbook integration + spellbook unit: green after the stale-test fix
  (the only remaining red was an UNRELATED pre-existing concurrent-conjure race,
  filed as EPIC-2026-06-14-aether-frame-spell-registry-concurrent-access-race and
  handed to compiler_strategy_0).

## Notes
- DATETIME: 2026-06-14T16:40:19Z
  TYPE: DECISION
  CLAIM: Commit deltas are redundant family-wide (eager mirrors, now race-safe
    under held claims). Unlink/sever added as a real mediated transaction that
    self-admits inside sever_link. Claim modes landed for link/bind/cluster;
    transfer already EXCLUSIVE. Validated green in the user's 3.14t venv.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py (sever_link self-admit; begin_transaction unlink branch)
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py (_remove_contract re-resolution; eager mirror unregister)
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/ (bind/cluster/unlink strategies)
  IMPACT: The story's family-claim-mode follow-up + the sever/unlink follow-up are
    both complete and validated.
  NEXT: optional dedicated Step C test (sever -> consumer re-resolve); eager->lazy
    migration; canonical src_components/src_architecture merge for unlink.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Companion to the link task. Bind/cluster claim modes, the new unlink/sever
transaction (A/B/C), and the family-wide decision that relational commit deltas
are unnecessary (eager mirrors) are all landed and green in the 3.14t venv. Two
stale pending-model tests reconciled. Remaining optional work: the dedicated
sever re-resolve test, the eager->lazy migration, and the canonical doc merge for
the unlink transaction (codex doc-drift lane owns system_docs).
