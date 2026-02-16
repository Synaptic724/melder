# Story: Deep Phase12 No-Overrides Codegen Strategy Discovery

## Metadata
- Story ID: STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## User Narrative
As a runtime/codegen maintainer, I want deep structural analysis of
`phase12_no_overrides_executor.py`, so we improve generated-executor quality
instead of repeatedly pushing low-yield runtime micro-slices.

## Value / MRP Alignment
This lane targets emitter architecture and generated function shape:
- compile lifecycle,
- executor size/branch density,
- transient-vs-step-plan generation strategy.

## Requirements (Functional)
- Map compile/execution path for no-overrides emitters.
- Identify deep generated-shape costs (signature width, branch fan-out, per-step boilerplate).
- Propose strategy alternatives with explicit tradeoffs.

## Requirements (Non-Functional)
- Discovery-only, no runtime contract changes in this story.
- Keep UNKNOWN discipline for unevidenced runtime-frequency claims.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- Step-plan and transient unrolled emitter paths.
- Out of scope:
- Overrides emitter internals.
- Non-codegen runtime API changes.

## Dependencies / Related Work
- `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md`
- `context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Tasks (Implementation Checklist)
- [x] Open and maintain low/medium/high risk-lane discovery tasks for this story.
- [ ] Quantify step-plan generated function growth versus plan size.
- [ ] Evaluate transient unrolled signature strategy and dependency-array prebind model.
- [ ] Define candidate generator strategies (shape-family split, cold-path extraction, selective helper fallback).
- [ ] Produce validation experiment plan and user-decision criteria (`DECISION_REQUEST` triggers + keep/revert options).
- [ ] Enforce benchmark gate for every follow-on optimization slice (pre-test baseline, post-test cadence, and mandatory `DECISION_REQUEST` escalation on failed/non-winning deltas).
- [ ] Execute `TASK-2026-02-16-phase12-no-overrides-low-risk-discovery`.
- [x] Execute `TASK-2026-02-16-phase12-no-overrides-medium-risk-discovery`.
- [x] Execute `TASK-2026-02-16-phase12-no-overrides-high-risk-discovery`.

## Acceptance Criteria
- At least three deep findings are documented with evidence.
- At least two new strategy candidates are recorded with tradeoffs.
- A concrete experiment plan is documented for follow-on implementation.

## Validation / Test Plan
- Discovery-only in this story.
- Follow-on validation lanes (for implementation):
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; $env:DI_PIN_P_CORES='1'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; $env:DI_PIN_P_CORES='1'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`

## Benchmark Gate (Mandatory)
- Pre-test baseline (before any code edit):
  - Run unit suite:
    - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py -q`
  - Run benchmark cadence using the same suites used throughout wave-1:
    - `$env:PYTHONPATH='src'; $env:DI_PIN_P_CORES='1'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (run twice sequentially)
    - `$env:PYTHONPATH='src'; $env:DI_PIN_P_CORES='1'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (run twice sequentially)
  - Capture medians and write baseline artifact/delta context against:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt`
- Post-test (after each candidate edit):
  - Re-run the same unit + benchmark cadence.
  - Emit a candidate delta artifact under:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`
- Decision gate (non-negotiable):
  - If unit or benchmark command fails, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - If measured delta is non-winning versus retained checkpoint, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - Emit `RESULT: DECISION_REQUEST` with failure/non-winning evidence and explicit keep/revert options before any state change.
  - If user selects revert, run one full post-revert validation pass:
    - unit suite once, fast cprofile once, overrides cprofile once.
  - Emit post-revert validation artifact and explicit result-announce note (`RESULT: REVERTED` + reason + artifact path).
- Retain gate:
  - Retain only candidates that pass validation, satisfy checkpoint comparison criteria, and have explicit user keep direction.
  - Emit explicit result-announce note (`RESULT: RETAINED` + median deltas + artifact path).

## Risk-Lane Discovery Queue (Required Reference)
Process rule:
- Before each new investigation or implementation iteration, select one task from this queue and reference its task ID in `## Notes`.
- Do not run ad-hoc candidate exploration outside this queue unless a `DECISION` note expands scope first.

