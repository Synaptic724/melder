- Completed: 2026-01-28
- Summary: Removed SpellContract local fallback and updated tests to enforce contracted-only resolution.

# Task: Remove local fallback for SpellContract resolution

## Metadata
- Task ID: TASK-2026-01-28-spellcontract-no-local-fallback
- Story: N/A
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Problem / Opportunity
Local fallback allows a SpellContract socket to resolve a local provider when a contracted provider is missing. The request is to treat this as a bug and remove fallback so a missing contract fails resolution.

## Context
Evidence of current fallback behavior:
- OccurrencePlan contract resolution collects contracted candidates and then falls back to local candidates.
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:_resolve_spell_contract_spell_id
- Tests expect contracted-first with local fallback after contract removal (to be updated if behavior changes).
  - tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py

## MRP Alignment
SpellContracts should be explicit and deterministic; missing contracted providers should not silently resolve to local bindings.

## Goals
- Remove local fallback from SpellContract resolution.
- Enforce contracted-only resolution for SpellContract sockets.

## Non-Goals
- Do not alter MutationContract resolution.
- Do not change contract key derivation logic.

## Requirements
- Contract resolution must raise when no contracted provider exists.
- Update tests to match new behavior.

## Acceptance Criteria
- SpellContract sockets fail with a clear error when no contracted provider exists.
- Local providers are no longer used as fallback for SpellContract sockets.

## Scope Boundaries
- In scope:
  - Contract resolution logic (OccurrencePlan / meld runtime path as needed).
  - Tests that assert local fallback behavior.
- Out of scope:
  - General DI fallback behavior for non-contract sockets.

## Steps / Checklist
- [x] Identify all code paths that implement local fallback for SpellContract.
- [x] Remove fallback logic and enforce contracted-only resolution.
- [x] Update relevant tests to match new behavior.

## Deliverables
- Contract resolution is contracted-only.
- Tests updated to reflect the new behavior.

## Files / Paths Impacted
- UNKNOWN (implementation-dependent). Likely:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py
  - tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py -k "contract"

## Risks / Rollback Notes
- Risk: Ownership-transfer and contract-removal flows that relied on local fallback will now fail unless re-contracted.
- Rollback: Restore local fallback resolution.

## Decision Log
- 2026-01-28: User requested removal of local fallback for SpellContract.

## Unknowns
- Exact list of tests and flows that rely on local fallback (needs verification).

## Context / Handoff Summary
Local fallback removed for SpellContract resolution; tests updated to expect contracted-only behavior.
