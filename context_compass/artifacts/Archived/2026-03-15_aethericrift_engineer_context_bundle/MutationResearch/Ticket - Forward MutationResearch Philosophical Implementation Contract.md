# [Ticket] Forward MutationResearch Philosophical Implementation Contract

**Type:** Philosophy / Architecture Ticket  
**Status:** Active Baseline  
**Priority:** Critical  
**Scope:** Melder mutation lab, AethericRift lane routing, CommandOps orchestration integration

---

## 1. Intent

This ticket is the forward-facing philosophical contract for MutationResearch.
It defines what must exist for AI-centric mutation workflows to operate safely,
observably, and reversibly.

This ticket reconciles older mutation tickets and sets the current target model.

---

## 2. Ticket Reconciliation (Keep / Change / Drop)

### Keep
- AI-centric lab workflow and structured world models.
- Explicit `MutationWorkspace` and staged release behavior.
- MutationResearch as the lineage/history authority.
- Spellbook as active-version runtime registry.

### Change
- Working-copy semantics:
  - Mutation edits happen in workspace copies/surrogates, not by editing the live prod-serving object in place.
- Promotion semantics:
  - Promotion is explicit release execution with pre/post state artifacts.

### Drop
- SpellFamily/SpellIdRef runtime indirection as core resolution mechanism.
- Pointer-based dynamic indirection in Spellbook.
- Multi-version storage in Spellbook runtime path.

---

## 3. Core Principles

1. Structured world models over logs.
2. Mutation in lab first, never direct prod mutation.
3. Explicit handles over hidden side effects.
4. Promotion is a release event, not a side effect.
5. Rollback path is mandatory before promotion.
6. Guardrailed codegen is default; mutation is explicit escalation.

## 3.1 Encoding Policy (Current)

- Current transport and state payloads are `JSON` (optionally minified).
- Payload design must remain `TOON-compatible` for future migration.
- Decision-making must rely on structured payloads, not free-text logs.

---

## 4. Responsibility Split

### Melder
- Runtime substrate and lifecycle truth.
- SpellState, ChangeControlCore, IncidentManager state.
- Structural mutation apply/revert mechanics.
- Promotion-time runtime rebind and validation execution.

### AethericRift
- Capability governance (ACL intersection).
- Safe lane vs mutation lane routing.
- Codegen guardrails (AST/symbol checks via manifest).
- Structured operation surfaces and audit identity envelope.

### CommandOps
- Long-running mutation campaigns.
- Multi-agent mission coordination.
- Retry/scheduling/zone orchestration policies.

---

## 5. Required Conceptual Surfaces

All of these must be available as small structured payloads (`JSON` now, TOON-compatible later).

1. `MutationWorkspace`
- `workspace_id`
- `status` (`draft|exploring|testing|ready_for_release|released|abandoned`)
- `root_targets{}`
- `imported_spells{}`
- `mutated_spells{}`
- `mocked_spells{}`
- `anchored_spells{}`

2. `MutationSpell`
- origin id, candidate id, stage
- graph-oriented change summary

3. `MockSpell` / `AnchoredSpell` descriptors
- behavior and limitations for mocks
- explicit non-mutable rationale for anchors

4. `ScenarioRun`
- workspace, root invocation, overrides, inputs
- result with outputs/side effects summary
- touched SpellState snapshots
- incidents emitted

5. `ReleasePlan`
- targeted promotions
- graph/state diff summary
- impacted roots
- rollback plan pointer

6. `ReleaseOutcome`
- applied plan id, success/failure
- incidents
- post-release SpellState/dirty-root summary

---

## 6. Lane Contract

### Safe Lane (default)
- Existing approved capabilities only.
- No structural mutation operations.
- Runs through manifest + AST/symbol validation + runtime ACL re-check.

### Mutation Lane (explicit)
- Add/remove/change/create structural operations.
- Requires mutation capability intersection.
- Requires lock and control-plane gates.

### Escalation Rule
- Safe lane can request escalation.
- Escalation is explicit and auditable.
- Ambiguous intent defaults to deny, not implicit mutation.

