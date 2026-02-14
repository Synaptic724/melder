# Epic: AI profile opt-in guard

## Metadata
- Epic ID: EPIC-2026-01-22-melder-ai-profile-opt-in
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-22
- Updated: 2026-01-22
- Target Window: 2026-Q1
- Related Program/Initiative: AethericRift readiness

## Problem / Opportunity
AI profiles are heavy and should not be constructed unless a user explicitly opts in. We need a config-level switch and guard so future AI tooling does not accidentally build dense profiles.

## MRP Alignment (Most Reasonable Product)
Keeps AI introspection as an explicit opt-in, preserving safety and resource control before richer AI profile inventory is implemented.

## Goals (Outcomes)
- Add an explicit configuration toggle for AI profile generation.
- Enforce a guard that blocks AI profile creation unless opt-in is enabled.

## Non-Goals (Explicit Exclusions)
- No changes to AI profile schema or data collection.
- No new AI tooling features.

## Scope Boundaries
- In scope:
  - Configuration option for AI profile opt-in.
  - Guard in AI profile entrypoint(s).
- Out of scope:
  - AI profile inventory expansion.
  - New profile data fields.

## Success Metrics
- AI profile generation is blocked by default.
- Opt-in flag enables AI profile generation without other changes.

## Requirements (Functional + Non-Functional)
- Configuration exposes a boolean `ai_profiles_enabled` with a default of false.
- AI profile entrypoint checks the flag and refuses when disabled.

## Constraints / Assumptions
- AI profiles are not used today; this is a preventive gate.

## Dependencies / External References
- `context_compass/stories/2026-01-22_melder_ai_profile_opt_in_story.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Configuration toggle + guard implemented

## Stories (Required to Complete)
- [ ] Story: STORY-2026-01-22-melder-ai-profile-opt-in - add config toggle + guard

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-01-22-melder-ai-profile-opt-in

## Acceptance Criteria (Epic Done)
- AI profile opt-in flag exists and defaults to false.
- AI profile creation raises or blocks when the flag is disabled.
- User confirms expected behavior.

## Risks / Mitigations
- Risk: Hidden call sites bypass guard.
  - Mitigation: guard central entrypoint(s) and document opt-in.

## Validation / Test Approach
- Manual smoke: call AI profile entrypoint with flag on/off.

## Rollout / Adoption Plan
- Default off; enable only in environments that need AI tooling.

## Open Questions
- Should guard be hard error or silent no-op?

## Decision Log
- 2026-01-22: Require explicit opt-in before AI profile creation.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic delivered: AI profile opt-in flag + guard implemented and accepted (2026-01-22).
