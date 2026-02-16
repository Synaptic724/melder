# Story: Deep CreationContext Codegen Strategy Discovery

## Metadata
- Story ID: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## User Narrative
As a runtime/codegen maintainer, I want deep structural analysis of
`creation_context_codegen.py`, so that we optimize code generation strategy
rather than only tuning runtime micro-branches.

## Value / MRP Alignment
This discovery lane targets generator architecture quality:
- template explosion risk,
- compile/exec lifecycle strategy,
- emitted-source reuse opportunities.

## Requirements (Functional)
- Audit template compile topology and route-key matrix depth.
- Identify high-confidence structural opportunities with measurable hypotheses.
- Document keep/defer risks before any implementation patching.

## Requirements (Non-Functional)
- No public API changes in this story.
- Evidence-first findings only; unknowns remain explicit.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- Template selection, emitted-source construction, and compile strategy.
- Out of scope:
- Runtime behavior changes in `creation_context.py`.
- Non-CreationContext Phase12 emitters.

## Dependencies / Related Work
- `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md`
- `context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Tasks (Implementation Checklist)
- [x] Open and maintain low/medium/high risk-lane discovery tasks for this story.
- [ ] Map current template matrix and specialization dimensions.
- [ ] Quantify compile-time template fan-out and identify dedupe opportunities.
- [ ] Propose 2-3 deep strategy options with tradeoffs (lazy compile, merged templates, code-object caching).
- [ ] Define validation experiment plan for selected option.
- [ ] Enforce benchmark gate for every follow-on optimization slice (pre-test baseline, post-test cadence, and mandatory `DECISION_REQUEST` escalation on failed/non-winning deltas).
- [x] Execute `TASK-2026-02-16-codegen-snapshot-average-process` to standardize averaged snapshot measurements (1000 default, 10000 optional) before next code slice.
- [x] Execute `TASK-2026-02-16-creationcontext-codegen-low-risk-discovery`.
- [x] Execute `TASK-2026-02-16-creationcontext-codegen-medium-risk-discovery`.
- [ ] Execute `TASK-2026-02-16-creationcontext-codegen-high-risk-discovery`.

## Acceptance Criteria
- Story documents at least three deep codegen findings with concrete evidence.
- At least two non-superficial strategy candidates are defined with tradeoffs.
- A measurable next-step experiment plan is recorded.

## Validation / Test Plan
- Discovery-only: no runtime edits in this story.
- Validation command recommendations for follow-on implementation:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -q`
  - `$env:PYTHONPATH='src'; $env:DI_PIN_P_CORES='1'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; $env:DI_PIN_P_CORES='1'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`

## Benchmark Gate (Mandatory)
- Pre-test baseline (before any code edit):
  - Run unit suite:
    - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -q`
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
| low | done | `context_compass/tasks/completed/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md` | contract-safe micro and compile-prep efficiency candidates |
| medium | done | `context_compass/tasks/completed/2026-02-16_creationcontext_codegen_medium_risk_discovery_task.md` | medium-reward template/compile strategy candidates |
| high | ready | `context_compass/tasks/2026-02-16_creationcontext_codegen_high_risk_discovery_task.md` | architectural redesign discovery with explicit guardrails |

## Risks / Mitigations
- Risk: overfitting strategy to source shape without compile-frequency evidence.
  Mitigation: keep compile-frequency as explicit UNKNOWN until measured.
- Risk: reducing template count may reintroduce runtime branching.
  Mitigation: preserve branch-depth constraints as a non-functional gate.

## Open Questions
- What is the actual compile frequency of CreationContext templates per session?
- Which template dimensions can be merged without runtime regression?

## Decision Log
- 2026-02-16: Story opened per user direction to run deeper codegen discovery (not superficial or medium-level tuning).

## Notes
- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: CreationContext codegen compiles emitted template source through `compile(..., "exec")` + `exec(...)` for both overrides-only and no-overrides-only paths.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-315, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:329-358
  IMPACT: Compile strategy is dynamic-source based; deep optimization can target compile lifecycle and source reuse.
  NEXT: quantify fan-out and candidate compile-caching shapes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Module-level template constants compile a large static matrix of route/return/fast-mode combinations at import time.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1015
  IMPACT: Startup/import-time compile fan-out is a deep strategic lever not targeted by runtime micro-slices.
  NEXT: classify which matrix dimensions are semantically required versus mergeable.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Emitted template source is assembled as string line arrays and joined per template factory generation.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420
  IMPACT: Structural source normalization/deduplication can be applied without changing public APIs.
  NEXT: draft candidate source-shape simplification options and expected performance impact vectors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: UNKNOWN
  CLAIM: Runtime compile-frequency and cache-hit behavior for CreationContext templates under real workloads is not yet measured.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-315, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1015
  IMPACT: We cannot prioritize lazy-compile versus precompile strategy confidently without frequency data.
  NEXT: define instrumentation plan to measure compile invocations and first-use latency.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Created a mandatory low/medium/high risk-lane task queue for this story and required each iteration to start from one queued task ID.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:85-96, context_compass/tasks/completed/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:1-78, context_compass/tasks/completed/2026-02-16_creationcontext_codegen_medium_risk_discovery_task.md:1-78, context_compass/tasks/2026-02-16_creationcontext_codegen_high_risk_discovery_task.md:1-77
  IMPACT: Iterations are now deterministic and no longer depend on hunt-and-seek rediscovery.
  NEXT: Select one queued task and record its task ID in notes before the next investigation tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: All three CreationContext risk-lane tasks now include expanded candidate backlogs plus reusable ops-reference steps so future iterations can run directly from ticket ops.
  EVIDENCE: context_compass/tasks/completed/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:38-86, context_compass/tasks/completed/2026-02-16_creationcontext_codegen_medium_risk_discovery_task.md:38-85, context_compass/tasks/2026-02-16_creationcontext_codegen_high_risk_discovery_task.md:38-85
  IMPACT: CreationContext lane can execute multiple iterations without repeating strategy setup.
  NEXT: Start with `CC-L1` or `CC-M1` depending on risk preference and publish `RESULT` note after first run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Before additional CreationContext code slices, the story now requires a dedicated non-cProfile snapshot process task so pre/post decisions use averaged outcomes with high-repeat support.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:45-53, context_compass/tasks/completed/2026-02-16_codegen_snapshot_average_process_task.md:1-102
  IMPACT: Candidate keep/revert decisions will be based on stable average metrics rather than single-run variance.
  NEXT: Complete the snapshot-process task and apply it as the default benchmark gate for the next candidate iteration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Deep discovery opened for `creation_context_codegen.py` focusing on compile
topology, template fan-out, and emitted-source strategy. Next step is option
design with measurable hypotheses before implementation. Low/medium/high
risk-lane discovery tasks are now opened and must be used as the iteration
entry queue. Medium-risk ticket is turned in and marked done.
