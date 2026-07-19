# component_patch_dev_ops_transactions

## Metadata
- Patch ID: conjure_transaction_2026_06_29
- Component: dev_ops change-control transaction plane (+ spellbook conjure boundary)
- Status: in_progress
- Owner: cowork
- Agent Name: mediator_builder_0
- Created: 2026-06-29T09:01:57Z
- Updated: 2026-06-29T09:01:57Z

## Component Purpose and Boundary
- Current boundary:
  - conjure (`Spellbook.conjure` -> `SpellbookCreationSystem.conjure`) runs under
    the Spellbook `_lock` + the `_conjured` single-conjure invariant ONLY; it
    opens no mediator transaction and holds no embargo claim
  - the genesis is invisible to the admission plane; serialization against
    bind/link/transfer relies on the lock, not the embargo lock table
- Target boundary:
  - conjure is admitted as a CONJURE transaction on the spellbook identity,
    claiming `scope:spellbook:<id>` EXCLUSIVE for the whole pipeline
  - the creation pipeline runs inside the held claim (envelope-only); the `_lock`
    + `_conjured` invariant remain as belt-and-suspenders

## Before/After Behavior Summary
- Before: two conjures of different spellbooks run fully in parallel and can
  contend on shared frame state (see `EPIC-2026-06-14-aether-frame-spell-registry-concurrent-access-race`);
  a bind/transfer can interleave with a conjure on the same spellbook except
  where the Spellbook lock happens to block it; the mediator has no record of an
  in-flight conjure.
- After: a conjure holds spellbook-X for its duration; bind/link/transfer/other
  spellbook-level transactions on that spellbook wait (X incompatible with all)
  and admit on release; different spellbooks still conjure in parallel;
  double-conjure -> one wins, the other blocks then raises the `_conjured` guard.

## Interface Deltas
- Inputs:
  - `ChangeTransactionType.CONJURE`
  - spellbook identity `available_transactions` gains `"conjure"`
  - `ConjureTransactionStrategy.build_start_plan` -> `{scope:spellbook:<id>: EXCLUSIVE}`,
    `initiator="spellbook:<id>"`, `conduit_ids=()`
- Outputs:
  - none new; envelope-only. The base `apply_commit_delta` still stamps the
    spellbook fact baseline at commit.
- Error semantics:
  - a blocked conjure waits up to the configured timeout then raises with
    blocking evidence (same exception path as other families); double-conjure
    raises the existing `RuntimeError` after winning the claim.

## State and Lifecycle Deltas
- `Spellbook.conjure` opens the transaction on the spellbook identity before
  `SpellbookCreationSystem.conjure()` and commits/aborts in a `finally`, all
  inside the existing `self._lock`.
- No new owned state in the embargo manager or mediator; reuses the moded lock
  table + scope-wait already landed by `devops_scope_acquisition_2026_06_12`.
- The conjure pipeline is verified transaction-free, so the conjure root never
  nests another root.

## Failure Mode Deltas
- New failure mode: conjure scope-wait timeout (bounded, evidenced) when another
  spellbook-level holder will not release.
- Changed failure mode: double-conjure becomes admission-serialized then guarded
  (clean) rather than lock-serialized only.

## Dependency and Ordering Constraints
1. Enum + strategy + builder registration land first (inert until conjure opens
   the transaction).
2. Identity `available_transactions` gains `"conjure"` before the spellbook wrap
   (the `supports_transaction` gate would otherwise reject it).
3. The `Spellbook.conjure` wrap lands last (general_0's hot file -- coordinate
   via mailbox before editing).

## Validation Expectations
- Strategy unit: claim-set equals `{scope:spellbook:<id>: X}`; builder resolves
  `"conjure"`; `on_start`/`on_end` no-ops.
- Integration: conjure blocks a concurrent bind on the same spellbook; two
  spellbooks conjure in parallel; double-conjure -> exactly one `RuntimeError`.
- Evidence target: tests under
  `tests/unit/melder/aether/dev_ops/change_control_manager/` + a spellbook
  conjure integration test. User-run 3.14t (agent: "Not run.").

## Unknowns and Open Decisions
- DECISION (user, chat): spellbook-local, not frame-wide; no conduit scope
  (conduit not created at admission).
- UNKNOWN: optional minted-conduit claim mid-pipeline for the future state
  effort -- deferred.

## Context / Handoff Summary
- Conjure becomes a spellbook-EXCLUSIVE mediated transaction, envelope-only, no
  conduit scope. The mediator-side pieces are in the dev_ops lane; the conjure
  wrap is in `spellbook.py` (general_0 active) -- coordinate before editing.
