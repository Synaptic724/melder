# Task: Gate validation when SpellContract provider is missing

## Metadata
- Task ID: TASK-2026-01-30-contract-provider-gating
- Story: N/A
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Ensure spells with missing SpellContract providers are marked as gated/validation-required
in Phase 4 so meld front door blocks late-phase resolution.

## Scope Boundaries
- In scope:
  - Phase 4 validation sets contract_unvalidated gating when SpellContract provider is missing.
  - Update docstrings for touched methods.
- Out of scope:
  - Broader contract resolution behavior changes.
  - Test refactors outside of contract gating.

## Steps / Checklist
- [x] Update Phase 4 validation to mark contract_unvalidated + gated when provider is missing.
- [x] Update Phase 4 docstring to reflect contract gating behavior.

## Deliverables
- Contract validation gating change in spell crafter.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/spell_crafter.py

## Validation
- Not run (relied on user test runs).
- Notes:
  - Updated test stubs to include `issues` where needed.

## Risks / Rollback Notes
- Risk: Additional gating may block flows that previously proceeded in dynamic mode.
- Rollback: Revert contract_unvalidated gating in Phase 4.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
User wants missing SpellContract providers to flip validation_required via the contract
state flag so meld front door blocks late-phase resolution. Apply gating in Phase 4
when SpellContract provider presence issues are detected.
