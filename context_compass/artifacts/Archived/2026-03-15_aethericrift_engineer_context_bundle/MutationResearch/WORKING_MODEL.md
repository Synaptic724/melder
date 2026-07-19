# MutationResearch Working Model

## Status
- Decision state: DECIDED direction, PROPOSED API detail set.

## 1. Goal
Provide a practical model where:

- agents can operate safely through codegen by default,
- agents can escalate into mutation research when structural change is needed,
- every escalation is policy-gated, observable, and recoverable.

## 2. Shared Baseline

### 2.1 Safe Lane Baseline
- Uses existing approved capabilities only.
- Runs through `CapabilityManifest` and AST/symbol validation.
- Does not perform structural graph changes.
- Can coexist with AR static/automatic operation as the lower-risk governed
  interaction path over the current runtime reality.
- In AR terms this aligns well with a `simple` workspace configuration using
  predeclared targets.

### 2.2 Mutation Lane Baseline
- Handles add/remove/change/create structural operations.
- Requires explicit mutation permissions.
- Requires lock and control-plane gates.
- Produces lineage events and promotion decisions.
- Should be treated as a dynamic-mode path rather than a static/automatic-mode
  feature.
- In AR terms this aligns with a `dynamic` workspace configuration where the
  agent can use conduit-backed local construction before crossing into canonical
  mutation flow.

## 3. Operational Split

### 3.1 Melder Responsibilities
- Structural mutation mechanics.
- Conduit/scope lifecycle truth.
- SpellState and ChangeControl state transitions.
- Validation execution and lineage operations.

### 3.2 AethericRift Responsibilities
- Capability and profile governance.
- Lane classification and operation routing.
- Guardrailed execution entrypoint.
- Audit and deny/error shape consistency.

### 3.3 CommandOps Responsibilities
- Mission-level orchestration.
- Long-running campaigns and retry policies.
- Multi-agent coordination and role assignment.
- Optional zone dispatch in enterprise mode.

## 4. Canonical Mutation Flow
1. Agent submits codeblock or operation request.
2. Request is validated and classified.
3. If safe: execute in safe lane.
4. If mutation intent detected: require mutation capability and route to mutation lane.
5. Acquire mutation lock and establish mutation scope.
6. Apply mutation candidate.
7. Run validation and collect diagnostics.
8. Decide promote, rollback, branch, or discard.
9. Emit incidents and lineage records.
10. Release lock and close scope.

## 5. Governance Principle
- Fast iteration is allowed.
- Structural risk is allowed.
- Ungoverned structural change is not allowed.

Mutation research is powerful because it is controlled, not because it is unrestricted.

## 6. Relationship to Existing Tickets
- Extends `Ticket - Workstation Codegen Guardrails and Capability Manifest.md`.
- Aligns with `CommandOps Mutation Research - Community vs Enterprise Networking (AgentNet vs CommandNet).md`.
- Preserves Ticket 111 boundary direction (Rift as governed surface, CommandOps as orchestrator).