| Risk lane | Status | Task | Focus |
|---|---|---|---|
| low | ready | `context_compass/tasks/2026-02-16_phase12_no_overrides_low_risk_discovery_task.md` | contract-safe no-overrides emitter candidates |
| medium | done | `context_compass/tasks/completed/2026-02-16_phase12_no_overrides_medium_risk_discovery_task.md` | medium-reward generated-shape and compile-lifecycle candidates |
| high | ready | `context_compass/tasks/2026-02-16_phase12_no_overrides_high_risk_discovery_task.md` | architectural no-overrides redesign discovery |

## Risks / Mitigations
- Risk: emitter simplification may increase runtime branching.
  Mitigation: preserve shape-specialization principles as hard constraints.
- Risk: optimization bias from benchmark noise.
  Mitigation: keep frozen-checkpoint deltas and repeated-cadence gates.

## Open Questions
- What plan sizes trigger generated-function quality degradation?
- Should transient and step-plan paths share more emitter infrastructure?

## Decision Log
- 2026-02-16: Story opened per user direction for deeper no-overrides codegen discovery.

## Notes
- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: No-overrides emitters compile generated source using `compile(..., "exec")` + `exec(...)` and require `_phase12_executor` to be callable.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:438-466
  IMPACT: Compile lifecycle strategy is a first-class optimization target, not just runtime helper internals.
  NEXT: evaluate whether code-object reuse/caching can reduce repeated compile overhead safely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Step-plan source emits one large monolithic executor with per-step locals and nested existence/lock routing blocks in generated code.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-520, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-725
  IMPACT: Generated-function size and branch density likely scale with step count, making code-shape strategy critical.
  NEXT: build size/branch metrics per generated executor to rank structural strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Transient unrolled source emits a very wide signature with many dependency arrays and an unrolled call-expression block with per-step exception index tracking.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1421
  IMPACT: Signature width and emitted-call expansion are deep strategic dimensions that were not the focus of prior micro-optimizations.
  NEXT: compare alternate unrolled-shape strategies (segmenting, split executors, cold-path helper extraction).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: UNKNOWN
  CLAIM: Current production compile frequency for step-plan vs transient emitters is not yet measured.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:55-147, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:151-238
  IMPACT: Prioritization between compile-lifecycle and generated-runtime shape improvements remains uncertain without frequency data.
  NEXT: define instrumentation plan for compile path frequency and executor reuse rate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Created a mandatory low/medium/high risk-lane queue for no-overrides discovery and required iterations to begin from a queued task ID.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:85-96, context_compass/tasks/2026-02-16_phase12_no_overrides_low_risk_discovery_task.md:1-78, context_compass/tasks/completed/2026-02-16_phase12_no_overrides_medium_risk_discovery_task.md:1-78, context_compass/tasks/2026-02-16_phase12_no_overrides_high_risk_discovery_task.md:1-77
  IMPACT: Future no-overrides iterations can run from a persistent, risk-labeled queue rather than ad-hoc path hunting.
  NEXT: Choose the next queued task and log the task ID before starting the next tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: No-overrides low/medium/high tasks are now fully loaded with candidate backlogs and reusable ops-reference sections for repeated execution loops.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_no_overrides_low_risk_discovery_task.md:35-84, context_compass/tasks/completed/2026-02-16_phase12_no_overrides_medium_risk_discovery_task.md:35-85, context_compass/tasks/2026-02-16_phase12_no_overrides_high_risk_discovery_task.md:35-84
  IMPACT: Iteration setup is now externalized in tickets, reducing repeated planning overhead.
  NEXT: Execute `NO-L1` first, then `NO-M1` if low-risk deltas plateau.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Deep no-overrides discovery opened with initial evidence on compile path, step
emitter size/branch density, and transient unrolled signature strategy. Next
step is option ranking with measurable hypotheses. Low/medium/high risk-lane
discovery tasks are now opened and serve as the required iteration queue.
Medium-risk ticket is turned in and marked done.
