# Task: Investigate change-control transaction coordination across conduits

## Metadata
- Task ID: TASK-2026-01-18-melder-change-control-transaction-investigation
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-20

## Objective
Investigate whether binding transactions should be coordinated through
change-control/system-state layers so that mutations in one conduit/spellbook
can influence other conduits (e.g., revalidation timing, safety gates, or
deferred resolution) in a multi-conduit runtime.

This is an analysis ticket: the deliverable is an evidence-backed proposal for
how (or whether) cross-conduit change coordination should work, including the
tradeoffs and integration points.

## Scope Boundaries
- In scope:
  - Current change-control and system-state modules (e.g., change control manager,
    spell system states, dev ops managers).
  - Conduit and Spellbook mutation lifecycle (bind/scan/conjure).
  - Existing validation and dirty-propagation flow.
  - Multi-conduit interaction patterns (contracted conduits, shared spellbooks).
- Out of scope:
  - Implementing cross-conduit coordination logic.
  - ACL or permission model changes.
  - New DI features or resolution semantics.

## Motivation / Problem Statement
We added a low-level binding transaction gate to prevent bind/scan during
uncoordinated mutation. However, Melder is a multi-conduit system and can
support contracted conduits, shared Aether state, and dynamic linkage between
conduits. A local gate may be insufficient if:

- Conduit A mutates a spellbook while Conduit B concurrently resolves against
  related frames or collections.
- The system needs to defer or revalidate dependent spells across conduits when
  bindings change.
- Change-control/validation already tracks system states, but the transaction
  semantics are not propagated across conduit boundaries.

We need to determine whether change coordination should be raised to a
system-level transaction (Aether / change control) instead of being purely local
to a Spellbook.

## Questions to Answer
- What existing change-control or system-state machinery already tracks or
  governs mutation, and how is it used today?
- Are conduits sharing a Spellbook expected to be the norm, or do we expect
  multiple spellbooks to coexist in a process?
- When Conduit A changes bindings, how can Conduit B detect it (if at all)
  today? Is it acceptable that it does not?
- Should a binding transaction be scoped to a Spellbook, a Conduit, or the
  Aether system state?
- Should a **single admission gate** (lock-based) be the required entrypoint
  for all change requests to avoid race conditions?
- What is the smallest viable coordination model that avoids revalidation
  thrash or nondeterministic resolution under concurrent mutation?

## Requirements (Analysis Deliverable)
- Summarize current code evidence for change-control / system-state hooks.
- Identify the minimal set of coordination scenarios we must support.
- Propose at least two viable coordination models (local vs system-level),
  with explicit tradeoffs and integration points.
- Recommend a preferred model with justification.
- Document follow-up engineering tasks that would be needed if adopted.

## Steps / Checklist
- [x] Inventory existing change-control/system-state modules and their roles.
- [x] Map current mutation points (bind/scan/conjure) and when validation runs.
- [x] Identify cross-conduit coordination gaps and expected runtime behavior.
- [x] Propose coordination options and evaluate tradeoffs.
- [x] Write a recommendation and list follow-up tasks.

## Deliverables
- A written proposal in this ticket (use Context / Handoff Summary section) or
  a linked artifact if the analysis is large.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control/`
- `src/melder/aether/dev_ops/spell_system_states/`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`

## Validation
- Not run (analysis-only).

## Risks / Rollback Notes
- Risk: Over-scoping the transaction model into a global lock.
  Mitigation: explicitly document scope limits and concurrency assumptions.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
