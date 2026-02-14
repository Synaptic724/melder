# Task: Add cProfile harness for deep transient DI benchmark

## Metadata
- Task ID: TASK-2026-01-30-profile-deep-all-di
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Create a standalone profiling script that mirrors the deep transient DI benchmark and emits cProfile summaries per library without relying on pytest.

## Problem / Opportunity
We need a fast, repeatable way to see where time is spent inside each DI library so we can target the next 500us of savings.

## Context
The existing benchmark is a pytest test. We want a direct script that can be run quickly and outputs cProfile summaries for each library.

## MRP Alignment
This supports performance engineering on the core resolution path without changing public APIs or runtime behavior.

## Goals
- Provide a new profiling script that mirrors the transient-only deep DI benchmark.
- Emit cProfile summaries per library with configurable in-file iteration counts.
- Avoid modifying the existing test file.

## Non-Goals
- Do not change benchmark logic or semantics.
- Do not add tests for this change.

## Scope Boundaries
- In scope: new profiling script, minimal shared helpers copied from benchmark.
- Out of scope: changes to existing tests or runtime behavior.

## Requirements
- In-file iteration variable (no CLI requirements).
- cProfile embedded with per-library summaries.
- Use library logging (no print calls).
- Fast enough for repeated local runs.

## Acceptance Criteria
- Script runs without pytest and profiles selected libraries.
- cProfile summaries show the hottest functions for each library.
- Iterations can be changed by editing the file.

## Steps / Checklist
- [x] Draft profiling task ticket.
- [x] Add profiling script with cProfile and per-library summary output.
- [ ] Verify script imports and runs (user-run).

## Deliverables
- New profiling script file.

## Files / Paths Impacted
- benchmarks/testing_other_di/profile_deep_all_di_transient_only_no_singletons.py

## Validation
- Not run.
- Recommended command:
  - python benchmarks/testing_other_di/profile_deep_all_di_transient_only_no_singletons.py

## Risks / Mitigations
- Risk: noisy profile output. Mitigation: configurable top-N and sorting.
- Risk: missing optional libs. Mitigation: skip with clear log message.

## Decision Log
- Use an in-file iteration variable instead of CLI arguments.
- Do not modify pytest benchmark; add a standalone script.

## Context / Handoff Summary
Ticket created for a standalone cProfile harness that mirrors the deep transient DI benchmark and emits per-library summaries.
