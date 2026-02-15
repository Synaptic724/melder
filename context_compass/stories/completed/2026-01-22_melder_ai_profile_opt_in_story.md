# Story: Add AI profile opt-in configuration and guard

## Metadata
- Story ID: STORY-2026-01-22-melder-ai-profile-opt-in
- Epic: EPIC-2026-01-22-melder-ai-profile-opt-in
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-22
- Updated: 2026-01-22

## User Narrative
As a engineer, I want AI profile generation to be opt-in, so that dense introspection is not created unless explicitly enabled.

## Value / MRP Alignment
Prevents accidental heavy introspection while keeping a simple path to enable AI tooling later.

## Requirements (Functional)
- Add `ai_profiles_enabled` configuration property with default false.
- Guard AI profile creation when the flag is disabled.

## Requirements (Non-Functional)
- No new AI profile data collection in this change.
- Keep current binding/resolution flows unchanged.

## Scope Boundaries
- In scope:
  - Configuration changes and AI profile guard.
- Out of scope:
  - AI profile schema expansion.
  - AI tool integrations.

## Dependencies / Related Work
- `context_compass/epics/completed/2026-01-22_melder_ai_profile_opt_in_epic.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-01-22-melder-ai-profile-opt-in-guard - implement config flag + guard

## Acceptance Criteria
- AI profile generation is blocked by default.
- Enabling `ai_profiles_enabled` allows AI profile generation.

## Validation / Test Plan
- Manual smoke: call AI profile entrypoint with flag on/off.

## UX / API / Data Notes
- Guard should be explicit (clear error message) when disabled.

## Risks / Mitigations
- Risk: Unclear enablement path.
  - Mitigation: provide fluent `Configuration.with_ai_profiles(...)`.

## Open Questions
- Should disabled behavior raise or return None?

## Decision Log
- 2026-01-22: Make AI profile generation opt-in via Configuration.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story delivered: AI profile opt-in flag + guard implemented and accepted (2026-01-22).
