# Task: Codegen Snapshot High-Repeat Average Runner

## Metadata
- Task ID: TASK-2026-02-16-codegen-snapshot-high-repeat-average
- Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Create a benchmark snapshot runner that is separate from cProfile and reports
high-repeat average timings per snapshot label for the same Melder fast/override
graph lanes.

## Scope Boundaries
- In scope:
- `benchmarks/testing_other_di/run_codegen_snapshot_averages.py`
- Reuse existing fast/override graph builders from current benchmark modules.
- Average and median reporting with configurable repeat counts.
- Out of scope:
- cProfile artifact generation paths (`*.prof`, hotspot/call-chain JSON).
- Runtime code changes in `src/melder/**`.

## Steps / Checklist
- [ ] Create dedicated non-cProfile snapshot runner with CLI flags.
- [ ] Use same fast/override benchmark graph lanes (`solo, shallow, wide, diamond`).
- [ ] Implement high-repeat timing loop (`--iterations` default `1000`, support `10000`).
- [ ] Emit durable JSON + text snapshot summaries under `benchmarks/testing_other_di/profiles/`.
- [ ] Run a smoke validation of the new runner command and record artifact path.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- New executable snapshot runner (non-cProfile).
- Snapshot summary artifacts with averages for fast and override timing lanes.
- Documented command usage for 1000 and 10000 iteration modes.

## Files / Paths Impacted
- `benchmarks/testing_other_di/run_codegen_snapshot_averages.py`
- `context_compass/attention_board.md`
- `context_compass/tasks/completed/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md`

## Validation
- Not run.
- Planned commands:
  - `$env:PYTHONPATH='src'; python benchmarks/testing_other_di/run_codegen_snapshot_averages.py --iterations 100 --warmup 25`
  - `$env:PYTHONPATH='src'; python benchmarks/testing_other_di/run_codegen_snapshot_averages.py --iterations 1000 --warmup 100`
  - Optional heavy run:
    - `$env:PYTHONPATH='src'; python benchmarks/testing_other_di/run_codegen_snapshot_averages.py --iterations 10000 --warmup 200`

## Risks / Rollback Notes
- Risk: high iteration counts increase runtime and can be noisy under background load.
- Mitigation: keep warmup configurable and report sample count + min/max/stddev.
- Rollback: remove runner script if it fails to produce stable artifacts.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: User directed a process shift from cProfile timing snapshots to high-repeat average snapshots; 1000 iterations is required and 10000 should be supported.
  EVIDENCE: context_compass/tasks/completed/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:169-177, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:634-662, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:603-631
  IMPACT: Benchmark gating will have a lower-noise timing signal for retain/revert decisions.
  NEXT: Implement `run_codegen_snapshot_averages.py` with repeat-count CLI and output artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task opened to create a non-cProfile benchmark snapshot process with high-repeat
averaging for the existing Melder fast/override timing lanes.
