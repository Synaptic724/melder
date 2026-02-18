

# Epic: Phase 12 Codegen and CreationContext Discovery Program

## Metadata
- Epic ID: EPIC-2026-02-17-phase12-codegen-creation-context-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T22:30:54Z
- Updated: 2026-02-17T22:32:40Z
- Target Window: 2026-Q1
- Related Program/Initiative: Phase 12 runtime performance hardening

## Problem / Opportunity
Phase 12 execution and `creation_context` dispatch are performance-critical runtime
surfaces, but we do not yet have a discovery package that explicitly ranks
mid-risk/mid-reward vs high-risk/high-reward optimization paths with a consistent
pre/post measurement contract.

The benchmark harness already supports route matrix timing, route-level cProfile
signals, baseline diffing, weighted cProfile/time scoring, and optional P-core
affinity pinning. We should use that capability to drive discovery before selecting
implementation work.

## MRP Alignment (Most Reasonable Product)
This epic builds a trustworthy discovery foundation for performance changes:
repeatable measurements, explicit risk lanes, and evidence-backed prioritization.
That avoids speculative rewrites and keeps Phase 12 optimization aligned to the
runtime contract.

## Ticket Contract
- ENTRY_GATE: user certified `active`; routing row points to the linked story.
- EXECUTION_BOUNDARY: discovery only for Phase 12 and `creation_context`; no broad
  refactor beyond benchmark instrumentation and evidence capture.
- DEPENDENCIES: `run_codegen_benchmark_deltas.py`, P-core affinity helper,
  Phase 12 executor emitters, `creation_context` runtime dispatch.
- EXIT_GATE: linked story accepted, discovery outputs archived, next tranche
  recommendation approved.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if baseline noise prevents clear
  ranking or if high-risk lane requires public contract changes.

## Goals (Outcomes)
- Establish a reproducible pre/post benchmark protocol for discovery.
- Produce two ranked candidate sets:
  mid-risk/mid-reward and high-risk/high-reward.
- Generate an evidence-backed recommendation for the first implementation tranche.

## Non-Goals (Explicit Exclusions)
- Immediate full implementation of all candidates in this epic.
- Public API shape changes for `Conduit.meld(...)` or Spellbook APIs.
- Repo-wide optimization sweeps outside Phase 12 and `creation_context`.

## Scope Boundaries
- In scope:
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
  - `benchmarks/p_core_affinity/p_core_affinity.py`
- Out of scope:
  - Unrelated spellbook/aether subsystems.
  - Packaging/release changes.
  - Non-performance feature work.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user explicitly requested immediate kickoff for discovery
  planning focused on Phase 12 and `creation_context`.

## Success Metrics
- Pre/post reports exist with baseline delta and weighted score sections.
- Discovery matrix includes at least:
  two mid-risk/mid-reward candidates and two high-risk/high-reward candidates.
- Weighted score uses 0.75 cProfile and 0.25 timing inputs for route ranking.

## Requirements (Functional + Non-Functional)
- Define and execute discovery in two lanes:
  mid-risk/mid-reward and high-risk/high-reward.
- Use `run_codegen_benchmark_deltas.py` for pre/post measurements.
- Use weighted scoring at 75% cProfile and 25% timing.
- Capture and report affinity status when optional P-core pinning is enabled.
- Keep changes scoped, reversible, and benchmark-evidenced.

## Constraints / Assumptions
- Windows affinity pinning is best-effort and may fall back safely.
- Benchmark variance may require repeated samples before ranking confidence.
- Discovery must preserve runtime correctness contracts.

## Benchmark Contract (Required)
- Pre-check and post-check must use the same sample/warmup counts and route set.
- Weighted decision input must remain:
  - cProfile weight: `--weighted-cprofile-weight 0.75`
  - timing weight: `--weighted-time-weight 0.25`
- Pre-check command:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1 --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json`
- Post-check command (must reference pre baseline):
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1 --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --pin-p-cores --baseline-path benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json --output-path benchmarks/testing_other_di/results/codegen_phase12_discovery_post.json`
- Evidence split for ranking:
  - 75% from `route_profile_report` cProfile call-density deltas.
  - 25% from `route_matrix_report` timing medians/ratios.
- Affinity policy:
  - keep P-core pinning enabled with `--pin-p-cores` when available.
  - always record `affinity` status from the benchmark report.

## Dependencies / External References
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/p_core_affinity/p_core_affinity.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Baseline and lane framing complete.
- [ ] Milestone 2: Ranked discovery recommendation complete.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-17-phase12-codegen-creation-context-discovery -
      run risk-lane discovery and benchmark comparisons.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-17-phase12-codegen-creation-context-discovery.
- [ ] Task: Confirm weighted scoring contract (0.75 cProfile / 0.25 timing)
      is applied in pre/post runs.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Linked story is accepted by user with evidence-backed findings.
- Discovery output clearly separates mid-risk and high-risk candidate lanes.
- Pre/post benchmark artifacts and weighted score interpretation are documented.

## Risks / Mitigations
- Risk: benchmark noise hides true deltas.
  - Mitigation: use repeated samples and keep baseline/post command parity.
- Risk: high-risk lane implies contract shifts.
  - Mitigation: force explicit decision gate before implementation.
- Risk: affinity pin assumptions are over-applied.
  - Mitigation: record affinity status from benchmark report on each run.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery baseline command:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1 --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json`
- Discovery post command:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1 --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --pin-p-cores --baseline-path benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json --output-path benchmarks/testing_other_di/results/codegen_phase12_discovery_post.json`

## Rollout / Adoption Plan
- Convert the selected lane into implementation story/task tickets after user
  review of discovery outputs.

## Open Questions
- Which route should be primary for tranche 1:
  warm root, targeted override, or mixed lane?
- What weighted-score regression threshold should block merge decisions?

## Decision Log
- 2026-02-17: Use weighted route scoring with cProfile=0.75 and timing=0.25 as
  the decision baseline for this discovery epic.
- 2026-02-17: Keep P-core pinning enabled for benchmark runs when supported and
  record the returned affinity status in artifacts.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_pre.json`
  - `benchmarks/testing_other_di/results/codegen_phase12_discovery_post.json`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: on epic closure, retain final artifacts and prune transient
  intermediates if superseded.

## Notes
- DATETIME: 2026-02-17T22:30:54Z
  TYPE: DECISION
  CLAIM: Discovery will use the existing weighted benchmark harness, optional
    P-core pinning, and Phase 12 plus `creation_context` runtime surfaces only.
  EVIDENCE:
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:353-354`
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:370-370`
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1338-1342`
  - `benchmarks/p_core_affinity/p_core_affinity.py:378-385`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py:282-331`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:112-163`
  IMPACT: Discovery is bounded, measurable, and aligned to the requested risk
    framing.
  NEXT: Create and route the linked story to begin structured discovery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic is now active and scoped to discovery only. The linked story is the single
execution lane for baseline capture, risk-lane analysis, and recommendation output.