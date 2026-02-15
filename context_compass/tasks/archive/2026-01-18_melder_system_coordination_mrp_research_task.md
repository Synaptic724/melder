# Task: Compile multi-conduit coordination research and MRP plan

## Metadata
- Task ID: TASK-2026-01-18-melder-system-coordination-mrp-research
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-20

## Objective
Consolidate current research on multi-conduit mutation/contract behavior into a
single evidence-backed writeup and draft an MRP plan for coordination and
revalidation within a single AethericFrame.

## Scope Boundaries
- In scope:
  - Compile code evidence for change-control, SpellSystemStates, and contract linking.
  - Identify coordination gaps affecting post-conjure binds and linked conduits.
  - Draft MRP plan (reasonable, durable core; no MVP shortcuts).
  - Propose follow-up tasks and decision points.
- Out of scope:
  - Implementing coordination features.
  - Any cross-aetheric-frame behavior.
  - ACL or permissions redesign.

## Steps / Checklist
- [x] Inventory current change-control + SpellSystemStates wiring.
- [x] Map contract/link spell flow and binding-key collision checks.
- [x] Identify gaps/risks in multi-conduit coordination (single frame).
- [x] Draft MRP plan (core outcomes + guardrails).
- [x] Outline follow-up tasks and decision checkpoints.

## Deliverables
- Consolidated research writeup in Context / Handoff Summary.
- Draft MRP plan and scope boundaries for coordination improvements.
- Follow-up task list with decision checkpoints.

