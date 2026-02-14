# Execution Model and Concurrency (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose
Define where execution, queueing, and concurrency live for Rift calls, without
accidentally building a hidden scheduler inside the rift.

## Baseline Execution Model (PROPOSED)
- Rift and Domain are facades:
  - no worker pools
  - no internal background threads
  - no consumer/producer queues
- All calls are synchronous and run on the caller's thread.
- Conduits/Scopes own object lifetime and (where applicable) concurrency rules
  for the created objects.

## Context Binding (PROPOSED)
Execution must be associated with:
- surface_id (which execution reality)
- scope_id (which lifetime envelope)
- principal/profile identity (who is acting)
- optional session_id (for ObjectRefs and AethericSpace)

Some tickets propose an internal CallSpec representation:
- session_id, surface_id, scope_id, target_id, action, args, acl_profile

## Queueing and Parallelism (Conflict)
Two competing themes in the idea tickets:
- PROPOSED (strict facade): Rift never queues; wrappers/CommandOps do.
- PROPOSED (toolchain UX): Rift supports queueing/batching/parallel semantics at
  least conceptually for multi-step toolchains.

## Proposed Resolution Direction (PROPOSED)
- Keep Rift core synchronous and queue-free.
- Allow higher layers (CommandOps, workstation UX, wrappers) to:
  - batch CallSpecs
  - run sequences
  - run in parallel when safe
  while still executing each CallSpec synchronously through the domain.

## Open Questions (UNKNOWN)
- If workstation mode has a command queue, where does it live (domain, session,
  CommandOps, wrapper)?
- What are the guarantees for ordering, idempotence, and cancellation?
- How do we represent "parallel but scoped" without inventing new lifetime rules?

## Sources
- `context_compass/artifacts/aethericrift_ticket87.md` (explicit synchronous facade stance)
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md` (queueing/parallel toolchain language)
- `context_compass/artifacts/aethericriftticket111.md` (CallSpec + workstation semantics)

