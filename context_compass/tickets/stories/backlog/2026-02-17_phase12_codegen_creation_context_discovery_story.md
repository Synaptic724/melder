# Story: Phase 12 and CreationContext Discovery Lanes

## Metadata
- Story ID: STORY-2026-02-17-phase12-codegen-creation-context-discovery
- Epic: EPIC-2026-02-17-phase12-codegen-creation-context-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T22:32:54Z
- Updated: 2026-02-17T22:41:06Z

## User Narrative
As a runtime maintainer, I want an evidence-backed discovery pass for Phase 12
and `creation_context`, so that we can choose the next optimization tranche by
measured risk/reward instead of guesswork.

## Value / MRP Alignment
This story strengthens the core runtime by defining a repeatable benchmark and
profiling contract, then mapping optimization candidates into clear risk lanes.
It keeps optimization work durable and avoids speculative rewrites.

## Ticket Contract
- ENTRY_GATE: active board row routes to this story; epic is in progress.
- EXECUTION_BOUNDARY: discovery-only analysis and benchmark evidence focused on
  Phase 12 executors and `creation_context`.
- DEPENDENCIES: benchmark harness with weighted scoring, optional P-core pin,
  and current Phase 12/creation_context runtime code.
- EXIT_GATE: user accepts risk-lane recommendation package with pre/post artifacts.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if data cannot separate risk
  lanes or if high-risk lane implies contract shifts.

## Requirements (Functional)
- Produce discovery findings in two lanes:
  - Mid-risk / mid-reward candidates.
  - High-risk / high-reward candidates.
- Capture pre and post benchmark reports using the same command contract.
- Keep weighted ranking fixed at:
  - cProfile contribution: 75%
  - timing contribution: 25%
- Record benchmark affinity status when P-core pinning is requested.
- Tie each candidate to concrete file/symbol evidence.

## Requirements (Non-Functional)
- Benchmark runs must be reproducible (same sample and warmup config).
- No public API shape changes during discovery.
- Notes must follow UNKNOWN-first evidence discipline.

## Scope Boundaries
- In scope:
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
  - `benchmarks/p_core_affinity/p_core_affinity.py`
- Out of scope:
  - Unrelated runtime subsystems.
  - Broad refactors outside discovery evidence capture.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user requested immediate story kickoff for Phase 12 and
  `creation_context` discovery.

## Dependencies / Related Work
- `EPIC-2026-02-17-phase12-codegen-creation-context-discovery`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/p_core_affinity/p_core_affinity.py`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-17-phase12-mid-risk-discovery - profile and rank
      low-complexity changes in creation-context dispatch and no-overrides paths.
- [ ] Task: TASK-2026-02-17-phase12-high-risk-discovery - profile and rank
      high-impact codegen shape changes for override/no-override executors.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Pre-benchmark artifact exists and includes:
  - `gate_report`, `route_matrix_report`, `route_profile_report`.
- Discovery notes include at least two candidates in each risk lane.
- Post-benchmark artifact exists and includes baseline delta reporting.
- Weighted-score comparison uses 0.75 cProfile + 0.25 timing inputs.
- Affinity status for benchmark runs is recorded in artifacts.

## Validation / Test Plan
- Pre-check:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1 --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json`
- Post-check:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1 --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --pin-p-cores --baseline-path benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json --output-path benchmarks/testing_other_di/results/codegen_phase12_discovery_post.json`

## UX / API / Data Notes
- No UX scope.
- API surface remains unchanged during discovery.
- Data artifacts are benchmark JSON reports and derived candidate notes.

## Risks / Mitigations
- Risk: benchmark variance obscures candidate ranking.
  - Mitigation: keep command parity and use median-based comparisons.
- Risk: high-risk lane expands beyond intended scope.
  - Mitigation: enforce explicit scope gate and decision escalation.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Which route family should be tranche-1 target:
  `warm_root_ns`, `warm_override_targeted_ns`, or `warm_mixed_ns`?
- What minimum weighted-score gain should be required before implementation?

## Decision Log
- 2026-02-17: use weighted benchmark scoring at 75% cProfile and 25% timing.
- 2026-02-17: include optional P-core pinning path via benchmark command flag.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_post.json`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: on story close, retain accepted baseline/post artifacts.

## Notes
- DATETIME: 2026-02-17T22:32:54Z
  TYPE: PLAN
  CLAIM: Discovery will use weighted route scoring from the codegen benchmark
    harness and focus candidate analysis on Phase 12 executor generation and
    `creation_context` compiled dispatch lanes.
  EVIDENCE:
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:353-354`
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1338-1342`
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1280-1307`
  - `benchmarks/p_core_affinity/p_core_affinity.py:378-385`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py:282-331`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py:1096-1229`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:112-163`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:636-667`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2647-2674`
  IMPACT: The story has a concrete measurement and evidence plan before any
    optimization changes are proposed.
  NEXT: Create the two child discovery tasks and capture the pre benchmark artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-17T22:36:37Z
  TYPE: FACT
  CLAIM: Mid-risk and high-risk child discovery task tickets are now created and
    linked in the story execution checklist.
  EVIDENCE:
  - `context_compass/tickets/tasks/backlog/2026-02-17_phase12_mid_risk_discovery_task.md:4-12`
  - `context_compass/tickets/tasks/backlog/2026-02-17_phase12_high_risk_discovery_task.md:4-12`
  - `context_compass/tickets/stories/backlog/2026-02-17_phase12_codegen_creation_context_discovery_story.md:70-74`
  IMPACT: Story execution can move from planning to baseline measurement.
  NEXT: run the pre benchmark command and capture the baseline artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-17T22:37:33Z
  TYPE: MEASURE
  CLAIM: Pre benchmark baseline ran successfully with weighted 75/25 settings
    and P-core pinning enabled; gate and route checks passed.
  EVIDENCE:
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json:2-15`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json:105-107`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json:127-139`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json:141-160`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json:162-170`
  IMPACT: Discovery now has a pinned and reproducible baseline for candidate
    comparison.
  NEXT: start mid-risk candidate identification in `creation_context` and
    no-overrides Phase 12 codegen paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-02-17T22:41:06Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Initial risk-lane candidate set is drafted: mid-risk MR-1/MR-2 for
    spellspace no-overrides path efficiency, plus high-risk HR-1/HR-2 for
    kwargs/codegen-shape specialization and override precompile strategy.
  EVIDENCE:
  - `context_compass/tickets/tasks/backlog/2026-02-17_phase12_mid_risk_discovery_task.md:148-170`
  - `context_compass/tickets/tasks/backlog/2026-02-17_phase12_high_risk_discovery_task.md:121-148`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json:551-557`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json:588-595`
  IMPACT: Discovery now has concrete hypothesis lanes to validate against post
    benchmark deltas.
  NEXT: execute MR-1 feasibility validation first and decide whether to prototype.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story is active with benchmark contract and pre baseline artifact captured at
`benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json`.
Risk-lane candidates are now documented in task notes. Next action is
MR-1 feasibility validation and prototype decisioning before any high-risk
activation.