## Files / Paths Impacted
- `src/melder/aether/aetheric_frame.py`
- `src/melder/aether/dev_ops/dev_ops_manager.py`
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spellbook.py`

## Validation
- Not run (analysis-only).

## Risks / Rollback Notes
- Risk: Over-scoping coordination into a global lock. Mitigation: keep scope at
  spellbook/contract or per-conduit resolution state within a single frame.
- Risk: MRP plan too narrow to avoid rework. Mitigation: include future-safe
  boundaries and explicit follow-up tasks.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
### Research consolidation (single AethericFrame scope only)
- Per-frame control plane lives in `AethericFrame` and owns `SpellSystemStates`
  and `DevOpsManager` (`src/melder/aether/aetheric_frame.py`).
- `DevOpsManager` exposes `ChangeControlManager` and delegates dirty-root
  revalidation (`src/melder/aether/dev_ops/dev_ops_manager.py`).
- `ChangeControlManager` tracks:
  - `component_of` (spell_id -> root ids) built from Phase 5 blueprints.
  - Dirty roots (`notify_spell_changed`) and revalidator hook
    (`set_revalidator`) for rerunning phases.
  (`src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`)
- `SpellSystemStates` owns lineages + per-conduit resolution state and tracks
  collection dependents **per Spellbook** (for list[Frame] revalidation).
  (`src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`)
- `SpellCrafter` wires change-control in Phase 5/7 by rebuilding `component_of`
  and registering `_revalidate_dirty_roots` (re-runs all phases for dirty roots).
  (`src/melder/spellbook/spell_crafter/spell_crafter.py`)
- `Spellbook` runs Phase 7 (`change_control`) as part of conduit-scoped phases
  5-7; each local spell executes `run_phase_change_control(...)`.
  (`src/melder/spellbook/spellbook.py`)
- `Meld` + `MeldRuntime` block execution when a root is dirty under change
  control or structurally gated (`src/melder/aether/conduit/meld/meld.py`,
  `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`).
- Linking/contracting:
  - `ConduitWard._add_spell_to_contract(...)` preflights collisions and
    adds contracted spells to the peer spellbook.
  - `Spellbook._assert_lookup_key_available(...)` enforces binding-key
    uniqueness across contracted maps only; local overlaps are permitted
    and local bindings resolve first.
  (`src/melder/aether/conduit/conduit_ward/conduit_ward.py`,
  `src/melder/spellbook/spellbook.py`)

### Gaps / risks identified
- `ChangeControlManager.rebuild_component_of(...)` is frame-wide and can be
  overwritten by whichever spellbook last runs Phase 5/7. This risks cross-
  spellbook interference inside the same frame.
- Contracted spells inherit local collection gating via `_mark_collection_dependents_dirty`,
  but there is no explicit contract-scoped change-control barrier.
- Post-conjure binding currently runs structural phases locally; conduit-scoped
  phases are run lazily during meld. This is correct but needs coordination
  rules for multi-conduit, linked scenarios.
- Local vs contracted binding-key overlap is allowed but undocumented; this
  can silently shadow contracted spells.

### Object map (single-frame only)
- AethericFrame: owns `DevOpsManager` + `SpellSystemStates`; seeds change-control
  for all conduits within the frame.
- DevOpsManager: top-level accessor for change-control + system-state tools.
- ChangeControlManager (facade): optional transaction manager + admission gate;
  maintains in-flight registry, dirty roots, minimal audit logging (no queue),
  and a link-mirror registry for active contracts.
- ConflictManager: evaluates scope-key overlap to decide parallel vs sequential.
- EmbargoManager: blocks requests by scope (hard) with advisory hints (soft locks);
  embargoes are transaction-driven internal state.
- Change Orchestrator: executes staged mutation pipeline (preflight, stage,
  validate, commit/abort) and serializes admission via a lock.
- Spellbook: local mutation surface (bind/scan); begins transactions when change
  management is enabled.
- Conduit / ConduitWard: link/contract/unlink/transfer surfaces; wrap changes in
  begin_transaction(type); invalidate contract consumers on change.
- SpellSystemStates: per-frame lineage registry + per-spellbook collection
  indices; per-conduit resolution state for Phases 5-7.

### Transaction stories (strategy per type)
1) **Bind/Scan**
   - Scope: spellbook_id + binding keys.
   - Strategy: stage new spells + lookup keys, preflight collisions, run
     structural phases 1-4, commit staged maps, mark collection dependents.
2) **Link/Contract**
   - Scope: borrower_conduit_id + provider_conduit_id + contract keys.
   - Strategy: preflight collisions, stage contracted maps, commit + invalidate
     contract consumers under orchestrator admission.
3) **Unlink/Remove Contract**
   - Scope: borrower_conduit_id + provider_conduit_id + contract keys.
   - Strategy: stage removals, clear contracted maps on commit, invalidate
     contract consumers, mark collection dependents dirty if needed.
4) **Transfer Ownership**
   - Scope: source_conduit_id + target_conduit_id + spell_index_id (+ deps).
   - Strategy: stage registry flips + contract updates; register pending change,
     commit or rollback to prior owner under orchestrator admission.
5) **Cluster Share/Refresh**
   - Scope: cluster_id + member conduit ids + spell_index_id.
   - Strategy: stage share map updates for all members, commit in a single step,
     invalidate local consumers where new shares appear.
6) **Mutation (placeholder)**
   - Scope: spell_index_id + mutation_lab_id (or equivalent).
   - Strategy: reserve scope; execution deferred until mutation system is in scope.

### Draft MRP plan (reasonable, durable core)
1) **Single-frame scope guarantee** (non-negotiable):
   - All coordination stays within a single AethericFrame.
   - No cross-frame dirty propagation or contract effects.
2) **Change-control namespacing** (core durability):
   - Avoid frame-global `component_of` collisions by scoping change-control to
     Spellbook or Conduit id, then merge only when conduits are explicitly linked.
3) **Contract-scoped gating**:
   - When contracted bindings change, gate only the borrower’s resolution state
     (and optionally the linked peer) rather than global frame gating.
4) **Deterministic transaction boundaries**:
   - Binding/scan requires an explicit transaction; a single completion point
     triggers structural phases + collection dirty marking; Phases 5-7 remain
     on-demand via meld.
   - Provide scaffolding for admission + embargo/conflict/orchestrator without
     forcing it on by default.
   - If a provider conduit is under change, embargo inbound link/contract
     requests that target that provider until commit/abort.
5) **Collision contract (explicit)**:
   - Contracted-vs-contracted binding-key collisions remain an error.
   - Local-vs-contracted overlaps are allowed with documented local precedence;
     disambiguation still encouraged via spellframe/binding_name.
6) **Minimal observability + coordination hints**:
   - Log request metadata (conduit_id, request_type, created_at) if a logger
     is configured; otherwise no-op.
   - Provide advisory embargo hints ("soft locks") for agent coordination.
7) **Single admission gate (no queue)**:
   - All change requests funnel through the orchestrator admission lock.
   - Conflict/embargo checks decide whether new work can run in parallel.

### Follow-up tasks (draft)
- Define change-control namespaces (spellbook_id vs conduit_id) and update
  `component_of` + dirty tracking to avoid frame-wide overwrite.
- Add contract-scoped change-control events and per-conduit dirty gates for
  linked conduits.
- Expand link/contract tests to cover overlap collisions and gating behavior.
