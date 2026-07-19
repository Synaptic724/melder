# Architecture Patch: Live Probe Lock Removal And Existing Only Meld

## Objective
Strip extra read-side locks from the live probe path and add an `existing_only`
option to the meld seam so callers can reuse-or-fail without triggering
creation.

## Non-Goals
- no broad lock sweep
- no static viewer redesign
- no capability handle design

## Changed Components
- `Meld`
- `Conduit`

## Invariants
- live probe remains read-only
- normal `meld(...)` behavior is unchanged
- `existing_only=True` never creates

## Interface Deltas
- `meld(...)` gains `existing_only`
- `Conduit.meld(...)` passes the option through

## Migration Order
1. remove read-side live probe locks
2. add `existing_only` to meld and conduit facades
3. update focused tests

## Rollback
Rollback is code-level only for this patch. Do not keep `existing_only`
partially wired on only one of the two meld seams.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-12_remove_read_locks_from_live_probe_and_add_existing_only_meld_task.md`
