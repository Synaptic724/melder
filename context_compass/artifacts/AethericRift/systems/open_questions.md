# Open Questions and Conflicts (System)

## Status
- Status: draft
- Tags: UNKNOWN

## Purpose
Centralize the major contradictions and missing decisions across the idea
tickets so we can resolve them explicitly and then update the active
discussion tasks.

## Top Conflicts (UNKNOWN)

### 1) "Remote" Means Two Different Things
- Remote as session view (RiftToken -> RemoteSession).
- Remote as stateful tool object (FSM/HSM) with RemoteACL.
- Remote API surface is also described as RiftDomain operations.

### 2) Queueing / Parallelism Location
- Some drafts want toolchain queueing/parallel semantics.
- Other drafts explicitly forbid queues/workers inside Rift/Domain.

### 3) ACL Layer Set
Observed variants:
- Spell + Conduit + Remote
- Spell + Conduit + Domain + Profile
- Object + Domain + Agent Profile
- RemoteTool ACL (transition-level)
We need a minimal v1 layer set that does not paint us into a corner.

### 4) Surface Identity
- Surfaces are first-class, but:
  - are they always just conduits?
  - are surrogate conduits required or optional?
  - how do we name surfaces consistently across multiple conduits?

### 5) Scope Selection and Object Targeting
- How invoke_spell selects/creates a scope.
- How get/set attr targets:
  - spell-level vs instance-level
  - handle vs (spell_key, scope_id)

### 6) Token Model
- RiftAuthKey vs RiftSessionToken vs RiftToken:
  - which ones exist in v1?
  - how do they map to profiles/domains?
  - what is the revocation/rotation story?

### 7) Audit Ledger Coupling
- Do we log only state mutations, or also log allow/deny enforcement decisions?
- What is the canonical actor identity for AI/agents?

## Mapping to Active Discussion Tasks
This is the "where we record decisions" plan:
- Core objects: `context_compass/tasks/2026-01-23_rift_core_objects_task.md`
- Exposure model: `context_compass/tasks/2026-01-23_rift_exposure_model_task.md`
- ACL stack: `context_compass/tasks/2026-01-23_rift_acl_stack_task.md`
- Runtime semantics: `context_compass/tasks/2026-01-23_rift_runtime_semantics_task.md`
- Interaction modes: `context_compass/tasks/2026-01-23_rift_interaction_modes_task.md`
- AethericSpace semantics: `context_compass/tasks/2026-01-23_aethericspace_semantics_task.md`
- Identity/auth: `context_compass/tasks/2026-01-23_rift_identity_auth_task.md`
- Audit ledger: `context_compass/tasks/2026-01-23_rift_audit_ledger_task.md`
- Governance modes: `context_compass/tasks/2026-01-23_rift_governance_modes_task.md`
- Synthesis: `context_compass/tasks/2026-01-23_open_questions_synthesis_task.md`

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericriftticket85.md`
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/aethericriftticket111.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`
- `context_compass/artifacts/transaction_audit_ledger.md`

