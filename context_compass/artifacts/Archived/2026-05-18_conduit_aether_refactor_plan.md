# Conduit Aether Refactor Plan

## Purpose
Capture the current architecture diagnosis and the planned staged refactor for
removing `Conduit -> Aether` as a direct dependency while preserving the real
runtime behavior of Melder.

## Current Diagnosis
The current system has three overlapping issues:

1. `Conduit` depends on `Aether` for too many frame-scoped operations.
2. The interface graph mirrors that dependency knot and causes import-time
   cycles when the interfaces are imported eagerly.
3. Some responsibilities currently owned by `Aether` are semantically
   frame-local or spellbook-local rather than true root-owner behavior.

This is not just a typing problem. The type layer is exposing a real ownership
and packaging problem.

## Core Constraint
`Conduit` must no longer directly access `Aether`.

That means every current `Conduit -> Aether` call must either:
- move to `Spellbook` when the operation is spellbook-owned,
- move to `ConduitCloud` when the operation is frame-scoped conduit/cluster
  behavior,
- or be replaced by a narrower injected runtime dependency when the operation
  is truly conduit-local and not owned by Spellbook or ConduitCloud.

## Conduit -> Aether Call Buckets
### Spellbook-owned
- local spell-index registration into Aether
- local spell-index removal from Aether
- spell-id existence checks
- owner-conduit lookup by spell id
- spell lookup through owner-conduit + owner-spellbook

These are now the first bounded cut and should live behind `Spellbook`.

### Conduit/Frame-scoped network behavior
- named conduit registration / unregistration
- conduit lookup by id / name
- conduit cloud retrieval
- cluster create / remove
- cluster join / leave
- cluster membership listing
- cluster share refresh

These are the strongest candidates to move behind `ConduitCloud`.

### DevOps / gate-controller access
- resolve frame `DevOpsManager`
- resolve `CreationGateController`
- gate lineage rebinding

The concrete dependency here is really `CreationGateController`, not the whole
`DevOpsManager`.

### MutationResearch
- one conduit accessor currently exposes Aether-owned `MutationResearch`

This is not a good fit for `Conduit` and should be removed from the conduit
surface instead of re-routed through another owner.

### Root/frame lifecycle
- root conduit registration / removal
- last-conduit frame cleanup checks

These are the trickiest remaining `Conduit -> Aether` edges because they are
closer to root ownership than the other buckets.

## Staged Plan
### Stage 1: Spellbook-owned Aether work
- Remove `MutationResearch` from `Conduit`.
- Move spell registration / spell-id lookup Aether work behind `Spellbook`.
- Keep the cut limited to:
  - `conduit.py`
  - `spellbook.py`
  - `iconduit.py`
  - `ispellbook.py`

### Stage 2: ConduitCloud as frame-scoped conduit access
- Make `ConduitCloud` the frame-scoped owner of:
  - named conduit registry operations
  - conduit lookup by id / name
  - cluster create / remove
  - cluster join / leave
  - cluster membership queries
  - cluster share refresh
- During transition, `Aether` may delegate to frame-owned `ConduitCloud`
  instead of owning duplicated logic.

### Stage 3: Gate/controller narrowing
- Inject `CreationGateController` directly into `Conduit`.
- Stop resolving/storing the whole `DevOpsManager` just to reach the controller.
- Handle all three wiring paths:
  - root conjure (`SpellbookCreationSystem`)
  - lesser conduit creation
  - lesser -> normal upgrade

### Stage 4: Remaining root-owner edges
- classify the residual frame/root lifecycle calls and decide whether they
  belong on:
  - `Spellbook`
  - `ConduitCloud`
  - a dedicated root/frame lifecycle boundary
- do not solve this with shims

## Design Rules
- No new sidecar runtime shims.
- Prefer `TYPE_CHECKING`-based leaf imports for typing-only dependency edges;
  avoid fake local structural shims instead.
- If an interface mirrors reality, the concrete ownership graph must be able
  to support that import structure honestly.
- `Spellbook` may own spellbook-local upstream queries.
- `ConduitCloud` may own frame-scoped conduit and cluster queries.
- `Aether` should remain the root/frame owner, not the long-term conduit
  service locator.

## Immediate Next Question
After the first spellbook-owned cut, the next architectural choice is:

- move the conduit network/cluster bucket to `ConduitCloud`, or
- narrow the gate/controller dependency first

The current recommendation is to move the conduit network/cluster bucket next,
because it removes the largest group of frame-local `Conduit -> Aether` calls
without enlarging `Spellbook`.
