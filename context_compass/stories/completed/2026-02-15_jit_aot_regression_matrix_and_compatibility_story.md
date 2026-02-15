# Story: JIT/AOT Regression Matrix and Compatibility

Completed: 2026-02-15
Summary: Closed after user acceptance; linked discovery/implementation tasks are complete and validated for this story scope.


## Metadata
- Story ID: STORY-2026-02-15-jit-aot-regression-matrix-and-compatibility
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## User Narrative
As a library maintainer, I want explicit regression coverage for AOT default and
JIT propagation paths so rollout is safe.

## Value / MRP Alignment
This protects backward compatibility while validating new opt-in behavior.

## Requirements (Functional)
- Validate AOT default (`full_ahead_of_time_compilation=true`) remains stable.
- Validate JIT opt-in behavior across conjure, late bind, and transfer owned-only paths.
- Validate runtime gate set/clear lifecycle and fail-fast paths.

## Requirements (Non-Functional)
- Tests must be deterministic and high-signal.
- No low-value attribute-shape tests.

## Scope Boundaries
- In scope:
- Unit/regression tests for all new mode propagation lanes.
- Out of scope:
- New runtime features beyond approved ticket scope.

## Dependencies / Related Work
- `STORY-2026-02-15-jit-aot-config-flag-and-fluent-api`
- `STORY-2026-02-15-jit-aot-conjure-propagation`
- `STORY-2026-02-15-jit-aot-post-conjure-bind-propagation`
- `STORY-2026-02-15-jit-aot-transfer-ownership-propagation-non-contracted`
- `STORY-2026-02-15-jit-aot-runtime-resolution-gate-lifecycle`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-15-implement-jit-aot-regression-matrix-and-compatibility - add regression matrix and execute targeted tests.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Regression matrix covers default AOT and JIT opt-in paths.
- Transfer tests assert owned-lineage propagation and contracted-spell exclusion.
- Validation report is truthful and scoped.

## Validation / Test Plan
- Run targeted pytest suites for config, bind/conjure propagation, transfer, and runtime gate behaviors.

## UX / API / Data Notes
- Test-only scope; no API additions.

## Risks / Mitigations
- Risk: insufficient coverage misses lifecycle regressions.
  Mitigation: require matrix cases for each propagation surface and both modes.

## Open Questions
- Which existing tests can be extended vs where new tests are required?

## Decision Log
- 2026-02-15: Story created to isolate compatibility assurance from implementation logic changes.

## Notes
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Regression work will validate non-breaking default behavior first, then JIT opt-in propagation scenarios in independent test lanes.
  EVIDENCE: context_compass/stories/2026-02-15_jit_aot_config_flag_and_fluent_api_story.md:1-83, context_compass/stories/2026-02-15_jit_aot_runtime_resolution_gate_lifecycle_story.md:1-84
  IMPACT: Prevents mixing validation scope with implementation scope and improves reviewability.
  NEXT: Finalize exact matrix after propagation discovery and implementation stories are complete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Ready validation story that executes after implementation lanes merge.

