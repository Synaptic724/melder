# Component patch: ConduitWard - contract invalidation, WITHDRAWN (slotted_lifetime_ownership_2026_10_14)

Status: WITHDRAWN - no change, by the owner's ruling (2026-10-14T23:00Z): the objects a contract change lets go of
stay pending for agents to manage (src_architecture, "Runtime Model: Structure Is the Contract"). The text below
records the proposal only; it was never applied.

Component: ConduitWard and Contracts (`_invalidate_contract_consumers`). Defect D3.

## Before / after
- A contract change (link sever, contract add/remove, contract clear) marks SpellContract consumers dirty and
  extracted each impacted consumer's entries from the conduit's store - every existence - dropping them undisposed.
  After: `Creations.retire_singleton_creation(spell_id)` retires a slotted consumer (with the children it owns) and
  runs its disposal methods; a `many` consumer's objects stay in the store (nothing is cached for them; they are
  disposed when the scope ends). Disposal failures are collected and logged through the ward logger with the
  ExceptionGroup attached: every call site runs inside a contract mutation that must complete and already swallows
  this helper's errors.

## Interface deltas
None (internal helper body and docstring).

## State / failure deltas
- A borrower's slotted consumer retired by a lender's sever or teardown is disposed once (b7, c1).
- Disposal can now run inside sever/link flows, under the ward locks those flows already hold - the same place a
  lesser's teardown already disposes during a root ward's cleanup.

## Dependency / ordering
Requires `Creations.retire_singleton_creation`. The store lock stays the only lock the helper takes; no build lock
is added under ward or contract locks.

## Validation expectations
Component: a lender's teardown and a sever dispose the borrower's per-conduit consumer once; a `many` consumer's
objects stay registered until the borrower's scope ends; a failing disposal is logged and the sever completes.
