# Story: JIT/AOT Config Flag and Fluent API

## Metadata
- Story ID: STORY-2026-02-15-jit-aot-config-flag-and-fluent-api
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## User Narrative
As a spellbook integrator, I want a first-class configuration switch for JIT vs
AOT so runtime behavior is explicit and stable.

## Value / MRP Alignment
This isolates config contract changes before runtime behavior edits so defaults
stay safe and adoption remains explicit.

## Requirements (Functional)
- Add `full_ahead_of_time_compilation: bool` to configuration.
- Keep default `true` (non-breaking default behavior).
- Add fluent API support to read/write the property.
- Ensure config validation/type behavior is explicit.

## Requirements (Non-Functional)
- No default behavior regression for existing users.
- No hidden side effects outside configuration and fluent API scope.

## Scope Boundaries
- In scope:
- `Configuration` property + fluent API surface.
- Out of scope:
- Runtime phase execution logic.

## Dependencies / Related Work
- `TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces`
- `STORY-2026-02-14-jit-aot-configuration-and-spell-contract`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-15-implement-jit-aot-config-flag-and-fluent-api - add property defaults, validation, and fluent accessors.
- [x] Task: TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces - confirm final insertion points before implementation.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Configuration has `full_ahead_of_time_compilation` with default `true`.
- Fluent API exposes this property with clear chaining behavior.
- No existing default-path behavior changes.

## Validation / Test Plan
- Unit tests for config defaults, mutation rules, and fluent API behavior.

## UX / API / Data Notes
- This is API-surface work and must remain backward-compatible by default.

## Risks / Mitigations
- Risk: accidental default flip to JIT.
  Mitigation: explicit unit assertions for default value and defaults loader.

## Open Questions
- Should fluent API include one generic setter only, or explicit enable/disable helpers as well?

## Decision Log
- 2026-02-15: Story created from user-approved direction to keep AOT default true and make JIT opt-in via config.

## Notes
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Config/fluent API lane is implemented and targeted configuration tests pass (`73 passed`).
  EVIDENCE: context_compass/tasks/2026-02-15_implement_jit_aot_config_flag_and_fluent_api_task.md:1-89, src/melder/spellbook/configuration/configuration.py:81-81, src/melder/spellbook/configuration/configuration.py:442-442, src/melder/spellbook/configuration/configuration.py:702-725, tests/unit/melder/spellbook/configuration/test_configuration.py:30-30, tests/unit/melder/spellbook/configuration/test_configuration.py:126-130, tests/unit/melder/spellbook/configuration/test_configuration.py:488-504
  IMPACT: Story acceptance is now review-only; downstream propagation lanes can consume the config flag.
  NEXT: Route active execution to `TASK-2026-02-15-implement-jit-aot-conjure-propagation`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Configuration surface is the first implementation lane because user approved `full_ahead_of_time_compilation` naming and non-breaking default behavior.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_assumption_challenge_task.md:31-53, src/melder/spellbook/configuration/configuration.py:431-450, src/melder/spellbook/configuration/configuration.py:785-918
  IMPACT: All downstream propagation lanes can consume one canonical config flag.
  NEXT: Complete discovery touchpoint map and then execute TASK-2026-02-15-implement-jit-aot-config-flag-and-fluent-api.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Ready implementation story. Gated on propagation discovery task completion.