- Code evidence (single-frame only; no cross-frame coordination):
  - `src/melder/aether/aetheric_frame.py` owns per-frame `SpellSystemStates` and
    `DevOpsManager` (which owns `ChangeControlManager`). This is the only scope
    for change-control; no cross-frame propagation is supported.
  - `src/melder/aether/dev_ops/dev_ops_manager.py` exposes `change_control_manager`
    and delegates `revalidate_dirty_roots()` to it. This is the DevOps-facing
    entrypoint for any cross-conduit coordination inside the frame.
  - `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
    tracks pending changes, `component_of` (spell_id -> root ids), and dirty
    roots. It does not run policies itself; it registers a revalidator hook and
    marks roots dirty via `notify_spell_changed()`.
  - `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
    is the per-frame control tower for lineages and per-conduit resolution
    states. It also tracks **collection dependency indices per Spellbook**
    (`_collection_dependents_by_spellbook`) and marks list[Frame] consumers
    dirty via `mark_collection_dependents_dirty(...)`.
    - `update_dependencies(...)` and `compute_impact_closure(...)` maintain
      reverse edges and dirty sets for structural gating (Phases 1-4).
    - `mark_structural_change(...)` is the explicit gate for rebind/mutation
      events and feeds the dirty lineage set.
  - `src/melder/spellbook/spell_crafter/spell_crafter.py` wires change-control
    during Phase 5/7 by calling `ChangeControlManager.rebuild_component_of(...)`
    and registering `_revalidate_dirty_roots(...)`. This hook re-runs all phases
    for dirty roots using a `SpellbookScanner`.
  - `src/melder/spellbook/spellbook.py` runs Phase 7 (`change_control`) as part
    of `_run_resolution_phases_for_conduit(...)` after root blueprints and
    system validation. Each local spell executes `spell.run_phase_change_control(...)`.
  - `src/melder/aether/conduit/meld/meld.py` gates resolution via
    `_gated_validation_required(...)`:
      - If the root is dirty under change-control, it raises `MeldExecutionError`.
      - If `SpellSystemState.validity` is UNKNOWN/GATED, it runs structural phases.
      - Resolution gating (Phases 5-7) is per-conduit via
        `ConduitResolutionState`.
  - `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py` also enforces
    change-control and validity gating before runtime execution, blocking
    `MeldRuntime.execute(...)` when roots are dirty or gated.
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
    registers pending changes and clears them on successful transfer, showing
    change-control is already used for mutation-like flows.
  - Binding/scan gating is Spellbook-local and transaction-based; post-conjure
    binds run structural phases 1-4 and mark local list[Frame] consumers dirty,
    but do not re-run Phases 5-7 unless meld triggers them.
  - Linking/contracting is handled by `ConduitWard`:
      - `src/melder/aether/conduit/conduit_ward/conduit_ward.py` creates link
        contracts, adds contracted spells, and invalidates SpellContract consumers.
      - `src/melder/spellbook/spellbook.py` stores contracted spells per peer
        conduit id and enforces binding-key uniqueness across local/contracted
        maps via `_assert_lookup_key_available(...)`.
      - `_preflight_contract_dependency_collisions(...)` checks for collisions
        across dependencies before linking.

- Observed gap: `ChangeControlManager.rebuild_component_of(...)` is **frame-wide**
  and appears to be overwritten by each Spellbook’s Phase 5/7 run. If multiple
  Spellbooks exist in one frame, component-of indexing and revalidator hooks may
  be overwritten by the last Spellbook that runs Phase 5/7.

- Coordination questions (within a single AethericFrame only):
  - Should change-control data be **spellbook-scoped** (like collection indices)
    or remain frame-global? If global, how do we avoid cross-spellbook overrides?
  - When a contracted spell is added/removed, which conduit(s) should be gated:
    borrower only, owner only, or both? The current invalidation is local.
  - Do we need an explicit **contract/cluster transaction** that gates meld for
    linked conduits while binding/contracting is in progress?

- Proposed coordination models to evaluate next:
  1) Spellbook-local transactions only; rely on `SpellSystemStates` list[Frame]
     gating + per-conduit resolution gating. Lowest complexity but no cross-
     conduit embargo.
  2) Frame-level change-control **namespaced by Spellbook id** (or Conduit id).
     Store component-of and dirty roots per spellbook, merge only when conduits
     are explicitly linked. Avoids cross-spellbook overwrite.
  3) Contract-scoped change control: `ConduitWard` emits change-control events
     for linked peers; meld gates only the participating conduits. This keeps
     scope within a single frame but avoids global locking.
  4) Global frame lock (explicitly not desired; would block unrelated conduits).

- Directional guardrails (MRP intent):
  - All change requests funnel through a single orchestrator admission lock
    (no queue), with conflict/embargo checks deciding parallelism.
  - Embargoes are transaction-driven internal state (implicit via bind/link/
    transfer/mutation) and released on commit/abort.
  - Provider changes embargo inbound link/contract requests targeting that
    provider while the change is active.

- Next investigation steps:
  - Trace all callers of `rebuild_component_of(...)` to confirm overwrite risk.
  - Identify whether any existing APIs already namespace change-control by
    spellbook or conduit id.
  - Define minimal deterministic transaction semantics for linked conduits
    without introducing cross-frame coordination.

### Recommendation (MRP)
- Prefer **contract-scoped change control** (Model 3) combined with spellbook-
  scoped change-control indices:
  - Keep the orchestrator admission gate as the only serialized step.
  - Require explicit link transactions that name borrower + provider conduits.
  - Gate only participating conduits (borrower + linked peer), not the full frame.
  - Preserve spellbook-local dirty propagation for list[Frame] consumers.

### Follow-up tasks / decision checkpoints
1) Define change-control namespacing (spellbook id vs conduit id) and update
   `ChangeControlManager.rebuild_component_of(...)` to avoid frame-wide override.
2) Implement contract-scoped dirty gates for borrower conduits when contracted
   bindings change.
3) Expand link/contract admission tests for concurrent borrowers and embargo
   conflicts under explicit link transactions.
4) Document agent-facing guidance for link transaction workflows and expected
   rejection behaviors.
