# Task: Add SpellContract consumer/provider indexes for targeted invalidation

## Metadata
- Task ID: TASK-2026-01-28-spellcontract-consumer-index
- Story: N/A
- Status: draft
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Problem / Opportunity
Contract changes (add/remove/transfer) do not currently mark SpellContract consumers dirty. Phase 8-10 artifacts can become stale, causing contracted-provider precedence to drift. The system already detects SpellContract sockets in phases 1-3, but no index exists to target invalidation.

## Context
Evidence:
- Contract sockets are detected in Phase 1-3 requirements/topology (e.g., `SpellRequirementsFinder` classifies `SpellContract` defaults and `SpellLocalTopology` carries `contract_key`).
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py
  - src/melder/spellbook/spell_crafter/topology/spell_local_topology.py
- Contract operations currently invalidate creations only (`_invalidate_contract_consumers`) without dirty-marking lineages.
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:_invalidate_contract_consumers
- Phase 7 only wires change-control revalidation; it does not generate dirty signals.
  - src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_change_control

## MRP Alignment
Use phase-derived contract metadata to drive targeted invalidation instead of runtime checks. This keeps meld/runtime lean and makes phase artifacts authoritative.

## Goals
- Build a Spellbook/SpellSystemStates index from phase artifacts: `contract_key -> set[lineage_id/root_id)`.
- Mark only the affected consumer lineages dirty on contract add/remove/transfer.
- Trigger existing change-control revalidator to rebuild phases 8-10.

## Non-Goals
- No new runtime validation checks in meld runtime/engine.
- No changes to contract resolution semantics beyond correct invalidation.

## Requirements
- Index must be derived from Phase 1-3 artifacts (no ad-hoc introspection in ConduitWard).
- Dirty-marking must be narrow (only contract-key consumers).
- Must use existing `SpellStateChangeReason.contract_unvalidated` when marking dirty.

## Acceptance Criteria
- Contract add/remove/transfer causes only relevant consumer roots to be marked dirty.
- Change-control revalidator rebuilds phases 8-10 for those roots.
- No new runtime checks are introduced in meld runtime/engine.

## Scope Boundaries
- In scope:
  - Add contract-key consumer index (location TBD per implementation).
  - Wire contract add/remove/transfer to dirty-marking.
- Out of scope:
  - Removing local fallback behavior.
  - Refactoring contract resolution logic.

## Steps / Checklist
- [ ] Identify the canonical phase artifact that holds contract_key data (Phase 1-3) and the best storage site.
- [ ] Implement contract consumer index build/update during phase runs.
- [ ] Add dirty-mark hooks in contract add/remove/transfer paths.
- [ ] Ensure dirty-marking uses `SpellStateChangeReason.contract_unvalidated`.

## Deliverables
- Contract consumer index stored and updated during phases.
- Targeted dirty-marking on contract changes.

## Files / Paths Impacted
- UNKNOWN (implementation-dependent). Likely:
  - src/melder/spellbook/spell_crafter/spell_crafter.py
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/integration/melder/conduit/test_conduit_integration_links_contracts.py -k "contract"

## Risks / Rollback Notes
- Risk: Incorrect scoping of dirty roots could cause over-revalidation.
- Rollback: Remove index + dirty hooks; restore prior behavior.

## Decision Log
- 2026-01-28: Use phase-derived contract metadata for invalidation instead of runtime checks.

## Unknowns
- Where to persist the contract-key consumer index (SpellSystemStates vs Spellbook).
- Exact contract change entry points that should mark dirty (add/remove/transfer specifics).

## Context / Handoff Summary
Created to drive targeted invalidation for SpellContract consumers using phase-derived metadata. Pending decision on storage location and hook points.
## Root Cause Discussion (Contract Precedence Drift)
The current Phase 8 OccurrencePlan can be reused after contract changes because contract operations only invalidate creations (`_invalidate_contract_consumers`) and do not mark contract-dependent consumers dirty. When a contract is added/removed, the cached plan still reflects the earlier contract state. As a result, SpellContract resolution falls back to local providers even when a contracted provider now exists.

Prior behavior relied on runtime validation (`_populate_contract_overrides_from_plan`) to reject stale plans when contracted-first resolution no longer matched the plan. That validation was removed during migration, so stale plans are accepted. The fix should be to use phase-derived contract metadata to mark the relevant consumer lineages dirty so Phase 8–10 artifacts rebuild under change-control, instead of reintroducing runtime checks.
