# Interaction Modes (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Capture the two-mode model proposed for Rift:
- Workstation/REPL mode for interactive, stateful workflows.
- Static exposure mode for narrow, call-only integrations.

## Shared Concepts (PROPOSED)
- Conduit reality always applies: surface + scope context matters.
- Sessions exist to bound ownership and cleanup.
- ObjectRefs exist to represent stateful objects across calls/boundaries.
- Both modes compile to a single internal CallSpec-like representation.

## Mode A: Workstation / REPL (PROPOSED)
Definition:
- Stateful bench where caller chains multi-step workflows over time.

Key semantics:
- Session + surface + one or more scopes.
- AethericSpace bench that stores ObjectRefs and named bindings.
- Optional command queueing/batching at the UX layer.

Policies (PROPOSED):
- Session TTL / idle timeout.
- Object count / memory policy (if needed).
- Explicit teardown discipline.

## Mode B: Static Exposure (PROPOSED)
Definition:
- Curated call-only surface with explicit registration of allowed targets/actions.

Key semantics:
- Still uses sessions/scopes for coherence and cleanup.
- May return ObjectRefs for stateful results, but no bench UX.
- Feels like: call(target_ref, method_id, args) -> result.

## Open Questions (UNKNOWN)
- Does static exposure require explicit sessions, or can wrappers create an
  ephemeral session per call?
- What is the minimum discovery surface in static mode (none vs list registered
  methods vs optional introspection under ACL)?
- How do multi-scope workstations behave (single active scope vs concurrent)?

## Sources
- `context_compass/artifacts/aethericriftticket111.md`
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`

