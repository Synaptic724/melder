# Architecture Patch: remediation lineage mediation

- Patch ID: remediation_lineage_mediation_2026_07_12
- Ticket: EPIC-2026-06-20-implement-new-mediator-strategies
- Status: active

## Objective
Close the CONFIRMED lineage race (probe-proven, owner run #3: a
remediation window straddling a notch writes a stale terminal verdict
onto the shared lineage record, permanently poisoning the notched-in
member). Owner ruling: MEDIATE BOTH THREADS - remediation is a writer,
writers ride admission.

## Interface Deltas
1. ChangeTransactionType.REMEDIATION = "remediation" (enum, additive).
2. ChangeControlTransactionManager.make_scope_key_lineage(index_id) ->
   "lineage:<index_id>" (mirrors the binding scope helper).
3. NEW strategies/remediation_transaction_strategy.py -
   RemediationTransactionStrategy: claims EXACTLY ONE scope - the
   lineage (spell_index_id from metadata) EXCLUSIVE. No staged binding
   keys (remediation runs its own phases; the commit-side structural
   validator stays out). Registered in TransactionStrategyBuilder.
4. NotchTransactionStrategy (+ add_to_index/remove_from_index/
   transfer follow-ups): the seal gains the lineage scope for the
   targeted index (metadata already carries spell_index_id on notch).
   Mutual exclusion both directions: no window spans a notch, no notch
   lands mid-window.
5. Meld._ensure_lineage_resolvable: the gated rerun branch admits a
   REMEDIATION transaction (spellbook identity; admission BEFORE
   spell._lock - the one-way order the families already obey) and
   commits/aborts around the rerun + validity write. Warm melds and
   plain reads NEVER enter the plane (readers-never-enter survives for
   reads; only the rerun-and-write branch pays).

## Non-goals
No envelope payloads (mediator stays scope-only); CONJURE stays out;
no epoch machinery (overruled).

## Validation expectations
The strict-xfail race probe converts to a REGRESSION test (owner:
"fix the test as a regression we can monitor") - with mediation the
notch must PARK until the window closes (or the window must complete
first); post-settle meld of the notched-in member succeeds. Scope-claim
unit rows for the new strategy + amended notch. Owner runs 3.14t.

## Rollback
Additive enum/strategy/scope-key + one wrapped branch: unwrap the meld
branch, drop the lineage claims, unregister.
