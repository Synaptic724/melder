# Lane Contract

## Purpose
Define hard boundaries between safe lane and mutation lane.

## Safe Lane
- Existing capabilities only.
- No structural graph or lineage writes.
- Operations must resolve through current `CapabilityManifest`.
- Runtime call boundaries still re-check ACL and lifecycle.

## Mutation Lane
- Any structural operation routes here:
- create new runtime object definitions
- modify spell wiring or behavior shape
- replace providers in structural sockets
- write lineage nodes or promotion state

## Classification Rule
- Unknown or ambiguous intent defaults to deny, not auto-escalate.
- Explicit profile + domain + object permissions are required for mutation routing.

## Escalation Rule
- Safe lane may request escalation.
- Escalation is an explicit transition event with audit metadata.
- Transition must include lock intent and mutation scope declaration.

## Non-Goals
- Lane contract does not define transport or UI.
- Lane contract does not define agent orchestration policy.

