# Task: Run structural phases for post-conjure bindings

## Metadata
- Task ID: TASK-2026-01-18-melder-post-conjure-structural-phases
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-18

## Objective
Ensure new spells bound or scanned after conjure immediately run Phases 1-4 so Phase 5-7 validation cannot fail on missing Phase 4 results.

## Scope Boundaries
- In scope: Spellbook.bind and Spellbook.scan flow when conjured, structural phase invocation, tests.
- Out of scope: system-level Phase 5-7 changes.

## Steps / Checklist
- [x] Identify the safest hook point in `Spellbook.bind` / scan to run Phases 1-4.
- [x] Run structural phases on newly bound spells when `Spellbook._conjured` is true.
- [x] Ensure cancellation/event handling and locks match existing patterns.
- [x] Add integration tests covering bind/scan after conjure.

## Deliverables
- Post-conjure structural phase execution for new spells.
- Integration tests for bind/scan after conjure.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell.py`
- `tests/integration/melder/spellbook/`

## Validation
- User reported tests passing after updates.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Risks / Rollback Notes
- Risk: Running phases under the wrong lock could deadlock. Mitigation: review existing spell locks and scheduler usage.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Post-conjure bind/scan now track newly bound spells during binding transactions
  and run Spell.run_structural_phases (Phases 1-4) on transaction end, with
  cancellation and SpellbookValidationError for broken spells. Added integration
  coverage for post-conjure bind/scan structural artifacts.
