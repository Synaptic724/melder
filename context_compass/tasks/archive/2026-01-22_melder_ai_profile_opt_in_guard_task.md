# Task: Implement AI profile opt-in flag and guard

## Metadata
- Task ID: TASK-2026-01-22-melder-ai-profile-opt-in-guard
- Story: STORY-2026-01-22-melder-ai-profile-opt-in
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-22
- Updated: 2026-01-22

## Objective
Add a configuration flag that enables AI profile generation and guard the AI profile entrypoint so it is blocked unless explicitly enabled.

## Scope Boundaries
- In scope:
  - Configuration property `ai_profiles_enabled` with default false.
  - Guard in AI profile entrypoint(s).
- Out of scope:
  - AI profile schema expansion.
  - AI tooling integrations.

## Steps / Checklist
- [x] Add configuration property, defaults, validation, and fluent helper.
- [x] Add AI profile guard against disabled flag.
- [x] Document expected behavior in task summary.

## Deliverables
- Code changes in configuration and spell examiner.

## Files / Paths Impacted
- `src/melder/spellbook/configuration/configuration.py`
- `src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py`

## Validation
- Not run.
- Recommended commands:
  - Manual smoke via a minimal script that toggles `ai_profiles_enabled`.

## Risks / Rollback Notes
- Risk: Guard blocks unexpected call sites.
  - Mitigation: provide explicit enablement path via config.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Added `ai_profiles_enabled` configuration property with default false, validation, and fluent setter `with_ai_profiles(...)`. (`src/melder/spellbook/configuration/configuration.py`)
- Guarded AI profile generation via `SpellExaminer.ai_profile_for_spell(...)` using configuration opt-in; raises when disabled or missing. (`src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py`)
- Expected behavior: AI profile creation is blocked unless `Configuration.with_ai_profiles(True)` is set before freeze.
- Completion (2026-01-22): user accepted raise-when-disabled guard; tests not run.
