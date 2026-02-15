# Task: Add AI profile opt-in guard tests

## Metadata
- Task ID: TASK-2026-01-22-melder-ai-profile-opt-in-guard-tests
- Story: STORY-2026-01-22-melder-ai-profile-opt-in
- Status: done
- Owner:
- Priority: p2
- Created: 2026-01-22
- Updated: 2026-01-22

## Objective
Add unit/component tests to cover the AI profile opt-in guard behavior.

## Scope Boundaries
- In scope:
  - Unit test for guard raise when AI profiles disabled.
  - Component test updates to enable AI profiles where needed.
- Out of scope:
  - Changes to AI profile implementation.

## Steps / Checklist
- [x] Add guard unit test in SpellExaminer tests.
- [x] Update component tests to pass enabled configuration.
- [x] Record validation status.

## Deliverables
- Updated unit/component tests.

## Files / Paths Impacted
- `tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py`
- `tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner.py`
- `tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_inspection.py`
- `tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_profiles.py`

## Validation
- Not run.

## Risks / Rollback Notes
- Low risk: test-only changes.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Added a guard test for AI profile opt-in and updated component tests to enable AI profiles via configuration.