---

## 7. Mutation Lifecycle Contract

Canonical states:

1. `proposed`
2. `authorized`
3. `locked`
4. `applied`
5. `validated`
6. `promoted` or `rolled_back` or `discarded`
7. `closed`

Required lifecycle artifacts:
- candidate identity/hash
- lock identity/scope
- validation report
- release decision record
- incident links

---

## 8. Control Plane Gates (Non-Negotiable)

1. Permission gate (Object ACL AND Domain ACL AND Profile ACL)
2. Lock gate (structural mutation lock)
3. SpellState gate (allowed mutation transition)
4. ChangeControl gate (blast-radius accounting)
5. Validation gate (policy-defined checks)
6. Promotion gate (promote/rollback/branch/discard)
7. Incident gate (structured failure/deny/conflict records)

No mutation workflow may bypass these gates.

---

## 9. Spellbook and Lineage Model

### Runtime Registry Rule
- Spellbook stores one active runtime version per binding target.
- Mutation history and DAG data live in MutationResearch, not Spellbook.

### Promotion Rule
- Promotion atomically rebinds active runtime spell identity.
- Rebuild/re-profile runtime blueprint artifacts needed for stable resolution.
- Apply configured cleanup/quarantine policy for obsolete creations.

### Identity Rule
- Identity update boundaries must be concurrency-safe and auditable.
- SyncString-style identity fields are allowed where needed for safe atomic swaps.

---

## 10. Workspace Isolation Model

1. Workspace creation forks/imports target context into lab scope.
2. Workspace owns mutation candidates and mock/anchor declarations.
3. Workspace failures are containable (dispose scope, release locks, incident emit).
4. Workspace closure finalizes lineage records.

This is a hard separation between exploration and production runtime.

---

## 11. Community vs Enterprise Topology

### Community
- Single runtime world, many isolated lab scopes.
- No CommandNet required.

### Enterprise
- Multiple zones/worlds with optional CommandNet coordination.
- Research zones can run campaigns and propose release plans.
- Primary operational zone remains promotion authority.

Topology changes where research runs, not what mutation means.

---

## 12. Observability Contract

Every meaningful mutation step should be representable as compact structured payloads:
- workspace descriptors
- mutation spell summaries
- scenario results
- release plan/outcome
- SpellState/ChangeControl snapshots
- incidents

Logs may exist, but decision-making must not depend on parsing logs.
Preferred current encoding is minified JSON.

---

## 13. Implementation Work Ahead (Philosophical Checklist)

1. Define stable JSON schema set for workspace/scenario/release/state surfaces (TOON-compatible).
2. Implement explicit lane classifier contract (safe vs mutation).
3. Implement mutation lock contract and conflict semantics.
4. Implement workspace lifecycle APIs and status transitions.
5. Implement scenario execution and structured result projection.
6. Implement release plan drafting and outcome recording.
7. Implement rollback planning and execution surfaces.
8. Wire IncidentManager emission for all mutation gate failures.
9. Wire SpellState and ChangeControl snapshots for pre/post comparisons.
10. Implement policy profiles for mutation capabilities across domains.
11. Implement community and enterprise topology adapters to same contract.
12. Add audit identity envelope for all mutation and release operations.

---

## 14. Non-Goals

- Precise Python class/module naming.
- Final storage backend selection.
- UI decisions (REPL vs API vs DSL frontends).
- Human unit test strategy details.

---

## 15. Acceptance Criteria (Conceptual)

This ticket is accepted when the team agrees that:

1. Mutation is workspace-first and release-driven.
2. Safe lane and mutation lane are clearly separated and enforced.
3. MutationResearch is the lineage authority.
4. Spellbook remains active-version runtime registry, not version DAG store.
5. Promotion and rollback are explicit, structured, and auditable.
6. Structured JSON payloads are sufficient for AI decision loops without log scraping, with TOON-compatibility preserved.
7. Community and enterprise topologies map to one coherent mutation contract.
