# [Ticket] Codegen Interaction Model - Safe Lane and Mutation Lane

**Type:** Architecture / Philosophy Ticket

**Status:** Active Planning Context

**Labels:** `aetheric-rift`, `commandops`, `codegen`, `safe-lane`, `mutation-lane`, `acl`, `objectref`, `workstation`, `agent-runtime`

---

## 1. Intent

Define a practical interaction model for AI agents where generated code is the primary interface style, without requiring a full text-REPL runtime in Melder/Rift.

This ticket locks the conceptual split:

- Safe execution lane for codegen over pre-defined objects.
- Mutation lane for structural creation/modification work.
- Clear boundary between Melder, Rift, CommandOps, and wrappers.

---

## 2. Core Decision Summary

1. We do not need a REPL-first architecture to deliver agentic workflows.
2. Generated code blocks can be inspected and executed safely when constrained.
3. Safe lane executes only against already-exposed and authorized objects/capabilities.
4. Mutation lane handles new object definitions or structural modifications through controlled mutation workflows.
5. Workstation semantics still exist (session/scope/object continuity), but text parsing is optional.

---

## 3. Responsibility Split

### 3.1 Melder

- Runtime substrate and lifecycle truth.
- Spells, conduits, scopes, existence, cleanup, change control, spell state, mutation mechanics.

### 3.2 AethericRift

- Governed capability surface.
- Session/scope/objectref routing.
- ACL intersection and authorization.
- Canonical execution of operation requests.

### 3.3 CommandOps

- Agent runtime orchestration.
- Long-running missions, scheduling, retries, queues, state-machine control.
- Optional UX layers (REPL shell, DSL, planners) that compile into Rift operations.

### 3.4 Wrappers

- Transport and authentication boundaries (HTTP/MCP/etc.).

---

## 4. Interaction Lanes

### 4.1 Safe Lane (Default)

Safe lane is for generated code that only uses existing, approved workspace objects and allowed operations.

Key properties:

- No structural runtime mutation.
- No arbitrary object definition in the block.
- Strict ACL/lifecycle checks at execution time.
- Deterministic routing through the same operation model as static/workstation calls.

### 4.2 Mutation Lane (Explicit Opt-In)

Mutation lane is for generated code that introduces:

- New object definitions.
- Modifications to existing object behavior/structure.
- Graph-level runtime changes.

Key properties:

- Explicit policy/ACL permission required.
- Validation and change-control gates required.
- Version lineage operations supported (notch-forward, rollback, branch, collapse).
- Lab-oriented domain posture recommended.

---

## 5. Safe Lane Pipeline (Conceptual)

1. Code block is submitted.
2. Parse to AST.
3. Static inspection pass:
- symbol resolution against known bindings,
- operation whitelist/blacklist enforcement,
- reject forbidden dynamic features in strict mode.
4. Classification:
- if no structural creation/modification patterns are detected, continue safe lane.
- otherwise route to mutation lane.
5. Execute using governed runtime operations.
6. Return values; box runtime objects as handles/bindings when needed.
7. Emit audit and incident-compatible operation traces.

---

## 6. ObjectRef Clarification

ObjectRef is not the real object owner. It is a governed handle/capability pointer to a runtime-owned object.

Ownership model:

- Conduit/scope runtime owns strong object references and cleanup semantics.
- ObjectRef maps caller operations to runtime objects under session/scope policy.

Why ObjectRef exists:

- Cross-call identity in stateful workflows.
- Session/scope expiry and revocation behavior.
- Consistent ACL/lifecycle checks before each operation.
- Boundary-safe addressing for wrappers/adapters.

Possible richer model:

- ObjectRef can include capability slice metadata, expiry, and lifecycle status.
- Canonical policy still comes from ACL stack, not from ad-hoc ref-local rules alone.

---

## 7. Workstation Semantics Without REPL Dependence

Workstation is a runtime control surface, not a text loop.

It can be driven by:

- Programmatic APIs.
- Codegen blocks.
- DSL frontends.
- Optional REPL shell in CommandOps.

Core workstation behaviors remain:

- Session continuity.
- Scope management.
- Object binding/reuse.
- Multi-step runtime workflows.

---

## 8. Example Workflows

### 8.1 Safe Lane Incident Triage

- Use pre-bound tools (`metrics`, `state_reader`, `incident_manager`).
- Codegen block inspects state, invokes diagnostics, creates incident artifacts.
- No structural mutation, executes directly in safe lane.

### 8.2 Safe Lane Operational Automation

- Use pre-bound service objects.
- Invoke methods with parameters and bind outputs for later steps.
- Works as controlled stateful automation without graph mutation.

### 8.3 Mutation Lane Experiment

- Codegen proposes candidate behavior/object definition.
- Classified as mutation lane.
- Run validation, version operations, and rollback/progression under policy gates.

---

## 9. Why This Is Useful

This model gives:

- Smooth AI UX through codegen.
- Strong governance and runtime control.
- No requirement to build a complex REPL kernel first.
- Clear path to long-running agent orchestration via CommandOps.

It supports a general "abstract MCP-like" control surface concept, while staying runtime-native and policy-first.

---

## 10. Open Questions

1. Strict-mode language boundary for safe lane:
- exactly which AST constructs are permitted or denied?
2. Symbol model:
- bind by explicit names only, or support pattern-based binding catalogs?
3. Ref lifecycle defaults:
- session-bound only vs TTL and explicit release policies.
4. Mutation classifier rules:
- exact threshold for lane promotion from safe to mutation.
5. Audit defaults:
- log all allow/deny checks or only state-changing operations by default?

---

## 11. Acceptance Criteria (Conceptual)

This ticket is accepted when the team agrees that:

- Codegen-first interaction is sufficient as primary UX for agent operations.
- Safe lane and mutation lane are separate, enforceable policy paths.
- Safe lane is constrained to existing approved objects/capabilities.
- Mutation lane is explicit, gated, and lineage-aware.
- Workstation semantics are preserved without requiring REPL-first implementation.
- ObjectRef is treated as governed handle identity, not as alternate lifetime owner.

