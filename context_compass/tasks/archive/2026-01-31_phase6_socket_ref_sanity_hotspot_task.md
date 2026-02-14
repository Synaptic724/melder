# Task: Reduce Phase 6 socket ref sanity hotspot

## Metadata
- Task ID: TASK-2026-01-31-phase6-socket-ref-sanity-hotspot
- Story:
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Identify and reduce the dominant Phase 6 runtime cost in `SocketRefSanityStrategy.run` without changing validation semantics.

## Problem / Opportunity
Phase 6 system validation is the largest contributor in the full conjure build profile. The top hotspot is `SocketRefSanityStrategy.run`, which currently consumes ~0.253s out of ~0.506s total for the full 1–11 phase run on the deep_layers benchmark. This blocks overall build-time improvements.

## Context
Evidence is from the user's `profile_conjure_build_direct.py` run on 2026-01-31: `SocketRefSanityStrategy.run` is the top cumulative-time function in Phase 6. This strategy lives in `src/melder/spellbook/spell_crafter/system/validation/socket_ref_sanity_strategy.py` and is invoked via `SpellCrafter.run_phase_system_validation` in `src/melder/spellbook/spell_crafter/spell_crafter.py`.

## MRP Alignment
We need Phase 6 validation to remain correct and trustworthy while reducing unnecessary CPU work. This is core to build-time reliability and performance.

## Goals
- Determine why `SocketRefSanityStrategy.run` dominates Phase 6 time on deep_layers.
- Identify redundant work (e.g., repeated hashing/equality checks, repeated traversal).
- Implement a targeted optimization that preserves validation behavior.
- Validate improvement using the same benchmark harness.

## Non-Goals
- Do not change validation outcomes or error semantics.
- Do not remove the strategy.
- Do not change public APIs.

## Scope Boundaries
- In scope: `SocketRefSanityStrategy` implementation and any immediate helper logic it owns.
- Out of scope: unrelated validation strategies, phase scheduler changes, or new caches with global lifetime.

## Requirements
- Maintain validation correctness (no loosened checks).
- Avoid new module-level mutable state.
- Keep changes localized and reviewable.
- Add or update tests that would catch regressions in socket ref validation behavior.

## Acceptance Criteria
- Measured runtime for `SocketRefSanityStrategy.run` decreases on the deep_layers build profile.
- Phase 6 still completes with identical validation outputs on existing tests (user-run).
- Added tests cover the optimized path and any new edge cases.

## Steps / Checklist
- [x] Inspect `SocketRefSanityStrategy.run` and identify the dominant loop(s).
- [x] Document current algorithm and identify redundant operations.
- [x] Propose a minimal optimization and get user approval.
- [x] Implement optimization with rich docstrings/comments.
- [ ] Add focused unit tests for the optimized behavior.
- [ ] Re-run the direct benchmark and record updated timing (user-run).

## Deliverables
- Optimized `SocketRefSanityStrategy`.
- Tests covering the optimized behavior.
- Benchmark comparison summary.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/system/validation/socket_ref_sanity_strategy.py
- src/melder/spellbook/spell_crafter/spell_crafter.py (only if strategy wiring needs adjustment)
- tests/unit/melder/spellbook/spell_crafter/system/ (new or updated tests)
- benchmarks/conjure/profile_conjure_build_direct.py (only if needed for measurement clarity)

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe benchmarks\conjure\profile_conjure_build_direct.py`
  - `pytest -q tests\unit\melder\spellbook\spell_crafter\system`

## Risks / Rollback Notes
- Risk: subtle validation regressions if optimization changes traversal semantics.
- Mitigation: add unit tests that assert expected diagnostics and coverage for typical socket refs.

## Decision Log
- Baseline hotspot recorded from profile run provided by user (2026-01-31).

## Context / Handoff Summary
Implemented a local-set based validation path in `SocketRefSanityStrategy.run` to avoid repeated list membership checks. Next: consider whether additional tests are needed (behavior should be unchanged) and re-run the direct benchmark to confirm the runtime reduction.
